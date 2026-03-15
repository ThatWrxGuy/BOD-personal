"""Financial Opportunity - represents a detected opportunity to improve financial condition."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class OpportunityType(str, Enum):
    """Types of financial opportunities."""
    ACCELERATED_DEBT_PAYOFF = "accelerated_debt_payoff"
    EXCESS_CASH_FLOW_INVESTMENT = "excess_cash_flow_investment"
    RESERVE_OPTIMIZATION = "reserve_optimization"
    ALLOCATION_REBALANCE = "allocation_rebalance"
    TAX_EFFICIENT_INVESTING = "tax_efficient_investing"
    DEBT_CONSOLIDATION = "debt_consolidation"
    HIGH_YIELD_SAVINGS = "high_yield_savings"


@dataclass
class FinancialOpportunity:
    """Represents a detected opportunity to improve financial condition."""
    opportunity_id: str
    profile_id: int
    opportunity_type: OpportunityType
    description: str
    trigger_metric: str
    trigger_value: Any
    expected_benefit: str
    detected_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "opportunity_id": self.opportunity_id,
            "profile_id": self.profile_id,
            "opportunity_type": self.opportunity_type.value,
            "description": self.description,
            "trigger_metric": self.trigger_metric,
            "trigger_value": self.trigger_value,
            "expected_benefit": self.expected_benefit,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
        }

    @classmethod
    def create(
        cls,
        profile_id: int,
        opportunity_type: OpportunityType,
        description: str,
        trigger_metric: str,
        trigger_value: Any,
        expected_benefit: str,
    ) -> "FinancialOpportunity":
        """Create a new financial opportunity."""
        import uuid
        return cls(
            opportunity_id=str(uuid.uuid4()),
            profile_id=profile_id,
            opportunity_type=opportunity_type,
            description=description,
            trigger_metric=trigger_metric,
            trigger_value=trigger_value,
            expected_benefit=expected_benefit,
        )
