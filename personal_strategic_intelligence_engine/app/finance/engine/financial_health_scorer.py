"""Financial Health Scorer - computes composite score based on liquidity, debt burden, free cash flow, diversification, and volatility exposure."""
from dataclasses import dataclass
from typing import List, Optional

from app.finance.models.asset import Asset
from app.finance.models.liability import Liability
from app.finance.engine.liquidity_analyzer import LiquidityAnalyzer
from app.finance.engine.debt_analyzer import DebtAnalyzer


@dataclass
class HealthScoreResult:
    """Result of financial health scoring."""
    overall_score: float
    liquidity_score: float
    debt_burden_score: float
    cash_flow_score: float
    diversification_score: float
    volatility_score: float
    score_breakdown: dict


class FinancialHealthScorer:
    """Computes composite financial health score (0-100)."""

    # Score weights
    LIQUIDITY_WEIGHT = 0.25
    DEBT_BURDEN_WEIGHT = 0.25
    CASH_FLOW_WEIGHT = 0.25
    DIVERSIFICATION_WEIGHT = 0.15
    VOLATILITY_WEIGHT = 0.10

    @staticmethod
    def calculate(
        assets: List[Asset],
        liabilities: List[Liability],
        monthly_income: float,
        monthly_expenses: float,
        free_cash_flow: float,
    ) -> HealthScoreResult:
        """
        Calculate financial health score.

        Args:
            assets: List of Asset objects
            liabilities: List of Liability objects
            monthly_income: Monthly income amount
            monthly_expenses: Monthly expenses amount
            free_cash_flow: Free cash flow amount

        Returns:
            HealthScoreResult with computed scores
        """
        # Calculate component scores
        liquidity_score = FinancialHealthScorer._score_liquidity(assets, monthly_expenses)
        debt_burden_score = FinancialHealthScorer._score_debt_burden(liabilities, monthly_income)
        cash_flow_score = FinancialHealthScorer._score_cash_flow(free_cash_flow, monthly_income)
        diversification_score = FinancialHealthScorer._score_diversification(assets)
        volatility_score = FinancialHealthScorer._score_volatility(assets)

        # Calculate weighted overall score
        overall_score = (
            liquidity_score * FinancialHealthScorer.LIQUIDITY_WEIGHT
            + debt_burden_score * FinancialHealthScorer.DEBT_BURDEN_WEIGHT
            + cash_flow_score * FinancialHealthScorer.CASH_FLOW_WEIGHT
            + diversification_score * FinancialHealthScorer.DIVERSIFICATION_WEIGHT
            + volatility_score * FinancialHealthScorer.VOLATILITY_WEIGHT
        )

        # Ensure score is within 0-100 range
        overall_score = max(0.0, min(100.0, overall_score))

        return HealthScoreResult(
            overall_score=overall_score,
            liquidity_score=liquidity_score,
            debt_burden_score=debt_burden_score,
            cash_flow_score=cash_flow_score,
            diversification_score=diversification_score,
            volatility_score=volatility_score,
            score_breakdown={
                "liquidity": {"score": liquidity_score, "weight": FinancialHealthScorer.LIQUIDITY_WEIGHT},
                "debt_burden": {"score": debt_burden_score, "weight": FinancialHealthScorer.DEBT_BURDEN_WEIGHT},
                "cash_flow": {"score": cash_flow_score, "weight": FinancialHealthScorer.CASH_FLOW_WEIGHT},
                "diversification": {"score": diversification_score, "weight": FinancialHealthScorer.DIVERSIFICATION_WEIGHT},
                "volatility": {"score": volatility_score, "weight": FinancialHealthScorer.VOLATILITY_WEIGHT},
            },
        )

    @staticmethod
    def _score_liquidity(assets: List[Asset], monthly_expenses: float) -> float:
        """
        Score liquidity (0-100).
        
        Higher score = better liquidity position.
        """
        if not assets or monthly_expenses <= 0:
            return 50.0  # Neutral score

        liquidity_result = LiquidityAnalyzer.calculate(assets, monthly_expenses)
        months = liquidity_result.emergency_fund_months

        # Score based on emergency fund months
        # 0 months = 0, 6+ months = 100
        score = min(100.0, (months / 6.0) * 100.0)
        return score

    @staticmethod
    def _score_debt_burden(liabilities: List[Liability], monthly_income: float) -> float:
        """
        Score debt burden (0-100).
        
        Higher score = lower debt burden.
        """
        if not liabilities or monthly_income <= 0:
            return 100.0  # No debt = perfect score

        debt_result = DebtAnalyzer.calculate(liabilities, monthly_income)
        dti = debt_result.debt_to_income_ratio

        # Score based on debt-to-income ratio
        # DTI 0% = 100, DTI 50%+ = 0
        score = max(0.0, 100.0 - (dti * 200.0))
        return score

    @staticmethod
    def _score_cash_flow(free_cash_flow: float, monthly_income: float) -> float:
        """
        Score cash flow (0-100).
        
        Higher score = positive cash flow.
        """
        if monthly_income <= 0:
            return 50.0  # Neutral score

        # Calculate cash flow ratio
        ratio = free_cash_flow / monthly_income

        # Positive cash flow > 20% of income = 100
        # Zero cash flow = 50
        # Negative cash flow = 0
        if ratio >= 0.20:
            return 100.0
        elif ratio >= 0:
            # Scale 0-20% to 50-100
            return 50.0 + (ratio / 0.20) * 50.0
        else:
            # Negative cash flow
            # Scale -50% to 0% to 0-50
            return max(0.0, 50.0 + (ratio * 100.0))

    @staticmethod
    def _score_diversification(assets: List[Asset]) -> float:
        """
        Score asset diversification (0-100).
        
        Higher score = better diversification.
        """
        if not assets:
            return 0.0

        # Count unique categories
        categories = set(asset.category for asset in assets)
        num_categories = len(categories)

        # Calculate total asset value
        total_value = sum(asset.current_value for asset in assets)

        if total_value <= 0:
            return 0.0

        # Calculate Herfindahl-Hirschman Index (HHI) for diversification
        # Lower HHI = more diversified
        hhi = sum((asset.current_value / total_value) ** 2 for asset in assets)

        # Convert HHI to score (1.0 = perfect concentration, lower = more diverse)
        # HHI of 1.0 = 0 score, HHI of 0.1 = 100 score
        diversification_score = max(0.0, (1.0 - hhi) * 100.0)

        # Boost score for having multiple categories
        category_bonus = min(20.0, num_categories * 5.0)

        return min(100.0, diversification_score + category_bonus)

    @staticmethod
    def _score_volatility(assets: List[Asset]) -> float:
        """
        Score volatility exposure (0-100).
        
        Higher score = lower volatility exposure.
        """
        if not assets:
            return 100.0  # No volatile assets

        total_value = sum(asset.current_value for asset in assets)

        if total_value <= 0:
            return 100.0

        # Calculate weighted volatility
        weighted_volatility = sum(
            asset.current_value * asset.volatility_score for asset in assets
        ) / total_value

        # Convert to score (0 volatility = 100, 1.0 volatility = 0)
        score = (1.0 - weighted_volatility) * 100.0

        return score

    @staticmethod
    def calculate_summary(
        assets: List[Asset],
        liabilities: List[Liability],
        monthly_income: float,
        monthly_expenses: float,
        free_cash_flow: float,
    ) -> dict:
        """
        Calculate health score and return as dictionary.

        Args:
            assets: List of Asset objects
            liabilities: List of Liability objects
            monthly_income: Monthly income amount
            monthly_expenses: Monthly expenses amount
            free_cash_flow: Free cash flow amount

        Returns:
            Dictionary with health score summary
        """
        result = FinancialHealthScorer.calculate(
            assets, liabilities, monthly_income, monthly_expenses, free_cash_flow
        )
        return {
            "financial_health_score": result.overall_score,
            "liquidity_score": result.liquidity_score,
            "debt_burden_score": result.debt_burden_score,
            "cash_flow_score": result.cash_flow_score,
            "diversification_score": result.diversification_score,
            "volatility_score": result.volatility_score,
            "score_breakdown": result.score_breakdown,
        }
