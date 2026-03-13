"""Doctrine gate - validates execution against doctrine alignment."""
import logging
from typing import Any, Dict, List, Optional

from app.execution.execution_models import (
    DoctrineGateResult,
    ExecutionIntent,
)

logger = logging.getLogger(__name__)


class DoctrineGate:
    """Validates execution against doctrine alignment."""

    def __init__(self):
        self._doctrine_available = self._check_doctrine_availability()

    def _check_doctrine_availability(self) -> bool:
        """Check if doctrine subsystem is available."""
        try:
            from app.doctrine import get_doctrine_controller
            return True
        except ImportError:
            logger.warning("Doctrine subsystem not available")
            return False

    def validate(self, intent: ExecutionIntent, context: Optional[Dict[str, Any]] = None) -> DoctrineGateResult:
        """
        Validate execution intent against doctrine alignment.
        
        Args:
            intent: The execution intent to validate
            context: Optional decision context for doctrine evaluation
            
        Returns:
            DoctrineGateResult with alignment status
        """
        # If doctrine is not available, allow with warning
        if not self._doctrine_available:
            logger.warning("Doctrine not available - bypassing doctrine gate")
            return DoctrineGateResult(
                aligned=True,
                alignment_score=0.5,
                alignment_level="neutral",
                risk_flags=["doctrine_unavailable"],
            )
        
        try:
            # Import doctrine controller
            from app.doctrine import get_doctrine_controller
            
            controller = get_doctrine_controller()
            
            # Build decision context for doctrine evaluation
            decision_context = self._build_context(intent, context)
            
            # Evaluate alignment
            assessment = controller.evaluate_alignment(
                cycle_id=intent.intent_id,
                signals=decision_context.get("signals", []),
                state_snapshot=decision_context.get("state", {}),
                optimization_output=decision_context.get("optimization", {}),
                candidate_recommendations=decision_context.get("recommendations", []),
                learning_feedback=decision_context.get("learning", {}),
                journal_history=decision_context.get("journal", []),
            )
            
            # Extract alignment status
            aligned = assessment.alignment_score.level.value in ["aligned", "neutral"]
            
            # Block execution if misaligned
            if assessment.alignment_score.level.value == "misaligned":
                aligned = False
                logger.warning(f"Doctrine gate blocked intent {intent.intent_id}: misaligned")
            
            result = DoctrineGateResult(
                aligned=aligned,
                alignment_score=assessment.alignment_score.score,
                alignment_level=assessment.alignment_score.level.value,
                risk_flags=assessment.risk_flags,
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in doctrine gate: {e}")
            # Fail safe - block execution on error
            return DoctrineGateResult(
                aligned=False,
                alignment_score=0.0,
                alignment_level="error",
                risk_flags=[f"doctrine_error: {str(e)}"],
            )

    def _build_context(self, intent: ExecutionIntent, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build decision context from intent and additional context."""
        
        # Start with intent information
        decision_context = {
            "signals": [],
            "state": {"domain": intent.domain},
            "optimization": {
                "confidence": intent.confidence,
            },
            "recommendations": [
                {
                    "target_domain": intent.domain,
                    "action_type": intent.action_type,
                    "parameters": intent.parameters,
                }
            ],
            "learning": {},
            "journal": [],
        }
        
        # Merge additional context if provided
        if context:
            for key in ["signals", "state", "optimization", "recommendations", "learning", "journal"]:
                if key in context:
                    decision_context[key] = context[key]
        
        return decision_context


# Global gate instance
_gate: Optional["DoctrineGate"] = None


def get_doctrine_gate() -> DoctrineGate:
    """Get the global doctrine gate instance."""
    global _gate
    if _gate is None:
        _gate = DoctrineGate()
    return _gate
