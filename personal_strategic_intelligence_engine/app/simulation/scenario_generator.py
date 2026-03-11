"""Scenario generator for creating simulation scenarios."""
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.logging import get_logger

logger = get_logger(__name__)


class ScenarioGenerator:
    """Generate scenarios for simulation."""
    
    def __init__(self):
        pass
    
    async def generate_scenarios(
        self,
        decision_type: str,
        decision_params: Dict[str, Any],
        time_horizon_days: int,
    ) -> List[Dict[str, Any]]:
        """Generate scenarios based on decision type."""
        
        if decision_type == "investment":
            return await self._generate_investment_scenarios(decision_params, time_horizon_days)
        
        elif decision_type == "spending":
            return await self._generate_spending_scenarios(decision_params, time_horizon_days)
        
        elif decision_type == "workload":
            return await self._generate_workload_scenarios(decision_params, time_horizon_days)
        
        elif decision_type == "expense":
            return await self._generate_expense_scenarios(decision_params, time_horizon_days)
        
        elif decision_type == "goal_timeline":
            return await self._generate_goal_scenarios(decision_params, time_horizon_days)
        
        else:
            # Default generic scenarios
            return await self._generate_generic_scenarios(decision_params, time_horizon_days)
    
    async def _generate_investment_scenarios(
        self,
        params: Dict[str, Any],
        time_horizon_days: int,
    ) -> List[Dict[str, Any]]:
        """Generate investment allocation scenarios."""
        
        base_amount = params.get("base_amount", 10000)
        
        scenarios = [
            {
                "scenario_name": "Conservative Allocation",
                "scenario_type": "conservative",
                "parameters": {
                    "allocation": {"stocks": 30, "bonds": 50, "cash": 20},
                    "expected_return": 0.04,
                    "volatility": 0.08,
                },
                "description": "Lower risk, stable returns",
            },
            {
                "scenario_name": "Balanced Allocation",
                "scenario_type": "balanced",
                "parameters": {
                    "allocation": {"stocks": 60, "bonds": 30, "cash": 10},
                    "expected_return": 0.07,
                    "volatility": 0.12,
                },
                "description": "Moderate risk and returns",
            },
            {
                "scenario_name": "Aggressive Allocation",
                "scenario_type": "aggressive",
                "parameters": {
                    "allocation": {"stocks": 80, "bonds": 15, "cash": 5},
                    "expected_return": 0.10,
                    "volatility": 0.18,
                },
                "description": "Higher risk, higher potential returns",
            },
            {
                "scenario_name": "Market Downturn",
                "scenario_type": "pessimistic",
                "parameters": {
                    "allocation": {"stocks": 60, "bonds": 30, "cash": 10},
                    "expected_return": -0.15,
                    "volatility": 0.25,
                },
                "description": "Simulated market downturn scenario",
            },
        ]
        
        return scenarios
    
    async def _generate_spending_scenarios(
        self,
        params: Dict[str, Any],
        time_horizon_days: int,
    ) -> List[Dict[str, Any]]:
        """Generate spending pattern scenarios."""
        
        current_spending = params.get("monthly_spending", 3000)
        
        scenarios = [
            {
                "scenario_name": "Maintain Current Spending",
                "scenario_type": "baseline",
                "parameters": {
                    "monthly_spending": current_spending,
                    "change_rate": 0.0,
                },
                "description": "Continue current spending patterns",
            },
            {
                "scenario_name": "Reduce Discretionary Spending",
                "scenario_type": "optimistic",
                "parameters": {
                    "monthly_spending": current_spending * 0.85,
                    "change_rate": -0.15,
                },
                "description": "15% reduction in discretionary spending",
            },
            {
                "scenario_name": "Aggressive Cost Cutting",
                "scenario_type": "aggressive",
                "parameters": {
                    "monthly_spending": current_spending * 0.70,
                    "change_rate": -0.30,
                },
                "description": "30% overall spending reduction",
            },
            {
                "scenario_name": "Increased Spending",
                "scenario_type": "pessimistic",
                "parameters": {
                    "monthly_spending": current_spending * 1.15,
                    "change_rate": 0.15,
                },
                "description": "15% increase in spending",
            },
        ]
        
        return scenarios
    
    async def _generate_workload_scenarios(
        self,
        params: Dict[str, Any],
        time_horizon_days: int,
    ) -> List[Dict[str, Any]]:
        """Generate workload scenarios."""
        
        current_hours = params.get("current_hours", 40)
        
        scenarios = [
            {
                "scenario_name": "Maintain Current Hours",
                "scenario_type": "baseline",
                "parameters": {
                    "weekly_hours": current_hours,
                    "change": 0,
                },
                "description": "Keep current workload",
            },
            {
                "scenario_name": "Reduce Hours",
                "scenario_type": "optimistic",
                "parameters": {
                    "weekly_hours": max(20, current_hours - 10),
                    "change": -10,
                },
                "description": "Reduce hours for work-life balance",
            },
            {
                "scenario_name": "Increase Hours",
                "scenario_type": "pessimistic",
                "parameters": {
                    "weekly_hours": min(60, current_hours + 10),
                    "change": 10,
                },
                "description": "Increase hours for more output",
            },
            {
                "scenario_name": "Flexible Hours",
                "scenario_type": "alternative",
                "parameters": {
                    "weekly_hours": current_hours,
                    "change": 0,
                    "flexible": True,
                },
                "description": "Same hours with flexible scheduling",
            },
        ]
        
        return scenarios
    
    async def _generate_expense_scenarios(
        self,
        params: Dict[str, Any],
        time_horizon_days: int,
    ) -> List[Dict[str, Any]]:
        """Generate major expense scenarios."""
        
        expense_amount = params.get("expense_amount", 5000)
        
        scenarios = [
            {
                "scenario_name": "Pay Full Immediately",
                "scenario_type": "baseline",
                "parameters": {
                    "payment_type": "full",
                    "amount": expense_amount,
                    "financing": False,
                },
                "description": "Pay the full amount from savings",
            },
            {
                "scenario_name": "Finance Over 12 Months",
                "scenario_type": "alternative",
                "parameters": {
                    "payment_type": "financed",
                    "amount": expense_amount,
                    "months": 12,
                    "interest_rate": 0.10,
                },
                "description": "Finance over 12 months",
            },
            {
                "scenario_name": "Finance Over 24 Months",
                "scenario_type": "alternative",
                "parameters": {
                    "payment_type": "financed",
                    "amount": expense_amount,
                    "months": 24,
                    "interest_rate": 0.12,
                },
                "description": "Finance over 24 months",
            },
            {
                "scenario_name": "Defer Purchase",
                "scenario_type": "optimistic",
                "parameters": {
                    "payment_type": "deferred",
                    "defer_months": 6,
                },
                "description": "Wait and save for purchase",
            },
        ]
        
        return scenarios
    
    async def _generate_goal_scenarios(
        self,
        params: Dict[str, Any],
        time_horizon_days: int,
    ) -> List[Dict[str, Any]]:
        """Generate goal timeline scenarios."""
        
        current_progress = params.get("current_progress", 0.5)  # 50%
        
        scenarios = [
            {
                "scenario_name": "Maintain Current Pace",
                "scenario_type": "baseline",
                "parameters": {
                    "progress_rate": 0.1,  # 10% per period
                    "strategy": "maintain",
                },
                "description": "Continue at current progress rate",
            },
            {
                "scenario_name": "Accelerate Progress",
                "scenario_type": "optimistic",
                "parameters": {
                    "progress_rate": 0.15,
                    "strategy": "accelerate",
                },
                "description": "Increase investment for faster progress",
            },
            {
                "scenario_name": "Reduced Effort",
                "scenario_type": "pessimistic",
                "parameters": {
                    "progress_rate": 0.05,
                    "strategy": "reduce",
                },
                "description": "Reduce effort/resources",
            },
        ]
        
        return scenarios
    
    async def _generate_generic_scenarios(
        self,
        params: Dict[str, Any],
        time_horizon_days: int,
    ) -> List[Dict[str, Any]]:
        """Generate generic scenarios."""
        
        return [
            {
                "scenario_name": "Baseline",
                "scenario_type": "baseline",
                "parameters": params,
                "description": "Current trajectory",
            },
            {
                "scenario_name": "Optimistic",
                "scenario_type": "optimistic",
                "parameters": {**params, "modifier": 1.2},
                "description": "Best case scenario",
            },
            {
                "scenario_name": "Pessimistic",
                "scenario_type": "pessimistic",
                "parameters": {**params, "modifier": 0.8},
                "description": "Worst case scenario",
            },
        ]


async def get_scenario_generator() -> ScenarioGenerator:
    """Get scenario generator instance."""
    return ScenarioGenerator()
