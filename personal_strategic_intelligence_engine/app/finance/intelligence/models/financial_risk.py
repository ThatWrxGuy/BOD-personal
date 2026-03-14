"""Financial Risk - represents a detected financial risk condition."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class RiskType(str, Enum):
    """Types of financial risks."""
    HIGH_INTEREST_DEBT = "high_interest_debt"
    LOW_LIQUIDITY = "low_liquidity"
    NEGATIVE_CASH_FLOW = "negative_cash_flow"
    HIGH_DEBT_TO_INCOME = "high_debt_to_income"
    ASSET_CONCENTRATION = "asset_concentration"
    VOLATILITY_EXPOSURE = "volatility_exposure"
    EMERGENCY_FUND_INSUFFICIENT = "emergency_fund_insufficient"
    CREDIT_UTILIZATION_HIGH = "credit_utilization_high"


class Severity(str, Enum):
    """Severity levels for risks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FinancialRisk:
    """Represents a detected financial risk condition."""
    risk_id: str
    profile_id: int
    risk_type: RiskType
    severity: Severity
    description: str
    trigger_metric: str
    trigger_value: Any
    recommended_mitigation: str
    detected_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "risk_id": self.risk_id,
            "profile_id": self.profile_id,
            "risk_type": self.risk_type.value,
            "severity": self.severity.value,
            "description": self.description,
            "trigger_metric": self.trigger_metric,
            "trigger_value": self.trigger_value,
            "recommended_mitigation": self.recommended_mitigation,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
        }

    @classmethod
    def create(
        cls,
        profile_id: int,
        risk_type: RiskType,
        severity: Severity,
        description: str,
        trigger_metric: str,
        trigger_value: Any,
        recommended_mitigation: str,
    ) -> "FinancialRisk":
        """Create a new financial risk."""
        import uuid
        return cls(
            risk_id=str(uuid.uuid4()),
            profile_id=profile_id,
            risk_type=risk_type,
            severity=severity,
            description=description,
            trigger_metric=trigger_metric,
            trigger_value=trigger_value,
            recommended_mitigation=recommended_mitigation,
        )
