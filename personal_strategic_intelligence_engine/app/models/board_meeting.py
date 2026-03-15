"""Board Meeting model."""
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class BoardMeeting(Base, TimestampMixin):
    """Strategic board meeting record."""

    __tablename__ = "board_meetings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    meeting_type: Mapped[str] = mapped_column(String(50), nullable=False)  # strategic, weekly, monthly
    trigger_type: Mapped[str] = mapped_column(String(50), nullable=False)  # manual, scheduled
    question: Mapped[str] = mapped_column(Text, nullable=False)
    context_snapshot: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    executive_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    consensus_recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    alternatives: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    risks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    tradeoffs: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    confidence_score: Mapped[Optional[float]] = mapped_column(Integer, nullable=True)
    data_gaps: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")

    # Relationships
    agent_responses: Mapped[list["AgentResponse"]] = relationship(
        "AgentResponse", back_populates="meeting", cascade="all, delete-orphan"
    )
    critique_responses: Mapped[list["CritiqueResponse"]] = relationship(
        "CritiqueResponse", back_populates="meeting", cascade="all, delete-orphan"
    )
    decisions: Mapped[list["DecisionRecord"]] = relationship(
        "DecisionRecord", back_populates="meeting", cascade="all, delete-orphan"
    )
