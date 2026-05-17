import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts'
import { format, parseISO } from 'date-fns'
import { he } from 'date-fns/locale'
import { api, WeightPoint, StrengthPoint, RunPoint } from '../api/client'
import WeightChart from '../components/WeightChart'

const EXERCISES = [
  { value: 'squat', label: 'סקוואט' },
  { value: 'bench press', label: 'לחיצת חזה' },
  { value: 'deadlift', label: 'דדליפט' },
  { value: 'overhead press', label: 'לחיצת כתפיים' },
  { value: 'Romanian deadlift', label: 'RDL' },
  { value: 'pull up', label: 'מתח' },
]

export default function TrendsView() {
  const [weights, setWeights] = useState<WeightPoint[]>([])
  const [runs, setRuns] = useState<RunPoint[]>([])
  const [exercise, setExercise] = useState('squat')
  const [strength, setStrength] = useState<StrengthPoint[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.weightTrend(12).then(setWeights),
      api.runStats(8).then(setRuns),
    ]).finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    api.strengthProgress(exercise).then(setStrength)
  }, [exercise])

  const runChartData = runs
    .filter(r => r.pace_min_per_km)
    .map(r => ({
      date: format(parseISO(r.date), 'd/M'),
      קצב: r.pace_min_per_km,
      km: r.distance_km,
    }))

  const strengthChartData = strength.map(s => ({
    date: format(parseISO(s.date), 'd/M'),
    משקל: s.max_kg,
  }))

  if (loading) return <div className="text-zinc-500 text-center py-16">טוען...</div>

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-bold">מגמות</h1>

      {/* Weight trend */}
      <div className="rounded-xl bg-zinc-900 p-4 space-y-3">
        <h2 className="text-sm font-semibold text-zinc-400">⚖️ משקל — 12 שבועות</h2>
        <WeightChart data={weights} />
        {weights.length >= 2 && (
          <p className="text-xs text-zinc-500">
            שינוי: {(weights[weights.length - 1].weight_kg - weights[0].weight_kg).toFixed(1)} ק״ג
          </p>
        )}
        {weights.length === 0 && <p className="text-zinc-600 text-sm">אין נתוני משקל עדיין.</p>}
      </div>

      {/* Strength progress */}
      <div className="rounded-xl bg-zinc-900 p-4 space-y-3">
        <div className="flex items-center gap-3">
          <h2 className="text-sm font-semibold text-zinc-400">🏋️ כוח</h2>
          <select
            value={exercise}
            onChange={e => setExercise(e.target.value)}
            className="mr-auto text-xs bg-zinc-800 text-white border border-zinc-700 rounded px-2 py-1"
          >
            {EXERCISES.map(ex => (
              <option key={ex.value} value={ex.value}>{ex.label}</option>
            ))}
          </select>
        </div>
        {strengthChartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={strengthChartData} margin={{ top: 5, right: 10, bottom: 0, left: 0 }}>
              <CartesianGrid stroke="#27272a" strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#71717a' }} />
              <YAxis tick={{ fontSize: 11, fill: '#71717a' }} unit="ק״ג" />
              <Tooltip
                contentStyle={{ background: '#18181b', border: '1px solid #3f3f46', borderRadius: 8 }}
                itemStyle={{ color: '#e5e5e5' }}
                formatter={(v: number) => [`${v} ק״ג`]}
              />
              <Line type="monotone" dataKey="משקל" stroke="#f59e0b" strokeWidth={2} dot={{ r: 4, fill: '#f59e0b' }} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-zinc-600 text-sm">אין נתונים לתרגיל זה עדיין.</p>
        )}
      </div>

      {/* Run pace */}
      <div className="rounded-xl bg-zinc-900 p-4 space-y-3">
        <h2 className="text-sm font-semibold text-zinc-400">🏃 קצב ריצה — 8 שבועות</h2>
        {runChartData.length > 0 ? (
          <>
            <ResponsiveContainer width="100%" height={160}>
              <LineChart data={runChartData} margin={{ top: 5, right: 10, bottom: 0, left: 0 }}>
                <CartesianGrid stroke="#27272a" strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#71717a' }} />
                <YAxis reversed tick={{ fontSize: 11, fill: '#71717a' }} />
                <Tooltip
                  contentStyle={{ background: '#18181b', border: '1px solid #3f3f46', borderRadius: 8 }}
                  itemStyle={{ color: '#e5e5e5' }}
                  formatter={(v: number) => {
                    const min = Math.floor(v)
                    const sec = Math.round((v - min) * 60)
                    return [`${min}:${String(sec).padStart(2, '0')} לק״מ`]
                  }}
                />
                <Line type="monotone" dataKey="קצב" stroke="#10b981" strokeWidth={2} dot={{ r: 3, fill: '#10b981' }} />
              </LineChart>
            </ResponsiveContainer>
            <p className="text-xs text-zinc-500">ציר Y הפוך — ציון נמוך = קצב מהיר יותר</p>
          </>
        ) : (
          <p className="text-zinc-600 text-sm">אין נתוני ריצה עדיין.</p>
        )}
      </div>
    </div>
  )
}
