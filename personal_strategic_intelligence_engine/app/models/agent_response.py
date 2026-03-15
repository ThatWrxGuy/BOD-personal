"""Agent Response model."""
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class AgentResponse(Base, TimestampMixin):
    """Response from a board agent during a meeting."""

    __tablename__ = "agent_responses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("board_meetings.id"), nullable=False)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agent_definitions.id"), nullable=False)
    summary_judgment: Mapped[str] = mapped_column(Text, nullable=False)
    main_recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    supporting_reasons: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    main_risks: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    tradeoffs: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    requested_followups: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    confidence_score: Mapped[Optional[float]] = mapped_column(Integer, nullable=True)
    version_id: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")
    raw_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    meeting: Mapped["BoardMeeting"] = relationship("BoardMeeting", back_populates="agent_responses")
    agent: Mapped["AgentDefinition"] = relationship("AgentDefinition")
