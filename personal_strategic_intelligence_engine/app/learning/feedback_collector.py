"""Learning Feedback Collector - Collects outputs from all learning components.

This module implements the collection layer that gathers feedback from:
- Operational learning (outcome_evaluator)
- Strategic learning (strategic_learning_service)
- Doctrine updates (doctrine_updater)
- Recommendation scoring (recommendation_scorer)
- Strategy effectiveness (strategy_effectiveness)
- Confidence calibration (confidence_calibrator)
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from app.learning.feedback_contract import (
    LearningFeedback,
    FeedbackSource,
    FeedbackCategory,
    FeedbackPriority,
    EffectivenessMetrics,
    DoctrineUpdate,
    RecommendationPerformance,
    ExecutionOutcomeSummary,
    ConfidenceAdjustment,
    FailurePattern,
    get_learning_feedback_contract,
)

logger = logging.getLogger(__name__)


class LearningFeedbackCollector:
    """Collects learning outputs and converts them to feedback."""
    
    def __init__(self):
        self.feedback_contract = get_learning_feedback_contract()
    
    async def collect_all_feedback(self) -> List[LearningFeedback]:
        """Collect feedback from all learning sources.
        
        Returns:
            List of all learning feedback
        """
        feedback_list = []
        
        # Collect from each source
        feedback_list.extend(await self._collect_operational_feedback())
        feedback_list.extend(await self._collect_strategic_feedback())
        feedback_list.extend(await self._collect_doctrine_updates())
        feedback_list.extend(await self._collect_recommendation_performance())
        feedback_list.extend(await self._collect_confidence_adjustments())
        
        # Store in contract
        for fb in feedback_list:
            await self.feedback_contract.add_feedback(fb)
        
        logger.info(f"Collected {len(feedback_list)} feedback items")
        
        return feedback_list
    
    async def _collect_operational_feedback(self) -> List[LearningFeedback]:
        """Collect feedback from operational learning (outcome_evaluator).
        
        In production, would query OutcomeEvaluator for recent outcomes.
        """
        feedback_list = []
        
        # Placeholder: In production would query actual outcomes
        # Example of what would be collected:
        # outcomes = await outcome_evaluator.get_recent_outcomes(days=7)
        # for outcome in outcomes:
        #     feedback = self._convert_outcome_to_feedback(outcome)
        #     feedback_list.append(feedback)
        
        logger.debug("Collecting operational learning feedback")
        return feedback_list
    
    async def _collect_strategic_feedback(self) -> List[LearningFeedback]:
        """Collect feedback from strategic learning (strategic_learning_service).
        
        In production, would query StrategicLearningService for strategy effectiveness.
        """
        feedback_list = []
        
        logger.debug("Collecting strategic learning feedback")
        return feedback_list
    
    async def _collect_doctrine_updates(self) -> List[LearningFeedback]:
        """Collect feedback from doctrine updates (doctrine_updater).
        
        In production, would query DoctrineUpdater for recent updates.
        """
        feedback_list = []
        
        # Placeholder: In production would query DoctrineUpdater
        logger.debug("Collecting doctrine update feedback")
        return feedback_list
    
    async def _collect_recommendation_performance(self) -> List[LearningFeedback]:
        """Collect feedback from recommendation scoring (recommendation_scorer).
        
        In production, would query RecommendationScorer for performance data.
        """
        feedback_list = []
        
        logger.debug("Collecting recommendation performance feedback")
        return feedback_list
    
    async def _collect_confidence_adjustments(self) -> List[LearningFeedback]:
        """Collect feedback from confidence calibration (confidence_calibrator).
        
        In production, would query ConfidenceCalibrator for adjustments.
        """
        feedback_list = []
        
        logger.debug("Collecting confidence adjustment feedback")
        return feedback_list
    
    async def _convert_outcome_to_feedback(self, outcome) -> LearningFeedback:
        """Convert an outcome to learning feedback."""
        return LearningFeedback(
            source=FeedbackSource.OUTCOME_EVALUATION,
            source_module="outcome_evaluator",
            category=FeedbackCategory.ADVISORY,
            execution_outcome=ExecutionOutcomeSummary(
                execution_id=str(outcome.execution_id),
                plan_id=str(outcome.plan_id) if outcome.plan_id else None,
                status=outcome.status,
                outcome_summary=outcome.summary,
            ),
            applicable_period_start=outcome.completed_at,
        )
    
    async def _convert_effectiveness_to_feedback(self, metrics) -> LearningFeedback:
        """Convert effectiveness metrics to feedback."""
        return LearningFeedback(
            source=FeedbackSource.STRATEGY_EFFECTIVENESS,
            source_module="strategy_effectiveness",
            category=FeedbackCategory.WEIGHTING,
            priority=FeedbackPriority.HIGH if metrics.effectiveness_score < 0.5 else FeedbackPriority.MEDIUM,
            effectiveness=EffectivenessMetrics(
                strategy_id=str(metrics.strategy_id),
                effectiveness_score=metrics.effectiveness_score,
                success_rate=metrics.success_rate,
                outcome_category=metrics.outcome_category,
                sample_size=metrics.sample_size,
                confidence=metrics.confidence,
            ),
            applicable_period_start=metrics.measured_at,
            applicable_period_end=metrics.measured_at + timedelta(days=30),
        )
    
    async def get_feedback_summary(self) -> Dict[str, Any]:
        """Get summary of collected feedback."""
        feedback = await self.feedback_contract.get_feedback_for_planning()
        
        by_category = {}
        by_source = {}
        by_priority = {}
        
        for fb in feedback:
            # By category
            cat = fb.category.value
            by_category[cat] = by_category.get(cat, 0) + 1
            
            # By source
            src = fb.source.value
            by_source[src] = by_source.get(src, 0) + 1
            
            # By priority
            pri = fb.priority.value
            by_priority[pri] = by_priority.get(pri, 0) + 1
        
        return {
            "total_feedback": len(feedback),
            "by_category": by_category,
            "by_source": by_source,
            "by_priority": by_priority,
        }


# Singleton
_collector: Optional[LearningFeedbackCollector] = None


def get_learning_feedback_collector() -> LearningFeedbackCollector:
    """Get learning feedback collector singleton."""
    global _collector
    if _collector is None:
        _collector = LearningFeedbackCollector()
    return _collector
