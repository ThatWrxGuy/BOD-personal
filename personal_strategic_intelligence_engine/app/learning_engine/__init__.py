"""Learning Engine - Strategic Memory & Learning subsystem for PSIE.

This module provides adaptive intelligence capabilities:
- Strategic memory for storing historical data
- Outcome evaluation and prediction accuracy tracking
- Performance tracking for strategies and agents
- Degradation detection for performance issues
- Confidence calibration based on historical accuracy

The Learning Engine enables PSIE to:
- Learn from historical decisions
- Detect strategy degradation
- Improve agent performance
- Evolve intelligence over time
"""
from app.learning_engine.memory_models import (
    MemoryCategory,
    SourceType,
    DegradationLevel,
    MemoryRecord,
    OutcomeRecord,
    StrategyPerformanceSnapshot,
    AgentPerformanceSnapshot,
    DegradationAlert,
    ConfidenceAdjustment,
    LearningStatistics,
    LearningInsight,
)

from app.learning_engine.strategic_memory import (
    StrategicMemoryStore,
    get_strategic_memory,
    reset_strategic_memory,
)

from app.learning_engine.outcome_evaluator import (
    OutcomeEvaluator,
    get_outcome_evaluator,
)

from app.learning_engine.performance_tracker import (
    PerformanceTracker,
    get_performance_tracker,
    reset_performance_tracker,
)

from app.learning_engine.degradation_detector import (
    DegradationDetector,
    get_degradation_detector,
)

from app.learning_engine.confidence_calibrator import (
    ConfidenceCalibrator,
    get_confidence_calibrator,
)

from app.learning_engine.learning_engine import (
    LearningEngine,
    get_learning_engine,
    reset_learning_engine,
)

from app.learning_engine.routes import router

__all__ = [
    # Memory Models
    "MemoryCategory",
    "SourceType",
    "DegradationLevel",
    "MemoryRecord",
    "OutcomeRecord",
    "StrategyPerformanceSnapshot",
    "AgentPerformanceSnapshot",
    "DegradationAlert",
    "ConfidenceAdjustment",
    "LearningStatistics",
    "LearningInsight",
    # Components
    "StrategicMemoryStore",
    "get_strategic_memory",
    "reset_strategic_memory",
    "OutcomeEvaluator",
    "get_outcome_evaluator",
    "PerformanceTracker",
    "get_performance_tracker",
    "reset_performance_tracker",
    "DegradationDetector",
    "get_degradation_detector",
    "ConfidenceCalibrator",
    "get_confidence_calibrator",
    "LearningEngine",
    "get_learning_engine",
    "reset_learning_engine",
    # Routes
    "router",
]
