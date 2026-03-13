"""Canonical signal models for live signal ingestion layer."""
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class SignalSourceCategory(str, Enum):
    """Categories of signal sources."""
    FINANCIAL_DATA = "financial_data"
    PRODUCTIVITY_SIGNALS = "productivity_signals"
    OPERATIONAL_METRICS = "operational_metrics"
    MARKET_NEWS = "market_news"
    SYSTEM_TELEMETRY = "system_telemetry"
    WEARABLE_DEVICES = "wearable_devices"
    CALENDAR_SCHEDULES = "calendar_schedules"
    CUSTOM = "custom"


class SignalType(str, Enum):
    """Types of signals."""
    PERFORMANCE = "performance"
    RISK = "risk"
    OPPORTUNITY = "opportunity"
    RESOURCE = "resource"
    MOMENTUM = "momentum"
    ALIGNMENT = "alignment"
    HEALTH = "health"
    WEALTH = "wealth"
    CAREER = "career"
    RELATIONSHIPS = "relationships"
    LEARNING = "learning"
    CUSTOM = "custom"


class SignalSource(BaseModel):
    """Represents a signal provider source."""
    source_id: str
    name: str
    category: SignalSourceCategory
    description: Optional[str] = None
    enabled: bool = True
    health_status: str = "unknown"
    last_ingestion: Optional[datetime] = None
    reliability_score: float = Field(ge=0, le=1, default=0.5)
    config: dict = Field(default_factory=dict)


class LiveSignal(BaseModel):
    """Raw signal from an external provider."""
    source_id: str
    signal_type: SignalType
    raw_payload: dict
    timestamp: datetime
    provider_specific_id: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class NormalizedSignal(BaseModel):
    """Canonical normalized signal for internal consumption."""
    source_id: str
    signal_type: SignalType
    raw_payload: dict
    normalized_payload: dict
    timestamp: datetime
    ingestion_timestamp: datetime = Field(default_factory=datetime.utcnow)
    freshness_score: float = Field(ge=0, le=1)
    confidence_score: float = Field(ge=0, le=1)
    signal_id: str = Field(default_factory=lambda: str(datetime.utcnow().timestamp()))


class SignalIntegrityReport(BaseModel):
    """Report on signal integrity validation."""
    signal_id: str
    is_valid: bool
    validation_errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    freshness_score: float = Field(ge=0, le=1)
    completeness_score: float = Field(ge=0, le=1)


class SignalIngestionEvent(BaseModel):
    """Structured log event for signal ingestion."""
    event_id: str = Field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    source_id: str
    signal_type: SignalType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ingestion_timestamp: datetime = Field(default_factory=datetime.utcnow)
    validation_status: str
    freshness_score: float = Field(ge=0, le=1)
    routing_destinations: list[str] = Field(default_factory=list)
    processing_latency_ms: float = 0.0
    error_message: Optional[str] = None


class SignalHealthStatus(BaseModel):
    """Health status of a signal source."""
    source_id: str
    status: str  # healthy, degraded, down, unknown
    uptime_percentage: float = 0.0
    avg_latency_ms: float = 0.0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    stale_signal_count: int = 0


# Constants
LIVE_EXECUTION_ENABLED = False  # Safety flag - no autonomous execution

DEFAULT_FRESHNESS_WINDOW_SECONDS = 300  # 5 minutes
MIN_CONFIDENCE_THRESHOLD = 0.3
