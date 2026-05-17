import uuid
from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utcnow, new_uuid


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    whatsapp_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Jerusalem")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    goals: Mapped[list["Goal"]] = relationship("Goal", back_populates="user", order_by="Goal.effective_date")
    nutrition_logs: Mapped[list["NutritionLog"]] = relationship("NutritionLog", back_populates="user")
    workout_logs: Mapped[list["WorkoutLog"]] = relationship("WorkoutLog", back_populates="user")
    weight_logs: Mapped[list["WeightLog"]] = relationship("WeightLog", back_populates="user")
    sleep_logs: Mapped[list["SleepLog"]] = relationship("SleepLog", back_populates="user")
    water_logs: Mapped[list["WaterLog"]] = relationship("WaterLog", back_populates="user")
    progress_photos: Mapped[list["ProgressPhoto"]] = relationship("ProgressPhoto", back_populates="user")
    weekly_plans: Mapped[list["WeeklyPlan"]] = relationship("WeeklyPlan", back_populates="user")
    conversation_context: Mapped["ConversationContext"] = relationship("ConversationContext", back_populates="user", uselist=False)
    oauth_tokens: Mapped[list["OAuthToken"]] = relationship("OAuthToken", back_populates="user")
