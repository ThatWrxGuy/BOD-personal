"""Approval policy controller - central orchestration."""
import logging
from typing import Any, Dict, List, Optional

from app.approval_policy.approval_policy_models import (
    ApprovalTierLevel,
    AutoExecutionEligibility,
    PolicyTransitionEvent,
    TierEligibility,
    AUTO_EXECUTION_ENABLED,
)
from app.approval_policy.approval_tier_classifier import get_approval_tier_classifier
from app.approval_policy.auto_execution_guard import get_auto_execution_guard
from app.approval_policy.tier_registry import get_tier_registry
from app.approval_policy.policy_transition_analyzer import get_policy_transition_analyzer

logger = logging.getLogger(__name__)


class ApprovalPolicyController:
    """Central orchestration for approval policy."""

    def __init__(self):
        self.classifier = get_approval_tier_classifier()
        self.guard = get_auto_execution_guard()
        self.registry = get_tier_registry()
        self.transition_analyzer = get_policy_transition_analyzer()

    def classify_tier(
        self,
        action_type: str,
        domain: str = "",
        reliability_score: Optional[float] = None,
        execution_count: int = 0,
        success_rate: float = 0.0,
        confidence: float = 0.0,
        risk_score: float = 0.0,
    ) -> TierEligibility:
        """Classify action into approval tier."""
        
        return self.classifier.classify(
            action_type=action_type,
            domain=domain,
            reliability_score=reliability_score,
            execution_count=execution_count,
            success_rate=success_rate,
            confidence=confidence,
            risk_score=risk_score,
        )

    def check_auto_execution(
        self,
        action_type: str,
        domain: str = "",
        reliability_score: Optional[float] = None,
        execution_count: int = 0,
        success_rate: float = 0.0,
        confidence: float = 0.0,
        risk_score: float = 0.0,
        doctrine_aligned: bool = True,
    ) -> AutoExecutionEligibility:
        """Check if action is eligible for auto-execution."""
        
        return self.guard.check_eligibility(
            action_type=action_type,
            domain=domain,
            reliability_score=reliability_score,
            execution_count=execution_count,
            success_rate=success_rate,
            confidence=confidence,
            risk_score=risk_score,
            doctrine_aligned=doctrine_aligned,
        )

    def analyze_transition(
        self,
        action_type: str,
        domain: str,
        current_tier: ApprovalTierLevel,
        reliability_score: Optional[float] = None,
        execution_count: int = 0,
        success_rate: float = 0.0,
    ) -> PolicyTransitionEvent:
        """Analyze potential tier transition."""
        
        return self.transition_analyzer.analyze(
            action_type=action_type,
            domain=domain,
            current_tier=current_tier,
            reliability_score=reliability_score,
            execution_count=execution_count,
            success_rate=success_rate,
        )

    def register_tier(
        self,
        action_type: str,
        domain: str,
        tier: ApprovalTierLevel,
        justification: str = "",
        factors: Optional[List[str]] = None,
    ):
        """Register tier assignment in registry."""
        
        return self.registry.register(
            action_type=action_type,
            domain=domain,
            tier=tier,
            justification=justification,
            factors=factors,
        )

    def get_tier_info(self, tier: ApprovalTierLevel) -> dict:
        """Get information about a tier."""
        
        from app.approval_policy.approval_policy_models import DEFAULT_TIERS
        
        tier_info = DEFAULT_TIERS.get(tier, {})
        
        return {
            "tier": tier.value,
            "name": tier_info.name if tier_info else "",
            "description": tier_info.description if tier_info else "",
            "requires_manual_approval": tier_info.requires_manual_approval if tier_info else True,
            "auto_execution_allowed": tier_info.auto_execution_allowed if tier_info else False,
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get policy statistics."""
        
        return {
            "auto_execution_enabled": AUTO_EXECUTION_ENABLED,
            "tier_registry": self.registry.get_statistics(),
            "thresholds": self.guard.thresholds.get_all(),
        }


# Global controller instance
_controller: Optional["ApprovalPolicyController"] = None


def get_approval_policy_controller() -> ApprovalPolicyController:
    """Get the global approval policy controller instance."""
    global _controller
    if _controller is None:
        _controller = ApprovalPolicyController()
    return _controller
