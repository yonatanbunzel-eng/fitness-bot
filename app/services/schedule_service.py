from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.weekly_plan import WeeklyPlan
from app.models.user import User


def get_week_start(d: date | None = None) -> date:
    d = d or date.today()
    return d - timedelta(days=d.weekday())  # Monday


def set_weekly_plan(db: Session, user: User, tool_input: dict) -> WeeklyPlan:
    week_start = get_week_start()
    plan = (
        db.query(WeeklyPlan)
        .filter(WeeklyPlan.user_id == user.id, WeeklyPlan.week_start == week_start)
        .first()
    )
    if plan:
        plan.planned_sessions = tool_input.get("planned_sessions", {})
        plan.user_stated_plan = tool_input.get("user_stated_plan", "")
    else:
        plan = WeeklyPlan(
            user_id=user.id,
            week_start=week_start,
            planned_sessions=tool_input.get("planned_sessions", {}),
            user_stated_plan=tool_input.get("user_stated_plan", ""),
        )
        db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def apply_adaptation(db: Session, plan: WeeklyPlan, tool_input: dict) -> WeeklyPlan:
    updated = tool_input.get("updated_sessions", {})
    reason = tool_input.get("adaptation_reason", "")

    sessions = dict(plan.planned_sessions or {})
    for day, session_data in updated.items():
        sessions[day] = session_data
    plan.planned_sessions = sessions

    adaptations = list(plan.adaptations or [])
    adaptations.append({
        "date": date.today().isoformat(),
        "reason": reason,
        "change": str(updated),
    })
    plan.adaptations = adaptations

    db.commit()
    db.refresh(plan)
    return plan


def record_adaptation(
    db: Session,
    plan: WeeklyPlan,
    trigger_date: date,
    reason: str,
    workout_type: str,
) -> None:
    adaptations = list(plan.adaptations or [])
    adaptations.append({
        "date": trigger_date.isoformat(),
        "reason": reason,
        "type": workout_type,
    })
    plan.adaptations = adaptations
    db.commit()


def calculate_completion_rate(plan: WeeklyPlan) -> float:
    sessions = plan.planned_sessions or {}
    planned = [d for d, s in sessions.items() if not s.get("rest")]
    completed = [d for d, s in sessions.items() if s.get("completed") and not s.get("rest")]
    if not planned:
        return 0.0
    return len(completed) / len(planned)
