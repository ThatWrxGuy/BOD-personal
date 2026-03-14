"""FinancialSnapshot model - immutable state snapshot for audit trails."""
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FinancialSnapshot(Base):
    """Immutable state snapshot used for audit trails."""

    __tablename__ = "financial_snapshots"

    snapshot_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("financial_profiles.profile_id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Core totals
    total_assets: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_liabilities: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    net_worth: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    # Cash flow
    monthly_income: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    monthly_expenses: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    free_cash_flow: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    # Liquidity
    available_liquidity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    # Debt breakdown
    revolving_debt_balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    secured_debt_balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    # Health score
    financial_health_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    # Version tracking
    assumptions_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Raw state payload for full audit
    raw_state_payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "snapshot_id": self.snapshot_id,
            "profile_id": self.profile_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "total_assets": self.total_assets,
            "total_liabilities": self.total_liabilities,
            "net_worth": self.net_worth,
            "monthly_income": self.monthly_income,
            "monthly_expenses": self.monthly_expenses,
            "free_cash_flow": self.free_cash_flow,
            "available_liquidity": self.available_liquidity,
            "revolving_debt_balance": self.revolving_debt_balance,
            "secured_debt_balance": self.secured_debt_balance,
            "financial_health_score": self.financial_health_score,
            "assumptions_version": self.assumptions_version,
            "raw_state_payload": self.raw_state_payload,
        }

    @classmethod
    def create_from_state(
        cls,
        profile_id: int,
        state: dict[str, Any],
        assumptions_version: Optional[str] = None,
    ) -> "FinancialSnapshot":
        """Create a snapshot from a financial state dictionary."""
        return cls(
            profile_id=profile_id,
            timestamp=datetime.utcnow(),
            total_assets=state.get("total_assets", 0.0),
            total_liabilities=state.get("total_liabilities", 0.0),
            net_worth=state.get("net_worth", 0.0),
            monthly_income=state.get("monthly_income", 0.0),
            monthly_expenses=state.get("monthly_expenses", 0.0),
            free_cash_flow=state.get("free_cash_flow", 0.0),
            available_liquidity=state.get("available_liquidity", 0.0),
            revolving_debt_balance=state.get("revolving_debt_balance", 0.0),
            secured_debt_balance=state.get("secured_debt_balance", 0.0),
            financial_health_score=state.get("financial_health_score", 0.0),
            assumptions_version=assumptions_version,
            raw_state_payload=str(state),
        )
