"""Decision Record model."""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class DecisionRecord(Base, TimestampMixin):
    """Record of a decision made by the user following a board recommendation."""

    __tablename__ = "decision_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    meeting_id: Mapped[Optional[int]] = mapped_column(ForeignKey("board_meetings.id"), nullable=True)
    decision_summary: Mapped[str] = mapped_column(Text, nullable=False)
    chosen_action: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")  # pending, decided, reviewed
    review_due_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    meeting: Mapped[Optional["BoardMeeting"]] = relationship("BoardMeeting", back_populates="decisions")
    outcome_reviews: Mapped[list["OutcomeReview"]] = relationship(
        "OutcomeReview", back_populates="decision", cascade="all, delete-orphan"
    )
