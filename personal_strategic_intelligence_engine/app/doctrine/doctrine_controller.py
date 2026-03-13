"""Doctrine controller for strategic alignment evaluation."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.doctrine.doctrine_models import (
    DecisionContext,
    DoctrineAssessment,
    LIVE_EXECUTION_ENABLED,
    DOCTRINE_VERSION,
)
from app.doctrine.doctrine_evaluator import get_doctrine_evaluator
from app.doctrine.doctrine_explanations import get_doctrine_explainer
from app.doctrine.doctrine_store import get_doctrine_store

logger = logging.getLogger(__name__)


class DoctrineController:
    """Primary orchestration entry point for doctrine evaluation."""

    def __init__(self):
        self.evaluator = get_doctrine_evaluator()
        self.explainer = get_doctrine_explainer()
        self.store = get_doctrine_store()

    def evaluate_alignment(
        self,
        cycle_id: str,
        signals: List[Dict[str, Any]] = None,
        state_snapshot: Dict[str, Any] = None,
        optimization_output: Dict[str, Any] = None,
        candidate_recommendations: List[Dict[str, Any]] = None,
        learning_feedback: Dict[str, Any] = None,
        journal_history: List[Dict[str, Any]] = None,
    ) -> DoctrineAssessment:
        """
        Evaluate doctrine alignment for a decision context.
        
        This is the primary entry point for doctrine evaluation.
        """
        # Safety check
        if LIVE_EXECUTION_ENABLED:
            logger.error("Cannot evaluate doctrine when LIVE_EXECUTION_ENABLED is True")
            raise RuntimeError("Doctrine evaluation blocked: LIVE_EXECUTION_ENABLED is True")
        
        # Create decision context
        context = DecisionContext(
            cycle_id=cycle_id,
            timestamp=datetime.utcnow(),
            signals=signals or [],
            state_snapshot=state_snapshot or {},
            optimization_output=optimization_output or {},
            candidate_recommendations=candidate_recommendations or [],
            learning_feedback=learning_feedback or {},
            journal_history=journal_history or [],
        )
        
        # Evaluate
        assessment = self.evaluator.evaluate(context)
        
        # Store assessment
        self.store.store_assessment(assessment)
        
        return assessment

    def get_explanation(self, assessment: DoctrineAssessment) -> Dict[str, Any]:
        """Get detailed explanation for a doctrine assessment."""
        return self.explainer.explain_assessment(assessment)

    def generate_audit_report(self, assessment: DoctrineAssessment) -> str:
        """Generate human-readable audit report."""
        return self.explainer.generate_audit_report(assessment)

    def get_assessment(self, cycle_id: str) -> Optional[DoctrineAssessment]:
        """Get a stored assessment by cycle ID."""
        return self.store.get_assessment(cycle_id)

    def get_recent_assessments(self, limit: int = 10) -> List[DoctrineAssessment]:
        """Get recent doctrine assessments."""
        return self.store.get_recent_assessments(limit)

    def get_conflicts(self, min_severity: float = 0.5) -> List[Dict[str, Any]]:
        """Get conflicts above severity threshold."""
        return self.store.get_conflicts(min_severity)

    def get_statistics(self) -> Dict[str, Any]:
        """Get doctrine statistics."""
        return {
            "store": self.store.get_statistics(),
            "version": DOCTRINE_VERSION,
            "safety": {
                "LIVE_EXECUTION_ENABLED": LIVE_EXECUTION_ENABLED,
            },
        }


# Global controller instance
_controller: Optional[DoctrineController] = None


def get_doctrine_controller() -> DoctrineController:
    """Get the global doctrine controller instance."""
    global _controller
    if _controller is None:
        _controller = DoctrineController()
    return _controller
