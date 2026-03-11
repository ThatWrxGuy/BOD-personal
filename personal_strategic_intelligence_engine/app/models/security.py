"""Security and connector configuration models."""
import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Boolean, DateTime, Float, String, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ConnectorAuditLog(Base, TimestampMixin):
    """Audit log for connector actions."""

    __tablename__ = "connector_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    connector_id: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # enabled, disabled, test, access_granted, access_denied
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # success, failure, blocked
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Workflow context
    workflow_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    correlation_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    # Metadata
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class ConnectorConfiguration(Base, TimestampMixin):
    """Configuration state for connectors."""

    __tablename__ = "connector_configurations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    connector_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    connector_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # State
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Risk
    risk_level: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high, critical
    
    # Domain
    domain: Mapped[str] = mapped_column(String(50), nullable=False)  # llm, data, email, calendar, task, financial
    
    # Timestamps
    last_validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_health_check_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Validation errors
    validation_errors: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    # Metadata
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)


# Connector definitions
class ConnectorDomain:
    """Connector domains."""
    LLM = "llm"
    DATA = "data"
    EMAIL = "email"
    CALENDAR = "calendar"
    TASK = "task"
    FINANCIAL = "financial"


class ConnectorRiskLevel:
    """Connector risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConnectorID:
    """Predefined connector IDs."""
    # LLM
    OPENAI_LLM = "openai_llm"
    ANTHROPIC_LLM = "anthropic_llm"
    
    # Data
    ALPHAVANTAGE_DATA = "alphavantage_data"
    POLYGON_DATA = "polygon_data"
    FRED_DATA = "fred_data"
    
    # Email
    GMAIL_EMAIL = "gmail_email"
    
    # Calendar
    GOOGLE_CALENDAR = "google_calendar"
    
    # Tasks
    TODOIST_TASKS = "todoist_tasks"
    NOTION_TASKS = "notion_tasks"
    
    # Financial
    SCHWAB_FINANCIAL = "schwab_financial"
    INTERACTIVE_BROKERS_FINANCIAL = "ib_financial"
    COINBASE_FINANCIAL = "coinbase_financial"


# Connector registry data
CONNECTOR_REGISTRY = {
    # LLM Connectors
    ConnectorID.OPENAI_LLM: {
        "name": "OpenAI LLM",
        "domain": ConnectorDomain.LLM,
        "risk_level": ConnectorRiskLevel.MEDIUM,
        "required_secrets": ["OPENAI_API_KEY"],
        "required_permissions": [],
        "description": "OpenAI GPT models for AI reasoning",
    },
    ConnectorID.ANTHROPIC_LLM: {
        "name": "Anthropic LLM",
        "domain": ConnectorDomain.LLM,
        "risk_level": ConnectorRiskLevel.MEDIUM,
        "required_secrets": ["ANTHROPIC_API_KEY"],
        "required_permissions": [],
        "description": "Anthropic Claude models for AI reasoning",
    },
    
    # Data Connectors
    ConnectorID.ALPHAVANTAGE_DATA: {
        "name": "Alpha Vantage",
        "domain": ConnectorDomain.DATA,
        "risk_level": ConnectorRiskLevel.LOW,
        "required_secrets": ["ALPHAVANTAGE_API_KEY"],
        "required_permissions": ["view_signals"],
        "description": "Market data provider",
    },
    ConnectorID.POLYGON_DATA: {
        "name": "Polygon",
        "domain": ConnectorDomain.DATA,
        "risk_level": ConnectorRiskLevel.LOW,
        "required_secrets": ["POLYGON_API_KEY"],
        "required_permissions": ["view_signals"],
        "description": "Market data provider",
    },
    ConnectorID.FRED_DATA: {
        "name": "FRED",
        "domain": ConnectorDomain.DATA,
        "risk_level": ConnectorRiskLevel.LOW,
        "required_secrets": ["FRED_API_KEY"],
        "required_permissions": ["view_signals"],
        "description": "Federal Reserve Economic Data",
    },
    
    # Email Connectors
    ConnectorID.GMAIL_EMAIL: {
        "name": "Gmail",
        "domain": ConnectorDomain.EMAIL,
        "risk_level": ConnectorRiskLevel.HIGH,
        "required_secrets": ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"],
        "required_permissions": ["manage_connectors"],
        "description": "Gmail email integration",
    },
    
    # Calendar Connectors
    ConnectorID.GOOGLE_CALENDAR: {
        "name": "Google Calendar",
        "domain": ConnectorDomain.CALENDAR,
        "risk_level": ConnectorRiskLevel.HIGH,
        "required_secrets": ["GOOGLE_CALENDAR_CLIENT_ID", "GOOGLE_CALENDAR_CLIENT_SECRET"],
        "required_permissions": ["manage_connectors"],
        "description": "Google Calendar integration",
    },
    
    # Task Connectors
    ConnectorID.TODOIST_TASKS: {
        "name": "Todoist",
        "domain": ConnectorDomain.TASK,
        "risk_level": ConnectorRiskLevel.MEDIUM,
        "required_secrets": ["TODOIST_API_TOKEN"],
        "required_permissions": ["manage_connectors"],
        "description": "Todoist task management",
    },
    ConnectorID.NOTION_TASKS: {
        "name": "Notion",
        "domain": ConnectorDomain.TASK,
        "risk_level": ConnectorRiskLevel.MEDIUM,
        "required_secrets": ["NOTION_API_KEY"],
        "required_permissions": ["manage_connectors"],
        "description": "Notion workspace integration",
    },
    
    # Financial Connectors
    ConnectorID.SCHWAB_FINANCIAL: {
        "name": "Charles Schwab",
        "domain": ConnectorDomain.FINANCIAL,
        "risk_level": ConnectorRiskLevel.CRITICAL,
        "required_secrets": ["SCHWAB_CLIENT_ID", "SCHWAB_CLIENT_SECRET"],
        "required_permissions": ["manage_connectors", "execute_financial_action"],
        "description": "Schwab brokerage integration",
    },
    ConnectorID.INTERACTIVE_BROKERS_FINANCIAL: {
        "name": "Interactive Brokers",
        "domain": ConnectorDomain.FINANCIAL,
        "risk_level": ConnectorRiskLevel.CRITICAL,
        "required_secrets": ["INTERACTIVE_BROKERS_HOST", "INTERACTIVE_BROKERS_PORT"],
        "required_permissions": ["manage_connectors", "execute_financial_action"],
        "description": "Interactive Brokers integration",
    },
    ConnectorID.COINBASE_FINANCIAL: {
        "name": "Coinbase",
        "domain": ConnectorDomain.FINANCIAL,
        "risk_level": ConnectorRiskLevel.CRITICAL,
        "required_secrets": ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
        "required_permissions": ["manage_connectors", "execute_financial_action"],
        "description": "Cryptocurrency exchange integration",
    },
}
