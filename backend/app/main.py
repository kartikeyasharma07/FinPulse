import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.db import supabase

app = FastAPI(title="FinPulse API")

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _latest_fundamentals(ticker: str):
    res = (
        supabase.table("fundamentals")
        .select("*")
        .eq("ticker", ticker)
        .order("as_of_date", desc=True)
        .limit(1)
        .execute()
    )
    return res.data[0] if res.data else None


def _latest_price(ticker: str):
    res = (
        supabase.table("price_history")
        .select("*")
        .eq("ticker", ticker)
        .order("date", desc=True)
        .limit(1)
        .execute()
    )
    return res.data[0] if res.data else None


@app.get("/")
def root():
    return {"status": "ok", "service": "FinPulse API"}


@app.get("/debug/yfinance-test")
def debug_yfinance_test():
    """
    TEMPORARY - not part of the real app. Tests whether yfinance can reach
    Yahoo Finance from Render's servers (as opposed to a local machine).
    Delete this endpoint once the network issue is diagnosed.
    """
    import yfinance as yf
    try:
        hist = yf.Ticker("RELIANCE.NS").history(period="5d")
        if hist.empty:
            return {"success": False, "reason": "empty response - no data returned"}
        return {
            "success": True,
            "rows_returned": len(hist),
            "latest_close": float(hist["Close"].iloc[-1]),
            "latest_date": str(hist.index[-1].date()),
        }
    except Exception as e:
        return {"success": False, "error_type": type(e).__name__, "error_message": str(e)}


@app.get("/companies")
def list_companies():
    """All tracked companies with their latest price snapshot."""
    companies = supabase.table("companies").select("*").execute().data
    for c in companies:
        c["latest_price"] = _latest_price(c["ticker"])
        c["fundamentals"] = _latest_fundamentals(c["ticker"])
    return companies


@app.get("/companies/{ticker}")
def get_company(ticker: str):
    """Fundamentals + latest price for a single company."""
    res = supabase.table("companies").select("*").eq("ticker", ticker).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail=f"{ticker} not found")

    company = res.data[0]
    company["latest_price"] = _latest_price(ticker)
    company["fundamentals"] = _latest_fundamentals(ticker)
    return company


@app.get("/companies/{ticker}/history")
def get_history(ticker: str, days: int = Query(365, ge=1, le=1825)):
    """OHLCV history for one company, most recent `days` calendar days."""
    res = (
        supabase.table("price_history")
        .select("*")
        .eq("ticker", ticker)
        .order("date", desc=True)
        .limit(days)
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail=f"No price history for {ticker}")

    return list(reversed(res.data))  # oldest -> newest, easier for charting


@app.get("/compare")
def compare(tickers: str = Query(..., description="Comma-separated tickers, e.g. TCS.NS,INFY.NS")):
    """Aligned history + latest fundamentals for 2-4 companies."""
    ticker_list = [t.strip() for t in tickers.split(",") if t.strip()]
    if not (2 <= len(ticker_list) <= 4):
        raise HTTPException(status_code=400, detail="Provide between 2 and 4 tickers")

    result = []
    for ticker in ticker_list:
        history = (
            supabase.table("price_history")
            .select("date, close")
            .eq("ticker", ticker)
            .order("date", desc=True)
            .limit(365)
            .execute()
            .data
        )
        result.append({
            "ticker": ticker,
            "history": list(reversed(history)),
            "fundamentals": _latest_fundamentals(ticker),
        })
    return result


@app.get("/market-summary")
def market_summary():
    """Aggregate stats for the landing page."""
    companies = supabase.table("companies").select("ticker").execute().data
    return {
        "tracked_companies": len(companies),
        "sectors": len(set(
            c["sector"] for c in
            supabase.table("companies").select("sector").execute().data
        )),
    }