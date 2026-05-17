import uuid
from datetime import datetime, date

from sqlalchemy import String, DateTime, Date, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utcnow, new_uuid


class WeeklyPlan(Base):
    __tablename__ = "weekly_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)  # always Monday

    user_stated_plan: Mapped[str] = mapped_column(Text, default="")

    # {"monday": {"type": "push", "target_exercises": [...]}, "tuesday": {"type": "run", ...}, ...}
    planned_sessions: Mapped[dict] = mapped_column(JSONB, default=dict)

    # [{"start": "2026-05-14T18:00", "end": "2026-05-14T20:00", "title": "Meeting"}]
    calendar_events: Mapped[list] = mapped_column(JSONB, default=list)

    # [{"date": "2026-05-15", "reason": "Busy evening", "change": "Moved run to Wednesday"}]
    adaptations: Mapped[list] = mapped_column(JSONB, default=list)

    completion_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship("User", back_populates="weekly_plans")
