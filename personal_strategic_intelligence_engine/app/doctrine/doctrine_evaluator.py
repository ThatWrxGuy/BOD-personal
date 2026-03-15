"""Doctrine evaluator for assessing decision alignment."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.doctrine.doctrine_models import (
    AlignmentLevel,
    AlignmentScore,
    DecisionContext,
    DoctrineAssessment,
    DoctrineConflict,
    DoctrineRecommendation,
    LIVE_EXECUTION_ENABLED,
    DOCTRINE_VERSION,
)
from app.doctrine.doctrine_registry import get_doctrine_registry

logger = logging.getLogger(__name__)


class DoctrineEvaluator:
    """Evaluates doctrine rules against a decision context."""

    def __init__(self):
        self.registry = get_doctrine_registry()

    def evaluate(self, context: DecisionContext) -> DoctrineAssessment:
        """Evaluate all enabled rules against the decision context."""
        
        # Safety check
        if LIVE_EXECUTION_ENABLED:
            logger.error("Cannot evaluate doctrine when LIVE_EXECUTION_ENABLED is True")
            return self._create_error_assessment(
                context.cycle_id,
                "LIVE_EXECUTION_ENABLED is True"
            )
        
        # Get enabled rules
        rules = self.registry.get_enabled_rules()
        
        if not rules:
            logger.warning("No enabled rules for evaluation")
            return self._create_neutral_assessment(context)
        
        # Evaluate each rule
        rule_results = []
        total_weight = 0.0
        weighted_score = 0.0
        
        conflicts = []
        risk_flags = []
        adjustments = []
        
        signals_considered = []
        rules_applied = []
        
        for rule in rules:
            try:
                result = rule.evaluate(context)
                rule_results.append(result)
                
                # Track applied rules
                rules_applied.append(rule.rule_id)
                
                # Aggregate score
                weight = rule.rule.weight
                score = result.get("score", 0.0)
                weighted_score += weight * score
                total_weight += weight
                
                # Collect conflicts
                level = result.get("level")
                if level in [AlignmentLevel.MISALIGNED, AlignmentLevel.REQUIRES_REVIEW]:
                    conflicts.append(DoctrineConflict(
                        conflict_type=rule.rule_type.value,
                        rules_involved=[rule.rule_id],
                        severity=abs(score),
                        description=result.get("explanation", ""),
                    ))
                    risk_flags.append(f"{rule.rule_type.value}: {result.get('explanation', '')}")
                
                # Generate adjustments for significant issues
                if level in [AlignmentLevel.MISALIGNED, AlignmentLevel.REQUIRES_REVIEW]:
                    adjustments.append(DoctrineRecommendation(
                        adjustment_type="review_required",
                        target=rule.rule_type.value,
                        adjustment=score,
                        rationale=result.get("explanation", ""),
                        priority=rule.rule.priority,
                    ))
                
                # Track signals considered
                if context.signals:
                    signals_considered = [s.get("signal_id", "unknown") for s in context.signals]
                
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.rule_id}: {e}")
                continue
        
        # Calculate final alignment score
        if total_weight > 0:
            final_score = weighted_score / total_weight
        else:
            final_score = 0.0
        
        # Determine alignment level
        alignment_level = self._determine_level(final_score)
        
        # Calculate confidence
        confidence = self._calculate_confidence(rule_results, context)
        
        alignment_score = AlignmentScore(
            level=alignment_level,
            score=final_score,
            confidence=confidence,
            factors={r["rule_id"]: r["score"] for r in rule_results},
        )
        
        # Create assessment
        assessment = DoctrineAssessment(
            cycle_id=context.cycle_id,
            timestamp=datetime.utcnow(),
            doctrine_version=DOCTRINE_VERSION,
            alignment_score=alignment_score,
            doctrine_conflicts=conflicts,
            risk_flags=risk_flags,
            recommended_adjustments=adjustments,
            policy_rules_applied=rules_applied,
            signals_considered=signals_considered[:10],  # Limit to 10
            journal_events_referenced=[],  # Would be populated from journal
            learning_feedback_used=list(context.learning_feedback.keys()) if context.learning_feedback else [],
            confidence_score=confidence,
            evaluation_summary=self._generate_summary(alignment_level, conflicts, adjustments),
        )
        
        return assessment

    def _determine_level(self, score: float) -> AlignmentLevel:
        """Determine alignment level from score."""
        if score >= 0.3:
            return AlignmentLevel.ALIGNED
        elif score >= -0.1:
            return AlignmentLevel.NEUTRAL
        elif score >= -0.5:
            return AlignmentLevel.REQUIRES_REVIEW
        else:
            return AlignmentLevel.MISALIGNED

    def _calculate_confidence(
        self,
        rule_results: List[Dict],
        context: DecisionContext
    ) -> float:
        """Calculate confidence in the evaluation."""
        
        # Base confidence from rule coverage
        rule_conf = min(0.6, len(rule_results) * 0.1)
        
        # Boost from having signals
        signal_factor = 0.2 if context.signals else 0.0
        
        # Boost from having recommendations
        rec_factor = 0.1 if context.candidate_recommendations else 0.0
        
        # Boost from learning feedback
        learning_factor = 0.1 if context.learning_feedback else 0.0
        
        base = 0.1
        
        return min(0.95, base + rule_conf + signal_factor + rec_factor + learning_factor)

    def _generate_summary(
        self,
        level: AlignmentLevel,
        conflicts: List[DoctrineConflict],
        adjustments: List[DoctrineRecommendation]
    ) -> str:
        """Generate human-readable evaluation summary."""
        
        parts = []
        
        parts.append(f"Alignment: {level.value}")
        
        if conflicts:
            parts.append(f"Conflicts: {len(conflicts)}")
        
        if adjustments:
            parts.append(f"Adjustments: {len(adjustments)}")
        
        if level == AlignmentLevel.ALIGNED:
            parts.append("Decision aligned with doctrine")
        elif level == AlignmentLevel.NEUTRAL:
            parts.append("Decision requires monitoring")
        elif level == AlignmentLevel.REQUIRES_REVIEW:
            parts.append("Decision requires manual review")
        else:
            parts.append("Decision conflicts with doctrine")
        
        return "; ".join(parts)

    def _create_neutral_assessment(self, context: DecisionContext) -> DoctrineAssessment:
        """Create a neutral assessment when no rules are available."""
        return DoctrineAssessment(
            cycle_id=context.cycle_id,
            timestamp=datetime.utcnow(),
            doctrine_version=DOCTRINE_VERSION,
            alignment_score=AlignmentScore(
                level=AlignmentLevel.NEUTRAL,
                score=0.0,
                confidence=0.1,
            ),
            evaluation_summary="No doctrine rules available for evaluation",
        )

    def _create_error_assessment(self, cycle_id: str, error: str) -> DoctrineAssessment:
        """Create an error assessment."""
        return DoctrineAssessment(
            cycle_id=cycle_id,
            timestamp=datetime.utcnow(),
            doctrine_version=DOCTRINE_VERSION,
            alignment_score=AlignmentScore(
                level=AlignmentLevel.NEUTRAL,
                score=0.0,
                confidence=0.0,
            ),
            evaluation_summary=f"Error: {error}",
        )


# Global evaluator instance
_evaluator: Optional[DoctrineEvaluator] = None


def get_doctrine_evaluator() -> DoctrineEvaluator:
    """Get the global doctrine evaluator instance."""
    global _evaluator
    if _evaluator is None:
        _evaluator = DoctrineEvaluator()
    return _evaluator
