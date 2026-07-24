"""
Pulls data from yfinance and writes it into Supabase.
Run this manually (`python -m app.ingestion`) whenever you want fresh data -
daily is plenty for this use case. The API never calls yfinance directly;
it only ever reads from Supabase, which keeps the dashboard fast and
insulated from yfinance rate limits.

Uses curl_cffi to impersonate a real Chrome browser's TLS fingerprint,
which avoids most of Yahoo's bot-detection blocking. Price history for
all 20 companies is fetched in a single batched request (not 20 separate
ones) to minimize load. Every network call has a hard timeout so a single
hung request can't block the whole run.
"""
import time
import concurrent.futures as cf
import yfinance as yf
from curl_cffi import requests as curl_requests
from datetime import date

from app.db import supabase
from app.companies_seed import COMPANIES

session = curl_requests.Session(impersonate="chrome")
TICKERS = [c["ticker"] for c in COMPANIES]
TIMEOUT_SECS = 30


def call_with_timeout(fn, timeout=TIMEOUT_SECS):
    """Run fn() but give up after `timeout` seconds instead of hanging forever."""
    with cf.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fn)
        return future.result(timeout=timeout)


def with_retry(fn, retries=3, delay=15):
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


def ingest_all_price_history(period: str = "1y"):
    """Fetch OHLCV history for ALL tickers in a single batched request."""
    print(f"Downloading {period} of price history for all {len(TICKERS)} tickers in one batch...")
    data = with_retry(lambda: yf.download(
        tickers=TICKERS,
        period=period,
        group_by="ticker",
        session=session,
        threads=False,
        progress=False,
    ))

    for ticker in TICKERS:
        try:
            df = data[ticker].dropna(how="all")
        except (KeyError, TypeError):
            print(f"  [warn] no price history returned for {ticker}")
            continue

        if df.empty:
            print(f"  [warn] no price history returned for {ticker}")
            continue

        rows = []
        for idx, row in df.iterrows():
            if row.isnull().any():
                continue
            rows.append({
                "ticker": ticker,
                "date": idx.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
            })

        if not rows:
            print(f"  [warn] no usable rows for {ticker}")
            continue

        for i in range(0, len(rows), 200):
            supabase.table("price_history").upsert(rows[i:i + 200]).execute()

        print(f"  {ticker}: upserted {len(rows)} price rows")


def ingest_fundamentals(ticker: str):
    """Fetch current fundamentals for one ticker and store today's snapshot."""
    info = with_retry(lambda: yf.Ticker(ticker, session=session).info)
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

    print()
    try:
        ingest_all_price_history()
    except Exception as e:
        print(f"[error] batched price history failed entirely: {e}")

    print("\nFetching fundamentals for each company...")
    for ticker in TICKERS:
        try:
            ingest_fundamentals(ticker)
        except Exception as e:
            print(f"  [warn] {ticker} fundamentals failed: {e}")
        time.sleep(3)

    print("\nIngestion complete.")


if __name__ == "__main__":
    run()