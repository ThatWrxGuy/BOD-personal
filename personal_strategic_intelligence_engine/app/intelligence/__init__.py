"""Intelligence package for predictive analytics."""

# Synthesizer module (V5-004)
from app.intelligence.synthesizer import (
    SynthesizerService,
    get_synthesizer_service,
    StrategicIntelligenceReport,
    StrategicInsight,
    StrategicRecommendation,
)

# Learning module (V5-005)
from app.intelligence.learning import (
    LearningService,
    get_learning_service,
    LearningReport,
    StrategyType,
)

# Planning module (V6-001, V6-002, V6-003)
from app.intelligence.planning import (
    PlanningService,
    get_planning_service,
    StrategicGoal,
    StrategicPlan,
    StrategicPlanPortfolio,
    PlanType,
    TimeHorizon,
    PriorityLevel,
    ExecutionService,
    get_execution_service,
    ExecutionProgram,
    ExecutionTask,
    ExecutionStatus,
    ReplanningService,
    get_replanning_service,
    ReplanningDecision,
    ReplanningAction,
)

# Validation module (V6-005)
from app.intelligence.validation import (
    ValidationService,
    get_validation_service,
    SimulationScenario,
    SimulationResult,
    PerformanceComparison,
    SystemAuditReport,
)

__all__ = [
    # Synthesizer (V5-004)
    "SynthesizerService",
    "get_synthesizer_service",
    "StrategicIntelligenceReport",
    "StrategicInsight",
    "StrategicRecommendation",
    # Learning (V5-005)
    "LearningService",
    "get_learning_service",
    "LearningReport",
    "StrategyType",
    # Planning (V6-001)
    "PlanningService",
    "get_planning_service",
    "StrategicGoal",
    "StrategicPlan",
    "StrategicPlanPortfolio",
    "PlanType",
    "TimeHorizon",
    "PriorityLevel",
    # Execution (V6-002)
    "ExecutionService",
    "get_execution_service",
    "ExecutionProgram",
    "ExecutionTask",
    "ExecutionStatus",
    # Replanning (V6-003)
    "ReplanningService",
    "get_replanning_service",
    "ReplanningDecision",
    "ReplanningAction",
    # Validation (V6-005)
    "ValidationService",
    "get_validation_service",
    "SimulationScenario",
    "SimulationResult",
    "PerformanceComparison",
    "SystemAuditReport",
]
