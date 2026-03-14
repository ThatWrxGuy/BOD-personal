"""Financial State Engine - aggregates assets, liabilities, income, expenses, and financial assumptions to produce a canonical Financial State Object."""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.finance.models.asset import Asset
from app.finance.models.liability import Liability
from app.finance.models.financial_profile import FinancialProfile
from app.finance.models.financial_assumptions import FinancialAssumptions
from app.finance.engine.net_worth_calculator import NetWorthCalculator
from app.finance.engine.cash_flow_analyzer import CashFlowAnalyzer
from app.finance.engine.liquidity_analyzer import LiquidityAnalyzer
from app.finance.engine.debt_analyzer import DebtAnalyzer
from app.finance.engine.financial_health_scorer import FinancialHealthScorer


@dataclass
class FinancialState:
    """
    Canonical Financial State Object.
    
    This is the source of truth for all financial intelligence,
    simulations, and recommendations.
    """
    profile_id: int
    
    # Core totals
    total_assets: float
    total_liabilities: float
    net_worth: float
    
    # Cash flow
    monthly_income: float
    monthly_expenses: float
    free_cash_flow: float
    
    # Liquidity
    liquid_assets: float
    available_liquidity: float
    
    # Debt breakdown
    revolving_debt_balance: float
    secured_debt_balance: float
    total_debt: float
    
    # Additional metrics
    debt_to_income_ratio: float
    savings_rate: float
    emergency_fund_months: float
    liquidity_ratio: float
    
    # Health score
    financial_health_score: float
    
    # Detailed breakdowns
    assets_by_category: Dict[str, float]
    liabilities_by_category: Dict[str, float]
    
    # Raw data references
    raw_state_payload: Dict[str, Any]


class FinancialStateEngine:
    """
    Aggregates all financial data to produce canonical Financial State.
    
    Responsibilities:
    - Aggregate assets, liabilities, income, expenses, financial assumptions
    - Produce a canonical Financial State Object
    """

    @staticmethod
    def compute(
        profile: FinancialProfile,
        assets: List[Asset],
        liabilities: List[Liability],
        assumptions: Optional[FinancialAssumptions] = None,
    ) -> FinancialState:
        """
        Compute the canonical financial state from all inputs.

        Args:
            profile: FinancialProfile object
            assets: List of Asset objects
            liabilities: List of Liability objects
            assumptions: Optional FinancialAssumptions

        Returns:
            FinancialState with all computed values
        """
        # Calculate net worth
        net_worth_result = NetWorthCalculator.calculate(assets, liabilities)

        # Calculate monthly debt payments
        monthly_debt_payments = sum(liability.minimum_payment for liability in liabilities)
        
        # Estimate monthly savings and investments
        monthly_savings = profile.monthly_income * 0.1  # Default 10%
        monthly_investments = profile.monthly_income * 0.1  # Default 10%

        # Calculate cash flow
        cash_flow_result = CashFlowAnalyzer.calculate_from_profile(
            profile, monthly_debt_payments, monthly_savings, monthly_investments
        )

        # Calculate liquidity
        liquidity_result = LiquidityAnalyzer.calculate(
            assets, cash_flow_result.monthly_expenses, assumptions
        )

        # Calculate debt metrics
        debt_result = DebtAnalyzer.calculate(liabilities, profile.monthly_income)

        # Calculate financial health score
        health_result = FinancialHealthScorer.calculate(
            assets,
            liabilities,
            profile.monthly_income,
            cash_flow_result.monthly_expenses,
            cash_flow_result.free_cash_flow,
        )

        # Build the canonical state
        state = FinancialState(
            profile_id=profile.profile_id,
            
            # Core totals
            total_assets=net_worth_result.total_assets,
            total_liabilities=net_worth_result.total_liabilities,
            net_worth=net_worth_result.net_worth,
            
            # Cash flow
            monthly_income=cash_flow_result.monthly_income,
            monthly_expenses=cash_flow_result.monthly_expenses,
            free_cash_flow=cash_flow_result.free_cash_flow,
            
            # Liquidity
            liquid_assets=liquidity_result.liquid_assets,
            available_liquidity=liquidity_result.cash_equivalents,
            
            # Debt breakdown
            revolving_debt_balance=debt_result.revolving_debt_balance,
            secured_debt_balance=debt_result.secured_debt_balance,
            total_debt=debt_result.total_debt_balance,
            
            # Additional metrics
            debt_to_income_ratio=debt_result.debt_to_income_ratio,
            savings_rate=cash_flow_result.savings_rate,
            emergency_fund_months=liquidity_result.emergency_fund_months,
            liquidity_ratio=liquidity_result.liquidity_ratio,
            
            # Health score
            financial_health_score=health_result.overall_score,
            
            # Detailed breakdowns
            assets_by_category=net_worth_result.assets_by_category,
            liabilities_by_category=net_worth_result.liabilities_by_category,
            
            # Raw payload
            raw_state_payload={},
        )

        return state

    @staticmethod
    def compute_summary(
        profile: FinancialProfile,
        assets: List[Asset],
        liabilities: List[Liability],
        assumptions: Optional[FinancialAssumptions] = None,
    ) -> Dict[str, Any]:
        """
        Compute financial state and return as dictionary for API responses.

        Args:
            profile: FinancialProfile object
            assets: List of Asset objects
            liabilities: List of Liability objects
            assumptions: Optional FinancialAssumptions

        Returns:
            Dictionary with financial state
        """
        state = FinancialStateEngine.compute(profile, assets, liabilities, assumptions)
        
        return {
            "net_worth": state.net_worth,
            "monthly_income": state.monthly_income,
            "monthly_expenses": state.monthly_expenses,
            "free_cash_flow": state.free_cash_flow,
            "total_assets": state.total_assets,
            "total_liabilities": state.total_liabilities,
            "liquid_assets": state.liquid_assets,
            "total_debt": state.total_debt,
            "debt_to_income_ratio": state.debt_to_income_ratio,
            "emergency_fund_months": state.emergency_fund_months,
            "financial_health_score": state.financial_health_score,
            "assets_by_category": state.assets_by_category,
            "liabilities_by_category": state.liabilities_by_category,
            "revolving_debt_balance": state.revolving_debt_balance,
            "secured_debt_balance": state.secured_debt_balance,
            "savings_rate": state.savings_rate,
            "liquidity_ratio": state.liquidity_ratio,
        }
