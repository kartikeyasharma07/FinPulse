import { useEffect, useMemo, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { formatCrores } from '../utils/format'

export default function SectorDashboard() {
  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getCompanies().then(setCompanies).finally(() => setLoading(false))
  }, [])

  const sectors = useMemo(() => {
    const groups = {}
    companies.forEach((c) => {
      const sector = c.sector || 'Other'
      if (!groups[sector]) groups[sector] = { sector, companies: [], totalCap: 0 }
      groups[sector].companies.push(c)
      groups[sector].totalCap += c.fundamentals?.market_cap || 0
    })
    return Object.values(groups).sort((a, b) => b.totalCap - a.totalCap)
  }, [companies])

  const chartData = sectors.map((s) => ({
    sector: s.sector,
    marketCapCr: Math.round(s.totalCap / 1e7),
  }))

  if (loading) return <p className="text-slate-500 dark:text-slate-400">Loading…</p>

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-1">Sector dashboard</h1>
      <p className="text-slate-500 dark:text-slate-400 text-sm mb-6">
        Tracked companies grouped by sector, by combined market cap.
      </p>

      <div className="rounded-lg border border-slate-200 dark:border-white/10 bg-card-light dark:bg-card-dark p-4 mb-8">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData} layout="vertical" margin={{ left: 24 }}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.15} horizontal={false} />
            <XAxis type="number" tick={{ fontSize: 11 }} unit=" Cr" />
            <YAxis type="category" dataKey="sector" width={140} tick={{ fontSize: 11 }} />
            <Tooltip formatter={(v) => `₹${v.toLocaleString('en-IN')} Cr`} />
            <Bar dataKey="marketCapCr" fill="#0F9D8A" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid sm:grid-cols-2 gap-4">
        {sectors.map((s) => (
          <div key={s.sector} className="rounded-lg border border-slate-200 dark:border-white/10 bg-card-light dark:bg-card-dark p-4">
            <div className="flex justify-between items-baseline mb-3">
              <h2 className="font-medium">{s.sector}</h2>
              <span className="text-xs text-slate-400 tabular">{formatCrores(s.totalCap)}</span>
            </div>
            <ul className="space-y-1.5">
              {s.companies.map((c) => (
                <li key={c.ticker}>
                  <Link to={`/companies/${c.ticker}`} className="text-sm hover:text-accent">
                    {c.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  )
}
