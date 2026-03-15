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


    is_estimated: Mapped[bool] = mapped_column(Boolean, default=False)
