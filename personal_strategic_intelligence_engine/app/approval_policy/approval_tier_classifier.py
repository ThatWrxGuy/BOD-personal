"""Approval tier classifier - assigns actions to approval tiers."""
import logging
from typing import Any, Dict, Optional

from app.approval_policy.approval_policy_models import (
    ApprovalTierLevel,
    ApprovalPolicyRule,
    TierEligibility,
    DEFAULT_TIERS,
)
from app.approval_policy.policy_thresholds import get_policy_thresholds
from app.execution_audit.reversibility_classifier import get_reversibility_classifier

logger = logging.getLogger(__name__)


class ApprovalTierClassifier:
    """Assigns actions to approval tiers based on characteristics."""

    # Default tier assignments by action type
    DEFAULT_ASSIGNMENTS = {
        # Tier 0 - Manual Only (high risk / irreversible)
        "allocate_resource": ApprovalTierLevel.TIER_0_MANUAL_ONLY,
        "modify_config": ApprovalTierLevel.TIER_0_MANUAL_ONLY,
        
        # Tier 1 - Manual Fast-Path (reversible, lower risk)
        "adjust_priority": ApprovalTierLevel.TIER_1_MANUAL_FAST_PATH,
        "update_parameter": ApprovalTierLevel.TIER_1_MANUAL_FAST_PATH,
        "adjust_threshold": ApprovalTierLevel.TIER_1_MANUAL_FAST_PATH,
        
        # Tier 2 - Conditional Auto (reliable, reversible)
        # (Assigned based on historical data)
        
        # Tier 3 - System Safe Auto (informational, no side effects)
        "generate_insight": ApprovalTierLevel.TIER_3_SYSTEM_SAFE_AUTO,
        "create_reminder": ApprovalTierLevel.TIER_3_SYSTEM_SAFE_AUTO,
    }

    def __init__(self):
        self.thresholds = get_policy_thresholds()
        self.reversibility_classifier = get_reversibility_classifier()
        self._custom_assignments: Dict[str, ApprovalTierLevel] = {}

    def classify(
        self,
        action_type: str,
        domain: str = "",
        reliability_score: Optional[float] = None,
        execution_count: int = 0,
        success_rate: float = 0.0,
        confidence: float = 0.0,
        risk_score: float = 0.0,
    ) -> TierEligibility:
        """
        Classify an action into an approval tier.
        
        Args:
            action_type: Type of action
            domain: Domain
            reliability_score: Historical reliability score (0-1)
            execution_count: Number of executions
            success_rate: Success rate (0-1)
            confidence: Confidence level (0-1)
            risk_score: Risk level (0-1)
            
        Returns:
            TierEligibility with tier assignment
        """
        # Check custom assignments first
        if action_type in self._custom_assignments:
            tier = self._custom_assignments[action_type]
        elif action_type in self.DEFAULT_ASSIGNMENTS:
            tier = self.DEFAULT_ASSIGNMENTS[action_type]
        else:
            # Default to tier 0 for unknown actions
            tier = ApprovalTierLevel.TIER_0_MANUAL_ONLY
        
        # Check eligibility for auto tiers
        eligible_for_auto, status, blockers = self._check_auto_eligibility(
            action_type=action_type,
            domain=domain,
            reliability_score=reliability_score,
            execution_count=execution_count,
            success_rate=success_rate,
            confidence=confidence,
            risk_score=risk_score,
            current_tier=tier,
        )
        
        # Get reversibility
        reversibility = self.reversibility_classifier.classify(action_type, domain)
        
        eligibility = TierEligibility(
            action_type=action_type,
            domain=domain,
            current_tier=tier,
            eligible_for_auto=eligible_for_auto,
            eligibility_status=status,
            reliability_score=reliability_score,
            reversibility_level=reversibility.reversibility.value,
            execution_count=execution_count,
            success_rate=success_rate,
            confidence=confidence,
            risk_score=risk_score,
            meets_threshold=eligible_for_auto,
            blockers=blockers,
        )
        
        logger.info(f"Classified {action_type}: tier={tier.value}, auto_eligible={eligible_for_auto}")
        
        return eligibility

    def _check_auto_eligibility(
        self,
        action_type: str,
        domain: str,
        reliability_score: Optional[float],
        execution_count: int,
        success_rate: float,
        confidence: float,
        risk_score: float,
        current_tier: ApprovalTierLevel,
    ) -> tuple:
        """
        Check if action is eligible for auto-execution tier.
        
        Returns:
            (eligible, status, blockers)
        """
        from app.approval_policy.approval_policy_models import EligibilityStatus
        
        blockers = []
        
        # Check reversibility
        reversibility = self.reversibility_classifier.classify(action_type, domain)
        is_reversible = reversibility.reversibility.value in ["fully_reversible"]
        
        if not is_reversible:
            blockers.append("Action is not fully reversible")
        
        # Check thresholds
        meets_requirements, requirement_blockers = self.thresholds.meets_auto_eligibility(
            execution_count=execution_count,
            success_rate=success_rate,
            confidence=confidence,
            risk_score=risk_score,
        )
        
        blockers.extend(requirement_blockers)
        
        # Determine status
        if execution_count < self.thresholds.min_execution_samples:
            status = EligibilityStatus.INSUFFICIENT_DATA
            return False, status, blockers
        elif not is_reversible:
            status = EligibilityStatus.NOT_ELIGIBLE
            return False, status, blockers
        elif not meets_requirements:
            status = EligibilityStatus.NOT_ELIGIBLE
            return False, status, blockers
        else:
            status = EligibilityStatus.ELIGIBLE
            return True, status, blockers

    def assign_tier(self, action_type: str, tier: ApprovalTierLevel):
        """Assign a custom tier to an action type."""
        self._custom_assignments[action_type] = tier
        logger.info(f"Assigned {action_type} to tier {tier.value}")

    def get_tier(self, action_type: str) -> ApprovalTierLevel:
        """Get the tier for an action type."""
        if action_type in self._custom_assignments:
            return self._custom_assignments[action_type]
        return self.DEFAULT_ASSIGNMENTS.get(action_type, ApprovalTierLevel.TIER_0_MANUAL_ONLY)

    def get_tier_info(self, tier: ApprovalTierLevel) -> dict:
        """Get information about a tier."""
        return DEFAULT_TIERS.get(tier, {})


# Global classifier instance
_classifier: Optional["ApprovalTierClassifier"] = None


def get_approval_tier_classifier() -> ApprovalTierClassifier:
    """Get the global approval tier classifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = ApprovalTierClassifier()
    return _classifier
