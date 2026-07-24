"""
Pulls price history from NSE (via nselib) and fundamentals from yfinance,
writing both into Supabase. Run manually whenever you want fresh data:

    python -m app.ingestion

The API never calls these sources directly - it only ever reads from
Supabase, which keeps the dashboard fast either way.

Price history: nselib talks to NSE directly and is confirmed working.
Fundamentals (P/E, EPS, market cap): best-effort via yfinance, since NSE
doesn't expose these as simply. If a company's fundamentals fail, it's
skipped and the dashboard just shows "N/A" for that field - not a blocker.
"""
import time
from datetime import date

from nselib import capital_market
import yfinance as yf
from curl_cffi import requests as curl_requests

from app.db import supabase
from app.companies_seed import COMPANIES

session = curl_requests.Session(impersonate="chrome")
TICKERS = [c["ticker"] for c in COMPANIES]


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


def ingest_fundamentals(ticker: str):
    """Best-effort fundamentals via yfinance. Failures are non-fatal."""
    info = yf.Ticker(ticker, session=session).info
    row = {
        "ticker": ticker,
        "as_of_date": date.today().isoformat(),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "eps": info.get("trailingEps"),
    }
    supabase.table("fundamentals").upsert([row]).execute()
    print(f"  {ticker}: fundamentals stored (P/E={info.get('trailingPE')})")


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

    print("\nFetching fundamentals (best-effort via yfinance)...")
    for ticker in TICKERS:
        try:
            ingest_fundamentals(ticker)
        except Exception as e:
            print(f"  [skip] {ticker} fundamentals unavailable: {e}")
        time.sleep(2)

    print("\nIngestion complete.")


if __name__ == "__main__":
    run()