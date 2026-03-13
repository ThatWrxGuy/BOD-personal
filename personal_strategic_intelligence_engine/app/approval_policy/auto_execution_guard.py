"""Auto-execution guard - prevents unsafe auto-execution."""
import logging
from typing import Any, Dict, Optional

from app.approval_policy.approval_policy_models import (
    ApprovalTierLevel,
    AutoExecutionEligibility,
    EligibilityStatus,
    AUTO_EXECUTION_ENABLED,
)
from app.approval_policy.approval_tier_classifier import get_approval_tier_classifier
from app.approval_policy.policy_thresholds import get_policy_thresholds

logger = logging.getLogger(__name__)


class AutoExecutionGuard:
    """Prevents unsafe auto-execution."""

    def __init__(self):
        self.classifier = get_approval_tier_classifier()
        self.thresholds = get_policy_thresholds()

    def check_eligibility(
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
        """
        Check if action is eligible for auto-execution.
        
        Args:
            action_type: Type of action
            domain: Domain
            reliability_score: Historical reliability score
            execution_count: Number of executions
            success_rate: Success rate
            confidence: Confidence level
            risk_score: Risk level
            doctrine_aligned: Whether doctrine is aligned
            
        Returns:
            AutoExecutionEligibility with decision
        """
        # Safety: Check if auto-execution is enabled
        if not AUTO_EXECUTION_ENABLED:
            return self._create_ineligible(
                action_type=action_type,
                domain=domain,
                status=EligibilityStatus.NOT_ELIGIBLE,
                blockers=["Auto-execution is disabled by policy"],
            )
        
        # Get tier eligibility
        tier_eligibility = self.classifier.classify(
            action_type=action_type,
            domain=domain,
            reliability_score=reliability_score,
            execution_count=execution_count,
            success_rate=success_rate,
            confidence=confidence,
            risk_score=risk_score,
        )
        
        # Build blockers and requirements
        blockers = list(tier_eligibility.blockers)
        requirements_met = []
        
        # Check minimum samples
        meets_min_samples = execution_count >= self.thresholds.min_execution_samples
        if meets_min_samples:
            requirements_met.append(f"Min samples: {execution_count} >= {self.thresholds.min_execution_samples}")
        else:
            blockers.append(f"Insufficient samples: {execution_count} < {self.thresholds.min_execution_samples}")
        
        # Check success rate
        meets_success_rate = success_rate >= self.thresholds.min_success_rate
        if meets_success_rate:
            requirements_met.append(f"Success rate: {success_rate:.1%} >= {self.thresholds.min_success_rate:.1%}")
        else:
            blockers.append(f"Success rate too low: {success_rate:.1%} < {self.thresholds.min_success_rate:.1%}")
        
        # Check confidence
        meets_confidence = confidence >= self.thresholds.min_confidence
        if meets_confidence:
            requirements_met.append(f"Confidence: {confidence:.1%} >= {self.thresholds.min_confidence:.1%}")
        else:
            blockers.append(f"Confidence too low: {confidence:.1%} < {self.thresholds.min_confidence:.1%}")
        
        # Check risk threshold
        meets_risk_threshold = risk_score <= self.thresholds.max_risk_score
        if meets_risk_threshold:
            requirements_met.append(f"Risk OK: {risk_score:.1%} <= {self.thresholds.max_risk_score:.1%}")
        else:
            blockers.append(f"Risk too high: {risk_score:.1%} > {self.thresholds.max_risk_score:.1%}")
        
        # Check reversibility
        is_reversible = tier_eligibility.reversibility_level == "fully_reversible"
        if is_reversible:
            requirements_met.append("Action is fully reversible")
        else:
            blockers.append("Action is not fully reversible")
        
        # Check doctrine alignment
        if doctrine_aligned:
            requirements_met.append("Doctrine aligned")
        else:
            blockers.append("Doctrine not aligned")
        
        # Determine eligibility
        all_checks_pass = (
            meets_min_samples and
            meets_success_rate and
            meets_confidence and
            meets_risk_threshold and
            is_reversible and
            doctrine_aligned
        )
        
        # Get tier
        tier = tier_eligibility.current_tier
        
        # Only Tier 2 and Tier 3 can auto-execute
        if tier not in [
            ApprovalTierLevel.TIER_2_CONDITIONAL_AUTO,
            ApprovalTierLevel.TIER_3_SYSTEM_SAFE_AUTO,
        ]:
            blockers.append(f"Action is in {tier.value} which does not allow auto-execution")
            all_checks_pass = False
        
        # Calculate confidence in decision
        decision_confidence = self._calculate_decision_confidence(
            meets_min_samples=meets_min_samples,
            meets_success_rate=meets_success_rate,
            meets_confidence=meets_confidence,
            meets_risk_threshold=meets_risk_threshold,
            is_reversible=is_reversible,
            doctrine_aligned=doctrine_aligned,
        )
        
        status = EligibilityStatus.ELIGIBLE if all_checks_pass else EligibilityStatus.NOT_ELIGIBLE
        
        eligibility = AutoExecutionEligibility(
            action_type=action_type,
            domain=domain,
            allowed=all_checks_pass,
            status=status,
            meets_min_samples=meets_min_samples,
            meets_success_rate=meets_success_rate,
            meets_confidence=meets_confidence,
            meets_risk_threshold=meets_risk_threshold,
            is_reversible=is_reversible,
            is_doctrine_aligned=doctrine_aligned,
            blockers=blockers,
            requirements_met=requirements_met,
            decision_confidence=decision_confidence,
        )
        
        logger.info(f"Auto-execution eligibility for {action_type}: allowed={all_checks_pass}")
        
        return eligibility

    def _create_ineligible(
        self,
        action_type: str,
        domain: str,
        status: EligibilityStatus,
        blockers: list,
    ) -> AutoExecutionEligibility:
        """Create an ineligible result."""
        
        return AutoExecutionEligibility(
            action_type=action_type,
            domain=domain,
            allowed=False,
            status=status,
            blockers=blockers,
            decision_confidence=1.0,
        )

    def _calculate_decision_confidence(
        self,
        meets_min_samples: bool,
        meets_success_rate: bool,
        meets_confidence: bool,
        meets_risk_threshold: bool,
        is_reversible: bool,
        doctrine_aligned: bool,
    ) -> float:
        """Calculate confidence in the eligibility decision."""
        
        confidence = 0.5  # Base
        
        # Add factors
        if meets_min_samples:
            confidence += 0.1
        if meets_success_rate:
            confidence += 0.1
        if meets_confidence:
            confidence += 0.1
        if meets_risk_threshold:
            confidence += 0.1
        if is_reversible:
            confidence += 0.05
        if doctrine_aligned:
            confidence += 0.05
        
        return min(0.95, confidence)


# Global guard instance
_guard: Optional["AutoExecutionGuard"] = None


def get_auto_execution_guard() -> AutoExecutionGuard:
    """Get the global auto-execution guard instance."""
    global _guard
    if _guard is None:
        _guard = AutoExecutionGuard()
    return _guard
