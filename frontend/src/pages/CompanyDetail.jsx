import { useEffect, useRef, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api/client'
import { formatPrice, formatCrores, formatNumber } from '../utils/format'
import { exportElementAsPdf } from '../utils/exportPdf'
import CandlestickChart from '../components/CandlestickChart'

export default function CompanyDetail() {
  const { ticker } = useParams()
  const [company, setCompany] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [exporting, setExporting] = useState(false)
  const reportRef = useRef(null)

  useEffect(() => {
    setLoading(true)
    Promise.all([api.getCompany(ticker), api.getHistory(ticker)])
      .then(([companyData, historyData]) => {
        setCompany(companyData)
        setHistory(historyData)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [ticker])

  const handleExport = async () => {
    setExporting(true)
    try {
      await exportElementAsPdf(reportRef.current, `${ticker}-report.pdf`)
    } finally {
      setExporting(false)
    }
  }

  if (loading) return <p className="text-slate-500 dark:text-slate-400">Loading…</p>
  if (error) return <p className="text-loss text-sm">Couldn't load {ticker}: {error}</p>
  if (!company) return null

  const f = company.fundamentals || {}
  const price = company.latest_price || {}

  const metrics = [
    { label: 'Current price', value: formatPrice(price.close) },
    { label: 'Market cap', value: formatCrores(f.market_cap) },
    { label: 'P/E ratio', value: f.pe_ratio ? formatNumber(f.pe_ratio) : 'N/A' },
    { label: 'EPS', value: f.eps ? formatPrice(f.eps) : 'N/A' },
  ]

  return (
    <div>
      <Link to="/" className="text-sm text-slate-500 hover:text-accent">← All companies</Link>

      <div className="flex items-start justify-between mt-3 mb-6 gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-semibold">{company.name}</h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm mt-1 max-w-xl">{company.description}</p>
        </div>
        <div className="flex gap-2 shrink-0">
          <Link
            to={`/compare?with=${ticker}`}
            className="px-3 py-2 rounded-md text-sm border border-slate-200 dark:border-white/10 hover:bg-slate-50 dark:hover:bg-white/5"
          >
            Compare
          </Link>
          <button
            onClick={handleExport}
            disabled={exporting}
            className="px-3 py-2 rounded-md text-sm bg-accent text-white hover:bg-accent-light disabled:opacity-50"
          >
            {exporting ? 'Exporting…' : 'Export PDF'}
          </button>
        </div>
      </div>

      <div ref={reportRef} className="bg-surface-light dark:bg-surface-dark">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
          {metrics.map((m) => (
            <div key={m.label} className="rounded-lg border border-slate-200 dark:border-white/10 bg-card-light dark:bg-card-dark p-4">
              <div className="text-xs text-slate-500 dark:text-slate-400">{m.label}</div>
              <div className="text-lg font-semibold tabular mt-1">{m.value}</div>
            </div>
          ))}
        </div>

        <div className="rounded-lg border border-slate-200 dark:border-white/10 bg-card-light dark:bg-card-dark p-4">
          <h2 className="text-sm font-medium mb-3">Price history</h2>
          {history.length > 0
            ? <CandlestickChart history={history} />
            : <p className="text-sm text-slate-400">No price history available yet.</p>}
        </div>
      </div>
    </div>
  )
}
