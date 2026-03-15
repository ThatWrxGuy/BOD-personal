"""Critique Response model."""
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class CritiqueResponse(Base, TimestampMixin):
    """Critique from one agent targeting another agent's recommendation."""

    __tablename__ = "critique_responses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("board_meetings.id"), nullable=False)
    source_agent_id: Mapped[int] = mapped_column(ForeignKey("agent_definitions.id"), nullable=False)
    target_agent_id: Mapped[int] = mapped_column(ForeignKey("agent_definitions.id"), nullable=False)
    critique_text: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="medium")  # low, medium, high, critical

    # Relationships
    meeting: Mapped["BoardMeeting"] = relationship("BoardMeeting", back_populates="critique_responses")
    source_agent: Mapped["AgentDefinition"] = relationship(
        "AgentDefinition", foreign_keys=[source_agent_id]
    )
    target_agent: Mapped["AgentDefinition"] = relationship(
        "AgentDefinition", foreign_keys=[target_agent_id]
    )
