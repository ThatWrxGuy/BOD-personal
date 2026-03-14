"""Research data models and types."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any

from sqlalchemy import DateTime, String, Text, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ResearchStatus(str, Enum):
    """Research task status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResearchPriority(str, Enum):
    """Research priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResearchScope(str, Enum):
    """Research scope."""
    QUICK = "quick"  # 5-10 minutes
    STANDARD = "standard"  # 15-30 minutes
    DEEP = "deep"  # 1+ hour


