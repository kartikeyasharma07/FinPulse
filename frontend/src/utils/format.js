export function formatCrores(value) {
  if (value == null) return '—'
  const crores = value / 1e7
  if (crores >= 1e5) return `₹${(crores / 1e5).toFixed(2)}L Cr`
  return `₹${crores.toFixed(0)} Cr`
}

export function formatPrice(value) {
  if (value == null) return '—'
  return `₹${Number(value).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`
}

export function formatNumber(value, digits = 2) {
  if (value == null) return '—'
  return Number(value).toFixed(digits)
}

export function pctChange(open, close) {
  if (!open || !close) return null
  return ((close - open) / open) * 100
}
