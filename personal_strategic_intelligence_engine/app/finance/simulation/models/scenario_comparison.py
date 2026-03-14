"""Scenario Comparison - compares two scenario results."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class ScenarioComparison:
    """Compares two scenario results."""
    comparison_id: str
    base_scenario_id: str
    comparison_scenario_id: str
    
    # Delta values (comparison - base)
    net_worth_delta: float = 0.0
    liquidity_delta: float = 0.0
    debt_delta: float = 0.0
    interest_delta: float = 0.0
    survival_months_delta: float = 0.0
    
    # Percentage changes
    net_worth_change_pct: float = 0.0
    liquidity_change_pct: float = 0.0
    
    # Risk comparison
    risk_delta: str = ""  # "improved", "worsened", "unchanged"
    
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "comparison_id": self.comparison_id,
            "base_scenario_id": self.base_scenario_id,
            "comparison_scenario_id": self.comparison_scenario_id,
            "net_worth_delta": self.net_worth_delta,
            "liquidity_delta": self.liquidity_delta,
            "debt_delta": self.debt_delta,
            "interest_delta": self.interest_delta,
            "survival_months_delta": self.survival_months_delta,
            "net_worth_change_pct": self.net_worth_change_pct,
            "liquidity_change_pct": self.liquidity_change_pct,
            "risk_delta": self.risk_delta,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def create(
        cls,
        base_scenario_id: str,
        comparison_scenario_id: str,
        base_result: Any,
        comparison_result: Any,
    ) -> "ScenarioComparison":
        """Create a comparison between two scenario results."""
        import uuid
        
        # Calculate deltas
        net_worth_delta = comparison_result.projected_net_worth - base_result.projected_net_worth
        liquidity_delta = comparison_result.projected_liquidity - base_result.projected_liquidity
        debt_delta = comparison_result.projected_debt_balance - base_result.projected_debt_balance
        interest_delta = comparison_result.interest_paid_total - base_result.interest_paid_total
        survival_months_delta = comparison_result.survival_months - base_result.survival_months
        
        # Calculate percentage changes
        if base_result.projected_net_worth != 0:
            net_worth_change_pct = (net_worth_delta / abs(base_result.projected_net_worth)) * 100
        else:
            net_worth_change_pct = 0.0
            
        if base_result.projected_liquidity != 0:
            liquidity_change_pct = (liquidity_delta / abs(base_result.projected_liquidity)) * 100
        else:
            liquidity_change_pct = 0.0
        
        # Determine risk change
        risk_order = {"low": 1, "moderate": 2, "high": 3, "severe": 4}
        base_risk = risk_order.get(base_result.risk_classification, 2)
        comp_risk = risk_order.get(comparison_result.risk_classification, 2)
        
        if comp_risk < base_risk:
            risk_delta = "improved"
        elif comp_risk > base_risk:
            risk_delta = "worsened"
        else:
            risk_delta = "unchanged"
        
        return cls(
            comparison_id=str(uuid.uuid4()),
            base_scenario_id=base_scenario_id,
            comparison_scenario_id=comparison_scenario_id,
            net_worth_delta=net_worth_delta,
            liquidity_delta=liquidity_delta,
            debt_delta=debt_delta,
            interest_delta=interest_delta,
            survival_months_delta=survival_months_delta,
            net_worth_change_pct=net_worth_change_pct,
            liquidity_change_pct=liquidity_change_pct,
            risk_delta=risk_delta,
        )
