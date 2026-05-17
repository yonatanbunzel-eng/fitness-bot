import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, ReferenceLine } from 'recharts'
import { format, parseISO } from 'date-fns'
import type { WeightPoint } from '../api/client'

interface Props {
  data: WeightPoint[]
}

export default function WeightChart({ data }: Props) {
  if (!data.length) return <p className="text-zinc-500 text-sm">No weight data yet.</p>

  const chartData = data.map(d => ({
    date: d.date,
    weight: d.weight_kg,
    label: format(parseISO(d.date), 'MMM d'),
  }))

  const weights = data.map(d => d.weight_kg)
  const min = Math.floor(Math.min(...weights)) - 1
  const max = Math.ceil(Math.max(...weights)) + 1

  // Simple moving average (5-point)
  const withMA = chartData.map((d, i, arr) => {
    const window = arr.slice(Math.max(0, i - 2), i + 3)
    const ma = window.reduce((s, x) => s + x.weight, 0) / window.length
    return { ...d, ma: parseFloat(ma.toFixed(2)) }
  })

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={withMA} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
        <CartesianGrid stroke="#27272a" strokeDasharray="3 3" />
        <XAxis dataKey="label" tick={{ fontSize: 11, fill: '#71717a' }} />
        <YAxis domain={[min, max]} tick={{ fontSize: 11, fill: '#71717a' }} unit="kg" />
        <Tooltip
          contentStyle={{ background: '#18181b', border: '1px solid #3f3f46', borderRadius: 8 }}
          labelStyle={{ color: '#a1a1aa' }}
          itemStyle={{ color: '#e5e5e5' }}
          formatter={(v: number) => [`${v}kg`]}
        />
        <Line type="monotone" dataKey="weight" stroke="#10b981" strokeWidth={2} dot={{ r: 3, fill: '#10b981' }} name="Weight" />
        <Line type="monotone" dataKey="ma" stroke="#6366f1" strokeWidth={1.5} dot={false} strokeDasharray="4 2" name="Avg" />
      </LineChart>
    </ResponsiveContainer>
  )
}
