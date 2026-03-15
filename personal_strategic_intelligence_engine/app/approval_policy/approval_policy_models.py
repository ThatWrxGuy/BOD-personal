"""Approval policy data models."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ApprovalTierLevel(str, Enum):
    """Approval tier levels."""
    TIER_0_MANUAL_ONLY = "tier_0_manual_only"
    TIER_1_MANUAL_FAST_PATH = "tier_1_manual_fast_path"
    TIER_2_CONDITIONAL_AUTO = "tier_2_conditional_auto"
    TIER_3_SYSTEM_SAFE_AUTO = "tier_3_system_safe_auto"


class EligibilityStatus(str, Enum):
    """Eligibility status for auto-execution."""
    ELIGIBLE = "eligible"
    NOT_ELIGIBLE = "not_eligible"
    PENDING = "pending"
    INSUFFICIENT_DATA = "insufficient_data"


class PolicyTransitionType(str, Enum):
    """Type of policy transition."""
    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"
    NO_CHANGE = "no_change"


class ApprovalTier(BaseModel):
    """Approval tier definition."""
    tier: ApprovalTierLevel
    name: str
    description: str
    requires_manual_approval: bool = True
    auto_execution_allowed: bool = False


class ApprovalPolicyRule(BaseModel):
    """Policy rule for approval tier."""
    rule_id: str = Field(default_factory=lambda: f"rule_{datetime.utcnow().timestamp()}")
    action_type: str
    domain: str
    
    # Tier assignment
    tier: ApprovalTierLevel
    
    # Justification
    justification: str = ""
    factors: List[str] = Field(default_factory=list)
    
    # Timestamps
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class TierEligibility(BaseModel):
    """Eligibility assessment for a tier."""
    action_type: str
    domain: str
    
    # Current tier
    current_tier: ApprovalTierLevel
    
    # Eligibility for auto-execution tier
    eligible_for_auto: bool = False
    eligibility_status: EligibilityStatus = EligibilityStatus.NOT_ELIGIBLE
    
    # Factors
    reliability_score: Optional[float] = None
    reversibility_level: Optional[str] = None
    execution_count: int = 0
    success_rate: float = 0.0
    confidence: float = 0.0
    risk_score: float = 0.0
    
    # Assessment
    meets_threshold: bool = False
    blockers: List[str] = Field(default_factory=list)


class AutoExecutionEligibility(BaseModel):
    """Eligibility for auto-execution."""
    action_type: str
    domain: str
    
    # Eligibility
    allowed: bool
    status: EligibilityStatus
    
    # Requirements check
    meets_min_samples: bool = False
    meets_success_rate: bool = False
    meets_confidence: bool = False
    meets_risk_threshold: bool = False
    is_reversible: bool = False
    is_doctrine_aligned: bool = False
    
    # Details
    blockers: List[str] = Field(default_factory=list)
    requirements_met: List[str] = Field(default_factory=list)
    
    # Confidence in decision
    decision_confidence: float = 0.0


class PolicyTransitionEvent(BaseModel):
    """Event for policy tier transitions."""
    event_id: str = Field(default_factory=lambda: f"transition_{datetime.utcnow().timestamp()}")
    action_type: str
    domain: str
    
    # Transition details
    from_tier: ApprovalTierLevel
    to_tier: ApprovalTierLevel
    transition_type: PolicyTransitionType
    
    # Trigger
    trigger: str = ""
    details: str = ""
    
    # Status
    approved: bool = False
    auto_approved: bool = False
    
    # Timing
    occurred_at: datetime = Field(default_factory=datetime.utcnow)


# Default tier definitions
DEFAULT_TIERS = {
    ApprovalTierLevel.TIER_0_MANUAL_ONLY: ApprovalTier(
        tier=ApprovalTierLevel.TIER_0_MANUAL_ONLY,
        name="Manual Only",
        description="Irreversible or high-risk actions requiring manual approval",
        requires_manual_approval=True,
        auto_execution_allowed=False,
    ),
    ApprovalTierLevel.TIER_1_MANUAL_FAST_PATH: ApprovalTier(
        tier=ApprovalTierLevel.TIER_1_MANUAL_FAST_PATH,
        name="Manual Fast-Path",
        description="Reversible actions with simplified approval",
        requires_manual_approval=True,
        auto_execution_allowed=False,
    ),
    ApprovalTierLevel.TIER_2_CONDITIONAL_AUTO: ApprovalTier(
        tier=ApprovalTierLevel.TIER_2_CONDITIONAL_AUTO,
        name="Conditional Auto-Execution",
        description="High-reliability reversible actions eligible for auto-execution",
        requires_manual_approval=False,
        auto_execution_allowed=True,
    ),
    ApprovalTierLevel.TIER_3_SYSTEM_SAFE_AUTO: ApprovalTier(
        tier=ApprovalTierLevel.TIER_3_SYSTEM_SAFE_AUTO,
        name="System-Safe Auto",
        description="Zero-side-effect informational actions",
        requires_manual_approval=False,
        auto_execution_allowed=True,
    ),
}


# Safety constant
AUTO_EXECUTION_ENABLED = False  # Disabled by default
