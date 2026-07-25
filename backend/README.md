# FinPulse backend

FastAPI service that reads market data from Supabase and serves it as REST endpoints.

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # then fill in your Supabase URL + key
```

## 1. Create the database

In your Supabase project: SQL Editor -> New query -> paste the contents of `schema.sql` -> Run.

## 2. Fill in fundamentals (one-time, ~10 minutes)

Fundamentals (P/E, market cap, EPS) are seeded from a local file rather
than live-fetched — see the root README for why. Create
`backend/data/fundamentals.json` (one entry per ticker, matching
`app/companies_seed.py`), then for each company visit
`https://finance.yahoo.com/quote/<TICKER>/key-statistics/` and fill in
Market Cap, Trailing P/E, and Diluted EPS. Values with a suffix like
`18.97T` can be pasted as-is (as a string); plain numbers don't need quotes.

## 3. Load data

```bash
python -m app.ingestion
```

This fetches ~1 year of price history for the 20 tracked companies from
NSE (via `nselib`) and loads your fundamentals file into Supabase. Re-run
any time you want fresh price data — it's safe to run repeatedly.

## 4. Run the API

```bash
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API docs (Swagger UI).

## Endpoints

| Endpoint | Description |
|---|---|
| `GET /companies` | All tracked companies + latest price |
| `GET /companies/{ticker}` | One company's fundamentals + latest price |
| `GET /companies/{ticker}/history?days=365` | OHLCV history |
| `GET /compare?tickers=TCS.NS,INFY.NS` | Aligned history + fundamentals for 2-4 companies |
| `GET /market-summary` | Aggregate stats |

## Deploying (Render)

1. Push this repo to GitHub.
2. Render -> New Web Service -> connect the repo, root directory `backend`.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add `SUPABASE_URL`, `SUPABASE_KEY`, and `ALLOWED_ORIGINS` (your Vercel URL) as environment variables.
6. Under Instance Type, select **Free** explicitly if not already selected.

Note: Render's free tier spins the service down after 15 minutes of
inactivity, so the first request after a break can take 30-60 seconds.
