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


@app.get("/debug/jugaad-test")
def debug_jugaad_test():
    """
    TEMPORARY - not part of the real app. Tests jugaad-data's live quote
    feature from Render's servers, with a hard timeout so a hang can't
    block the request forever. Delete once diagnosed.
    """
    import concurrent.futures as cf
    from jugaad_data.nse import NSELive

    def fetch():
        nse = NSELive()
        return nse.stock_quote("RELIANCE")

    try:
        with cf.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(fetch)
            data = future.result(timeout=20)

        if not data:
            return {"success": False, "reason": "empty response - no data returned"}

        price_info = data.get("priceInfo", {})
        metadata = data.get("metadata", {})
        security_info = data.get("securityInfo", {})
        return {
            "success": True,
            "top_level_keys": list(data.keys()),
            "last_price": price_info.get("lastPrice"),
            "pe_ratio": metadata.get("pdSymbolPe"),
            "issued_size": security_info.get("issuedSize"),
        }
    except cf.TimeoutError:
        return {"success": False, "reason": "timed out after 20s - request hung"}
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