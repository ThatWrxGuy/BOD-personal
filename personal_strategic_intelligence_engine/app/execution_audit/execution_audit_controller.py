"""Execution audit controller - central orchestration for audit subsystem."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.execution_audit.outcome_models import (
    ApprovalPolicyRecommendation,
    ExecutionOutcomeSnapshot,
    OutcomeEvaluation,
    ExecutionReliabilityScore,
    ReversibilityClassification,
)
from app.execution_audit.outcome_tracker import get_outcome_tracker
from app.execution_audit.outcome_evaluator import get_outcome_evaluator
from app.execution_audit.execution_reliability_analyzer import get_reliability_analyzer
from app.execution_audit.reversibility_classifier import get_reversibility_classifier
from app.execution_audit.approval_policy_advisor import get_approval_policy_advisor

logger = logging.getLogger(__name__)


class ExecutionAuditController:
    """Central orchestration for execution audit subsystem."""

    def __init__(self):
        self.tracker = get_outcome_tracker()
        self.evaluator = get_outcome_evaluator()
        self.reliability_analyzer = get_reliability_analyzer()
        self.reversibility_classifier = get_reversibility_classifier()
        self.policy_advisor = get_approval_policy_advisor()

    def capture_outcome(
        self,
        execution_id: str,
        recommendation_id: str,
        action_type: str,
        domain: str,
        pre_execution_state: Optional[Dict[str, Any]] = None,
        post_execution_state: Optional[Dict[str, Any]] = None,
        observed_signals: Optional[List[Dict[str, Any]]] = None,
        confidence: float = 0.5,
        error_message: Optional[str] = None,
    ) -> ExecutionOutcomeSnapshot:
        """Capture an execution outcome."""
        
        return self.tracker.capture_outcome(
            execution_id=execution_id,
            recommendation_id=recommendation_id,
            action_type=action_type,
            domain=domain,
            pre_execution_state=pre_execution_state,
            post_execution_state=post_execution_state,
            observed_signals=observed_signals,
            confidence=confidence,
            error_message=error_message,
        )

    def evaluate_outcome(
        self,
        snapshot_id: str,
    ) -> Optional[OutcomeEvaluation]:
        """Evaluate an outcome snapshot."""
        
        snapshot = self.tracker.get_snapshot(snapshot_id)
        
        if not snapshot:
            logger.warning(f"Snapshot not found: {snapshot_id}")
            return None
        
        return self.evaluator.evaluate(snapshot)

    def evaluate_all_outcomes(self) -> List[OutcomeEvaluation]:
        """Evaluate all tracked outcomes."""
        
        snapshots = self.tracker.get_recent_snapshots()
        
        evaluations = []
        for snapshot in snapshots:
            eval_result = self.evaluator.evaluate(snapshot)
            evaluations.append(eval_result)
        
        return evaluations

    def classify_reversibility(
        self,
        action_type: str,
        domain: str = "",
    ) -> ReversibilityClassification:
        """Classify reversibility of an action."""
        
        return self.reversibility_classifier.classify(action_type, domain)

    def analyze_reliability(self) -> List[ExecutionReliabilityScore]:
        """Analyze execution reliability."""
        
        snapshots = self.tracker.get_recent_snapshots()
        
        return self.reliability_analyzer.analyze(snapshots)

    def get_reliability_score(
        self,
        action_type: str,
        domain: str,
    ) -> Optional[ExecutionReliabilityScore]:
        """Get reliability score for an action."""
        
        return self.reliability_analyzer.get_score(action_type, domain)

    def recommend_policy(
        self,
        action_type: str,
        domain: str,
    ) -> ApprovalPolicyRecommendation:
        """Recommend approval policy for an action."""
        
        return self.policy_advisor.recommend_policy(action_type, domain)

    def recommend_all_policies(self) -> List[ApprovalPolicyRecommendation]:
        """Recommend policies for all tracked actions."""
        
        return self.policy_advisor.recommend_policies_for_all()

    def get_statistics(self) -> Dict[str, Any]:
        """Get audit subsystem statistics."""
        
        return {
            "tracker": self.tracker.get_statistics(),
            "reliability": self.reliability_analyzer.get_statistics(),
        }

    def get_outcome_summary(self) -> Dict[str, Any]:
        """Get summary of outcomes."""
        
        snapshots = self.tracker.get_recent_snapshots()
        
        if not snapshots:
            return {
                "total": 0,
                "by_domain": {},
                "by_action_type": {},
            }
        
        by_domain = {}
        by_action_type = {}
        
        for s in snapshots:
            by_domain[s.domain] = by_domain.get(s.domain, 0) + 1
            by_action_type[s.action_type] = by_action_type.get(s.action_type, 0) + 1
        
        return {
            "total": len(snapshots),
            "by_domain": by_domain,
            "by_action_type": by_action_type,
        }


# Global controller instance
_controller: Optional["ExecutionAuditController"] = None


def get_execution_audit_controller() -> ExecutionAuditController:
    """Get the global execution audit controller instance."""
    global _controller
    if _controller is None:
        _controller = ExecutionAuditController()
    return _controller
