"""Connector Models.

Defines standardized connector objects and signal schemas.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ConnectorStatus(str, Enum):
    """Connector operational status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    DISABLED = "disabled"
    CONNECTING = "connecting"


class ConnectorType(str, Enum):
    """Types of connectors."""
    CALENDAR = "calendar"
    FINANCE = "finance"
    TASKS = "tasks"
    HEALTH = "health"
    CUSTOM = "custom"


class SignalPriority(str, Enum):
    """Priority of signals from connectors."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConnectorSource(BaseModel):
    """Represents a configured connector source."""
    name: str
    connector_type: ConnectorType
    status: ConnectorStatus = ConnectorStatus.INACTIVE
    enabled: bool = False
    config: Dict[str, Any] = Field(default_factory=dict)
    credentials: Dict[str, str] = Field(default_factory=dict)
    interval_seconds: int = 300
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_sync: Optional[datetime] = None
    last_success: Optional[datetime] = None


class ConnectorSignal(BaseModel):
    """Normalized signal from a connector."""
    connector_name: str
    signal_type: str
    category: str
    priority: SignalPriority = SignalPriority.MEDIUM
    
    # Signal content
    title: str
    description: Optional[str] = None
    value: float = 0.0
    unit: Optional[str] = None
    
    # Source metadata
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    external_timestamp: Optional[datetime] = None
    
    # Processing metadata
    confidence: float = 0.8
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConnectorHealth(BaseModel):
    """Health metrics for a connector."""
    connector_name: str
    status: ConnectorStatus
    
    # Uptime metrics
    uptime_seconds: float = 0.0
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    
    # Performance metrics
    avg_latency_ms: float = 0.0
    last_latency_ms: float = 0.0
    
    # Data quality
    signals_produced: int = 0
    signals_failed: int = 0
    last_signal_count: int = 0
    
    # Error tracking
    last_error: Optional[str] = None
    consecutive_failures: int = 0
    
    # Timestamps
    last_check: datetime = Field(default_factory=datetime.utcnow)
    last_success: Optional[datetime] = None


class ConnectorEvent(BaseModel):
    """Event log entry for connector activity."""
    connector_name: str
    event_type: str  # sync_start, sync_complete, sync_error, etc.
    status: str  # success, failure, warning
    message: Optional[str] = None
    
    # Metrics
    signals_count: int = 0
    duration_ms: float = 0.0
    
    # Error details
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConnectorConfig(BaseModel):
    """Configuration for a connector."""
    name: str
    connector_type: ConnectorType
    enabled: bool = True
    
    # Scheduling
    interval_seconds: int = 300
    retry_count: int = 3
    retry_delay_seconds: int = 60
    
    # Filtering
    signal_types: List[str] = Field(default_factory=list)
    exclude_tags: List[str] = Field(default_factory=list)
    
    # Processing
    batch_size: int = 50
    timeout_seconds: int = 30
    
    # Validation
    validate_signals: bool = True
    min_confidence: float = 0.5


# Safety constants
LIVE_EXECUTION_ENABLED = False
CONNECTOR_WRITE_MODE = "read_only"
