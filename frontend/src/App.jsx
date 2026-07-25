import { Suspense, lazy } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import Navbar from './components/Navbar'
import CompanyList from './pages/CompanyList'

// Lazy-loaded: these pull in heavier chart libraries, so keep them out of
// the initial bundle and only fetch when someone actually visits the page.
const CompanyDetail = lazy(() => import('./pages/CompanyDetail'))
const Compare = lazy(() => import('./pages/Compare'))
const SectorDashboard = lazy(() => import('./pages/SectorDashboard'))

function PageLoading() {
  return <p className="text-slate-500 dark:text-slate-400">Loading…</p>
}

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Navbar />
        <main className="max-w-6xl mx-auto px-4 py-6">
          <Suspense fallback={<PageLoading />}>
            <Routes>
              <Route path="/" element={<CompanyList />} />
              <Route path="/companies/:ticker" element={<CompanyDetail />} />
              <Route path="/compare" element={<Compare />} />
              <Route path="/sectors" element={<SectorDashboard />} />
            </Routes>
          </Suspense>
        </main>
      </BrowserRouter>
    </ThemeProvider>
  )
}
