"""Strategic Foresight Module.

Provides predictive intelligence and scenario anticipation.
"""
from app.strategic_foresight.foresight_models import (
    Domain,
    ForecastHorizon,
    FutureTrajectory,
    OpportunityType,
    RiskType,
    ScenarioProjection,
    ScenarioType,
    StrategicForecastReport,
    StrategicOpportunityProjection,
    StrategicRiskProjection,
    ForecastProbability,
    ForesightSummary,
    LIVE_EXECUTION_ENABLED,
    FORESIGHT_MODE,
)
from app.strategic_foresight.trajectory_simulator import (
    TrajectorySimulator,
    RiskProjectionEngine,
    OpportunityProjectionEngine,
    ScenarioGenerator,
    ForecastProbabilityEngine,
    ForesightController,
    get_foresight_controller,
)

__all__ = [
    # Models
    "Domain",
    "ForecastHorizon",
    "FutureTrajectory",
    "OpportunityType",
    "RiskType",
    "ScenarioProjection",
    "ScenarioType",
    "StrategicForecastReport",
    "StrategicOpportunityProjection",
    "StrategicRiskProjection",
    "ForecastProbability",
    "ForesightSummary",
    # Safety
    "LIVE_EXECUTION_ENABLED",
    "FORESIGHT_MODE",
    # Components
    "TrajectorySimulator",
    "RiskProjectionEngine",
    "OpportunityProjectionEngine",
    "ScenarioGenerator",
    "ForecastProbabilityEngine",
    "ForesightController",
    "get_foresight_controller",
]
