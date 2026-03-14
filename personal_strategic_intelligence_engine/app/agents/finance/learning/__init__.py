"""Tactical Learning Subsystem.

Provides learning and calibration capabilities for the tactical decision stack.
"""

from app.agents.finance.learning.learning_models import (
    SignalOutcomeRecord,
    SignalOutcome,
    SignalDirection,
    ConfidenceBucket,
    MarketRegime,
    TimingDecision,
    SuppressionCategory,
    FeaturePerformance,
    FeaturePerformanceReport,
    ConfidenceBucketStats,
    ConfidenceCalibrationReport,
    SuppressionEffectivenessRecord,
    SuppressionEffectivenessReport,
    RegimePerformance,
    RegimePerformanceReport,
    TimingPerformance,
    TimingPerformanceReport,
    ScoreOptimizationProposal,
    TacticalLearningSnapshot,
)
from app.agents.finance.learning.signal_outcome_analyzer import SignalOutcomeAnalyzer, create_analyzer
from app.agents.finance.learning.feature_importance_engine import FeatureImportanceEngine, create_engine
from app.agents.finance.learning.confidence_calibrator import ConfidenceCalibrator, create_calibrator
from app.agents.finance.learning.suppression_effectiveness import SuppressionEffectivenessAnalyzer, create_analyzer
from app.agents.finance.learning.regime_performance_analyzer import RegimePerformanceAnalyzer, create_analyzer
from app.agents.finance.learning.timing_performance_analyzer import TimingPerformanceAnalyzer, create_analyzer
from app.agents.finance.learning.score_optimizer import ScoreOptimizer, create_optimizer
from app.agents.finance.learning.learning_logger import LearningLogger, create_logger

__all__ = [
    # Models
    "SignalOutcomeRecord",
    "SignalOutcome",
    "SignalDirection",
    "ConfidenceBucket",
    "MarketRegime",
    "TimingDecision",
    "SuppressionCategory",
    "FeaturePerformance",
    "FeaturePerformanceReport",
    "ConfidenceBucketStats",
    "ConfidenceCalibrationReport",
    "SuppressionEffectivenessRecord",
    "SuppressionEffectivenessReport",
    "RegimePerformance",
    "RegimePerformanceReport",
    "TimingPerformance",
    "TimingPerformanceReport",
    "ScoreOptimizationProposal",
    "TacticalLearningSnapshot",
    # Analyzers
    "SignalOutcomeAnalyzer",
    "create_analyzer",
    "FeatureImportanceEngine",
    "create_engine",
    "ConfidenceCalibrator",
    "create_calibrator",
    "SuppressionEffectivenessAnalyzer",
    "RegimePerformanceAnalyzer",
    "TimingPerformanceAnalyzer",
    # Optimizer
    "ScoreOptimizer",
    "create_optimizer",
    # Logger
    "LearningLogger",
    "create_logger",
]
