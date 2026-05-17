import uuid
from datetime import datetime, date

from sqlalchemy import String, DateTime, Date, Integer, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utcnow, new_uuid


class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    workout_date: Mapped[date] = mapped_column(Date, nullable=False)

    source: Mapped[str] = mapped_column(String(20))  # voice|strava|text
    workout_type: Mapped[str] = mapped_column(String(20))  # strength|run|flexibility|other

    # For strength: [{"name": "squat", "sets": [{"reps": 8, "kg": 100}, ...]}]
    exercises: Mapped[list] = mapped_column(JSONB, default=list)

    # For running
    distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pace_min_per_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    strava_activity_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str] = mapped_column(Text, default="")

    user: Mapped["User"] = relationship("User", back_populates="workout_logs")
