"""Financial Profile - represents the user's baseline financial identity."""
from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Date, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class RiskTolerance(str, Enum):
    """Risk tolerance levels."""
    CONSERVATIVE = "conservative"
    MODERATE_CONSERVATIVE = "moderate_conservative"
    MODERATE = "moderate"
    MODERATE_AGGRESSIVE = "moderate_aggressive"
    AGGRESSIVE = "aggressive"


class LiquidityPreference(str, Enum):
    """Liquidity preference levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class IncomeStability(str, Enum):
    """Income stability scores."""
    VERY_STABLE = "very_stable"
    STABLE = "stable"
    MODERATE = "moderate"
    VARIABLE = "variable"
    UNSTABLE = "unstable"


class FinancialProfile(Base, TimestampMixin):
    """User's baseline financial identity."""

    __tablename__ = "financial_profiles"

    profile_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Link to user if available
    monthly_income: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    monthly_fixed_expenses: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    monthly_variable_expenses: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    risk_tolerance: Mapped[str] = mapped_column(String(50), nullable=False, default=RiskTolerance.MODERATE.value)
    liquidity_preference: Mapped[str] = mapped_column(String(50), nullable=False, default=LiquidityPreference.MEDIUM.value)
    investment_horizon_years: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    income_stability_score: Mapped[str] = mapped_column(String(50), nullable=False, default=IncomeStability.STABLE.value)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "profile_id": self.profile_id,
            "user_id": self.user_id,
            "monthly_income": self.monthly_income,
            "monthly_fixed_expenses": self.monthly_fixed_expenses,
            "monthly_variable_expenses": self.monthly_variable_expenses,
            "risk_tolerance": self.risk_tolerance,
            "liquidity_preference": self.liquidity_preference,
            "investment_horizon_years": self.investment_horizon_years,
            "income_stability_score": self.income_stability_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
