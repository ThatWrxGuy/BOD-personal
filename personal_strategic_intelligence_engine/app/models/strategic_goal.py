"""Strategic Goal model."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class StrategicGoal(Base, TimestampMixin):
    """Strategic goal model."""

    __tablename__ = "strategic_goals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # CAREER, FINANCE, HEALTH, etc.
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=5)  # 1-10
    target_value: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    current_value: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    target_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")  # ACTIVE, COMPLETED, ABANDONED


class GoalCategory:
    """Goal category constants."""

    CAREER = "CAREER"
    FINANCE = "FINANCE"
    HEALTH = "HEALTH"
    RELATIONSHIPS = "RELATIONSHIPS"
    PERSONAL_GROWTH = "PERSONAL_GROWTH"
    OPERATIONS = "OPERATIONS"
    LEGACY = "LEGACY"
    OTHER = "OTHER"

    ALL = [CAREER, FINANCE, HEALTH, RELATIONSHIPS, PERSONAL_GROWTH, OPERATIONS, LEGACY, OTHER]


class GoalStatus:
    """Goal status constants."""

    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"

    ALL = [ACTIVE, COMPLETED, ABANDONED]
