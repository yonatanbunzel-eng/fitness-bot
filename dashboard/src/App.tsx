import { Routes, Route, NavLink } from 'react-router-dom'
import DailyView from './pages/DailyView'
import WeeklyView from './pages/WeeklyView'
import TrendsView from './pages/TrendsView'
import PhotosView from './pages/PhotosView'

const navClass = ({ isActive }: { isActive: boolean }) =>
  `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
    isActive ? 'bg-emerald-600 text-white' : 'text-zinc-400 hover:text-white hover:bg-zinc-800'
  }`

export default function App() {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <header className="sticky top-0 z-10 border-b border-zinc-800 bg-zinc-950/90 backdrop-blur">
        <div className="mx-auto max-w-5xl flex items-center gap-2 px-4 py-3">
          <span className="text-lg font-bold text-emerald-400 ml-4">💪 כושר ותזונה</span>
          <nav className="flex gap-1 mr-auto">
            <NavLink to="/" end className={navClass}>היום</NavLink>
            <NavLink to="/week" className={navClass}>שבוע</NavLink>
            <NavLink to="/trends" className={navClass}>מגמות</NavLink>
            <NavLink to="/photos" className={navClass}>תמונות</NavLink>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-4 py-6">
        <Routes>
          <Route path="/" element={<DailyView />} />
          <Route path="/week" element={<WeeklyView />} />
          <Route path="/trends" element={<TrendsView />} />
          <Route path="/photos" element={<PhotosView />} />
        </Routes>
      </main>
    </div>
  )
}
