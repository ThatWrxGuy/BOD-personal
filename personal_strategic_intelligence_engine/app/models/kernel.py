"""Kernel data models for PSIE V2 Strategic Kernel."""
import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class SystemStateSnapshot(Base, TimestampMixin):
    """Snapshot of system state at a point in time."""

    __tablename__ = "system_state_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Financial state
    total_assets: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_liabilities: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    net_worth: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cash_reserves: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    monthly_income: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    monthly_expenses: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Risk state
    risk_tolerance: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    current_risk_exposure: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    volatility_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Market state
    market_regime: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    market_sentiment: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Goal progress (JSON)
    goal_progress: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # System health
    system_health_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    active_agents: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    
    # Raw state data
    raw_state: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)


class StrategicPriority(Base, TimestampMixin):
    """Strategic priority definition."""

    __tablename__ = "strategic_priorities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    priority_name: Mapped[str] = mapped_column(String(100), nullable=False)
    priority_type: Mapped[str] = mapped_column(String(50), nullable=False)
    priority_weight: Mapped[float] = mapped_column(Float, default=0.5)
    
    # Activation conditions
    activation_conditions: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    deactivation_conditions: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    priority_order: Mapped[int] = mapped_column(Integer, default=0)


class PolicyRule(Base, TimestampMixin):
    """Policy rule for governance."""

    __tablename__ = "policy_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    policy_name: Mapped[str] = mapped_column(String(100), nullable=False)
    policy_category: Mapped[str] = mapped_column(String(50), nullable=False)
    policy_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Rule definition
    rule_expression: Mapped[str] = mapped_column(Text, nullable=False)
    threshold_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Enforcement
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    enforcement_action: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)


class DecisionUtilityScore(Base, TimestampMixin):
    """Utility score for a candidate decision."""

    __tablename__ = "decision_utility_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    decision_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    decision_type: Mapped[str] = mapped_column(String(50), nullable=False)
    decision_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Score components
    expected_value: Mapped[float] = mapped_column(Float, default=0.0)
    risk_penalty: Mapped[float] = mapped_column(Float, default=0.0)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5)
    alignment_score: Mapped[float] = mapped_column(Float, default=0.5)
    reversibility_score: Mapped[float] = mapped_column(Float, default=0.5)
    resource_cost: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Final utility score
    utility_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Context
    market_regime: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    active_priorities: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    # Decision
    recommended_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class StrategicDoctrine(Base, TimestampMixin):
    """Strategic doctrine learned from outcomes."""

    __tablename__ = "strategic_doctrine"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    doctrine_name: Mapped[str] = mapped_column(String(255), nullable=False)
    rule_description: Mapped[str] = mapped_column(Text, nullable=False)
    doctrine_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Source
    source_pattern: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    
    # Applicability
    applicable_regimes: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    applicable_conditions: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Usage
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    success_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_provisional: Mapped[bool] = mapped_column(Boolean, default=False)


class KernelCycleLog(Base, TimestampMixin):
    """Log of kernel control loop cycles."""

    __tablename__ = "kernel_cycle_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    cycle_number: Mapped[int] = mapped_column(Integer, nullable=False)
    cycle_mode: Mapped[str] = mapped_column(String(20), nullable=False)  # OBSERVATION, ADVISORY, AUTONOMOUS
    
    # What happened in this cycle
    signals_collected: Mapped[int] = mapped_column(Integer, default=0)
    state_updates: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    priorities_updated: Mapped[bool] = mapped_column(Boolean, default=False)
    decisions_evaluated: Mapped[int] = mapped_column(Integer, default=0)
    actions_recommended: Mapped[int] = mapped_column(Integer, default=0)
    actions_executed: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timing
    cycle_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cycle_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cycle_duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


# Kernel operation modes
class KernelMode:
    """Kernel operation modes."""
    OBSERVATION = "OBSERVATION"
    ADVISORY = "ADVISORY"
    AUTONOMOUS = "AUTONOMOUS"


class PriorityType:
    """Priority types."""
    PRESERVATION = "preservation"  # Preserve liquidity, capital
    GROWTH = "growth"  # Increase wealth, opportunity
    EFFICIENCY = "efficiency"  # Optimize operations
    PROTECTION = "protection"  # Protect health, stability


class PolicyCategory:
    """Policy categories."""
    RISK = "risk"
    EXECUTION = "execution"
    SAFETY = "safety"
    STRATEGIC = "strategic"
