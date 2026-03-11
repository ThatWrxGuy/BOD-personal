"""Simulation Run database model."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class SimulationRun(Base, TimestampMixin):
    """Simulation run model."""

    __tablename__ = "simulation_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    scenario_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # BASELINE, STRESS, RECOVERY, OPPORTUNITY, MIXED
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING",
    )  # PENDING, RUNNING, COMPLETED, FAILED
    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    simulated_days: Mapped[int] = mapped_column(Integer, nullable=False, default=14)
    seed_config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


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
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="MEDIUM",
    )  # LOW, MEDIUM, HIGH, CRITICAL
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)


class AuditReport(Base, TimestampMixin):
    """Audit report model."""

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
    executive_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    system_readiness_score: Mapped[float] = mapped_column(default=0.0)
    component_scores: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    strengths: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    weaknesses: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    failures: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    recommendations: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    report_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
