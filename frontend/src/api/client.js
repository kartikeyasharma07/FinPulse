const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path) {
  const res = await fetch(`${BASE_URL}${path}`)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed: ${res.status}`)
  }
  return res.json()
}

export const api = {
  getCompanies: () => request('/companies'),
  getCompany: (ticker) => request(`/companies/${ticker}`),
  getHistory: (ticker, days = 365) => request(`/companies/${ticker}/history?days=${days}`),
  compare: (tickers) => request(`/compare?tickers=${tickers.join(',')}`),
  marketSummary: () => request('/market-summary'),
}
