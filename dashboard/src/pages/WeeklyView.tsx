import { useEffect, useState } from 'react'
import { parseISO, format } from 'date-fns'
import { he } from 'date-fns/locale'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { api, WeeklySummary } from '../api/client'
import WorkoutHeatmap from '../components/WorkoutHeatmap'

const WORKOUT_LABELS: Record<string, string> = {
  run: 'ריצה', strength: 'כוח', flexibility: 'גמישות', other: 'אחר',
}

export default function WeeklyView() {
  const [data, setData] = useState<WeeklySummary | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.weeklySummary().then(setData).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-zinc-500 text-center py-16">טוען...</div>
  if (!data) return <div className="text-zinc-500 text-center py-16">אין נתונים.</div>

  const DAYS_SHORT = ['א׳', 'ב׳', 'ג׳', 'ד׳', 'ה׳', 'ו׳', 'ש׳']
  const calChartData = data.daily_calories.map((d, i) => ({
    day: DAYS_SHORT[parseISO(d.date).getDay()],
    קלוריות: d.calories,
  }))

  const runPct = data.run_km_goal > 0
    ? Math.round((data.run_km_total / data.run_km_goal) * 100)
    : null

  const weekStartFormatted = format(parseISO(data.week_start), "d בMMMM", { locale: he })

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-bold">שבוע {weekStartFormatted}</h1>

      {/* Training plan */}
      <div className="rounded-xl bg-zinc-900 p-4 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-zinc-400">תוכנית אימונים</h2>
          {data.plan?.completion_rate != null && (
            <span className="text-sm font-bold text-emerald-400">
              {Math.round(data.plan.completion_rate * 100)}% הושלם
            </span>
          )}
        </div>
        <WorkoutHeatmap sessions={data.plan} />

        {data.plan?.adaptations && data.plan.adaptations.length > 0 && (
          <div className="mt-2 space-y-1 border-t border-zinc-800 pt-3">
            <p className="text-xs text-zinc-500 font-medium">שינויים השבוע:</p>
            {data.plan.adaptations.map((a, i) => (
              <p key={i} className="text-xs text-zinc-400">
                {format(parseISO(a.date), "EEEE", { locale: he })} — {a.reason}
              </p>
            ))}
          </div>
        )}
      </div>

      {/* Calorie chart */}
      <div className="rounded-xl bg-zinc-900 p-4 space-y-3">
        <h2 className="text-sm font-semibold text-zinc-400">קלוריות יומיות</h2>
        <ResponsiveContainer width="100%" height={160}>
          <BarChart data={calChartData} margin={{ top: 5, right: 10, bottom: 0, left: 0 }}>
            <CartesianGrid stroke="#27272a" strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#71717a' }} />
            <YAxis tick={{ fontSize: 11, fill: '#71717a' }} />
            <Tooltip
              contentStyle={{ background: '#18181b', border: '1px solid #3f3f46', borderRadius: 8 }}
              itemStyle={{ color: '#e5e5e5' }}
              formatter={(v: number) => [`${v} קל׳`]}
            />
            <Bar dataKey="קלוריות" fill="#10b981" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Run progress */}
      {data.run_km_goal > 0 && (
        <div className="rounded-xl bg-zinc-900 p-4 space-y-2">
          <h2 className="text-sm font-semibold text-zinc-400">🏃 ריצה שבועית</h2>
          <div className="flex justify-between items-baseline">
            <span className="text-2xl font-bold text-emerald-400">{data.run_km_total.toFixed(1)} ק״מ</span>
            <span className="text-zinc-500 text-sm">יעד: {data.run_km_goal} ק״מ</span>
          </div>
          <div className="h-3 bg-zinc-800 rounded-full" dir="ltr">
            <div
              className="h-full bg-emerald-500 rounded-full transition-all"
              style={{ width: `${Math.min(runPct || 0, 100)}%` }}
            />
          </div>
          <p className="text-xs text-zinc-500">{runPct}% מהיעד השבועי</p>
        </div>
      )}

      {/* Workout list */}
      <div className="rounded-xl bg-zinc-900 p-4 space-y-3">
        <h2 className="text-sm font-semibold text-zinc-400">סשנים ({data.workouts.length})</h2>
        {data.workouts.length === 0 ? (
          <p className="text-zinc-600 text-sm">לא נרשמו אימונים השבוע.</p>
        ) : (
          data.workouts.map(w => (
            <div key={w.id} className="flex items-center gap-3 py-2 border-b border-zinc-800 last:border-0">
              <span>{w.workout_type === 'run' ? '🏃' : '🏋️'}</span>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{WORKOUT_LABELS[w.workout_type] || w.workout_type}</span>
                  <span className="text-xs text-zinc-500">
                    {format(parseISO(w.date), "EEEE d", { locale: he })}
                  </span>
                </div>
                <p className="text-xs text-zinc-400">{w.summary}</p>
              </div>
              {w.distance_km && (
                <span className="text-xs text-emerald-400 font-medium">{w.distance_km} ק״מ</span>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
