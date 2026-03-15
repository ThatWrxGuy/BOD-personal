"""Strategic Signal model for external data ingestion."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class StrategicSignal(Base, TimestampMixin):
    """Strategic signal from external sources."""

    __tablename__ = "strategic_signals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # MARKET, PERSONAL_FINANCE, HEALTH, MACRO, CALENDAR, RESEARCH, SYSTEM
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    signal_strength: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # 0-10
    urgency: Mapped[int] = mapped_column(Integer, nullable=False, default=5)  # 1-10
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)  # 0-1
    signal_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Processed fields
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    meeting_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class SignalCategory:
    """Signal category constants."""

    MARKET = "MARKET"
    PERSONAL_FINANCE = "PERSONAL_FINANCE"
    HEALTH = "HEALTH"
    MACRO = "MACRO"
    CALENDAR = "CALENDAR"
    RESEARCH = "RESEARCH"
    SYSTEM = "SYSTEM"

    ALL = [
        MARKET,
        PERSONAL_FINANCE,
        HEALTH,
        MACRO,
        CALENDAR,
        RESEARCH,
        SYSTEM,
    ]
