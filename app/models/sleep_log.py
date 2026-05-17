import uuid
from datetime import datetime, date

from sqlalchemy import String, DateTime, Date, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utcnow, new_uuid


class SleepLog(Base):
    __tablename__ = "sleep_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    sleep_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sleep_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_hours: Mapped[float] = mapped_column(Float, nullable=False)
    quality_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-10
    source: Mapped[str] = mapped_column(String(20), default="manual")  # apple_health|manual

    user: Mapped["User"] = relationship("User", back_populates="sleep_logs")
