import { useEffect, useState } from 'react'
import { api, DailySummary } from '../api/client'
import MacroRing from '../components/MacroRing'
import CalorieBar from '../components/CalorieBar'

const DAYS_HE: Record<number, string> = {
  0: 'יום ראשון', 1: 'יום שני', 2: 'יום שלישי', 3: 'יום רביעי',
  4: 'יום חמישי', 5: 'יום שישי', 6: 'שבת',
}

const MONTHS_HE = ['ינואר','פברואר','מרץ','אפריל','מאי','יוני','יולי','אוגוסט','ספטמבר','אוקטובר','נובמבר','דצמבר']

const MEAL_LABELS: Record<string, string> = {
  breakfast: 'ארוחת בוקר',
  lunch: 'ארוחת צהריים',
  dinner: 'ארוחת ערב',
  snack: 'חטיף',
}

export default function DailyView() {
  const [data, setData] = useState<DailySummary | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.dailySummary().then(setData).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-zinc-500 text-center py-16">טוען...</div>
  if (!data) return (
    <div className="text-zinc-500 text-center py-16 space-y-2">
      <p>אין נתונים עדיין.</p>
      <p className="text-sm">שלח הודעה לבוט בוואטסאפ כדי להתחיל!</p>
    </div>
  )

  const { goals, consumed, water_ml, sleep, weight_kg, meals, workouts } = data
  const now = new Date()
  const dateStr = `${DAYS_HE[now.getDay()]}, ${now.getDate()} ב${MONTHS_HE[now.getMonth()]}`

  const waterPct = Math.round((water_ml / goals.water_ml) * 100)
  const sleepPct = sleep ? Math.round((sleep.hours / goals.sleep_hours) * 100) : 0

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{dateStr}</h1>
        {weight_kg && (
          <div className="text-sm text-zinc-400">
            ⚖️ <span className="text-white font-medium">{weight_kg} ק״ג</span>
          </div>
        )}
      </div>

      {/* Calorie bar */}
      <div className="rounded-xl bg-zinc-900 p-4 space-y-3">
        <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide">קלוריות</h2>
        <CalorieBar consumed={consumed.calories} goal={goals.calories_target} />
      </div>

      {/* Macro rings */}
      <div className="rounded-xl bg-zinc-900 p-4">
        <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide mb-4">מקרואים</h2>
        <div className="flex justify-around">
          <MacroRing label="חלבון" value={consumed.protein_g} goal={goals.protein_g} color="#10b981" />
          <MacroRing label="פחמימות" value={consumed.carbs_g} goal={goals.carbs_g} color="#f59e0b" />
          <MacroRing label="שומן" value={consumed.fat_g} goal={goals.fat_g} color="#8b5cf6" />
        </div>
      </div>

      {/* Water + Sleep */}
      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-xl bg-zinc-900 p-4 space-y-2">
          <h2 className="text-sm font-semibold text-zinc-400">💧 מים</h2>
          <div className="text-2xl font-bold text-blue-400">{waterPct}%</div>
          <div className="h-2 bg-zinc-800 rounded-full" dir="ltr">
            <div className="h-full bg-blue-500 rounded-full" style={{ width: `${Math.min(waterPct, 100)}%` }} />
          </div>
          <p className="text-xs text-zinc-500">{water_ml} / {goals.water_ml} מ״ל</p>
        </div>

        <div className="rounded-xl bg-zinc-900 p-4 space-y-2">
          <h2 className="text-sm font-semibold text-zinc-400">😴 שינה</h2>
          {sleep ? (
            <>
              <div className="text-2xl font-bold text-indigo-400">{sleep.hours.toFixed(1)}ש׳</div>
              <div className="h-2 bg-zinc-800 rounded-full" dir="ltr">
                <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${Math.min(sleepPct, 100)}%` }} />
              </div>
              <p className="text-xs text-zinc-500">יעד: {goals.sleep_hours}ש׳{sleep.quality ? ` · איכות: ${sleep.quality}/10` : ''}</p>
            </>
          ) : (
            <p className="text-zinc-600 text-sm">לא נרשם עדיין</p>
          )}
        </div>
      </div>

      {/* Workouts */}
      {workouts.length > 0 && (
        <div className="rounded-xl bg-zinc-900 p-4 space-y-3">
          <h2 className="text-sm font-semibold text-zinc-400">💪 אימונים</h2>
          {workouts.map(w => (
            <div key={w.id} className="flex items-start gap-3">
              <span className="text-lg">{w.workout_type === 'run' ? '🏃' : w.workout_type === 'flexibility' ? '🧘' : '🏋️'}</span>
              <div>
                <p className="text-sm font-medium">
                  {w.workout_type === 'run' ? 'ריצה' : w.workout_type === 'flexibility' ? 'גמישות' : 'כוח'}
                </p>
                <p className="text-xs text-zinc-400">{w.summary}</p>
                {w.distance_km && <p className="text-xs text-emerald-400">{w.distance_km} ק״מ · {w.duration_minutes} דקות</p>}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Meals */}
      <div className="rounded-xl bg-zinc-900 p-4 space-y-3">
        <h2 className="text-sm font-semibold text-zinc-400">🥗 ארוחות</h2>
        {meals.length === 0 ? (
          <p className="text-zinc-600 text-sm">לא נרשמו ארוחות היום.</p>
        ) : (
          meals.map(m => (
            <div key={m.id} className="flex items-start gap-3 py-2 border-b border-zinc-800 last:border-0">
              {m.photo_url && (
                <img src={m.photo_url} className="w-12 h-12 rounded-lg object-cover flex-shrink-0" alt="ארוחה" />
              )}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{MEAL_LABELS[m.meal_type] || m.meal_type}</span>
                  {m.confidence === 'low' && <span className="text-xs text-amber-500">הערכה</span>}
                </div>
                <p className="text-xs text-zinc-400 truncate">
                  {m.food_items.map(f => f.name).join(', ')}
                </p>
                <p className="text-xs text-zinc-500 mt-1">{m.calories} קל׳ · {m.protein_g.toFixed(0)}g חלבון</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
