import { useEffect, useRef } from 'react'
import { createChart, CandlestickSeries, HistogramSeries, ColorType } from 'lightweight-charts'
import { useTheme } from '../context/ThemeContext'

// history: array of { date, open, high, low, close, volume }, oldest -> newest
export default function CandlestickChart({ history }) {
  const containerRef = useRef(null)
  const { dark } = useTheme()

  useEffect(() => {
    if (!containerRef.current || !history?.length) return

    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 360,
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: dark ? '#94A3B8' : '#475569',
      },
      grid: {
        vertLines: { color: dark ? '#1E293B' : '#F1F5F9' },
        horzLines: { color: dark ? '#1E293B' : '#F1F5F9' },
      },
      rightPriceScale: { borderVisible: false },
      timeScale: { borderVisible: false },
    })

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#16A34A',
      downColor: '#DC2626',
      borderVisible: false,
      wickUpColor: '#16A34A',
      wickDownColor: '#DC2626',
    })
    candleSeries.setData(
      history.map((h) => ({ time: h.date, open: h.open, high: h.high, low: h.low, close: h.close }))
    )

    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: 'volume' },
      priceScaleId: 'volume',
    })
    chart.priceScale('volume').applyOptions({
      scaleMargins: { top: 0.85, bottom: 0 }, // squeeze volume into bottom 15%
    })
    volumeSeries.setData(
      history.map((h) => ({
        time: h.date,
        value: h.volume,
        color: h.close >= h.open ? 'rgba(22,163,74,0.4)' : 'rgba(220,38,38,0.4)',
      }))
    )

    chart.timeScale().fitContent()

    const handleResize = () => chart.applyOptions({ width: containerRef.current.clientWidth })
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [history, dark])

  return <div ref={containerRef} className="w-full" />
}
