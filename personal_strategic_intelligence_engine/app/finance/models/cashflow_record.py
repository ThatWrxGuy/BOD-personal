"""CashFlowRecord model - manual-input friendly monthly cash flow."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class CashFlowRecord(Base, TimestampMixin):
    """Manual-input friendly monthly cash flow record."""

    __tablename__ = "cash_flow_records"

    record_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("financial_profiles.profile_id"), nullable=False)
    month: Mapped[str] = mapped_column(String(7), nullable=False)  # Format: YYYY-MM
    gross_income: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    net_income: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    fixed_expenses: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    variable_expenses: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    debt_payments: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    savings_contributions: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    investment_contributions: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "record_id": self.record_id,
            "profile_id": self.profile_id,
            "month": self.month,
            "gross_income": self.gross_income,
            "net_income": self.net_income,
            "fixed_expenses": self.fixed_expenses,
            "variable_expenses": self.variable_expenses,
            "debt_payments": self.debt_payments,
            "savings_contributions": self.savings_contributions,
            "investment_contributions": self.investment_contributions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def total_expenses(self) -> float:
        """Calculate total expenses."""
        return self.fixed_expenses + self.variable_expenses + self.debt_payments

    def total_outflow(self) -> float:
        """Calculate total outflow (expenses + savings + investments)."""
        return self.total_expenses() + self.savings_contributions + self.investment_contributions

    def cash_flow(self) -> float:
        """Calculate net cash flow (income - outflow)."""
        return self.net_income - self.total_outflow()
