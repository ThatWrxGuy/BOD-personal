"""Scenario Result - represents the output of a simulation run."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.finance.simulation.models.scenario_definition import ScenarioType


@dataclass
class ScenarioResult:
    """Represents the output of a simulation run."""
    result_id: str
    scenario_id: str
    profile_id: int
    scenario_type: ScenarioType
    
    # Projected values
    projected_net_worth: float
    projected_liquidity: float
    projected_debt_balance: float
    
    # Additional metrics
    interest_paid_total: float = 0.0
    interest_saved_vs_baseline: float = 0.0
    payoff_timeline_months: int = 0
    
    # Survival metrics
    survival_months: float = 0.0  # How long until money runs out
    minimum_liquidity: float = 0.0
    
    # Confidence
    confidence_score: float = 0.75
    
    # Timeline data (month-by-month projections)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    
    # Risk classification
    risk_classification: str = "moderate"  # low, moderate, high, severe
    
    simulation_timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "result_id": self.result_id,
            "scenario_id": self.scenario_id,
            "profile_id": self.profile_id,
            "scenario_type": self.scenario_type.value,
            "projected_net_worth": self.projected_net_worth,
            "projected_liquidity": self.projected_liquidity,
            "projected_debt_balance": self.projected_debt_balance,
            "interest_paid_total": self.interest_paid_total,
            "interest_saved_vs_baseline": self.interest_saved_vs_baseline,
            "payoff_timeline_months": self.payoff_timeline_months,
            "survival_months": self.survival_months,
            "minimum_liquidity": self.minimum_liquidity,
            "confidence_score": self.confidence_score,
            "risk_classification": self.risk_classification,
            "simulation_timestamp": self.simulation_timestamp.isoformat() if self.simulation_timestamp else None,
        }

    @classmethod
    def create(
        cls,
        scenario_id: str,
        profile_id: int,
        scenario_type: ScenarioType,
        projected_net_worth: float,
        projected_liquidity: float,
        projected_debt_balance: float,
        interest_paid_total: float = 0.0,
        interest_saved_vs_baseline: float = 0.0,
        payoff_timeline_months: int = 0,
        survival_months: float = 0.0,
        minimum_liquidity: float = 0.0,
        confidence_score: float = 0.75,
        timeline: Optional[List[Dict[str, Any]]] = None,
        risk_classification: str = "moderate",
    ) -> "ScenarioResult":
        """Create a new scenario result."""
        import uuid
        return cls(
            result_id=str(uuid.uuid4()),
            scenario_id=scenario_id,
            profile_id=profile_id,
            scenario_type=scenario_type,
            projected_net_worth=projected_net_worth,
            projected_liquidity=projected_liquidity,
            projected_debt_balance=projected_debt_balance,
            interest_paid_total=interest_paid_total,
            interest_saved_vs_baseline=interest_saved_vs_baseline,
            payoff_timeline_months=payoff_timeline_months,
            survival_months=survival_months,
            minimum_liquidity=minimum_liquidity,
            confidence_score=confidence_score,
            timeline=timeline or [],
            risk_classification=risk_classification,
        )
