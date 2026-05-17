"""
GET /api/v1/* — all dashboard data endpoints.
Protected by X-Api-Key header matching DASHBOARD_API_KEY.
"""
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, verify_dashboard_key
from app.models.user import User
from app.models.nutrition_log import NutritionLog
from app.models.workout_log import WorkoutLog
from app.models.weight_log import WeightLog
from app.models.sleep_log import SleepLog
from app.models.water_log import WaterLog
from app.models.progress_photo import ProgressPhoto
from app.models.weekly_plan import WeeklyPlan
from app.claude.context_builder import get_active_goal, get_current_weekly_plan

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_dashboard_key)])


@router.get("/daily-summary")
def daily_summary(
    date_str: Optional[str] = Query(None, alias="date"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    target_date = date.fromisoformat(date_str) if date_str else date.today()
    next_day = target_date + timedelta(days=1)

    goal = get_active_goal(db, user)
    nutrition_logs = db.query(NutritionLog).filter(
        NutritionLog.user_id == user.id,
        NutritionLog.logged_at >= target_date,
        NutritionLog.logged_at < next_day,
    ).all()

    water_ml = db.query(func.sum(WaterLog.amount_ml)).filter(
        WaterLog.user_id == user.id,
        WaterLog.logged_at >= target_date,
        WaterLog.logged_at < next_day,
    ).scalar() or 0

    sleep = db.query(SleepLog).filter(
        SleepLog.user_id == user.id, SleepLog.date == target_date
    ).first()

    workouts = db.query(WorkoutLog).filter(
        WorkoutLog.user_id == user.id, WorkoutLog.workout_date == target_date
    ).all()

    weight = db.query(WeightLog).filter(
        WeightLog.user_id == user.id,
        WeightLog.logged_at >= target_date,
        WeightLog.logged_at < next_day,
    ).order_by(WeightLog.logged_at.desc()).first()

    total_calories = sum(n.calories for n in nutrition_logs)
    total_protein = sum(n.protein_g for n in nutrition_logs)
    total_carbs = sum(n.carbs_g for n in nutrition_logs)
    total_fat = sum(n.fat_g for n in nutrition_logs)

    return {
        "date": target_date.isoformat(),
        "goals": {
            "calories": goal.calories_target if goal else 2000,
            "protein_g": goal.protein_g if goal else 150,
            "carbs_g": goal.carbs_g if goal else 200,
            "fat_g": goal.fat_g if goal else 70,
            "water_ml": goal.water_ml if goal else 3000,
            "sleep_hours": goal.sleep_hours if goal else 8.0,
        },
        "consumed": {
            "calories": total_calories,
            "protein_g": round(total_protein, 1),
            "carbs_g": round(total_carbs, 1),
            "fat_g": round(total_fat, 1),
        },
        "water_ml": water_ml,
        "sleep": {"hours": sleep.duration_hours, "quality": sleep.quality_score} if sleep else None,
        "weight_kg": weight.weight_kg if weight else None,
        "meals": [
            {
                "id": str(n.id),
                "meal_type": n.meal_type,
                "logged_at": n.logged_at.isoformat(),
                "calories": n.calories,
                "protein_g": n.protein_g,
                "food_items": n.food_items,
                "photo_url": n.photo_url,
                "confidence": n.confidence,
            }
            for n in nutrition_logs
        ],
        "workouts": [
            {
                "id": str(w.id),
                "workout_type": w.workout_type,
                "summary": w.summary,
                "duration_minutes": w.duration_minutes,
                "distance_km": w.distance_km,
                "source": w.source,
            }
            for w in workouts
        ],
    }


@router.get("/weekly-summary")
def weekly_summary(
    week_start_str: Optional[str] = Query(None, alias="week_start"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if week_start_str:
        week_start = date.fromisoformat(week_start_str)
    else:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=7)

    goal = get_active_goal(db, user)
    plan = db.query(WeeklyPlan).filter(
        WeeklyPlan.user_id == user.id, WeeklyPlan.week_start == week_start
    ).first()

    workouts = db.query(WorkoutLog).filter(
        WorkoutLog.user_id == user.id,
        WorkoutLog.workout_date >= week_start,
        WorkoutLog.workout_date < week_end,
    ).all()

    # Daily calorie totals
    daily = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        cals = db.query(func.sum(NutritionLog.calories)).filter(
            NutritionLog.user_id == user.id,
            NutritionLog.logged_at >= day,
            NutritionLog.logged_at < day + timedelta(days=1),
        ).scalar() or 0
        daily.append({"date": day.isoformat(), "calories": cals})

    run_km = sum(w.distance_km or 0 for w in workouts if w.workout_type == "run")

    return {
        "week_start": week_start.isoformat(),
        "plan": {
            "sessions": plan.planned_sessions if plan else {},
            "adaptations": plan.adaptations if plan else [],
            "completion_rate": plan.completion_rate,
        } if plan else None,
        "workouts": [
            {
                "id": str(w.id),
                "date": w.workout_date.isoformat(),
                "type": w.workout_type,
                "summary": w.summary,
                "distance_km": w.distance_km,
                "duration_minutes": w.duration_minutes,
                "source": w.source,
            }
            for w in workouts
        ],
        "daily_calories": daily,
        "run_km_total": round(run_km, 2),
        "run_km_goal": goal.weekly_run_km if goal else 0,
    }


@router.get("/weight-trend")
def weight_trend(
    weeks: int = Query(12),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    since = date.today() - timedelta(weeks=weeks)
    logs = db.query(WeightLog).filter(
        WeightLog.user_id == user.id,
        WeightLog.logged_at >= since,
    ).order_by(WeightLog.logged_at).all()

    return [
        {
            "date": w.logged_at.date().isoformat(),
            "weight_kg": w.weight_kg,
            "body_fat_pct": w.body_fat_pct,
            "source": w.source,
        }
        for w in logs
    ]


@router.get("/strength-progress")
def strength_progress(
    exercise: str = Query(...),
    weeks: int = Query(12),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    since = date.today() - timedelta(weeks=weeks)
    logs = db.query(WorkoutLog).filter(
        WorkoutLog.user_id == user.id,
        WorkoutLog.workout_type == "strength",
        WorkoutLog.workout_date >= since,
    ).order_by(WorkoutLog.workout_date).all()

    results = []
    exercise_lower = exercise.lower()
    for log in logs:
        for ex in (log.exercises or []):
            if exercise_lower in ex.get("name", "").lower():
                sets = ex.get("sets", [])
                if sets:
                    max_weight = max((s.get("kg", 0) for s in sets), default=0)
                    results.append({
                        "date": log.workout_date.isoformat(),
                        "max_kg": max_weight,
                        "sets": len(sets),
                    })
    return results


@router.get("/run-stats")
def run_stats(
    weeks: int = Query(8),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    since = date.today() - timedelta(weeks=weeks)
    runs = db.query(WorkoutLog).filter(
        WorkoutLog.user_id == user.id,
        WorkoutLog.workout_type == "run",
        WorkoutLog.workout_date >= since,
    ).order_by(WorkoutLog.workout_date).all()

    return [
        {
            "date": r.workout_date.isoformat(),
            "distance_km": r.distance_km,
            "duration_minutes": r.duration_minutes,
            "pace_min_per_km": r.pace_min_per_km,
            "source": r.source,
        }
        for r in runs
    ]


@router.get("/photos")
def get_photos(
    week: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(ProgressPhoto).filter(ProgressPhoto.user_id == user.id)
    if week:
        week_date = date.fromisoformat(week)
        iso = week_date.isocalendar()
        q = q.filter(ProgressPhoto.week_number == iso.week, ProgressPhoto.year == iso.year)
    if category:
        q = q.filter(ProgressPhoto.category == category)
    photos = q.order_by(ProgressPhoto.taken_at.desc()).limit(100).all()

    return [
        {
            "id": str(p.id),
            "taken_at": p.taken_at.isoformat(),
            "week": p.week_number,
            "year": p.year,
            "category": p.category,
            "thumbnail_url": p.thumbnail_url,
            "storage_url": p.storage_url,
            "weight_kg": p.weight_kg,
            "caption": p.caption,
        }
        for p in photos
    ]


@router.get("/goals/current")
def current_goals(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    goal = get_active_goal(db, user)
    if not goal:
        return {}
    return {
        "calories_target": goal.calories_target,
        "protein_g": goal.protein_g,
        "carbs_g": goal.carbs_g,
        "fat_g": goal.fat_g,
        "water_ml": goal.water_ml,
        "sleep_hours": goal.sleep_hours,
        "supplements": goal.supplements,
        "weekly_training_split": goal.weekly_training_split,
        "weekly_run_km": goal.weekly_run_km,
    }
