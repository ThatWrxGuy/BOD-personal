"""Financial operations data types and models."""
import uuid
from datetime import datetime, date
from enum import Enum
from typing import Optional, List

from sqlalchemy import DateTime, String, Float, ForeignKey, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class BillCategory(str, Enum):
    """Bill categories."""
    HOUSING = "housing"
    UTILITIES = "utilities"
    INSURANCE = "insurance"
    DEBT = "debt"
    SUBSCRIPTION = "subscription"
    TRANSPORTATION = "transportation"
    TAXES = "taxes"
    MEMBERSHIP = "membership"
    OTHER = "other"


class RecurrenceType(str, Enum):
    """Bill recurrence types."""
    ONE_TIME = "one_time"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class BillStatus(str, Enum):
    """Bill status."""
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class ExpenseCategory(str, Enum):
    """Expense categories."""
    HOUSING = "housing"
    TRANSPORTATION = "transportation"
    FOOD = "food"
    UTILITIES = "utilities"
    INSURANCE = "insurance"
    DEBT = "debt"
    SUBSCRIPTIONS = "subscriptions"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    SHOPPING = "shopping"
    OTHER = "other"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Bill(Base, TimestampMixin):
    """Bill record."""

    __tablename__ = "finance_ops_bills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Amount
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    # Timing
    due_date: Mapped[date] = mapped_column(nullable=False)
    recurrence: Mapped[str] = mapped_column(String(20), default=RecurrenceType.ONE_TIME)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default=BillStatus.PENDING)
    autopay_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Priority
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high
    
    # Details
    source_account: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timestamps
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index("idx_bill_due_date", "due_date"),
        Index("idx_bill_status", "status"),
    )


class ExpenseRecord(Base, TimestampMixin):
    """Expense record."""

    __tablename__ = "finance_ops_expenses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    # Details
    merchant: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timing
    transaction_date: Mapped[date] = mapped_column(nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Bill link
    bill_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("finance_ops_bills.id"),
        nullable=True,
    )


class SubscriptionRecord(Base, TimestampMixin):
    """Subscription record."""

    __tablename__ = "finance_ops_subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="subscriptions")
    
    # Amount
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    billing_cycle: Mapped[str] = mapped_column(String(20), default="monthly")  # weekly, monthly, yearly
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_essential: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Usage
    usage_frequency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # daily, weekly, rarely
    last_used: Mapped[Optional[date]] = mapped_column(nullable=True)
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)


class CashFlowForecast(Base, TimestampMixin):
    """Cash flow forecast."""

    __tablename__ = "finance_ops_cashflow_forecasts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    forecast_date: Mapped[date] = mapped_column(nullable=False)
    projected_balance: Mapped[float] = mapped_column(Float, nullable=False)
    
    time_horizon_days: Mapped[int] = mapped_column(default=30)
    
    # Breakdown
    projected_income: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    projected_expenses: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Details
    forecast_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)


class LiquidityAlert(Base, TimestampMixin):
    """Liquidity alert."""

    __tablename__ = "finance_ops_liquidity_alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default=AlertSeverity.MEDIUM)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Context
    projected_date: Mapped[Optional[date]] = mapped_column(nullable=True)
    projected_balance: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Status
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class AccountBalance(Base, TimestampMixin):
    """Account balance record."""

    __tablename__ = "finance_ops_account_balances"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    account_name: Mapped[str] = mapped_column(String(200), nullable=False)
    account_type: Mapped[str] = mapped_column(String(50), nullable=False)  # checking, savings, credit, investment
    
    balance: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    as_of_date: Mapped[date] = mapped_column(nullable=False)
    is_estimated: Mapped[bool] = mapped_column(Boolean, default=False)
