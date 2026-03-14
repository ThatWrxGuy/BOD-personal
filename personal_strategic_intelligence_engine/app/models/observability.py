"""Observability data models."""
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import DateTime, Float, Integer, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class SystemMetricSnapshot(Base, TimestampMixin):
    """System metric snapshot."""

    __tablename__ = "system_metric_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    metric_type: Mapped[str] = mapped_column(String(20), nullable=False)  # counter, gauge, histogram
    domain: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # system, workflow, execution, etc.
    
    # Metadata
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    event_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    __table_args__ = (
        Index("idx_metric_domain_time", "domain", "timestamp"),
    )


class HealthStatusRecord(Base, TimestampMixin):
    """Health status record."""

    __tablename__ = "health_status_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    component: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # healthy, degraded, unavailable, misconfigured
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class AlertEvent(Base, TimestampMixin):
    """Alert event."""

    __tablename__ = "alert_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # info, warning, error, critical
    message: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Context
    workflow_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    correlation_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    # Status
    is_resolved: Mapped[bool] = mapped_column(default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    event_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)


# Health component constants
class HealthComponent:
    """Health check components."""
    APPLICATION = "application"
    DATABASE = "database"
    EVENT_BUS = "event_bus"
    WORKFLOW_ENGINE = "workflow_engine"
    CONNECTORS = "connectors"
    LLM_PROVIDERS = "llm_providers"
    SECURITY = "security"


class HealthStatus:
    """Health statuses."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    MISCONFIGURED = "misconfigured"


# Metric domains
class MetricDomain:
    """Metric domains."""
    SYSTEM = "system"
    WORKFLOW = "workflow"
    EXECUTION = "execution"
    CONNECTOR = "connector"
    SECURITY = "security"
    AGENT = "agent"
    API = "api"


# Metric names
class MetricName:
    """Common metric names."""
    # Workflow
    WORKFLOWS_STARTED = "workflows_started"
    WORKFLOWS_COMPLETED = "workflows_completed"
    WORKFLOWS_FAILED = "workflows_failed"
    WORKFLOW_DURATION_MS = "workflow_duration_ms"
    
    # Execution
    EXECUTIONS_REQUESTED = "executions_requested"
    EXECUTIONS_APPROVED = "executions_approved"
    EXECUTIONS_REJECTED = "executions_rejected"
    EXECUTIONS_COMPLETED = "executions_completed"
    EXECUTIONS_FAILED = "executions_failed"
    EXECUTION_DURATION_MS = "execution_duration_ms"
    
    # Connectors
    CONNECTOR_VALIDATIONS = "connector_validations"
    CONNECTOR_ENABLED = "connector_enabled"
    CONNECTOR_DISABLED = "connector_disabled"
    CONNECTOR_ACCESS_GRANTED = "connector_access_granted"
    CONNECTOR_ACCESS_DENIED = "connector_access_denied"
    CONNECTOR_ERRORS = "connector_errors"
    
    # Security
    LOGIN_ATTEMPTS = "login_attempts"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    FORBIDDEN_ACCESS = "forbidden_access"
    
    # API
    API_REQUESTS = "api_requests"
    API_LATENCY_MS = "api_latency_ms"
    API_ERRORS = "api_errors"
