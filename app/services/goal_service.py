from datetime import date

from sqlalchemy.orm import Session

from app.models.goal import Goal
from app.models.user import User


def update_goals(db: Session, user: User, tool_input: dict) -> Goal:
    goal = Goal(
        user_id=user.id,
        effective_date=date.today(),
        calories_target=tool_input.get("calories_target", 2000),
        protein_g=tool_input.get("protein_g", 150.0),
        carbs_g=tool_input.get("carbs_g", 200.0),
        fat_g=tool_input.get("fat_g", 70.0),
        water_ml=tool_input.get("water_ml", 3000),
        sleep_hours=tool_input.get("sleep_hours", 8.0),
        supplements=tool_input.get("supplements", []),
        weekly_training_split=tool_input.get("weekly_training_split", {}),
        weekly_run_km=tool_input.get("weekly_run_km", 0.0),
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal
