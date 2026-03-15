"""Expense Shock Simulator - models unexpected financial obligations."""
from typing import Any, Dict, List

from app.finance.simulation.models.scenario_result import ScenarioResult
from app.finance.simulation.models.scenario_definition import ScenarioType


class ExpenseShockSimulator:
    """
    Models unexpected financial obligations.
    
    Examples:
    - Medical expense
    - Home repair
    - Vehicle replacement
    
    Returns:
    - Impact on liquidity
    - Cash flow disruption
    - Recovery timeline
    """

    @staticmethod
    def simulate(
        financial_state: Dict[str, Any],
        expense_shock_amount: float,
        expense_type: str = "one_time",
        recovery_contribution: float = 0,
        simulation_horizon_months: int = 24,
    ) -> ScenarioResult:
        """
        Simulate expense shock.

        Args:
            financial_state: Current financial state
            expense_shock_amount: Amount of unexpected expense
            expense_type: "one_time" or "recurring"
            recovery_contribution: Additional monthly payment toward recovery
            simulation_horizon_months: Maximum months to simulate

        Returns:
            ScenarioResult with expense shock projections
        """
        profile_id = financial_state.get("profile_id", 0)
        
        # Get current values
        monthly_income = financial_state.get("monthly_income", 0)
        monthly_expenses = financial_state.get("monthly_expenses", 0)
        liquid_assets = financial_state.get("liquid_assets", 0)
        total_liabilities = financial_state.get("total_liabilities", 0)
        
        # Simulate month by month
        timeline = []
        current_month = 0
        minimum_liquidity = liquid_assets
        recovery_month = None
        
        # Apply one-time shock at month 1
        liquid_assets -= expense_shock_amount
        
        while current_month < simulation_horizon_months and liquid_assets > 0:
            current_month += 1
            
            # Calculate cash flow
            base_cash_flow = monthly_income - monthly_expenses
            
            # Add recovery contribution if still recovering
            if recovery_month is None and liquid_assets < 0:
                # Will need time to recover
                pass
            
            # Apply additional expenses if recurring
            if expense_type == "recurring":
                monthly_expenses += expense_shock_amount
            
            # Cash flow with recovery
            cash_flow = base_cash_flow + recovery_contribution
            
            # Update liquid assets
            liquid_assets += cash_flow
            
            # Track minimum
            if liquid_assets < minimum_liquidity:
                minimum_liquidity = liquid_assets
            
            # Track recovery
            if recovery_month is None and liquid_assets >= 0 and current_month > 1:
                recovery_month = current_month
            
            timeline.append({
                "month": current_month,
                "liquid_assets": liquid_assets,
                "cash_flow": cash_flow,
                "cumulative_impact": expense_shock_amount - (financial_state.get("liquid_assets", 0) - liquid_assets),
            })
        
        # Calculate recovery timeline
        if recovery_month is None:
            recovery_month = simulation_horizon_months + 1  # Never recovered
        
        # Calculate impact metrics
        initial_liquidity = financial_state.get("liquid_assets", 0)
        liquidity_impact = initial_liquidity - minimum_liquidity
        
        # Project final values
        total_assets = financial_state.get("total_assets", 0)
        
        projected_net_worth = liquid_assets + (total_assets - financial_state.get("liquid_assets", 0)) - total_liabilities
        projected_liquidity = max(0, liquid_assets)
        projected_debt_balance = total_liabilities
        
        # Determine risk classification based on recovery ability
        if minimum_liquidity > 0:
            risk_classification = "low"
        elif minimum_liquidity > -monthly_income * 3:
            risk_classification = "moderate"
        elif minimum_liquidity > -monthly_income * 6:
            risk_classification = "high"
        else:
            risk_classification = "severe"
        
        return ScenarioResult.create(
            scenario_id="",  # Will be set by caller
            profile_id=profile_id,
            scenario_type=ScenarioType.EXPENSE_SHOCK,
            projected_net_worth=projected_net_worth,
            projected_liquidity=projected_liquidity,
            projected_debt_balance=projected_debt_balance,
            interest_paid_total=0,
            interest_saved_vs_baseline=0,
            payoff_timeline_months=0,
            survival_months=float('inf'),  # Expense shock doesn't typically deplete all reserves
            minimum_liquidity=minimum_liquidity,
            confidence_score=0.80,
            timeline=timeline,
            risk_classification=risk_classification,
        )

    @staticmethod
    def get_common_shock_scenarios() -> List[Dict[str, Any]]:
        """
        Get common expense shock scenarios.
        
        Returns:
            List of common shock configurations
        """
        return [
            {"name": "Medical Emergency", "amount": 5000, "type": "one_time"},
            {"name": "Home Repair", "amount": 8000, "type": "one_time"},
            {"name": "Vehicle Replacement", "amount": 25000, "type": "one_time"},
            {"name": "Job Loss", "amount": 0, "type": "recurring", "description": "Complete income loss"},
        ]
