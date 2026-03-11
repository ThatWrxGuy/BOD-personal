"""Outcome Review model."""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class OutcomeReview(Base, TimestampMixin):
    """Outcome review for a decision record."""

    __tablename__ = "outcome_reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    decision_id: Mapped[int] = mapped_column(ForeignKey("decision_records.id"), nullable=False)
    actual_result: Mapped[str] = mapped_column(Text, nullable=False)
    success_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-10
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    decision: Mapped["DecisionRecord"] = relationship("DecisionRecord", back_populates="outcome_reviews")
