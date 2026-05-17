import uuid
from datetime import datetime, date

from sqlalchemy import String, DateTime, Date, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utcnow, new_uuid


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Nutrition
    calories_target: Mapped[int] = mapped_column(Integer, default=2000)
    protein_g: Mapped[float] = mapped_column(Float, default=150.0)
    carbs_g: Mapped[float] = mapped_column(Float, default=200.0)
    fat_g: Mapped[float] = mapped_column(Float, default=70.0)

    # Hydration & sleep
    water_ml: Mapped[int] = mapped_column(Integer, default=3000)
    sleep_hours: Mapped[float] = mapped_column(Float, default=8.0)

    # Supplements: [{"name": "Creatine", "dose": "5g", "timing": "morning"}, ...]
    supplements: Mapped[dict] = mapped_column(JSONB, default=list)

    # Weekly training split: {"monday": "push", "tuesday": "run", ...}
    weekly_training_split: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Running
    weekly_run_km: Mapped[float] = mapped_column(Float, default=0.0)
    weekly_run_sessions: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship("User", back_populates="goals")
