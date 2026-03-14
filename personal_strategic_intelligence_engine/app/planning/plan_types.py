"""Planning data models."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy import DateTime, String, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class PlanType(str, Enum):
    """Strategic plan types."""
    FINANCIAL = "financial"
    HEALTH = "health"
    PRODUCTIVITY = "productivity"
    CROSS_DOMAIN = "cross_domain"
    QUARTERLY = "quarterly"


class TimeHorizon(str, Enum):
    """Plan time horizons."""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class PlanStatus(str, Enum):
    """Plan status."""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ActionStatus(str, Enum):
    """Plan action status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


# Domain relationships mapping
DOMAIN_RELATIONSHIPS = {
    "financial_health": {
        "source": "financial",
        "target": "health",
        "weight": 0.7,
        "description": "Financial stability enables health investments",
    },
    "health_productivity": {
        "source": "health",
        "target": "productivity",
        "weight": 0.8,
        "description": "Good health improves productivity",
    },
    "productivity_financial": {
        "source": "productivity",
        "target": "financial",
        "weight": 0.6,
        "description": "Productivity leads to financial gains",
    },
}


