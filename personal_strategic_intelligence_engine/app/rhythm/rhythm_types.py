"""Operating rhythm data models."""
import uuid
from datetime import datetime, date, time
from enum import Enum
from typing import Optional, List

from sqlalchemy import DateTime, String, Float, ForeignKey, Index, Time, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class CycleType(str, Enum):
    """Operating cycle types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class HabitCategory(str, Enum):
    """Habit categories."""
    HEALTH = "health"
    PRODUCTIVITY = "productivity"
    LEARNING = "learning"
    FINANCIAL = "financial"
    SOCIAL = "social"


class FocusBlockType(str, Enum):
    """Focus block types."""
    DEEP_WORK = "deep_work"
    STRATEGIC = "strategic"
    RESEARCH = "research"
    OPERATIONAL = "operational"
    CREATIVE = "creative"


