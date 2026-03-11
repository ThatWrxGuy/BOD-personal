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
    
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # opportunity, risk, anomaly, pattern
    domain: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Classification
    severity: Mapped[str] = mapped_column(String(20), default=DetectionSeverity.MEDIUM)
    status: Mapped[str] = mapped_column(String(20), default=DetectionStatus.ACTIVE)
    
    # Content
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Confidence
    confidence_score: Mapped[float] = mapped_column(Float, nullable=True)
    
    # Impact estimates
    impact_estimate: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    probability_estimate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Recommended action
    recommended_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Source
    source_signals: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    # Context
    correlation_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    # Timestamps
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class OpportunitySignal(Base):
    """Opportunity detection signal."""
    
    __tablename__ = "opportunity_signals"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    detected_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("detected_events.id"),
        nullable=False,
    )
    
    opportunity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    potential_value: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    time_sensitivity: Mapped[str] = mapped_column(String(20), default="medium")


class RiskSignal(Base):
    """Risk detection signal."""
    
    __tablename__ = "risk_signals"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    detected_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("detected_events.id"),
        nullable=False,
    )
    
    risk_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default=DetectionSeverity.MEDIUM)
    mitigation_suggestion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
