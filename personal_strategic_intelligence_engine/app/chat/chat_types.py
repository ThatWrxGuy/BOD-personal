"""Chat and conversation data models."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, String, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class IntentType(str, Enum):
    """Chat intent types."""
    QUERY_RISKS = "query_risks"
    QUERY_OPPORTUNITIES = "query_opportunities"
    RUN_SIMULATION = "run_simulation"
    START_RESEARCH = "start_research"
    GENERATE_PLAN = "generate_plan"
    RUN_REVIEW = "run_review"
    CHECK_FINANCES = "check_finances"
    QUERY_GOALS = "query_goals"
    SYSTEM_STATUS = "system_status"
    QUERY_INSIGHTS = "query_insights"
    LIST_BILLS = "list_bills"
    CHECK_LIQUIDITY = "check_liquidity"
    GENERAL_QUERY = "general_query"
    UNKNOWN = "unknown"


class ChatSessionStatus(str, Enum):
    """Chat session status."""
    ACTIVE = "active"
    COMPLETED = "completed"
    TIMEOUT = "timeout"


class ChatMessageStatus(str, Enum):
    """Chat message status."""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


