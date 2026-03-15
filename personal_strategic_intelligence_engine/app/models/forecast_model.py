"""Forecast Model database model."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ForecastModel(Base, TimestampMixin):
    """Forecast model for predictive analytics."""

    __tablename__ = "forecast_models"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    forecast_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # FINANCIAL, HEALTH, GOAL_PROGRESS, WORKLOAD, RISK
    forecast_target: Mapped[str] = mapped_column(String(255), nullable=False)
    forecast_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    prediction_horizon: Mapped[str] = mapped_column(String(50), nullable=False)
    # e.g., "30_days", "90_days", "1_year"
    source_data_range: Mapped[str] = mapped_column(String(50), nullable=True)
    methodology: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # e.g., "linear_regression", "moving_average", "trend_extrapolation"


class ForecastType:
    """Forecast type constants."""

    FINANCIAL = "FINANCIAL"
    HEALTH = "HEALTH"
    GOAL_PROGRESS = "GOAL_PROGRESS"
    WORKLOAD = "WORKLOAD"
    RISK = "RISK"

    ALL = [FINANCIAL, HEALTH, GOAL_PROGRESS, WORKLOAD, RISK]
