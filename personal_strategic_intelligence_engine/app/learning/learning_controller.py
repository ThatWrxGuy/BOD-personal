"""Learning controller orchestrating the learning pipeline."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.learning.outcome_models import (
    LifecycleStatus,
    LearningCycleSummary,
    LearningEvent,
    LIVE_EXECUTION_ENABLED,
    LEARNING_MODE,
)
from app.learning.recommendation_tracker import get_recommendation_tracker
from app.learning.outcome_linker import get_outcome_linker
from app.learning.outcome_evaluator import get_outcome_evaluator
from app.learning.recommendation_scorer import get_recommendation_scorer
from app.learning.confidence_calibrator import get_confidence_calibrator
from app.decision_journal.journal_store import get_journal_store

logger = logging.getLogger(__name__)


class LearningController:
    """Orchestrates the learning pipeline."""

    def __init__(self):
        self.tracker = get_recommendation_tracker()
        self.linker = get_outcome_linker()
        self.evaluator = get_outcome_evaluator()
        self.scorer = get_recommendation_scorer()
        self.calibrator = get_confidence_calibrator()
        self.journal = get_journal_store()

    def track_recommendation(
        self,
        recommendation_id: str,
        cycle_id: str,
        target_domain: str,
        action: str,
        baseline_state: Dict[str, Any] = None,
    ) -> bool:
        """Track a newly issued recommendation."""
        
        start_time = datetime.utcnow()

        # Verify safety
        if not LEARNING_MODE:
            logger.error("Learning mode is not enabled")
            return False

        result = self.tracker.register_recommendation(
            recommendation_id=recommendation_id,
            cycle_id=cycle_id,
            target_domain=target_domain,
            action=action,
            issued_timestamp=datetime.utcnow(),
            baseline_state=baseline_state or {},
        )

        # Create observation window
        if result:
            window = self.linker.link_outcome(
                recommendation_id=recommendation_id,
                domain=target_domain,
                baseline_timestamp=datetime.utcnow(),
            )
            self.tracker.set_observation_window(recommendation_id, window)

        # Log event
        self._log_event(
            "recommendation_tracked",
            recommendation_id=recommendation_id,
            cycle_id=cycle_id,
            lifecycle_status="issued",
            processing_latency_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
        )

        return result

    def link_followup_outcomes(
        self,
        recommendation_id: str,
        followup_signals: List[Dict[str, Any]],
    ) -> bool:
        """Link follow-up signals to a recommendation."""
        
        result = self.tracker.add_followup_signals(
            recommendation_id=recommendation_id,
            signals=followup_signals,
        )

        if result:
            # Update status
            self.tracker.update_status(
                recommendation_id,
                LifecycleStatus.OBSERVED
            )

        return result

    def evaluate_outcome(
        self,
        recommendation_id: str,
    ) -> Optional[Any]:
        """Evaluate the outcome of a recommendation."""
        
        start_time = datetime.utcnow()

        # Get recommendation record
        record = self.tracker.get_recommendation(recommendation_id)
        if not record:
            logger.warning(f"Recommendation not found: {recommendation_id}")
            return None

        # Get follow-up signals
        followup_signals = record.followup_signals
        followup_state = {}
        
        for sig in followup_signals:
            if "normalized_payload" in sig:
                followup_state.update(sig["normalized_payload"])

        # Evaluate outcome
        evaluation = self.evaluator.evaluate_outcome(
            recommendation_id=recommendation_id,
            lifecycle_status=record.lifecycle_status,
            baseline_state=record.baseline_state,
            followup_state=followup_state,
            evidence_summary={
                "signal_count": len(followup_signals),
                "followup_state": followup_state,
            },
        )

        # Update record with evaluation
        record.outcome_quality = evaluation.outcome_quality
        record.effectiveness_score = evaluation.magnitude_of_change
        record.evaluation_rationale = evaluation.evaluation_rationale
        record.evaluated_at = datetime.utcnow()

        # Update status based on outcome
        if evaluation.outcome_quality.value in ["improvement"]:
            self.tracker.update_status(recommendation_id, LifecycleStatus.FOLLOWED)
        elif evaluation.outcome_quality.value in ["deterioration", "mixed"]:
            self.tracker.update_status(recommendation_id, LifecycleStatus.IGNORED)

        # Score the recommendation
        score = self.scorer.score_recommendation(
            recommendation_id=recommendation_id,
            outcome_quality=evaluation.outcome_quality,
            magnitude=evaluation.magnitude_of_change,
            urgency="medium",  # Would come from recommendation
        )

        # Calibrate confidence
        calibration = self.calibrator.calibrate_confidence(
            domain=record.target_domain,
            effectiveness_score=score,
        )

        # Update record with confidence adjustment
        record.confidence_adjustment = calibration.calibration_factor

        # Log event
        self._log_event(
            "outcome_evaluated",
            recommendation_id=recommendation_id,
            cycle_id=record.cycle_id,
            lifecycle_status=record.lifecycle_status.value,
            outcome_quality=evaluation.outcome_quality.value,
            effectiveness_score=evaluation.magnitude_of_change,
            confidence_adjustment=calibration.calibration_factor,
            processing_latency_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
        )

        return evaluation

    def evaluate_recent_recommendations(
        self,
        max_age_hours: int = 168,
    ) -> LearningCycleSummary:
        """Evaluate all recent recommendations that are ready."""
        
        start_time = datetime.utcnow()

        # Get pending recommendations
        pending = self.tracker.get_pending_evaluations(max_age_hours)

        positive = 0
        negative = 0
        neutral = 0
        total_effectiveness = 0.0
        adjustments = {}

        for rec in pending:
            # Evaluate
            result = self.evaluate_outcome(rec.recommendation_id)
            
            if result:
                if result.outcome_quality.value == "improvement":
                    positive += 1
                elif result.outcome_quality.value == "deterioration":
                    negative += 1
                else:
                    neutral += 1
                
                total_effectiveness += abs(result.magnitude_of_change)
                
                # Track adjustments
                adj = rec.confidence_adjustment
                domain = rec.target_domain
                adjustments[domain] = adjustments.get(domain, 0) + adj

        count = len(pending)
        avg_effectiveness = total_effectiveness / count if count > 0 else 0.0

        summary = LearningCycleSummary(
            cycle_id=f"learning_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.utcnow(),
            recommendations_evaluated=count,
            positive_outcomes=positive,
            negative_outcomes=negative,
            neutral_outcomes=neutral,
            avg_effectiveness_score=avg_effectiveness,
            confidence_adjustments=adjustments,
            learning_insights=self._generate_insights(positive, negative, neutral),
        )

        logger.info(
            f"Learning cycle complete: {count} evaluated, "
            f"{positive} positive, {negative} negative, {neutral} neutral"
        )

        return summary

    def _generate_insights(
        self,
        positive: int,
        negative: int,
        neutral: int,
    ) -> List[str]:
        """Generate learning insights from evaluation results."""
        insights = []

        total = positive + negative + neutral
        if total == 0:
            return ["No recommendations evaluated"]

        positive_rate = positive / total
        negative_rate = negative / total

        if positive_rate >= 0.7:
            insights.append("High success rate - recommendations are effective")
        elif negative_rate >= 0.5:
            insights.append("Low success rate - review recommendation logic")

        if positive > negative:
            insights.append("Positive outcomes exceed negative")
        elif negative > positive:
            insights.append("Negative outcomes exceed positive - intervention needed")

        return insights

    def _log_event(
        self,
        event_type: str,
        recommendation_id: Optional[str] = None,
        cycle_id: Optional[str] = None,
        lifecycle_status: Optional[str] = None,
        outcome_quality: Optional[str] = None,
        effectiveness_score: Optional[float] = None,
        confidence_adjustment: float = 0.0,
        processing_latency_ms: float = 0.0,
        error_message: Optional[str] = None,
    ):
        """Log a learning event."""
        event = LearningEvent(
            event_type=event_type,
            recommendation_id=recommendation_id,
            cycle_id=cycle_id,
            lifecycle_status=lifecycle_status,
            outcome_quality=outcome_quality,
            effectiveness_score=effectiveness_score,
            confidence_adjustment=confidence_adjustment,
            processing_latency_ms=processing_latency_ms,
            error_message=error_message,
        )
        logger.info(f"Learning event: {event_type} - {recommendation_id}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get learning statistics."""
        return {
            "tracker": self.tracker.get_statistics(),
            "scorer": self.scorer.get_statistics(),
            "calibrator": self.calibrator.get_statistics(),
            "safety": {
                "LIVE_EXECUTION_ENABLED": LIVE_EXECUTION_ENABLED,
                "LEARNING_MODE": LEARNING_MODE,
            },
        }


# Global controller instance
_controller: Optional[LearningController] = None


def get_learning_controller() -> LearningController:
    """Get the global learning controller instance."""
    global _controller
    if _controller is None:
        _controller = LearningController()
    return _controller
