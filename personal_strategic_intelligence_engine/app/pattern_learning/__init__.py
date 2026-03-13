"""Pattern Learning Module.

Provides decision pattern learning and contextual strategy scoring.
"""
from app.pattern_learning.pattern_models import (
    ContextCluster,
    ContextualStrategyScore,
    DecisionContextProfile,
    DecisionPattern,
    OutcomeType,
    PatternLearningSummary,
    PatternOutcomeSummary,
    RecommendationFamily,
    StrategyEffectivenessScore,
    StrategyFamily,
    LIVE_EXECUTION_ENABLED,
    PATTERN_LEARNING_MODE,
)
from app.pattern_learning.decision_pattern_extractor import (
    DecisionPatternExtractor,
    get_decision_pattern_extractor,
)
from app.pattern_learning.context_clusterer import (
    ContextClusterer,
    get_context_clusterer,
)
from app.pattern_learning.recommendation_family_classifier import (
    RecommendationFamilyClassifier,
    get_recommendation_family_classifier,
)
from app.pattern_learning.outcome_pattern_analyzer import (
    OutcomePatternAnalyzer,
    get_outcome_pattern_analyzer,
)
from app.pattern_learning.strategy_effectiveness_ranker import (
    StrategyEffectivenessRanker,
    get_strategy_effectiveness_ranker,
)
from app.pattern_learning.contextual_strategy_scorer import (
    ContextualStrategyScorer,
    get_contextual_strategy_scorer,
)
from app.pattern_learning.pattern_store import (
    PatternStore,
    get_pattern_store,
)
from app.pattern_learning.pattern_reporter import (
    PatternReporter,
    get_pattern_reporter,
)

__all__ = [
    # Models
    "ContextCluster",
    "ContextualStrategyScore",
    "DecisionContextProfile",
    "DecisionPattern",
    "OutcomeType",
    "PatternLearningSummary",
    "PatternOutcomeSummary",
    "RecommendationFamily",
    "StrategyEffectivenessScore",
    "StrategyFamily",
    # Safety
    "LIVE_EXECUTION_ENABLED",
    "PATTERN_LEARNING_MODE",
    # Components
    "DecisionPatternExtractor",
    "get_decision_pattern_extractor",
    "ContextClusterer",
    "get_context_clusterer",
    "RecommendationFamilyClassifier",
    "get_recommendation_family_classifier",
    "OutcomePatternAnalyzer",
    "get_outcome_pattern_analyzer",
    "StrategyEffectivenessRanker",
    "get_strategy_effectiveness_ranker",
    "ContextualStrategyScorer",
    "get_contextual_strategy_scorer",
    "PatternStore",
    "get_pattern_store",
    "PatternReporter",
    "get_pattern_reporter",
]
