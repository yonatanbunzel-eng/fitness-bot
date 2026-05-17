const API_KEY = import.meta.env.VITE_API_KEY || ''
const BASE = import.meta.env.VITE_API_BASE || ''

async function get<T>(path: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(`${BASE}${path}`, window.location.origin)
  if (params) Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v))
  const res = await fetch(url.toString(), {
    headers: { 'X-Api-Key': API_KEY },
  })
  if (!res.ok) throw new Error(`API error ${res.status}`)
  return res.json()
}

export const api = {
  dailySummary: (date?: string) =>
    get<DailySummary>('/api/v1/daily-summary', date ? { date } : {}),

  weeklySummary: (weekStart?: string) =>
    get<WeeklySummary>('/api/v1/weekly-summary', weekStart ? { week_start: weekStart } : {}),

  weightTrend: (weeks = 12) =>
    get<WeightPoint[]>('/api/v1/weight-trend', { weeks: String(weeks) }),

  strengthProgress: (exercise: string, weeks = 12) =>
    get<StrengthPoint[]>('/api/v1/strength-progress', { exercise, weeks: String(weeks) }),

  runStats: (weeks = 8) =>
    get<RunPoint[]>('/api/v1/run-stats', { weeks: String(weeks) }),

  photos: (week?: string, category?: string) => {
    const params: Record<string, string> = {}
    if (week) params.week = week
    if (category) params.category = category
    return get<Photo[]>('/api/v1/photos', params)
  },

  currentGoals: () => get<Goals>('/api/v1/goals/current'),
}

// Types
export interface Goals {
  calories_target: number
  protein_g: number
  carbs_g: number
  fat_g: number
  water_ml: number
  sleep_hours: number
  supplements: { name: string; dose: string; timing: string }[]
  weekly_run_km: number
}

export interface Meal {
  id: string
  meal_type: string
  logged_at: string
  calories: number
  protein_g: number
  food_items: { name: string; calories: number }[]
  photo_url: string | null
  confidence: string
}

export interface Workout {
  id: string
  workout_type: string
  summary: string
  duration_minutes: number | null
  distance_km: number | null
  source: string
}

export interface DailySummary {
  date: string
  goals: Goals
  consumed: { calories: number; protein_g: number; carbs_g: number; fat_g: number }
  water_ml: number
  sleep: { hours: number; quality: number | null } | null
  weight_kg: number | null
  meals: Meal[]
  workouts: Workout[]
}

export interface WeeklySummary {
  week_start: string
  plan: {
    sessions: Record<string, { type: string; rest?: boolean; completed?: boolean; notes?: string }>
    adaptations: { date: string; reason: string; change: string }[]
    completion_rate: number | null
  } | null
  workouts: (Workout & { date: string })[]
  daily_calories: { date: string; calories: number }[]
  run_km_total: number
  run_km_goal: number
}

export interface WeightPoint {
  date: string
  weight_kg: number
  body_fat_pct: number | null
  source: string
}

export interface StrengthPoint {
  date: string
  max_kg: number
  sets: number
}

export interface RunPoint {
  date: string
  distance_km: number | null
  duration_minutes: number | null
  pace_min_per_km: number | null
  source: string
}

export interface Photo {
  id: string
  taken_at: string
  week: number
  year: number
  category: string
  thumbnail_url: string
  storage_url: string
  weight_kg: number | null
  caption: string | null
}
