import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Integer, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utcnow, new_uuid


class ProgressPhoto(Base):
    __tablename__ = "progress_photos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    taken_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    # front|side|back|weight_checkin|food
    category: Mapped[str] = mapped_column(String(20), default="front")
    storage_url: Mapped[str] = mapped_column(Text, nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="progress_photos")
