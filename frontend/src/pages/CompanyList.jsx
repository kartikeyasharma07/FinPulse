import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { formatPrice, pctChange } from '../utils/format'

export default function CompanyList() {
  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [sector, setSector] = useState('All')

  useEffect(() => {
    api.getCompanies()
      .then(setCompanies)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const sectors = useMemo(
    () => ['All', ...new Set(companies.map((c) => c.sector).filter(Boolean))],
    [companies]
  )

  const filtered = companies.filter((c) => {
    const matchesSearch =
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.ticker.toLowerCase().includes(search.toLowerCase())
    const matchesSector = sector === 'All' || c.sector === sector
    return matchesSearch && matchesSector
  })

  if (loading) return <p className="text-slate-500 dark:text-slate-400">Loading companies…</p>
  if (error) return <ErrorState message={error} />

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold mb-1">Companies</h1>
        <p className="text-slate-500 dark:text-slate-400 text-sm">
          Tracking {companies.length} large-cap NSE companies
        </p>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by name or ticker…"
          className="flex-1 px-3 py-2 rounded-md border border-slate-200 dark:border-white/10 bg-card-light dark:bg-card-dark text-sm focus:outline-none focus:ring-2 focus:ring-accent"
        />
        <select
          value={sector}
          onChange={(e) => setSector(e.target.value)}
          className="px-3 py-2 rounded-md border border-slate-200 dark:border-white/10 bg-card-light dark:bg-card-dark text-sm"
        >
          {sectors.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <div className="overflow-x-auto rounded-lg border border-slate-200 dark:border-white/10">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 dark:bg-white/5 text-left text-slate-500 dark:text-slate-400">
            <tr>
              <th className="px-4 py-3 font-medium">Company</th>
              <th className="px-4 py-3 font-medium">Sector</th>
              <th className="px-4 py-3 font-medium text-right">Price</th>
              <th className="px-4 py-3 font-medium text-right">Day change</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((c) => {
              const p = c.latest_price
              const change = p ? pctChange(p.open, p.close) : null
              return (
                <tr
                  key={c.ticker}
                  className="border-t border-slate-100 dark:border-white/5 hover:bg-slate-50 dark:hover:bg-white/5"
                >
                  <td className="px-4 py-3">
                    <Link to={`/companies/${c.ticker}`} className="font-medium hover:text-accent">
                      {c.name}
                    </Link>
                    <div className="text-xs text-slate-400 tabular">{c.ticker}</div>
                  </td>
                  <td className="px-4 py-3 text-slate-500 dark:text-slate-400">{c.sector}</td>
                  <td className="px-4 py-3 text-right tabular">{formatPrice(p?.close)}</td>
                  <td className={`px-4 py-3 text-right tabular ${
                    change == null ? '' : change >= 0 ? 'text-gain' : 'text-loss'
                  }`}>
                    {change == null ? '—' : `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <p className="p-6 text-center text-slate-400 text-sm">No companies match your filters.</p>
        )}
      </div>
    </div>
  )
}

function ErrorState({ message }) {
  return (
    <div className="p-6 rounded-lg border border-loss/30 bg-loss/5 text-loss text-sm">
      Couldn't load companies: {message}. Is the backend running?
    </div>
  )
}
