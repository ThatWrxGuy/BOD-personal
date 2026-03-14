"""Financial Board Brief - board-ready financial intelligence report."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class FinancialStatus(str, Enum):
    """Financial status values."""
    STABLE = "stable"
    WATCH = "watch"
    AT_RISK = "at_risk"


class RiskLevel(str, Enum):
    """Risk level values."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class ConfidenceLevel(str, Enum):
    """Confidence level values."""
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"


@dataclass
class FinancialBoardBrief:
    """Represents a board-ready financial intelligence report."""
    brief_id: str
    profile_id: int
    snapshot_id: Optional[str] = None
    
    # Financial status
    financial_status: FinancialStatus = FinancialStatus.STABLE
    risk_level: RiskLevel = RiskLevel.LOW
    confidence_level: ConfidenceLevel = ConfidenceLevel.MODERATE
    
    # Key metrics
    net_worth: float = 0.0
    free_cash_flow: float = 0.0
    liquid_reserves: float = 0.0
    debt_exposure: float = 0.0
    
    # Intelligence
    top_risks: List[str] = field(default_factory=list)
    top_opportunities: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    
    # Scenario summary
    scenario_summary: Dict[str, Any] = field(default_factory=dict)
    
    generated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "brief_id": self.brief_id,
            "profile_id": self.profile_id,
            "snapshot_id": self.snapshot_id,
            "financial_status": self.financial_status.value,
            "risk_level": self.risk_level.value,
            "confidence_level": self.confidence_level.value,
            "net_worth": self.net_worth,
            "free_cash_flow": self.free_cash_flow,
            "liquid_reserves": self.liquid_reserves,
            "debt_exposure": self.debt_exposure,
            "top_risks": self.top_risks,
            "top_opportunities": self.top_opportunities,
            "recommended_actions": self.recommended_actions,
            "scenario_summary": self.scenario_summary,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
        }

    @classmethod
    def create(
        cls,
        profile_id: int,
        snapshot_id: Optional[str] = None,
        financial_status: FinancialStatus = FinancialStatus.STABLE,
        risk_level: RiskLevel = RiskLevel.LOW,
        confidence_level: ConfidenceLevel = ConfidenceLevel.MODERATE,
        net_worth: float = 0.0,
        free_cash_flow: float = 0.0,
        liquid_reserves: float = 0.0,
        debt_exposure: float = 0.0,
        top_risks: Optional[List[str]] = None,
        top_opportunities: Optional[List[str]] = None,
        recommended_actions: Optional[List[str]] = None,
        scenario_summary: Optional[Dict[str, Any]] = None,
    ) -> "FinancialBoardBrief":
        """Create a new financial board brief."""
        import uuid
        return cls(
            brief_id=str(uuid.uuid4()),
            profile_id=profile_id,
            snapshot_id=snapshot_id,
            financial_status=financial_status,
            risk_level=risk_level,
            confidence_level=confidence_level,
            net_worth=net_worth,
            free_cash_flow=free_cash_flow,
            liquid_reserves=liquid_reserves,
            debt_exposure=debt_exposure,
            top_risks=top_risks or [],
            top_opportunities=top_opportunities or [],
            recommended_actions=recommended_actions or [],
            scenario_summary=scenario_summary or {},
        )
