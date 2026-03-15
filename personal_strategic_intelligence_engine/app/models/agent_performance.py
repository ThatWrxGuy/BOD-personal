"""Agent Performance model."""
from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class AgentPerformance(Base, TimestampMixin):
    """Performance metrics for an agent version."""

    __tablename__ = "agent_performance"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agent_definitions.id"), nullable=False)
    version_id: Mapped[str] = mapped_column(String(50), nullable=False)
    accuracy_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-10
    usefulness_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-10
    calibration_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-10
    false_positive_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-1
    false_negative_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-1
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    agent: Mapped["AgentDefinition"] = relationship("AgentDefinition")
