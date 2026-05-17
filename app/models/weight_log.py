import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utcnow, new_uuid


class WeightLog(Base):
    __tablename__ = "weight_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(String(20), default="manual")  # apple_health|manual|photo_check_in
    body_fat_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="weight_logs")
