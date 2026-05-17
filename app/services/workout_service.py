from datetime import date

from sqlalchemy.orm import Session

from app.models.workout_log import WorkoutLog
from app.models.user import User


def create_log(db: Session, user: User, tool_input: dict) -> WorkoutLog:
    workout_date_str = tool_input.get("workout_date")
    workout_date = date.fromisoformat(workout_date_str) if workout_date_str else date.today()

    log = WorkoutLog(
        user_id=user.id,
        workout_date=workout_date,
        source=tool_input.get("source", "text"),
        workout_type=tool_input.get("workout_type", "other"),
        exercises=tool_input.get("exercises", []),
        distance_km=tool_input.get("distance_km"),
        duration_minutes=tool_input.get("duration_minutes"),
        pace_min_per_km=tool_input.get("pace_min_per_km"),
        strava_activity_id=tool_input.get("strava_activity_id"),
        transcript=tool_input.get("transcript"),
        summary=tool_input.get("summary", ""),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def create_from_strava(db: Session, user: User, activity: dict) -> WorkoutLog:
    distance_km = activity.get("distance", 0) / 1000
    duration_min = activity.get("moving_time", 0) // 60
    pace = (activity.get("moving_time", 0) / 60) / (distance_km or 1)

    log = WorkoutLog(
        user_id=user.id,
        workout_date=date.today(),
        source="strava",
        workout_type="run" if activity.get("type") == "Run" else "other",
        distance_km=round(distance_km, 2),
        duration_minutes=duration_min,
        pace_min_per_km=round(pace, 2),
        strava_activity_id=str(activity.get("id", "")),
        summary=f"{distance_km:.1f}km in {duration_min}min — {activity.get('name', 'Activity')}",
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def mark_plan_session_complete(db: Session, workout_log: WorkoutLog, weekly_plan) -> None:
    """Mark today's session in the weekly plan as completed."""
    if not weekly_plan:
        return
    day_name = workout_log.workout_date.strftime("%A").lower()
    sessions = dict(weekly_plan.planned_sessions or {})
    if day_name in sessions:
        sessions[day_name]["completed"] = True
        weekly_plan.planned_sessions = sessions
        db.commit()
