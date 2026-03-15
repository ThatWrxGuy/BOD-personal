"""Simulation data models."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Float, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class SimulationRun(Base, TimestampMixin):
    """Simulation run record."""

    __tablename__ = "simulation_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    decision_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    decision_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    decision_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    time_horizon_days: Mapped[int] = mapped_column(default=30)
    domain: Mapped[str] = mapped_column(String(50), default="financial")
    
    status: Mapped[str] = mapped_column(String(20), default="pending")
    
    scenarios_generated: Mapped[int] = mapped_column(default=0)
    current_step: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    recommended_scenario: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    overall_risk_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    error_message: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)


class SimulationScenario(Base, TimestampMixin):
    """Simulation scenario."""

    __tablename__ = "simulation_scenarios"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    simulation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("simulation_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    scenario_name: Mapped[str] = mapped_column(String(100), nullable=False)
    scenario_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    parameters: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    expected_outcome: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    projected_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    risk_factors: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)


class SimulationResult(Base, TimestampMixin):
    """Simulation result."""

    __tablename__ = "simulation_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    simulation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("simulation_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("simulation_scenarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    outcome_type: Mapped[str] = mapped_column(String(50), nullable=False)
    expected_value: Mapped[float] = mapped_column(Float, nullable=False)
    
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5)
    
    risk_level: Mapped[str] = mapped_column(String(20), default="medium")
    risk_factors: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)


class SimulationEvent(Base, TimestampMixin):
    """Simulation event model."""

    __tablename__ = "simulation_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    simulation_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    event_day: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # SIGNAL, TRIGGER, MEETING, DECISION, FORECAST, GOAL_UPDATE, ALERT, FAILURE
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    component: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="info")


class AuditReport(Base, TimestampMixin):
    """Audit report for simulations."""

    __tablename__ = "audit_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    simulation_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    audit_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    findings: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    recommendations: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="info")
