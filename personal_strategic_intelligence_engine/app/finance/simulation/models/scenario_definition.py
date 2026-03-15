"""Scenario Definition - defines a scenario type for simulation."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class ScenarioType(str, Enum):
    """Types of financial scenarios."""
    DEBT_PAYOFF = "debt_payoff"
    INCOME_SHOCK = "income_shock"
    EXPENSE_SHOCK = "expense_shock"
    LIQUIDITY_STRESS = "liquidity_stress"
    INVESTMENT_ALLOCATION = "investment_allocation"


@dataclass
class ScenarioDefinition:
    """Defines a scenario type for simulation."""
    scenario_id: str
    profile_id: int
    scenario_type: ScenarioType
    description: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scenario_id": self.scenario_id,
            "profile_id": self.profile_id,
            "scenario_type": self.scenario_type.value,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def create(
        cls,
        profile_id: int,
        scenario_type: ScenarioType,
        description: str,
    ) -> "ScenarioDefinition":
        """Create a new scenario definition."""
        import uuid
        return cls(
            scenario_id=str(uuid.uuid4()),
            profile_id=profile_id,
            scenario_type=scenario_type,
            description=description,
        )
