from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.goal import Goal
from app.models.nutrition_log import NutritionLog
from app.models.workout_log import WorkoutLog
from app.models.water_log import WaterLog
from app.models.weekly_plan import WeeklyPlan
from app.models.conversation_context import ConversationContext


def get_active_goal(db: Session, user: User) -> Goal | None:
    today = date.today()
    return (
        db.query(Goal)
        .filter(Goal.user_id == user.id, Goal.effective_date <= today)
        .order_by(Goal.effective_date.desc())
        .first()
    )


def get_today_nutrition_totals(db: Session, user: User) -> dict:
    today = date.today()
    logs = (
        db.query(NutritionLog)
        .filter(
            NutritionLog.user_id == user.id,
            NutritionLog.logged_at >= today,
        )
        .all()
    )
    return {
        "calories": sum(l.calories for l in logs),
        "protein_g": sum(l.protein_g for l in logs),
        "carbs_g": sum(l.carbs_g for l in logs),
        "fat_g": sum(l.fat_g for l in logs),
    }


def get_today_water_ml(db: Session, user: User) -> int:
    today = date.today()
    from sqlalchemy import func
    result = (
        db.query(func.sum(WaterLog.amount_ml))
        .filter(WaterLog.user_id == user.id, WaterLog.logged_at >= today)
        .scalar()
    )
    return result or 0


def get_today_workout_summaries(db: Session, user: User) -> list[str]:
    today = date.today()
    logs = (
        db.query(WorkoutLog)
        .filter(WorkoutLog.user_id == user.id, WorkoutLog.workout_date == today)
        .all()
    )
    return [f"{w.workout_type}: {w.summary[:60]}" for w in logs]


def get_current_weekly_plan(db: Session, user: User) -> WeeklyPlan | None:
    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # Monday
    return (
        db.query(WeeklyPlan)
        .filter(WeeklyPlan.user_id == user.id, WeeklyPlan.week_start == week_start)
        .first()
    )


DAYS_HE = {
    "monday": "ב׳", "tuesday": "ג׳", "wednesday": "ד׳",
    "thursday": "ה׳", "friday": "ו׳", "saturday": "ש׳", "sunday": "א׳",
}


def format_weekly_plan_summary(plan: WeeklyPlan | None) -> str:
    if not plan or not plan.planned_sessions:
        return "לא נקבעה תוכנית שבועית."
    lines = []
    days_order = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for day in days_order:
        session = plan.planned_sessions.get(day)
        if session:
            day_label = DAYS_HE.get(day, day)
            if session.get("rest"):
                lines.append(f"  {day_label}: מנוחה")
            else:
                stype = session.get("type", "אימון")
                note = session.get("notes", "")
                done = "✓" if session.get("completed") else "○"
                lines.append(f"  {done} {day_label}: {stype}" + (f" — {note}" if note else ""))
    return "\n".join(lines)


def get_conversation_history(db: Session, user: User, max_turns: int = 10) -> list[dict]:
    ctx = (
        db.query(ConversationContext)
        .filter(ConversationContext.user_id == user.id)
        .first()
    )
    if not ctx or not ctx.messages:
        return []
    messages = ctx.messages[-max_turns * 2:]  # each turn = 2 messages
    return [{"role": m["role"], "content": m["content"]} for m in messages]


def append_to_conversation(db: Session, user: User, role: str, content: str) -> None:
    ctx = (
        db.query(ConversationContext)
        .filter(ConversationContext.user_id == user.id)
        .first()
    )
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).isoformat()
    new_msg = {"role": role, "content": content, "ts": ts}

    if not ctx:
        ctx = ConversationContext(user_id=user.id, messages=[new_msg])
        db.add(ctx)
    else:
        messages = list(ctx.messages or [])
        messages.append(new_msg)
        # Keep last 40 entries (20 turns)
        if len(messages) > 40:
            messages = messages[-40:]
        ctx.messages = messages

    db.commit()
