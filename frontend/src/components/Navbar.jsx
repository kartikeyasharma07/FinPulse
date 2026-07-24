import { NavLink } from 'react-router-dom'
import { useTheme } from '../context/ThemeContext'

const linkClass = ({ isActive }) =>
  `px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
    isActive
      ? 'bg-accent/10 text-accent'
      : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/5'
  }`

export default function Navbar() {
  const { dark, toggle } = useTheme()

  return (
    <header className="border-b border-slate-200 dark:border-white/10 bg-card-light dark:bg-card-dark">
      <div className="max-w-6xl mx-auto flex items-center justify-between px-4 py-3">
        <NavLink to="/" className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-accent" />
          <span className="font-semibold tracking-tight">FinPulse</span>
        </NavLink>

        <nav className="flex items-center gap-1">
          <NavLink to="/" end className={linkClass}>Companies</NavLink>
          <NavLink to="/compare" className={linkClass}>Compare</NavLink>
          <NavLink to="/sectors" className={linkClass}>Sectors</NavLink>
        </nav>

        <button
          onClick={toggle}
          aria-label="Toggle dark mode"
          className="w-9 h-9 flex items-center justify-center rounded-md border border-slate-200 dark:border-white/10 hover:bg-slate-100 dark:hover:bg-white/5"
        >
          {dark ? '☀' : '☾'}
        </button>
      </div>
    </header>
  )
}
