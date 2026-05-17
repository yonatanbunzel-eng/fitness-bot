import { useEffect, useState } from 'react'
import { format, parseISO } from 'date-fns'
import { he } from 'date-fns/locale'
import { api, Photo } from '../api/client'

type Category = 'all' | 'front' | 'side' | 'back' | 'weight_checkin' | 'food'

const CATEGORY_LABELS: Record<Category, string> = {
  all: 'הכל',
  front: 'קדמי',
  side: 'צד',
  back: 'אחורי',
  weight_checkin: 'משקל',
  food: 'אוכל',
}

export default function PhotosView() {
  const [photos, setPhotos] = useState<Photo[]>([])
  const [category, setCategory] = useState<Category>('all')
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<Photo | null>(null)

  useEffect(() => {
    setLoading(true)
    api.photos(undefined, category === 'all' ? undefined : category)
      .then(setPhotos)
      .finally(() => setLoading(false))
  }, [category])

  // Group by week
  const byWeek: Record<string, Photo[]> = {}
  for (const p of photos) {
    const key = `${p.year}-W${String(p.week).padStart(2, '0')}`
    if (!byWeek[key]) byWeek[key] = []
    byWeek[key].push(p)
  }
  const weeks = Object.keys(byWeek).sort((a, b) => b.localeCompare(a))

  return (
    <div className="space-y-5">
      {/* Header + filters */}
      <div className="flex items-center gap-3 flex-wrap">
        <h1 className="text-xl font-bold">תמונות</h1>
        <div className="flex gap-1 mr-auto flex-wrap">
          {(Object.keys(CATEGORY_LABELS) as Category[]).map(c => (
            <button
              key={c}
              onClick={() => setCategory(c)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                category === c ? 'bg-emerald-600 text-white' : 'bg-zinc-800 text-zinc-400 hover:text-white'
              }`}
            >
              {CATEGORY_LABELS[c]}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="text-zinc-500 text-center py-16">טוען...</div>
      ) : weeks.length === 0 ? (
        <div className="text-zinc-500 text-center py-16 space-y-2">
          <p>אין תמונות עדיין.</p>
          <p className="text-sm">שלח תמונה בוואטסאפ כדי להתחיל!</p>
        </div>
      ) : (
        weeks.map(week => (
          <div key={week} className="space-y-3">
            <h2 className="text-sm font-semibold text-zinc-400">
              שבוע {week.split('-W')[1]}, {week.split('-W')[0]}
              {byWeek[week][0]?.weight_kg && (
                <span className="text-zinc-500 font-normal mr-2">— {byWeek[week][0].weight_kg} ק״ג</span>
              )}
            </h2>
            <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
              {byWeek[week].map(p => (
                <button
                  key={p.id}
                  onClick={() => setSelected(p)}
                  className="relative aspect-square rounded-lg overflow-hidden bg-zinc-800 hover:ring-2 hover:ring-emerald-500 transition-all"
                >
                  <img
                    src={p.thumbnail_url || p.storage_url}
                    alt={CATEGORY_LABELS[p.category as Category] || p.category}
                    className="w-full h-full object-cover"
                  />
                  <span className="absolute bottom-1 right-1 text-xs bg-black/60 rounded px-1 text-white">
                    {CATEGORY_LABELS[p.category as Category] || p.category}
                  </span>
                </button>
              ))}
            </div>
          </div>
        ))
      )}

      {/* Lightbox */}
      {selected && (
        <div
          className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
          onClick={() => setSelected(null)}
        >
          <div className="max-w-md w-full space-y-3" onClick={e => e.stopPropagation()}>
            <img
              src={selected.storage_url}
              alt={selected.category}
              className="w-full rounded-xl object-contain max-h-[70vh]"
            />
            <div className="text-sm text-zinc-300 space-y-1">
              <p className="font-medium">
                {CATEGORY_LABELS[selected.category as Category] || selected.category}
                {' '} — שבוע {selected.week}/{selected.year}
              </p>
              <p className="text-zinc-500">
                {format(parseISO(selected.taken_at), "d בMMMM yyyy", { locale: he })}
              </p>
              {selected.weight_kg && <p>משקל: {selected.weight_kg} ק״ג</p>}
              {selected.caption && <p className="text-zinc-400 italic">"{selected.caption}"</p>}
            </div>
            <button
              onClick={() => setSelected(null)}
              className="w-full py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-sm text-zinc-300"
            >
              סגור
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
