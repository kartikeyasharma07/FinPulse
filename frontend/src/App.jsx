import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import Navbar from './components/Navbar'
import CompanyList from './pages/CompanyList'
import CompanyDetail from './pages/CompanyDetail'
import Compare from './pages/Compare'
import SectorDashboard from './pages/SectorDashboard'

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Navbar />
        <main className="max-w-6xl mx-auto px-4 py-6">
          <Routes>
            <Route path="/" element={<CompanyList />} />
            <Route path="/companies/:ticker" element={<CompanyDetail />} />
            <Route path="/compare" element={<Compare />} />
            <Route path="/sectors" element={<SectorDashboard />} />
          </Routes>
        </main>
      </BrowserRouter>
    </ThemeProvider>
  )
}
