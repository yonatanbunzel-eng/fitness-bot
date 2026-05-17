from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.nutrition_log import NutritionLog
from app.models.user import User


def create_log(db: Session, user: User, tool_input: dict) -> NutritionLog:
    log = NutritionLog(
        user_id=user.id,
        meal_type=tool_input.get("meal_type", "snack"),
        source=tool_input.get("source", "text"),
        raw_input_description=tool_input.get("raw_input_description", ""),
        food_items=tool_input.get("food_items", []),
        calories=tool_input.get("total_calories", 0),
        protein_g=tool_input.get("total_protein_g", 0.0),
        carbs_g=tool_input.get("total_carbs_g", 0.0),
        fat_g=tool_input.get("total_fat_g", 0.0),
        fiber_g=tool_input.get("total_fiber_g", 0.0),
        photo_url=tool_input.get("photo_url"),
        confidence=tool_input.get("confidence", "medium"),
        notes=tool_input.get("notes"),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
