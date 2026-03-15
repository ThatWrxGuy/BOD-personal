"""Approval policy advisor - recommends approval policy changes."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.execution_audit.outcome_models import (
    ApprovalPolicyLevel,
    ApprovalPolicyRecommendation,
    ExecutionReliabilityScore,
    ReversibilityLevel,
)
from app.execution_audit.execution_reliability_analyzer import get_reliability_analyzer
from app.execution_audit.reversibility_classifier import get_reversibility_classifier

logger = logging.getLogger(__name__)


class ApprovalPolicyAdvisor:
    """Recommends approval policy changes based on execution history."""

    # Thresholds for policy recommendations
    HIGH_RELIABILITY_THRESHOLD = 0.8
    MEDIUM_RELIABILITY_THRESHOLD = 0.6
    LOW_RELIABILITY_THRESHOLD = 0.4

    # Minimum executions before considering auto-approval
    MIN_EXECUTIONS_FOR_AUTO = 10
    MIN_EXECUTIONS_FOR_REVIEW = 5

    def __init__(self):
        self.reliability_analyzer = get_reliability_analyzer()
        self.reversibility_classifier = get_reversibility_classifier()

    def recommend_policy(
        self,
        action_type: str,
        domain: str,
    ) -> ApprovalPolicyRecommendation:
        """
        Recommend approval policy for an action type.
        
        Args:
            action_type: Type of action
            domain: Domain
            
        Returns:
            ApprovalPolicyRecommendation
        """
        # Get reliability score
        reliability = self.reliability_analyzer.get_score(action_type, domain)
        
        # Get reversibility
        reversibility = self.reversibility_classifier.classify(action_type, domain)
        
        # Determine current policy (simplified - would be from config)
        current_level = ApprovalPolicyLevel.MANUAL_ONLY
        
        # Determine recommended policy
        recommended_level = self._determine_policy(reliability, reversibility)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            recommended_level,
            reliability,
            reversibility,
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(reliability)
        
        recommendation = ApprovalPolicyRecommendation(
            action_type=action_type,
            domain=domain,
            current_level=current_level,
            recommended_level=recommended_level,
            confidence=confidence,
            reasoning=reasoning,
            supporting_evidence=self._get_evidence(reliability, reversibility),
            risk_assessment=self._assess_risk(recommended_level, reversibility),
        )
        
        logger.info(f"Generated policy recommendation for {action_type}: {recommended_level.value}")
        
        return recommendation

    def recommend_policies_for_all(self) -> List[ApprovalPolicyRecommendation]:
        """Generate policy recommendations for all tracked actions."""
        
        recommendations = []
        
        scores = self.reliability_analyzer.get_all_scores()
        
        for score in scores:
            rec = self.recommend_policy(score.action_type, score.domain)
            recommendations.append(rec)
        
        return recommendations

    def _determine_policy(
        self,
        reliability: Optional[ExecutionReliabilityScore],
        reversibility,
    ) -> ApprovalPolicyLevel:
        """Determine recommended policy level."""
        
        # Default to manual only
        if not reliability:
            return ApprovalPolicyLevel.MANUAL_ONLY
        
        # Check if we have enough data
        if reliability.total_executions < self.MIN_EXECUTIONS_FOR_REVIEW:
            return ApprovalPolicyLevel.MANUAL_ONLY
        
        # Check reversibility - never auto-approve irreversible
        if reversibility.reversibility == ReversibilityLevel.IRREVERSIBLE:
            return ApprovalPolicyLevel.MANUAL_ONLY
        
        # Check success rate
        success_rate = reliability.success_rate
        
        # High reliability + enough samples + reversible = eligible for auto
        if (success_rate >= self.HIGH_RELIABILITY_THRESHOLD and
            reliability.total_executions >= self.MIN_EXECUTIONS_FOR_AUTO and
            reversibility.reversibility == ReversibilityLevel.FULLY_REVERSIBLE):
            return ApprovalPolicyLevel.ELIGIBLE_FOR_AUTO
        
        # Medium reliability = require additional review
        if success_rate >= self.MEDIUM_RELIABILITY_THRESHOLD:
            return ApprovalPolicyLevel.REQUIRE_ADDITIONAL_REVIEW
        
        # Low reliability = manual only
        return ApprovalPolicyLevel.MANUAL_ONLY

    def _generate_reasoning(
        self,
        recommended_level: ApprovalPolicyLevel,
        reliability: Optional[ExecutionReliabilityScore],
        reversibility,
    ) -> str:
        """Generate reasoning for recommendation."""
        
        parts = []
        
        parts.append(f"Recommended: {recommended_level.value}")
        
        if reliability:
            parts.append(f"Success rate: {reliability.success_rate:.1%}")
            parts.append(f"Total executions: {reliability.total_executions}")
        
        parts.append(f"Reversibility: {reversibility.reversibility.value}")
        
        return "; ".join(parts)

    def _calculate_confidence(
        self,
        reliability: Optional[ExecutionReliabilityScore],
    ) -> float:
        """Calculate confidence in the recommendation."""
        
        if not reliability:
            return 0.1
        
        # Base confidence from sample size
        confidence = min(0.8, reliability.total_executions / 20)
        
        # Boost from stable trend
        if reliability.recent_trend == "stable":
            confidence += 0.1
        
        return min(0.95, confidence)

    def _get_evidence(
        self,
        reliability: Optional[ExecutionReliabilityScore],
        reversibility,
    ) -> List[str]:
        """Get supporting evidence for recommendation."""
        
        evidence = []
        
        if reliability:
            evidence.append(f"Historical success rate: {reliability.success_rate:.1%}")
            evidence.append(f"Recent trend: {reliability.recent_trend}")
        
        evidence.append(f"Reversibility: {reversibility.reversibility.value}")
        
        return evidence

    def _assess_risk(
        self,
        policy_level: ApprovalPolicyLevel,
        reversibility,
    ) -> str:
        """Assess risk of the recommended policy."""
        
        if policy_level == ApprovalPolicyLevel.ELIGIBLE_FOR_AUTO:
            if reversibility.reversibility == ReversibilityLevel.FULLY_REVERSIBLE:
                return "Low - fully reversible actions with high success rate"
            return "Medium - auto-approved despite partial reversibility"
        
        if policy_level == ApprovalPolicyLevel.REQUIRE_ADDITIONAL_REVIEW:
            return "Medium - additional review provides safety margin"
        
        return "Low - manual approval ensures human oversight"


# Global advisor instance
_advisor: Optional["ApprovalPolicyAdvisor"] = None


def get_approval_policy_advisor() -> ApprovalPolicyAdvisor:
    """Get the global approval policy advisor instance."""
    global _advisor
    if _advisor is None:
        _advisor = ApprovalPolicyAdvisor()
    return _advisor
