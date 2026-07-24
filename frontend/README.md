# FinPulse frontend

React + Vite + Tailwind dashboard. Talks to the FastAPI backend over REST.

## Setup

```bash
cd frontend
npm install
cp .env.example .env    # set VITE_API_URL to your backend URL
npm run dev
```

Visit `http://localhost:5173`. Make sure the backend is running first (see `../backend/README.md`).

## Pages

- `/` — company list, search + sector filter
- `/companies/:ticker` — fundamentals, candlestick + volume chart, PDF export
- `/compare` — pick 2-4 companies, normalized % change chart + metrics table
- `/sectors` — sector-wise market cap breakdown

## Deploying (Vercel)

1. Push this repo to GitHub.
2. Vercel -> New Project -> import the repo, set root directory to `frontend`.
3. Framework preset: Vite (auto-detected).
4. Add environment variable `VITE_API_URL` = your deployed Render backend URL.
5. Deploy.

Once both are deployed, update the backend's `ALLOWED_ORIGINS` env var on Render to your Vercel URL so CORS allows the frontend to call it.
