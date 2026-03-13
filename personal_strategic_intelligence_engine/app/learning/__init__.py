"""Learning Layer for Outcome Tracking & Recommendation Learning.

This module provides outcome tracking, evaluation, and confidence
calibration based on observed results.

All operations are observational only - no execution permitted.
"""
from app.learning.outcome_models import (
    LIVE_EXECUTION_ENABLED,
    LEARNING_MODE,
    LifecycleStatus,
    OutcomeQuality,
    ObservationWindow,
    RecommendationOutcomeRecord,
    OutcomeEvaluationResult,
    RecommendationEffectivenessScore,
    ConfidenceCalibrationResult,
    LearningCycleSummary,
    LearningEvent,
)

from app.learning.recommendation_tracker import (
    RecommendationTracker,
    get_recommendation_tracker,
)

from app.learning.outcome_linker import (
    OutcomeLinker,
    get_outcome_linker,
)

from app.learning.outcome_evaluator import (
    OutcomeEvaluator,
    get_outcome_evaluator,
)

from app.learning.recommendation_scorer import (
    RecommendationScorer,
    get_recommendation_scorer,
)

from app.learning.confidence_calibrator import (
    ConfidenceCalibrator,
    get_confidence_calibrator,
)

from app.learning.learning_controller import (
    LearningController,
    get_learning_controller,
)

__all__ = [
    # Constants
    "LIVE_EXECUTION_ENABLED",
    "LEARNING_MODE",
    # Models
    "LifecycleStatus",
    "OutcomeQuality",
    "ObservationWindow",
    "RecommendationOutcomeRecord",
    "OutcomeEvaluationResult",
    "RecommendationEffectivenessScore",
    "ConfidenceCalibrationResult",
    "LearningCycleSummary",
    "LearningEvent",
    # Components
    "RecommendationTracker",
    "OutcomeLinker",
    "OutcomeEvaluator",
    "RecommendationScorer",
    "ConfidenceCalibrator",
    "LearningController",
    # Factories
    "get_recommendation_tracker",
    "get_outcome_linker",
    "get_outcome_evaluator",
    "get_recommendation_scorer",
    "get_confidence_calibrator",
    "get_learning_controller",
]
