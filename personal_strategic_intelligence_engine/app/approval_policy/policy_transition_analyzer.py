"""Policy transition analyzer - monitors tier transitions."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.approval_policy.approval_policy_models import (
    ApprovalTierLevel,
    PolicyTransitionEvent,
    PolicyTransitionType,
    DEFAULT_TIERS,
)
from app.approval_policy.policy_thresholds import get_policy_thresholds

logger = logging.getLogger(__name__)


class PolicyTransitionAnalyzer:
    """Monitors and analyzes policy tier transitions."""

    def __init__(self):
        self.thresholds = get_policy_thresholds()
        self._transition_history: List[PolicyTransitionEvent] = []

    def analyze(
        self,
        action_type: str,
        domain: str,
        current_tier: ApprovalTierLevel,
        reliability_score: Optional[float] = None,
        execution_count: int = 0,
        success_rate: float = 0.0,
    ) -> PolicyTransitionEvent:
        """
        Analyze whether a tier transition should occur.
        
        Args:
            action_type: Type of action
            domain: Domain
            current_tier: Current tier level
            reliability_score: Historical reliability
            execution_count: Number of executions
            success_rate: Success rate
            
        Returns:
            PolicyTransitionEvent with transition analysis
        """
        # Determine recommended tier
        recommended_tier = self._determine_recommended_tier(
            action_type=action_type,
            reliability_score=reliability_score,
            execution_count=execution_count,
            success_rate=success_rate,
        )
        
        # Determine transition type
        if recommended_tier == current_tier:
            transition_type = PolicyTransitionType.NO_CHANGE
        elif self._tier_value(recommended_tier) > self._tier_value(current_tier):
            transition_type = PolicyTransitionType.UPGRADE
        else:
            transition_type = PolicyTransitionType.DOWNGRADE
        
        # Build transition event
        event = PolicyTransitionEvent(
            action_type=action_type,
            domain=domain,
            from_tier=current_tier,
            to_tier=recommended_tier,
            transition_type=transition_type,
            trigger=self._get_trigger(transition_type, success_rate, execution_count),
            details=self._get_details(transition_type, recommended_tier, success_rate, execution_count),
        )
        
        # Store in history
        self._transition_history.append(event)
        
        logger.info(f"Transition analysis for {action_type}: {current_tier.value} -> {recommended_tier.value}")
        
        return event

    def _determine_recommended_tier(
        self,
        action_type: str,
        reliability_score: Optional[float],
        execution_count: int,
        success_rate: float,
    ) -> ApprovalTierLevel:
        """Determine recommended tier based on metrics."""
        
        # Check for Tier 3 (system-safe auto)
        if action_type in ["generate_insight", "create_reminder"]:
            return ApprovalTierLevel.TIER_3_SYSTEM_SAFE_AUTO
        
        # Check for Tier 2 (conditional auto)
        if (execution_count >= self.thresholds.min_execution_samples and
            success_rate >= self.thresholds.min_success_rate):
            return ApprovalTierLevel.TIER_2_CONDITIONAL_AUTO
        
        # Check for Tier 1 (manual fast-path)
        if (execution_count >= self.thresholds.fast_path_min_samples and
            success_rate >= self.thresholds.fast_path_min_success_rate):
            return ApprovalTierLevel.TIER_1_MANUAL_FAST_PATH
        
        # Default to Tier 0
        return ApprovalTierLevel.TIER_0_MANUAL_ONLY

    def _tier_value(self, tier: ApprovalTierLevel) -> int:
        """Get numeric value for tier (higher = more permissive)."""
        tier_values = {
            ApprovalTierLevel.TIER_0_MANUAL_ONLY: 0,
            ApprovalTierLevel.TIER_1_MANUAL_FAST_PATH: 1,
            ApprovalTierLevel.TIER_2_CONDITIONAL_AUTO: 2,
            ApprovalTierLevel.TIER_3_SYSTEM_SAFE_AUTO: 3,
        }
        return tier_values.get(tier, 0)

    def _get_trigger(self, transition_type: PolicyTransitionType, success_rate: float, execution_count: int) -> str:
        """Get trigger description for transition."""
        
        if transition_type == PolicyTransitionType.UPGRADE:
            return f"Reliability improved: {success_rate:.1%} success rate with {execution_count} executions"
        elif transition_type == PolicyTransitionType.DOWNGRADE:
            return f"Reliability degradation: {success_rate:.1%} success rate"
        else:
            return "No significant change in metrics"

    def _get_details(
        self,
        transition_type: PolicyTransitionType,
        tier: ApprovalTierLevel,
        success_rate: float,
        execution_count: int,
    ) -> str:
        """Get detailed description."""
        
        tier_name = DEFAULT_TIERS.get(tier, {}).name or tier.value
        
        if transition_type == PolicyTransitionType.UPGRADE:
            return f"Recommending upgrade to {tier_name} based on {execution_count} executions and {success_rate:.1%} success rate"
        elif transition_type == PolicyTransitionType.DOWNGRADE:
            return f"Recommending downgrade to {tier_name} due to reliability concerns"
        else:
            return f"Remaining at {tier_name}"

    def get_upgrade_candidates(self) -> List[PolicyTransitionEvent]:
        """Get all potential upgrades."""
        return [
            e for e in self._transition_history
            if e.transition_type == PolicyTransitionType.UPGRADE
        ]

    def get_downgrade_warnings(self) -> List[PolicyTransitionEvent]:
        """Get all potential downgrades."""
        return [
            e for e in self._transition_history
            if e.transition_type == PolicyTransitionType.DOWNGRADE
        ]

    def get_history(self, limit: int = 100) -> List[PolicyTransitionEvent]:
        """Get transition history."""
        return self._transition_history[-limit:]


# Global analyzer instance
_analyzer: Optional["PolicyTransitionAnalyzer"] = None


def get_policy_transition_analyzer() -> PolicyTransitionAnalyzer:
    """Get the global policy transition analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = PolicyTransitionAnalyzer()
    return _analyzer
