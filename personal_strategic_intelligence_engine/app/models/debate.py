"""Debate Session database models."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class DebateSession(Base, TimestampMixin):
    """Debate session for multi-agent strategic deliberation."""

    __tablename__ = "debate_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    decision_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timing
    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Progress
    rounds_completed: Mapped[int] = mapped_column(Integer, default=0)
    max_rounds: Mapped[int] = mapped_column(Integer, default=4)
    
    # Results
    consensus_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    final_recommendation: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="INITIALIZED",
    )  # INITIALIZED, IN_PROGRESS, COMPLETED, FAILED
    
    # Metadata
    topic: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    participants: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)


class DebateArgument(Base, TimestampMixin):
    """Arguments presented by agents in a debate."""

    __tablename__ = "debate_arguments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    debate_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    agent_id: Mapped[str] = mapped_column(String(50), nullable=False)
    agent_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Argument content
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    position: Mapped[str] = mapped_column(String(50), nullable=False)  # SUPPORT, OPPOSE, NEUTRAL
    argument_text: Mapped[str] = mapped_column(Text, nullable=False)
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Supporting data
    supporting_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    risk_assessment: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5)
    
    # References
    parent_argument_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )  # For counter-arguments


class DebateVote(Base, TimestampMixin):
    """Votes cast by agents in a debate."""

    __tablename__ = "debate_votes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    debate_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    agent_id: Mapped[str] = mapped_column(String(50), nullable=False)
    agent_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Vote content
    vote: Mapped[str] = mapped_column(String(20), nullable=False)  # APPROVE, REJECT, ABSTAIN
    justification: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    weight: Mapped[float] = mapped_column(Float, default=1.0)  # Weighted vote based on expertise
    
    # Round
    round_number: Mapped[int] = mapped_column(Integer, default=4)


class DebateHistory(Base, TimestampMixin):
    """Historical record of debate activities."""

    __tablename__ = "debate_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    debate_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    agent_id: Mapped[str] = mapped_column(String(50), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


# Debate constants
class DebateStatus:
    """Debate session status constants."""
    INITIALIZED = "INITIALIZED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class VoteType:
    """Vote type constants."""
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    ABSTAIN = "ABSTAIN"


class Position:
    """Argument position constants."""
    SUPPORT = "SUPPORT"
    OPPOSE = "OPPOSE"
    NEUTRAL = "NEUTRAL"


class AgentWeights:
    """Default agent weights for voting."""
    STRATEGY = 1.2
    FINANCE = 1.2
    RISK = 1.3
    HEALTH = 1.0
    OPERATIONS = 1.0
    LEGACY = 1.0
