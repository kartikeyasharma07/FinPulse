import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend, ResponsiveContainer } from 'recharts'
import { api } from '../api/client'
import { formatCrores, formatNumber } from '../utils/format'

const LINE_COLORS = ['#0F9D8A', '#D85A30', '#378ADD', '#BA7517']

export default function Compare() {
  const [searchParams] = useSearchParams()
  const [companies, setCompanies] = useState([])
  const [selected, setSelected] = useState(() => {
    const preselect = searchParams.get('with')
    return preselect ? [preselect] : []
  })
  const [result, setResult] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    api.getCompanies().then(setCompanies)
  }, [])

  useEffect(() => {
    if (selected.length < 2) {
      setResult([])
      return
    }
    api.compare(selected).then(setResult).catch((e) => setError(e.message))
  }, [selected])

  const toggle = (ticker) => {
    setSelected((prev) => {
      if (prev.includes(ticker)) return prev.filter((t) => t !== ticker)
      if (prev.length >= 4) return prev
      return [...prev, ticker]
    })
  }

  // Normalize each series to % change from its first available close.
  const chartData = useMemo(() => {
    if (result.length === 0) return []
    const dateMap = {}
    result.forEach((r) => {
      const base = r.history[0]?.close
      if (!base) return
      r.history.forEach((point) => {
        const pct = ((point.close - base) / base) * 100
        dateMap[point.date] = { ...(dateMap[point.date] || {}), date: point.date, [r.ticker]: pct }
      })
    })
    return Object.values(dateMap).sort((a, b) => a.date.localeCompare(b.date))
  }, [result])

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-1">Compare companies</h1>
      <p className="text-slate-500 dark:text-slate-400 text-sm mb-6">Pick 2 to 4 companies to compare.</p>

      <div className="flex flex-wrap gap-2 mb-6">
        {companies.map((c) => {
          const active = selected.includes(c.ticker)
          return (
            <button
              key={c.ticker}
              onClick={() => toggle(c.ticker)}
              className={`px-3 py-1.5 rounded-full text-sm border transition-colors ${
                active
                  ? 'bg-accent text-white border-accent'
                  : 'border-slate-200 dark:border-white/10 hover:bg-slate-50 dark:hover:bg-white/5'
              }`}
            >
              {c.ticker.replace('.NS', '')}
            </button>
          )
        })}
      </div>

      {error && <p className="text-loss text-sm mb-4">{error}</p>}

      {selected.length < 2 && (
        <p className="text-sm text-slate-400 border border-dashed border-slate-200 dark:border-white/10 rounded-lg p-6 text-center">
          Select at least 2 companies to see the comparison.
        </p>
      )}

      {chartData.length > 0 && (
        <div className="rounded-lg border border-slate-200 dark:border-white/10 bg-card-light dark:bg-card-dark p-4 mb-6">
          <h2 className="text-sm font-medium mb-3">% change over the last year</h2>
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} minTickGap={40} />
              <YAxis tick={{ fontSize: 11 }} unit="%" />
              <Tooltip formatter={(v) => `${v.toFixed(2)}%`} />
              <Legend />
              {result.map((r, i) => (
                <Line
                  key={r.ticker}
                  type="monotone"
                  dataKey={r.ticker}
                  stroke={LINE_COLORS[i % LINE_COLORS.length]}
                  dot={false}
                  strokeWidth={2}
                  name={r.ticker.replace('.NS', '')}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {result.length > 0 && (
        <div className="overflow-x-auto rounded-lg border border-slate-200 dark:border-white/10">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 dark:bg-white/5 text-left text-slate-500 dark:text-slate-400">
              <tr>
                <th className="px-4 py-3 font-medium">Metric</th>
                {result.map((r) => (
                  <th key={r.ticker} className="px-4 py-3 font-medium text-right">{r.ticker.replace('.NS', '')}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              <MetricRow label="Market cap" values={result.map((r) => formatCrores(r.fundamentals?.market_cap))} />
              <MetricRow label="P/E ratio" values={result.map((r) => r.fundamentals?.pe_ratio ? formatNumber(r.fundamentals.pe_ratio) : 'N/A')} />
              <MetricRow label="EPS" values={result.map((r) => r.fundamentals?.eps ? formatNumber(r.fundamentals.eps) : 'N/A')} />
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

function MetricRow({ label, values }) {
  return (
    <tr className="border-t border-slate-100 dark:border-white/5">
      <td className="px-4 py-3 text-slate-500 dark:text-slate-400">{label}</td>
      {values.map((v, i) => <td key={i} className="px-4 py-3 text-right tabular">{v}</td>)}
    </tr>
  )
}
