"""Scenario Simulation database model."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Float, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ScenarioSimulation(Base, TimestampMixin):
    """Scenario simulation model."""

    __tablename__ = "scenario_simulations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    scenario_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parameters: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    predicted_outcomes: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    baseline_comparison: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
