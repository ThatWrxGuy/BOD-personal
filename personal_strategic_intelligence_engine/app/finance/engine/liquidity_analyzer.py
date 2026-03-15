"""Liquidity Analyzer - computes liquid assets, emergency fund months, and liquidity ratio."""
from dataclasses import dataclass
from typing import List, Optional

from app.finance.models.asset import Asset
from app.finance.models.financial_assumptions import FinancialAssumptions


@dataclass
class LiquidityResult:
    """Result of liquidity analysis."""
    liquid_assets: float
    emergency_fund_months: float
    liquidity_ratio: float
    cash_equivalents: float
    highly_liquid_assets: float
    illiquid_assets: float


class LiquidityAnalyzer:
    """Analyzes liquidity position."""

    @staticmethod
    def calculate(
        assets: List[Asset],
        monthly_expenses: float,
        assumptions: Optional[FinancialAssumptions] = None,
    ) -> LiquidityResult:
        """
        Calculate liquidity metrics.

        Args:
            assets: List of Asset objects
            monthly_expenses: Monthly expenses amount
            assumptions: Optional FinancialAssumptions for target months

        Returns:
            LiquidityResult with computed values
        """
        # Target emergency fund months (default 6 if not provided)
        target_months = 6
        if assumptions:
            target_months = assumptions.emergency_fund_target_months

        # Calculate cash equivalents (highest liquidity)
        cash_equivalents = sum(
            asset.current_value for asset in assets if asset.is_cash_equivalent()
        )

        # Calculate highly liquid assets (liquidity score >= 0.8)
        highly_liquid_assets = sum(
            asset.current_value for asset in assets if asset.is_liquid()
        )

        # Total liquid assets (all assets with liquidity score > 0)
        liquid_assets = sum(
            asset.current_value for asset in assets if asset.liquidity_score > 0
        )

        # Illiquid assets
        illiquid_assets = sum(
            asset.current_value for asset in assets if asset.liquidity_score == 0
        )

        # Emergency fund months = liquid assets / monthly expenses
        emergency_fund_months = (
            liquid_assets / monthly_expenses if monthly_expenses > 0 else 0.0
        )

        # Liquidity ratio = liquid assets / (total assets)
        total_assets = sum(asset.current_value for asset in assets)
        liquidity_ratio = (
            liquid_assets / total_assets if total_assets > 0 else 0.0
        )

        return LiquidityResult(
            liquid_assets=liquid_assets,
            emergency_fund_months=emergency_fund_months,
            liquidity_ratio=liquidity_ratio,
            cash_equivalents=cash_equivalents,
            highly_liquid_assets=highly_liquid_assets,
            illiquid_assets=illiquid_assets,
        )

    @staticmethod
    def calculate_summary(
        assets: List[Asset],
        monthly_expenses: float,
        assumptions: Optional[FinancialAssumptions] = None,
    ) -> dict:
        """
        Calculate liquidity metrics and return as dictionary.

        Args:
            assets: List of Asset objects
            monthly_expenses: Monthly expenses amount
            assumptions: Optional FinancialAssumptions

        Returns:
            Dictionary with liquidity summary
        """
        result = LiquidityAnalyzer.calculate(assets, monthly_expenses, assumptions)
        return {
            "liquid_assets": result.liquid_assets,
            "emergency_fund_months": result.emergency_fund_months,
            "liquidity_ratio": result.liquidity_ratio,
            "cash_equivalents": result.cash_equivalents,
            "highly_liquid_assets": result.highly_liquid_assets,
            "illiquid_assets": result.illiquid_assets,
        }

    @staticmethod
    def is_emergency_fund_sufficient(
        assets: List[Asset],
        monthly_expenses: float,
        target_months: int = 6,
    ) -> bool:
        """
        Check if emergency fund is sufficient.

        Args:
            assets: List of Asset objects
            monthly_expenses: Monthly expenses amount
            target_months: Target number of months

        Returns:
            True if emergency fund is sufficient
        """
        result = LiquidityAnalyzer.calculate(assets, monthly_expenses)
        return result.emergency_fund_months >= target_months
