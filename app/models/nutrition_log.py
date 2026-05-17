import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Integer, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utcnow, new_uuid


class NutritionLog(Base):
    __tablename__ = "nutrition_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    meal_type: Mapped[str] = mapped_column(String(20))  # breakfast|lunch|dinner|snack

    source: Mapped[str] = mapped_column(String(20))  # photo|text|voice
    raw_input_description: Mapped[str] = mapped_column(Text, default="")

    # [{"name": "chicken breast", "grams": 150, "calories": 248, "protein": 46, "carbs": 0, "fat": 5}]
    food_items: Mapped[list] = mapped_column(JSONB, default=list)
    calories: Mapped[int] = mapped_column(Integer, default=0)
    protein_g: Mapped[float] = mapped_column(Float, default=0.0)
    carbs_g: Mapped[float] = mapped_column(Float, default=0.0)
    fat_g: Mapped[float] = mapped_column(Float, default=0.0)
    fiber_g: Mapped[float] = mapped_column(Float, default=0.0)

    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[str] = mapped_column(String(10), default="medium")  # high|medium|low
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="nutrition_logs")
