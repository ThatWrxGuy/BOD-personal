"""Strategy Simulation Subsystem.

Provides strategy simulation and discovery capabilities.
"""

from app.intelligence.strategy_simulation.simulation_models import (
    SimulationStatus,
    StrategyType,
    StrategyConfig,
    SimulatedTrade,
    SimulationMetrics,
    RegimeBreakdown,
    SimulationResult,
    MonteCarloResult,
    StrategyComparison,
    StrategyDiscovery,
    OptimizationProposal,
    SimulationSnapshot,
)
from app.intelligence.strategy_simulation.strategy_generator import StrategyGenerator, create_generator
from app.intelligence.strategy_simulation.historical_replay_engine import HistoricalReplayEngine, create_engine
from app.intelligence.strategy_simulation.monte_carlo_engine import MonteCarloEngine, create_engine
from app.intelligence.strategy_simulation.strategy_evaluator import StrategyEvaluator, create_evaluator
from app.intelligence.strategy_simulation.strategy_comparator import StrategyComparator, create_comparator
from app.intelligence.strategy_simulation.strategy_discovery_engine import StrategyDiscoveryEngine, create_engine
from app.intelligence.strategy_simulation.simulation_scheduler import SimulationScheduler, get_scheduler, start_scheduler, stop_scheduler
from app.intelligence.strategy_simulation.simulation_logger import SimulationLogger, create_logger

__all__ = [
    # Models
    "SimulationStatus",
    "StrategyType",
    "StrategyConfig",
    "SimulatedTrade",
    "SimulationMetrics",
    "RegimeBreakdown",
    "SimulationResult",
    "MonteCarloResult",
    "StrategyComparison",
    "StrategyDiscovery",
    "OptimizationProposal",
    "SimulationSnapshot",
    # Engines
    "StrategyGenerator",
    "HistoricalReplayEngine",
    "MonteCarloEngine",
    "StrategyEvaluator",
    "StrategyComparator",
    "StrategyDiscoveryEngine",
    # Factory functions
    "create_generator",
    "create_engine",
    "create_evaluator",
    "create_comparator",
    # Scheduler
    "SimulationScheduler",
    "get_scheduler",
    "start_scheduler",
    "stop_scheduler",
    # Logger
    "SimulationLogger",
    "create_logger",
]
