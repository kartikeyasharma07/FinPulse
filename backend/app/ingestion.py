"""
Pulls price history from NSE (via nselib) and writes it into Supabase,
along with fundamentals from a manually filled local file. Run manually
whenever you want fresh price data:

    python -m app.ingestion

The API never calls these sources directly - it only ever reads from
Supabase, which keeps the dashboard fast either way.

Price history: nselib talks to NSE directly and is confirmed working.
Fundamentals (P/E, EPS, market cap): loaded from data/fundamentals.json,
since NSE doesn't expose these simply and Yahoo Finance blocks automated
requests. Fill that file in once (see README) - it doesn't change often,
so it doesn't need to be re-scraped on every run.
"""
import json
import re
import time
from datetime import date
from pathlib import Path

from nselib import capital_market

from app.db import supabase
from app.companies_seed import COMPANIES

TICKERS = [c["ticker"] for c in COMPANIES]
FUNDAMENTALS_FILE = Path(__file__).parent.parent / "data" / "fundamentals.json"
SUFFIX_MULTIPLIERS = {"K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}


def parse_number(value):
    """Accepts a plain number, or a string like '18.97T' / '500.5B'."""
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    value = str(value).strip().upper().replace(",", "").replace("₹", "")
    match = re.match(r"^(-?\d+\.?\d*)([KMBT]?)$", value)
    if not match:
        return None
    number, suffix = match.groups()
    return float(number) * SUFFIX_MULTIPLIERS.get(suffix, 1)


def seed_companies():
    """Insert/update the static list of 20 tracked companies."""
    print(f"Seeding {len(COMPANIES)} companies...")
    supabase.table("companies").upsert(COMPANIES).execute()
    print("Companies table up to date.")


def ingest_price_history(ticker: str):
    """Fetch ~1 year of OHLCV history for one ticker from NSE via nselib."""
    nse_symbol = ticker.replace(".NS", "")

    df = capital_market.price_volume_data(symbol=nse_symbol, period="1Y")
    if df is None or df.empty:
        print(f"  [warn] no price history returned for {ticker}")
        return

    rows = []
    for _, row in df.iterrows():
        try:
            import pandas as pd
            parsed_date = pd.to_datetime(row["Date"], format="%d-%b-%Y").strftime("%Y-%m-%d")

            def clean_num(x):
                # nselib numbers come formatted like "1,012.60" - strip commas
                return float(str(x).replace(",", ""))

            rows.append({
                "ticker": ticker,
                "date": parsed_date,
                "open": round(clean_num(row["OpenPrice"]), 2),
                "high": round(clean_num(row["HighPrice"]), 2),
                "low": round(clean_num(row["LowPrice"]), 2),
                "close": round(clean_num(row["ClosePrice"]), 2),
                "volume": int(clean_num(row["TotalTradedQuantity"])),
            })
        except (ValueError, TypeError, KeyError) as e:
            continue  # skip malformed rows rather than failing the whole ticker

    if not rows:
        print(f"  [warn] no usable rows parsed for {ticker}")
        return

    # nselib occasionally returns duplicate rows for the same date - keep
    # only the last occurrence of each date, since Postgres can't handle
    # two rows for the same conflict key within a single upsert batch.
    deduped = {r["date"]: r for r in rows}
    rows = list(deduped.values())

    for i in range(0, len(rows), 200):
        supabase.table("price_history").upsert(rows[i:i + 200]).execute()

    print(f"  {ticker}: upserted {len(rows)} price rows")


def load_fundamentals():
    """Load fundamentals from the manually filled local JSON file."""
    if not FUNDAMENTALS_FILE.exists():
        print(f"[skip] fundamentals file not found at {FUNDAMENTALS_FILE}")
        return

    with open(FUNDAMENTALS_FILE) as f:
        data = json.load(f)

    today = date.today().isoformat()

    for ticker, values in data.items():
        market_cap = parse_number(values.get("market_cap"))
        pe_ratio = parse_number(values.get("pe_ratio"))
        eps = parse_number(values.get("eps"))

        if market_cap is None and pe_ratio is None and eps is None:
            print(f"  [skip] {ticker}: no fundamentals filled in yet")
            continue

        row = {
            "ticker": ticker,
            "as_of_date": today,
            "market_cap": market_cap,
            "pe_ratio": pe_ratio,
            "eps": eps,
        }
        supabase.table("fundamentals").upsert([row]).execute()
        print(f"  {ticker}: fundamentals stored (P/E={pe_ratio}, EPS={eps})")


def run():
    seed_companies()

    print("\nFetching price history from NSE (via nselib) for each company...")
    for ticker in TICKERS:
        print(f"\n{ticker}")
        try:
            ingest_price_history(ticker)
        except Exception as e:
            print(f"  [error] {ticker} price history failed: {e}")
        time.sleep(1)  # be reasonably polite to NSE

    print("\nLoading fundamentals from data/fundamentals.json...")
    load_fundamentals()

    print("\nIngestion complete.")


if __name__ == "__main__":
    run()