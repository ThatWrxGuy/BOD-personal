"""Board Schedule model."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class BoardSchedule(Base, TimestampMixin):
    """Board meeting schedule model."""

    __tablename__ = "board_schedules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    meeting_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )  # DAILY, WEEKLY, MONTHLY, QUARTERLY, ANNUAL
    scheduled_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    frequency: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "every day", "every monday"
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_run: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class MeetingType:
    """Meeting type constants."""

    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUAL = "ANNUAL"

    ALL = [DAILY, WEEKLY, MONTHLY, QUARTERLY, ANNUAL]
