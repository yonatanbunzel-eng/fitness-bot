import type { WeeklySummary } from '../api/client'

const DAYS_EN = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
const DAYS_HE = ['ב׳', 'ג׳', 'ד׳', 'ה׳', 'ו׳', 'ש׳', 'א׳']

const TYPE_COLORS: Record<string, string> = {
  push: 'bg-blue-600', דחיפה: 'bg-blue-600',
  pull: 'bg-purple-600', משיכה: 'bg-purple-600',
  legs: 'bg-orange-600', רגליים: 'bg-orange-600',
  run: 'bg-emerald-600', ריצה: 'bg-emerald-600',
  flexibility: 'bg-teal-600', גמישות: 'bg-teal-600',
  rest: 'bg-zinc-800', מנוחה: 'bg-zinc-800',
  other: 'bg-zinc-600',
}

const TYPE_LABELS: Record<string, string> = {
  push: 'דחיפה', pull: 'משיכה', legs: 'רגליים',
  run: 'ריצה', flexibility: 'גמישות', rest: 'מנוחה', other: 'אחר',
}

interface Props {
  sessions: WeeklySummary['plan']
}

export default function WorkoutHeatmap({ sessions }: Props) {
  if (!sessions) return <p className="text-zinc-500 text-sm">לא נקבעה תוכנית שבועית.</p>

  return (
    <div className="grid grid-cols-7 gap-2" dir="rtl">
      {DAYS_EN.map((day, i) => {
        const session = sessions.sessions[day]
        const isRest = !session || session.rest
        const isCompleted = session?.completed
        const type = session?.type?.toLowerCase() || 'rest'
        const colorClass = isRest ? 'bg-zinc-800' : (TYPE_COLORS[type] || TYPE_COLORS[session?.type || ''] || 'bg-zinc-600')
        const labelHe = TYPE_LABELS[type] || session?.type || 'מנוחה'

        return (
          <div key={day} className="flex flex-col items-center gap-1">
            <span className="text-xs text-zinc-500">{DAYS_HE[i]}</span>
            <div
              className={`w-10 h-10 rounded-lg flex items-center justify-center text-sm font-bold ${colorClass} ${isCompleted ? 'ring-2 ring-white/30' : ''}`}
              title={session ? `${session.type}${session.notes ? ` — ${session.notes}` : ''}` : 'מנוחה'}
            >
              {isCompleted ? '✓' : isRest ? '—' : labelHe.slice(0, 1)}
            </div>
            <span className="text-xs text-zinc-600">{isRest ? 'מנוחה' : labelHe}</span>
          </div>
        )
      })}
    </div>
  )
}
