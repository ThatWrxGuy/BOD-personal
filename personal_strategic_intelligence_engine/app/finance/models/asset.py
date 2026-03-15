"""Asset model - represents any owned financial or physical asset."""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class AssetCategory(str, Enum):
    """Allowed asset categories."""
    CASH = "cash"
    CHECKING = "checking"
    SAVINGS = "savings"
    INVESTMENT = "investment"
    RETIREMENT = "retirement"
    CRYPTO = "crypto"
    PROPERTY = "property"
    VEHICLE = "vehicle"
    BUSINESS_EQUITY = "business_equity"
    TOOLS_EQUIPMENT = "tools_equipment"


class Asset(Base, TimestampMixin):
    """Represents any owned financial or physical asset."""

    __tablename__ = "assets"

    asset_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("financial_profiles.profile_id"), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    current_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    liquidity_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)  # 0-1 scale
    volatility_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # 0-1 scale

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "asset_id": self.asset_id,
            "profile_id": self.profile_id,
            "category": self.category,
            "name": self.name,
            "current_value": self.current_value,
            "liquidity_score": self.liquidity_score,
            "volatility_score": self.volatility_score,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def is_liquid(self) -> bool:
        """Check if asset is highly liquid."""
        return self.liquidity_score >= 0.8

    def is_cash_equivalent(self) -> bool:
        """Check if asset is cash or cash equivalent."""
        return self.category in (
            AssetCategory.CASH.value,
            AssetCategory.CHECKING.value,
            AssetCategory.SAVINGS.value,
        )
