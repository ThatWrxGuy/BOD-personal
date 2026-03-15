"""Net Worth Calculator - computes total assets, liabilities, and net worth."""
from dataclasses import dataclass
from typing import List

from app.finance.models.asset import Asset
from app.finance.models.liability import Liability


@dataclass
class NetWorthResult:
    """Result of net worth calculation."""
    total_assets: float
    total_liabilities: float
    net_worth: float
    liquid_net_worth: float
    assets_by_category: dict[str, float]
    liabilities_by_category: dict[str, float]


class NetWorthCalculator:
    """Computes total assets, liabilities, and net worth."""

    @staticmethod
    def calculate(
        assets: List[Asset],
        liabilities: List[Liability],
    ) -> NetWorthResult:
        """
        Calculate net worth from assets and liabilities.

        Args:
            assets: List of Asset objects
            liabilities: List of Liability objects

        Returns:
            NetWorthResult with computed values
        """
        # Calculate total assets
        total_assets = sum(asset.current_value for asset in assets)
        
        # Calculate assets by category
        assets_by_category: dict[str, float] = {}
        for asset in assets:
            assets_by_category[asset.category] = (
                assets_by_category.get(asset.category, 0.0) + asset.current_value
            )

        # Calculate total liabilities
        total_liabilities = sum(liability.balance for liability in liabilities)
        
        # Calculate liabilities by category
        liabilities_by_category: dict[str, float] = {}
        for liability in liabilities:
            liabilities_by_category[liability.category] = (
                liabilities_by_category.get(liability.category, 0.0) + liability.balance
            )

        # Calculate net worth
        net_worth = total_assets - total_liabilities

        # Calculate liquid net worth (only from liquid assets)
        liquid_net_worth = sum(
            asset.current_value for asset in assets if asset.is_liquid()
        ) - total_liabilities

        return NetWorthResult(
            total_assets=total_assets,
            total_liabilities=total_liabilities,
            net_worth=net_worth,
            liquid_net_worth=liquid_net_worth,
            assets_by_category=assets_by_category,
            liabilities_by_category=liabilities_by_category,
        )

    @staticmethod
    def calculate_summary(assets: List[Asset], liabilities: List[Liability]) -> dict:
        """
        Calculate net worth and return as dictionary.

        Args:
            assets: List of Asset objects
            liabilities: List of Liability objects

        Returns:
            Dictionary with net worth summary
        """
        result = NetWorthCalculator.calculate(assets, liabilities)
        return {
            "total_assets": result.total_assets,
            "total_liabilities": result.total_liabilities,
            "net_worth": result.net_worth,
            "liquid_net_worth": result.liquid_net_worth,
            "assets_by_category": result.assets_by_category,
            "liabilities_by_category": result.liabilities_by_category,
        }
