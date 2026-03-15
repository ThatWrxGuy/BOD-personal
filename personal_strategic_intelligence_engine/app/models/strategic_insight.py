"""Strategic Insight model."""
from typing import Optional

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class StrategicInsight(Base, TimestampMixin):
    """Strategic insight extracted from meetings or reviews."""

    __tablename__ = "strategic_insights"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # strategy, finance, risk, etc.
    insight_text: Mapped[str] = mapped_column(Text, nullable=False)
    supporting_evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-10
    meeting_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Optional link to meeting
