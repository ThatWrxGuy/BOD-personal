"""Liability model - represents any debt obligation."""
from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class LiabilityCategory(str, Enum):
    """Allowed liability categories."""
    MORTGAGE = "mortgage"
    AUTO_LOAN = "auto_loan"
    CREDIT_CARD = "credit_card"
    PERSONAL_LOAN = "personal_loan"
    TAX_DEBT = "tax_debt"


class Liability(Base, TimestampMixin):
    """Represents any debt obligation."""

    __tablename__ = "liabilities"

    liability_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("financial_profiles.profile_id"), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    minimum_payment: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    interest_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # Annual percentage
    term_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    secured_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "liability_id": self.liability_id,
            "profile_id": self.profile_id,
            "category": self.category,
            "name": self.name,
            "balance": self.balance,
            "minimum_payment": self.minimum_payment,
            "interest_rate": self.interest_rate,
            "term_end_date": self.term_end_date.isoformat() if self.term_end_date else None,
            "secured_flag": self.secured_flag,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def is_secured(self) -> bool:
        """Check if liability is secured."""
        return self.secured_flag

    def is_revolving(self) -> bool:
        """Check if liability is revolving (e.g., credit card)."""
        return self.category == LiabilityCategory.CREDIT_CARD.value

    def monthly_interest(self) -> float:
        """Calculate monthly interest amount."""
        return (self.balance * self.interest_rate / 100) / 12
