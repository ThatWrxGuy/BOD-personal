"""Goal Probability database model."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class GoalProbability(Base, TimestampMixin):
    """Goal probability estimation model."""

    __tablename__ = "goal_probabilities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    goal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategic_goals.id"),
        nullable=False,
    )
    probability_of_success: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    estimated_completion_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    calculation_method: Mapped[str] = mapped_column(String(100), nullable=False)
    # e.g., "linear_projection", "velocity_analysis", "historical_pattern"
    factors: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationship
    goal = relationship("StrategicGoal", backref="probability_estimates")
