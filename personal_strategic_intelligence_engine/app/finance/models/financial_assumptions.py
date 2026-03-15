"""FinancialAssumptions model - stores configurable financial modeling assumptions."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class FinancialAssumptions(Base, TimestampMixin):
    """Stores configurable financial modeling assumptions."""

    __tablename__ = "financial_assumptions"

    assumptions_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("financial_profiles.profile_id"), nullable=False)
    expected_market_return: Mapped[float] = mapped_column(Float, nullable=False, default=0.07)  # 7% annual
    inflation_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.025)  # 2.5% annual
    income_growth_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.03)  # 3% annual
    emergency_fund_target_months: Mapped[int] = mapped_column(Integer, nullable=False, default=6)
    tax_drag_estimate: Mapped[float] = mapped_column(Float, nullable=False, default=0.15)  # 15% tax drag
    crypto_volatility_factor: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)  # 0-1 scale
    recession_probability: Mapped[float] = mapped_column(Float, nullable=False, default=0.2)  # 20% probability

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "assumptions_id": self.assumptions_id,
            "profile_id": self.profile_id,
            "expected_market_return": self.expected_market_return,
            "inflation_rate": self.inflation_rate,
            "income_growth_rate": self.income_growth_rate,
            "emergency_fund_target_months": self.emergency_fund_target_months,
            "tax_drag_estimate": self.tax_drag_estimate,
            "crypto_volatility_factor": self.crypto_volatility_factor,
            "recession_probability": self.recession_probability,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def real_return(self) -> float:
        """Calculate real return after inflation."""
        return (1 + self.expected_market_return) / (1 + self.inflation_rate) - 1

    def adjusted_return(self) -> float:
        """Calculate return after tax drag."""
        return self.expected_market_return * (1 - self.tax_drag_estimate)
