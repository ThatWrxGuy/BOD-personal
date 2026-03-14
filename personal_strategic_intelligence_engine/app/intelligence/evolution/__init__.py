"""Intelligence Evolution Subsystem.

Provides adaptive quantitative intelligence capabilities.
"""

from app.intelligence.evolution.evolution_models import (
    PatternType,
    OptimizationType,
    ApprovalLevel,
    RegimeType,
    QuantitativeMetrics,
    PatternDiscovery,
    FeatureImportance,
    OptimizationProposal,
    RegimeAnalysis,
    CalibrationReport,
    EvolutionSnapshot,
    LearningSchedule,
)
from app.intelligence.evolution.quantitative_analysis_engine import QuantitativeAnalysisEngine, create_engine
from app.intelligence.evolution.pattern_discovery_engine import PatternDiscoveryEngine, create_engine
from app.intelligence.evolution.feature_learning_engine import FeatureLearningEngine, create_engine
from app.intelligence.evolution.strategy_optimizer import StrategyOptimizer, create_optimizer
from app.intelligence.evolution.regime_adaptation_engine import RegimeAdaptationEngine, create_engine
from app.intelligence.evolution.model_calibration_engine import ModelCalibrationEngine, create_engine
from app.intelligence.evolution.confidence_evolution_engine import ConfidenceEvolutionEngine, create_engine
from app.intelligence.evolution.learning_scheduler import LearningScheduler, get_scheduler, start_scheduler, stop_scheduler
from app.intelligence.evolution.evolution_logger import EvolutionLogger, create_logger

__all__ = [
    # Models
    "PatternType",
    "OptimizationType",
    "ApprovalLevel",
    "RegimeType",
    "QuantitativeMetrics",
    "PatternDiscovery",
    "FeatureImportance",
    "OptimizationProposal",
    "RegimeAnalysis",
    "CalibrationReport",
    "EvolutionSnapshot",
    "LearningSchedule",
    # Engines
    "QuantitativeAnalysisEngine",
    "PatternDiscoveryEngine",
    "FeatureLearningEngine",
    "StrategyOptimizer",
    "RegimeAdaptationEngine",
    "ModelCalibrationEngine",
    "ConfidenceEvolutionEngine",
    # Factory functions
    "create_engine",
    "create_optimizer",
    "create_logger",
    # Scheduler
    "LearningScheduler",
    "get_scheduler",
    "start_scheduler",
    "stop_scheduler",
    # Logger
    "EvolutionLogger",
]
