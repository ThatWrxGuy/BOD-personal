"""Goal Progress model."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Numeric, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class GoalProgress(Base, TimestampMixin):
    """Goal progress tracking model."""

    __tablename__ = "goal_progress"

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
    recorded_value: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship
    goal = relationship("StrategicGoal", backref="progress_records")
