"""Scenario Parameters - defines adjustable parameters for simulations."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

from app.finance.simulation.models.scenario_definition import ScenarioType


@dataclass
class ScenarioParameters:
    """Defines adjustable parameters for simulations."""
    parameters_id: str
    scenario_id: str
    
    # Debt payoff parameters
    extra_payment_amount: Optional[float] = None
    extra_payment_frequency: str = "monthly"  # monthly, biweekly
    
    # Income shock parameters
    income_reduction_percentage: Optional[float] = None
    income_shock_duration_months: Optional[int] = None
    
    # Expense shock parameters
    expense_increase_amount: Optional[float] = None
    expense_shock_type: Optional[str] = None  # one_time, recurring
    
    # Market/economic parameters
    market_return_rate: Optional[float] = None  # Annual return rate
    inflation_rate: Optional[float] = None  # Annual inflation rate
    
    # Simulation parameters
    simulation_horizon_months: int = 60  # Default 5 years
    confidence_level: float = 0.90
    
    # Allocation parameters (for investment_allocation scenario)
    target_allocation: Optional[Dict[str, float]] = None  # e.g., {"stocks": 0.6, "bonds": 0.4}
    current_allocation: Optional[Dict[str, float]] = None
    
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "parameters_id": self.parameters_id,
            "scenario_id": self.scenario_id,
            "extra_payment_amount": self.extra_payment_amount,
            "extra_payment_frequency": self.extra_payment_frequency,
            "income_reduction_percentage": self.income_reduction_percentage,
            "income_shock_duration_months": self.income_shock_duration_months,
            "expense_increase_amount": self.expense_increase_amount,
            "expense_shock_type": self.expense_shock_type,
            "market_return_rate": self.market_return_rate,
            "inflation_rate": self.inflation_rate,
            "simulation_horizon_months": self.simulation_horizon_months,
            "confidence_level": self.confidence_level,
            "target_allocation": self.target_allocation,
            "current_allocation": self.current_allocation,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def create(
        cls,
        scenario_id: str,
        extra_payment_amount: Optional[float] = None,
        extra_payment_frequency: str = "monthly",
        income_reduction_percentage: Optional[float] = None,
        income_shock_duration_months: Optional[int] = None,
        expense_increase_amount: Optional[float] = None,
        expense_shock_type: Optional[str] = None,
        market_return_rate: Optional[float] = None,
        inflation_rate: Optional[float] = None,
        simulation_horizon_months: int = 60,
        confidence_level: float = 0.90,
        target_allocation: Optional[Dict[str, float]] = None,
        current_allocation: Optional[Dict[str, float]] = None,
    ) -> "ScenarioParameters":
        """Create new scenario parameters."""
        import uuid
        return cls(
            parameters_id=str(uuid.uuid4()),
            scenario_id=scenario_id,
            extra_payment_amount=extra_payment_amount,
            extra_payment_frequency=extra_payment_frequency,
            income_reduction_percentage=income_reduction_percentage,
            income_shock_duration_months=income_shock_duration_months,
            expense_increase_amount=expense_increase_amount,
            expense_shock_type=expense_shock_type,
            market_return_rate=market_return_rate,
            inflation_rate=inflation_rate,
            simulation_horizon_months=simulation_horizon_months,
            confidence_level=confidence_level,
            target_allocation=target_allocation,
            current_allocation=current_allocation,
        )
