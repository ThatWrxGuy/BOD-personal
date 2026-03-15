"""Income Shock Simulator - models the effects of reduced income."""
from typing import Any, Dict, List

from app.finance.simulation.models.scenario_result import ScenarioResult
from app.finance.simulation.models.scenario_definition import ScenarioType


class IncomeShockSimulator:
    """
    Models the effects of reduced income.
    
    Test scenarios:
    - 10% reduction
    - 25% reduction
    - 50% reduction
    
    Returns:
    - New free cash flow
    - Survival months
    - Debt stress exposure
    """

    @staticmethod
    def simulate(
        financial_state: Dict[str, Any],
        income_reduction_percentage: float = 0.25,
        income_shock_duration_months: int = 6,
        simulation_horizon_months: int = 24,
    ) -> ScenarioResult:
        """
        Simulate income reduction shock.

        Args:
            financial_state: Current financial state
            income_reduction_percentage: Percentage of income lost (0.0-1.0)
            income_shock_duration_months: How long the reduction lasts
            simulation_horizon_months: Maximum months to simulate

        Returns:
            ScenarioResult with income shock projections
        """
        profile_id = financial_state.get("profile_id", 0)
        
        # Get current values
        monthly_income = financial_state.get("monthly_income", 0)
        monthly_expenses = financial_state.get("monthly_expenses", 0)
        liquid_assets = financial_state.get("liquid_assets", 0)
        total_debt = financial_state.get("total_debt", 0)
        
        # Calculate reduced income
        reduced_income = monthly_income * (1 - income_reduction_percentage)
        income_loss = monthly_income - reduced_income
        
        # Simulate month by month
        timeline = []
        current_month = 0
        minimum_liquidity = liquid_assets
        cumulative_deficit = 0
        
        while current_month < simulation_horizon_months:
            current_month += 1
            
            # Determine if income is still reduced
            if current_month <= income_shock_duration_months:
                current_income = reduced_income
                income_active = True
            else:
                current_income = monthly_income
                income_active = True
            
            # Calculate cash flow
            cash_flow = current_income - monthly_expenses
            
            # Track deficit during shock period
            if current_month <= income_shock_duration_months:
                if cash_flow < 0:
                    cumulative_deficit += abs(cash_flow)
            
            # Update liquid assets
            liquid_assets += cash_flow
            
            # Track minimum liquidity
            if liquid_assets < minimum_liquidity:
                minimum_liquidity = liquid_assets
            
            timeline.append({
                "month": current_month,
                "income": current_income,
                "expenses": monthly_expenses,
                "cash_flow": cash_flow,
                "liquid_assets": liquid_assets,
                "shock_active": current_month <= income_shock_duration_months,
            })
        
        # Calculate survival months (how long until reserves deplete during shock)
        if monthly_expenses > reduced_income:
            monthly_deficit = monthly_expenses - reduced_income
            if monthly_deficit > 0:
                survival_months = liquid_assets / monthly_deficit if liquid_assets > 0 else 0
            else:
                survival_months = float('inf')
        else:
            survival_months = float('inf')
        
        # Calculate new free cash flow after shock
        new_free_cash_flow = monthly_income - monthly_expenses  # Post-shock (normal)
        
        # Calculate debt stress (debt relative to income)
        debt_to_income_ratio = total_debt / monthly_income if monthly_income > 0 else 0
        
        # Determine risk classification
        if survival_months >= 12:
            risk_classification = "low"
        elif survival_months >= 6:
            risk_classification = "moderate"
        elif survival_months >= 3:
            risk_classification = "high"
        else:
            risk_classification = "severe"
        
        # Project final values
        total_assets = financial_state.get("total_assets", 0)
        total_liabilities = financial_state.get("total_liabilities", 0)
        
        projected_net_worth = liquid_assets + (total_assets - financial_state.get("liquid_assets", 0)) - total_liabilities
        projected_liquidity = max(0, liquid_assets)
        projected_debt_balance = total_liabilities
        
        return ScenarioResult.create(
            scenario_id="",  # Will be set by caller
            profile_id=profile_id,
            scenario_type=ScenarioType.INCOME_SHOCK,
            projected_net_worth=projected_net_worth,
            projected_liquidity=projected_liquidity,
            projected_debt_balance=projected_debt_balance,
            interest_paid_total=0,
            interest_saved_vs_baseline=0,
            payoff_timeline_months=0,
            survival_months=survival_months if survival_months != float('inf') else 999,
            minimum_liquidity=minimum_liquidity,
            confidence_score=0.75,
            timeline=timeline,
            risk_classification=risk_classification,
        )

    @staticmethod
    def get_shock_levels() -> List[Dict[str, Any]]:
        """
        Get predefined income shock levels.
        
        Returns:
            List of shock level configurations
        """
        return [
            {"name": "Minor", "percentage": 0.10, "description": "10% income reduction"},
            {"name": "Moderate", "percentage": 0.25, "description": "25% income reduction"},
            {"name": "Severe", "percentage": 0.50, "description": "50% income reduction"},
            {"name": "Critical", "percentage": 0.75, "description": "75% income reduction"},
        ]
