# FinPulse

**Live site: https://finpulse-iota-ten.vercel.app**

A stock market monitoring dashboard tracking 20 large-cap NSE companies —
price history, fundamentals, historical candlestick charts, sector
breakdown, and side-by-side comparison.

## Architecture

```
NSE (via nselib)  --(ingestion script)-->  Supabase (Postgres)
                                                   |
                                         FastAPI reads from DB only
                                                   |
                                         React frontend (Vite + Tailwind)
```

The backend never fetches live market data on a request — a separate
ingestion script populates the database ahead of time, and the API only
ever reads from it. This keeps the dashboard fast and fully decoupled
from any single data source's availability.

## Project structure

```
finpulse/
├── backend/     FastAPI app + ingestion script
└── frontend/    React + Vite + Tailwind dashboard
```

## Quickstart

1. **Database**: create a free Supabase project, run `backend/schema.sql` in its SQL editor.
2. **Backend**: follow `backend/README.md` — install deps, set `.env`, fill in `backend/data/fundamentals.json`, run `python -m app.ingestion`, then `uvicorn app.main:app --reload`.
3. **Frontend**: follow `frontend/README.md` — install deps, set `.env`, `npm run dev`.
4. Open `http://localhost:5173`.

## Tech stack

| Layer | Choice |
|---|---|
| Backend | FastAPI |
| Database | Supabase (Postgres) |
| Price data source | nselib (talks to NSE directly) |
| Fundamentals | Seeded once from `data/fundamentals.json` (see note below) |
| Frontend | React + Vite + Tailwind CSS |
| Charts | lightweight-charts (candlestick), Recharts (comparison, sector) |
| Deployment | Render (backend) + Vercel (frontend) |

## Features

- Track 20 large-cap NSE companies (price, market cap, P/E, EPS)
- Searchable/filterable company list
- Candlestick + volume chart per company
- Side-by-side comparison (2-4 companies, normalized % change)
- Sector-wise dashboard with per-company market cap
- Light/dark mode toggle

## A note on data sources

Price history is fully automated via `nselib`, which talks to NSE's own
site and has proven reliable in testing. Fundamentals (P/E, market cap,
EPS) are **seeded once from a manually-filled file** rather than
live-fetched. This was a deliberate choice, not a shortcut: after testing
six different approaches (yfinance, jugaad-data, nsepython, nselib's
quote endpoint, and two raw manual requests) across two separate
networks, every one hit the same firewall-level block from NSE/Yahoo's
bot protection on live quote/fundamentals endpoints specifically — while
the historical price endpoint (used by nselib) is not behind the same
protection. Since fundamentals change quarterly, not by the second,
treating them as seeded reference data rather than something re-fetched
on every run is a reasonable trade-off, not a limitation of the
architecture.

## Libraries, APIs, and AI tools used

**Backend:** FastAPI, Uvicorn, Supabase Python client, python-dotenv,
Pydantic, pandas, [nselib](https://pypi.org/project/nselib/) (NSE price
data).

**Frontend:** React, Vite, Tailwind CSS, React Router,
[lightweight-charts](https://github.com/tradingview/lightweight-charts)
(candlestick charts), [Recharts](https://recharts.org/) (comparison and
sector charts).

**Data sources:** NSE (via `nselib`) for price history; Yahoo Finance
(manually, via browser) for the seeded fundamentals reference data — see
"A note on data sources" above.

**Infrastructure:** Supabase (Postgres database), Render (backend
hosting), Vercel (frontend hosting), GitHub (version control).

**AI assistance:** Claude (Anthropic) was used throughout development for
architecture planning, code generation, debugging (including the
multi-library data-source investigation documented above), and writing
this documentation. All code was reviewed and tested before use.

## Deploying

See the "Deploying" section in `backend/README.md` (Render) and
`frontend/README.md` (Vercel). Deploy the backend first, then point the
frontend's `VITE_API_URL` at it, then update the backend's
`ALLOWED_ORIGINS` to the deployed frontend URL.
