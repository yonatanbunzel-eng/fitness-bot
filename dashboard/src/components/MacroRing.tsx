import { PieChart, Pie, Cell } from 'recharts'

interface Props {
  label: string
  value: number
  goal: number
  color: string
  unit?: string
}

export default function MacroRing({ label, value, goal, color, unit = 'g' }: Props) {
  const pct = Math.min((value / (goal || 1)) * 100, 100)
  const data = [{ value: pct }, { value: 100 - pct }]

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative w-20 h-20">
        <PieChart width={80} height={80}>
          <Pie
            data={data} cx={35} cy={35}
            innerRadius={28} outerRadius={36}
            startAngle={90} endAngle={-270}
            dataKey="value" strokeWidth={0}
          >
            <Cell fill={color} />
            <Cell fill="#27272a" />
          </Pie>
        </PieChart>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-xs font-bold text-white">{Math.round(pct)}%</span>
        </div>
      </div>
      <p className="text-xs font-medium text-zinc-300">{label}</p>
      <p className="text-xs text-zinc-500">{Math.round(value)}/{goal}{unit}</p>
    </div>
  )
}
