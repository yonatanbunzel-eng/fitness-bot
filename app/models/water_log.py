import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utcnow, new_uuid


class WaterLog(Base):
    __tablename__ = "water_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    amount_ml: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="water_logs")
