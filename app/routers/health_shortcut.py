"""
POST /health/shortcut
Receives data from iOS Shortcuts automation (Apple Health sync).
"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.weight_log import WeightLog
from app.models.sleep_log import SleepLog

router = APIRouter()


class HealthData(BaseModel):
    api_key: str
    date: Optional[str] = None  # YYYY-MM-DD, defaults to today
    weight_kg: Optional[float] = None
    sleep_hours: Optional[float] = None
    sleep_quality: Optional[int] = None  # 1-10
    steps: Optional[int] = None
    body_fat_pct: Optional[float] = None


@router.post("/health/shortcut")
async def receive_health_data(
    data: HealthData,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if data.api_key != settings.health_shortcut_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    log_date = date.fromisoformat(data.date) if data.date else date.today()
    results = []

    if data.weight_kg is not None:
        # Upsert: remove any existing apple_health entry for today then add new
        db.query(WeightLog).filter(
            WeightLog.user_id == user.id,
            WeightLog.source == "apple_health",
        ).filter(
            WeightLog.logged_at >= log_date,
        ).delete()

        log = WeightLog(
            user_id=user.id,
            weight_kg=data.weight_kg,
            source="apple_health",
            body_fat_pct=data.body_fat_pct,
        )
        db.add(log)
        results.append(f"weight: {data.weight_kg}kg")

    if data.sleep_hours is not None:
        existing = (
            db.query(SleepLog)
            .filter(SleepLog.user_id == user.id, SleepLog.date == log_date, SleepLog.source == "apple_health")
            .first()
        )
        if existing:
            existing.duration_hours = data.sleep_hours
            existing.quality_score = data.sleep_quality
        else:
            log = SleepLog(
                user_id=user.id,
                date=log_date,
                duration_hours=data.sleep_hours,
                quality_score=data.sleep_quality,
                source="apple_health",
            )
            db.add(log)
        results.append(f"sleep: {data.sleep_hours}h")

    db.commit()
    return {"status": "ok", "logged": results}
