"""Risk Projection database model."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class RiskProjection(Base, TimestampMixin):
    """Risk projection model."""

    __tablename__ = "risk_projections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    risk_category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # FINANCIAL, HEALTH, OPERATIONS, MACRO
    risk_probability: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    impact_estimate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    time_horizon: Mapped[str] = mapped_column(String(50), nullable=False)
    risk_description: Mapped[str] = mapped_column(Text, nullable=False)
    indicators: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    mitigation_suggestions: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)


class RiskCategory:
    """Risk category constants."""

    FINANCIAL = "FINANCIAL"
    HEALTH = "HEALTH"
    OPERATIONS = "OPERATIONS"
    MACRO = "MACRO"

    ALL = [FINANCIAL, HEALTH, OPERATIONS, MACRO]
