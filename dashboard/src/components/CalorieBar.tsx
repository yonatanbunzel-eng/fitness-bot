interface Props {
  consumed: number
  goal: number
}

export default function CalorieBar({ consumed, goal }: Props) {
  const pct = Math.min((consumed / (goal || 1)) * 100, 110)
  const remaining = Math.max(goal - consumed, 0)
  const color = pct > 110 ? 'bg-red-500' : pct > 100 ? 'bg-amber-500' : pct >= 85 ? 'bg-emerald-500' : 'bg-blue-500'

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="font-semibold text-white">{consumed.toLocaleString('he-IL')} קלוריות</span>
        <span className="text-zinc-400">{remaining > 0 ? `נותרו ${remaining}` : 'יעד הושג!'}</span>
      </div>
      <div className="h-3 bg-zinc-800 rounded-full overflow-hidden" dir="ltr">
        <div
          className={`h-full rounded-full transition-all duration-500 ${color}`}
          style={{ width: `${Math.min(pct, 100)}%` }}
        />
      </div>
      <div className="flex justify-between text-xs text-zinc-500">
        <span>0</span>
        <span>יעד: {goal.toLocaleString('he-IL')} קלוריות</span>
      </div>
    </div>
  )
}
