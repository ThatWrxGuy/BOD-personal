"""Detection data models."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, String, Text, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class DetectionEventType(str, Enum):
    """Detection event types."""
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    ANOMALY = "anomaly"
    PATTERN = "pattern"


class DetectionSeverity(str, Enum):
    """Detection severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DetectionStatus(str, Enum):
    """Detection event status."""
    ACTIVE = "active"
    INVESTIGATING = "investigating"
    ADDRESSED = "addressed"
    DISMISSED = "dismissed"


class DomainType(str, Enum):
    """Detection domains."""
    FINANCIAL = "financial"
    HEALTH = "health"
    PRODUCTIVITY = "productivity"
    PROJECTS = "projects"
    STRATEGIC = "strategic"


class DetectedEvent(Base, TimestampMixin):
    """Detected event record."""

    __tablename__ = "detected_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    domain: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default=DetectionSeverity.MEDIUM)
    status: Mapped[str] = mapped_column(String(20), default=DetectionStatus.ACTIVE)
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    impact_estimate: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    probability_estimate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recommended_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_signals: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    correlation_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
