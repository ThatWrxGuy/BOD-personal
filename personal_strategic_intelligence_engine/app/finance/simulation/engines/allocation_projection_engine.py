"""Allocation Projection Engine - projects asset growth under different allocation assumptions."""
from typing import Any, Dict, List, Optional

from app.finance.simulation.models.scenario_result import ScenarioResult
from app.finance.simulation.models.scenario_definition import ScenarioType


class AllocationProjectionEngine:
    """
    Projects asset growth under different allocation assumptions.
    
    Inputs:
    - Asset allocation
    - Expected return assumptions
    - Simulation horizon
    
    Outputs:
    - Projected portfolio value
    - Risk exposure classification
    - Volatility impact
    """

    # Asset class return assumptions (annual)
    DEFAULT_RETURNS = {
        "stocks": 0.10,       # 10% annual return
        "bonds": 0.05,        # 5% annual return
        "cash": 0.02,         # 2% annual return
        "real_estate": 0.08,  # 8% annual return
        "crypto": 0.20,       # 20% annual return (high volatility)
        "alternatives": 0.07, # 7% annual return
    }
    
    # Volatility (standard deviation)
    DEFAULT_VOLATILITY = {
        "stocks": 0.20,
        "bonds": 0.08,
        "cash": 0.01,
        "real_estate": 0.12,
        "crypto": 0.60,
        "alternatives": 0.15,
    }

    @staticmethod
    def simulate(
        financial_state: Dict[str, Any],
        target_allocation: Optional[Dict[str, float]] = None,
        market_return_rate: float = 0.07,
        inflation_rate: float = 0.03,
        simulation_horizon_months: int = 60,
    ) -> ScenarioResult:
        """
        Simulate asset allocation projection.

        Args:
            financial_state: Current financial state
            target_allocation: Target asset allocation (e.g., {"stocks": 0.6, "bonds": 0.4})
            market_return_rate: Expected market return rate
            inflation_rate: Expected inflation rate
            simulation_horizon_months: Maximum months to simulate

        Returns:
            ScenarioResult with allocation projections
        """
        profile_id = financial_state.get("profile_id", 0)
        
        # Get current assets
        total_assets = financial_state.get("total_assets", 0)
        assets_by_category = financial_state.get("assets_by_category", {})
        liquid_assets = financial_state.get("liquid_assets", 0)
        
        # Default allocation if not provided
        if target_allocation is None:
            target_allocation = {
                "stocks": 0.60,
                "bonds": 0.30,
                "cash": 0.10,
            }
        
        # Validate allocation sums to 1.0
        total_alloc = sum(target_allocation.values())
        if abs(total_alloc - 1.0) > 0.01:
            # Normalize
            target_allocation = {k: v/total_alloc for k, v in target_allocation.items()}
        
        # Calculate weighted return and volatility
        weighted_return = 0
        weighted_volatility = 0
        
        for asset_class, weight in target_allocation.items():
            return_rate = AllocationProjectionEngine.DEFAULT_RETURNS.get(asset_class, market_return_rate)
            volatility = AllocationProjectionEngine.DEFAULT_VOLATILITY.get(asset_class, 0.15)
            
            weighted_return += weight * return_rate
            weighted_volatility += weight * volatility * weight  # Simplified
        
        # Adjust for inflation (real return)
        real_return = (1 + weighted_return) / (1 + inflation_rate) - 1
        
        # Simulate month by month
        timeline = []
        current_assets = total_assets
        months = simulation_horizon_months
        
        for month in range(1, months + 1):
            # Apply monthly return (simplified - using real return)
            monthly_return = real_return / 12
            monthly_growth = current_assets * monthly_return
            
            # Add monthly contributions (if any - assume 10% of income goes to investments)
            monthly_income = financial_state.get("monthly_income", 0)
            monthly_contribution = monthly_income * 0.10  # 10% savings rate
            
            current_assets += monthly_growth + monthly_contribution
            
            timeline.append({
                "month": month,
                "portfolio_value": current_assets,
                "monthly_growth": monthly_growth,
                "cumulative_growth": current_assets - total_assets - (monthly_contribution * month),
            })
        
        # Calculate projected values
        projected_liquidity = liquid_assets  # Liquidity doesn't change in this sim
        total_liabilities = financial_state.get("total_liabilities", 0)
        
        projected_net_worth = current_assets - total_liabilities
        projected_debt_balance = total_liabilities
        
        # Calculate risk classification based on allocation
        crypto_weight = target_allocation.get("crypto", 0)
        stock_weight = target_allocation.get("stocks", 0)
        cash_weight = target_allocation.get("cash", 0)
        
        if crypto_weight > 0.2 or stock_weight > 0.8:
            risk_classification = "high"
        elif stock_weight > 0.6 or (stock_weight + crypto_weight) > 0.7:
            risk_classification = "moderate"
        else:
            risk_classification = "low"
        
        # Confidence score based on allocation stability
        confidence_score = 0.90 - (crypto_weight * 0.3) - (stock_weight * 0.1)
        confidence_score = max(0.5, min(0.95, confidence_score))
        
        return ScenarioResult.create(
            scenario_id="",  # Will be set by caller
            profile_id=profile_id,
            scenario_type=ScenarioType.INVESTMENT_ALLOCATION,
            projected_net_worth=projected_net_worth,
            projected_liquidity=projected_liquidity,
            projected_debt_balance=projected_debt_balance,
            interest_paid_total=0,
            interest_saved_vs_baseline=0,
            payoff_timeline_months=0,
            survival_months=float('inf'),
            minimum_liquidity=projected_liquidity,
            confidence_score=confidence_score,
            timeline=timeline,
            risk_classification=risk_classification,
        )

    @staticmethod
    def get_recommended_allocations() -> List[Dict[str, Any]]:
        """
        Get recommended asset allocations based on risk tolerance.
        
        Returns:
            List of allocation profiles
        """
        return [
            {
                "name": "Conservative",
                "allocation": {"stocks": 0.30, "bonds": 0.50, "cash": 0.20},
                "expected_return": 0.055,
                "risk_level": "low",
            },
            {
                "name": "Moderate",
                "allocation": {"stocks": 0.50, "bonds": 0.35, "cash": 0.15},
                "expected_return": 0.065,
                "risk_level": "moderate",
            },
            {
                "name": "Aggressive",
                "allocation": {"stocks": 0.70, "bonds": 0.20, "cash": 0.10},
                "expected_return": 0.075,
                "risk_level": "high",
            },
            {
                "name": "Very Aggressive",
                "allocation": {"stocks": 0.80, "bonds": 0.10, "cash": 0.05, "alternatives": 0.05},
                "expected_return": 0.085,
                "risk_level": "high",
            },
        ]
