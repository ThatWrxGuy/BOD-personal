"""Learning and Memory database models."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class DecisionMemory(Base, TimestampMixin):
    """Persistent memory for strategic decisions."""

    __tablename__ = "decision_memory"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    decision_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    debate_session_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    execution_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    decision_type: Mapped[str] = mapped_column(String(50), nullable=False)
    decision_summary: Mapped[str] = mapped_column(Text, nullable=False)
    rationale_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Scores
    consensus_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    approval_result: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Execution
    execution_result: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Outcomes
    predicted_outcome: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    actual_outcome: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    outcome_delta: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    outcome_category: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Learning
    lessons_learned: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    outcome_evaluated: Mapped[bool] = mapped_column(default=False)
    evaluation_window: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)


class AgentScorecard(Base, TimestampMixin):
    """Agent performance scorecard."""

    __tablename__ = "agent_scorecards"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    agent_id: Mapped[str] = mapped_column(String(50), nullable=False)
    agent_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Overall scores
    total_decisions: Mapped[int] = mapped_column(Integer, default=0)
    accurate_predictions: Mapped[int] = mapped_column(Integer, default=0)
    accuracy_score: Mapped[float] = mapped_column(Float, default=0.5)
    
    # Domain-specific
    domain_scores: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Confidence tracking
    avg_confidence: Mapped[float] = mapped_column(Float, default=0.5)
    confidence_accuracy: Mapped[float] = mapped_column(Float, default=0.5)
    
    # Weight
    current_weight: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Last update
    last_decision_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class StrategicLesson(Base, TimestampMixin):
    """Extracted strategic lessons."""

    __tablename__ = "strategic_lessons"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    lesson_type: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    domain: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    risk_level: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Context
    related_decisions: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    conditions: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Quality
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    is_provisional: Mapped[bool] = mapped_column(default=False)
    times_referenced: Mapped[int] = mapped_column(Integer, default=0)


class StrategicPattern(Base, TimestampMixin):
    """Recurring strategic patterns."""

    __tablename__ = "strategic_patterns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    pattern_type: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    domain: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    conditions: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    historical_frequency: Mapped[int] = mapped_column(Integer, default=1)
    average_outcome_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    last_observed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


# Learning constants
class OutcomeCategory:
    """Outcome categories."""
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    NEUTRAL = "NEUTRAL"
    UNDERPERFORMED = "UNDERPERFORMED"
    FAILED = "FAILED"


class LessonType:
    """Lesson types."""
    SUCCESS_PATTERN = "SUCCESS_PATTERN"
    FAILURE_PATTERN = "FAILURE_PATTERN"
    RISK_PATTERN = "RISK_PATTERN"
    PROCESS_PATTERN = "PROCESS_PATTERN"
    STRATEGIC_PATTERN = "STRATEGIC_PATTERN"


class PatternType:
    """Pattern types."""
    RECURRING = "RECURRING"
    EMERGING = "EMERGING"
    DECLINING = "DECLINING"


class EvaluationWindow:
    """Evaluation windows."""
    IMMEDIATE = "IMMEDIATE"
    SHORT_TERM = "SHORT_TERM"
    MEDIUM_TERM = "MEDIUM_TERM"
    LONG_TERM = "LONG_TERM"
