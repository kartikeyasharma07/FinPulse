"""
Pulls data from NSE (via nsepython) and writes it into Supabase.
Run this manually (`python -m app.ingestion`) whenever you want fresh data -
daily is plenty for this use case. The API never calls NSE directly; it only
ever reads from Supabase, which keeps the dashboard fast.

Both price history and fundamentals (P/E, market cap) come from NSE's own
website via nsepython - no Yahoo Finance dependency at all, which avoids
the rate-limiting issues that source has had recently.

Every network call is wrapped with a hard timeout: if a single company's
request hangs, we skip it and move on instead of blocking the entire run.
"""
import time
import concurrent.futures as cf
from datetime import date, timedelta

import pandas as pd
from nsepython import equity_history, nse_eq

from app.db import supabase
from app.companies_seed import COMPANIES

TICKERS = [c["ticker"] for c in COMPANIES]
TIMEOUT_SECS = 25


def call_with_timeout(fn, timeout=TIMEOUT_SECS):
    """Run fn() but give up after `timeout` seconds instead of hanging forever."""
    with cf.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fn)
        return future.result(timeout=timeout)


def with_retry(fn, retries=2, delay=8):
    """Retry a flaky network call with a growing delay."""
    for attempt in range(1, retries + 1):
        try:
            return call_with_timeout(fn)
        except Exception as e:
            if attempt == retries:
                raise
            wait = delay * attempt
            print(f"  [retry] attempt {attempt} failed ({e}); waiting {wait}s")
            time.sleep(wait)


def seed_companies():
    """Insert/update the static list of 20 tracked companies."""
    print(f"Seeding {len(COMPANIES)} companies...")
    supabase.table("companies").upsert(COMPANIES).execute()
    print("Companies table up to date.")


def _find_col(row, *candidates):
    """Find the first column whose name contains one of the candidate substrings
    (case-insensitive) - NSE's raw field names vary by endpoint version."""
    for col in row.index:
        col_norm = str(col).strip().upper()
        for cand in candidates:
            if cand in col_norm:
                return row[col]
    return None


def ingest_price_history(ticker: str):
    """Fetch ~1 year of OHLCV history for one ticker from NSE and upsert it."""
    nse_symbol = ticker.replace(".NS", "")
    to_date = date.today()
    from_date = to_date - timedelta(days=365)

    df = with_retry(lambda: equity_history(
        nse_symbol, "EQ",
        from_date.strftime("%d-%m-%Y"),
        to_date.strftime("%d-%m-%Y"),
    ))

    if df is None or df.empty:
        print(f"  [warn] no price history returned for {ticker}")
        return

    rows = []
    for _, row in df.iterrows():
        try:
            date_val = _find_col(row, "TIMESTAMP", "DATE")
            open_val = _find_col(row, "OPENING_PRICE", "OPEN")
            high_val = _find_col(row, "TRADE_HIGH", "HIGH")
            low_val = _find_col(row, "TRADE_LOW", "LOW")
            close_val = _find_col(row, "CLOSING_PRICE", "LAST_TRADED_PRICE", "CLOSE")
            volume_val = _find_col(row, "TOT_TRADED_QTY", "TRADED_QTY", "VOLUME")

            if any(v is None for v in [date_val, open_val, high_val, low_val, close_val, volume_val]):
                continue

            parsed_date = pd.to_datetime(date_val).strftime("%Y-%m-%d")

            rows.append({
                "ticker": ticker,
                "date": parsed_date,
                "open": round(float(open_val), 2),
                "high": round(float(high_val), 2),
                "low": round(float(low_val), 2),
                "close": round(float(close_val), 2),
                "volume": int(float(volume_val)),
            })
        except (ValueError, TypeError):
            continue  # skip any malformed row rather than failing the whole ticker

    if not rows:
        print(f"  [warn] no usable price rows for {ticker}")
        return

    # Supabase upsert has a payload size limit - send in chunks.
    for i in range(0, len(rows), 200):
        supabase.table("price_history").upsert(rows[i:i + 200]).execute()

    print(f"  {ticker}: upserted {len(rows)} price rows")


def ingest_fundamentals(ticker: str):
    """Fetch current P/E and market cap from NSE. EPS is derived (price / P/E)
    since NSE's quote endpoint doesn't expose it directly - this is exact math,
    not an estimate."""
    nse_symbol = ticker.replace(".NS", "")
    data = with_retry(lambda: nse_eq(nse_symbol))

    pe_ratio = (data.get("metadata") or {}).get("pdSymbolPe")
    last_price = (data.get("priceInfo") or {}).get("lastPrice")
    issued_size = (data.get("securityInfo") or {}).get("issuedSize")

    market_cap = None
    if last_price and issued_size:
        market_cap = round(float(last_price) * float(issued_size), 2)

    eps = None
    if last_price and pe_ratio and float(pe_ratio) != 0:
        eps = round(float(last_price) / float(pe_ratio), 2)

    row = {
        "ticker": ticker,
        "as_of_date": date.today().isoformat(),
        "market_cap": market_cap,
        "pe_ratio": pe_ratio,
        "eps": eps,
    }
    supabase.table("fundamentals").upsert([row]).execute()
    print(f"  {ticker}: fundamentals stored (P/E={pe_ratio})")


def run():
    seed_companies()

    print("\nFetching price history from NSE for each company...")
    for ticker in TICKERS:
        print(f"\n{ticker}")
        try:
            ingest_price_history(ticker)
        except Exception as e:
            print(f"  [error] {ticker} price history failed/timed out: {e}")
        time.sleep(1)

    print("\nFetching fundamentals from NSE for each company...")
    for ticker in TICKERS:
        try:
            ingest_fundamentals(ticker)
        except Exception as e:
            print(f"  [warn] {ticker} fundamentals failed/timed out: {e}")
        time.sleep(1)

    print("\nIngestion complete.")


if __name__ == "__main__":
    run()