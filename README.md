# FinPulse

A stock market monitoring dashboard tracking 20 large-cap NSE companies —
live-ish price data, fundamentals, historical candlestick charts, sector
breakdown, and side-by-side comparison.

## Architecture

```
yfinance  --(scheduled ingestion script)-->  Supabase (Postgres)
                                                    |
                                          FastAPI reads from DB only
                                                    |
                                          React frontend (Vite + Tailwind)
```

The backend never calls yfinance on a live request — a separate ingestion
script populates the database, and the API only ever reads from it. This
keeps the dashboard fast and isolated from yfinance rate limits.

## Project structure

```
finpulse/
├── backend/     FastAPI app + Supabase ingestion script
└── frontend/    React + Vite + Tailwind dashboard
```

## Quickstart

1. **Database**: create a free Supabase project, run `backend/schema.sql` in its SQL editor.
2. **Backend**: follow `backend/README.md` — install deps, set `.env`, run `python -m app.ingestion` once to load data, then `uvicorn app.main:app --reload`.
3. **Frontend**: follow `frontend/README.md` — install deps, set `.env`, `npm run dev`.
4. Open `http://localhost:5173`.

## Tech stack

| Layer | Choice |
|---|---|
| Backend | FastAPI |
| Database | Supabase (Postgres) |
| Data source | yfinance |
| Frontend | React + Vite + Tailwind CSS |
| Charts | lightweight-charts (candlestick), Recharts (comparison, sector) |
| PDF export | jsPDF + html2canvas |
| Deployment | Render (backend) + Vercel (frontend) |

## Features

- Track 20 large-cap NSE companies (price, market cap, P/E, EPS)
- Searchable/filterable company list
- Candlestick + volume chart per company
- Side-by-side comparison (2-4 companies, normalized % change)
- Sector-wise market cap dashboard
- Light/dark mode toggle
- Per-company PDF report export

## Deploying

See the "Deploying" section in `backend/README.md` (Render) and
`frontend/README.md` (Vercel). Deploy the backend first, then point the
frontend's `VITE_API_URL` at it, then update the backend's
`ALLOWED_ORIGINS` to the deployed frontend URL.
