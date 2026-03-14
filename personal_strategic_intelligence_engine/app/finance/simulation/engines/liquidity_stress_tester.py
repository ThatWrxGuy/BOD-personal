"""Liquidity Stress Tester - evaluates resilience to financial disruption."""
from typing import Any, Dict, List

from app.finance.simulation.models.scenario_result import ScenarioResult
from app.finance.simulation.models.scenario_definition import ScenarioType


class LiquidityStressTester:
    """
    Evaluates resilience to financial disruption.
    
    Simulates:
    - Income interruption
    - Expense shock
    - Reserve depletion
    
    Returns:
    - Months until reserve depletion
    - Minimum survival liquidity
    - Risk classification
    """

    @staticmethod
    def simulate(
        financial_state: Dict[str, Any],
        income_interruption_months: int = 3,
        expense_shock_amount: float = 0,
        simulation_horizon_months: int = 24,
    ) -> ScenarioResult:
        """
        Simulate liquidity stress conditions.

        Args:
            financial_state: Current financial state
            income_interruption_months: Months without income
            expense_shock_amount: One-time expense shock
            simulation_horizon_months: Maximum months to simulate

        Returns:
            ScenarioResult with stress test projections
        """
        profile_id = financial_state.get("profile_id", 0)
        
        # Get current values
        liquid_assets = financial_state.get("liquid_assets", 0)
        monthly_income = financial_state.get("monthly_income", 0)
        monthly_expenses = financial_state.get("monthly_expenses", 0)
        
        # Apply expense shock immediately
        liquid_assets -= expense_shock_amount
        
        # Simulate month by month
        timeline = []
        current_month = 0
        minimum_liquidity = liquid_assets
        
        while current_month < simulation_horizon_months and liquid_assets > 0:
            current_month += 1
            
            # Determine if income is interrupted
            if current_month <= income_interruption_months:
                # No income
                cash_flow = -monthly_expenses
            else:
                # Normal cash flow
                monthly_savings = monthly_income - monthly_expenses
                cash_flow = monthly_savings
            
            # Update liquid assets
            liquid_assets += cash_flow
            
            # Track minimum
            if liquid_assets < minimum_liquidity:
                minimum_liquidity = liquid_assets
            
            timeline.append({
                "month": current_month,
                "liquid_assets": liquid_assets,
                "cash_flow": cash_flow,
                "income_active": current_month > income_interruption_months,
            })
        
        # Calculate survival months
        survival_months = current_month
        
        # If still solvent at end, project indefinitely
        if liquid_assets > 0:
            # Calculate how many more months until depletion at 0 income
            if monthly_expenses > 0:
                additional_months = liquid_assets / monthly_expenses
                survival_months = income_interruption_months + additional_months
        
        # Project final values
        total_assets = financial_state.get("total_assets", 0)
        total_liabilities = financial_state.get("total_liabilities", 0)
        
        projected_net_worth = liquid_assets + (total_assets - financial_state.get("liquid_assets", 0)) - total_liabilities
        projected_debt_balance = total_liabilities
        
        # Determine risk classification based on survival months
        if survival_months >= 12:
            risk_classification = "low"
        elif survival_months >= 6:
            risk_classification = "moderate"
        elif survival_months >= 3:
            risk_classification = "high"
        else:
            risk_classification = "severe"
        
        return ScenarioResult.create(
            scenario_id="",  # Will be set by caller
            profile_id=profile_id,
            scenario_type=ScenarioType.LIQUIDITY_STRESS,
            projected_net_worth=projected_net_worth,
            projected_liquidity=max(0, liquid_assets),
            projected_debt_balance=projected_debt_balance,
            interest_paid_total=0,
            interest_saved_vs_baseline=0,
            payoff_timeline_months=0,
            survival_months=survival_months,
            minimum_liquidity=minimum_liquidity,
            confidence_score=0.85,
            timeline=timeline,
            risk_classification=risk_classification,
        )

    @staticmethod
    def calculate_survival_months(
        financial_state: Dict[str, Any],
    ) -> float:
        """
        Calculate how many months until reserves are depleted with no income.
        
        Args:
            financial_state: Current financial state
            
        Returns:
            Number of months until depletion
        """
        liquid_assets = financial_state.get("liquid_assets", 0)
        monthly_expenses = financial_state.get("monthly_expenses", 0)
        
        if monthly_expenses <= 0:
            return float('inf')
        
        return liquid_assets / monthly_expenses
