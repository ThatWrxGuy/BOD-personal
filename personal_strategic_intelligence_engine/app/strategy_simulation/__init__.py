"""DEPRECATED: Legacy Strategy Simulation Module.

This module is DEPRECATED. All strategy simulation functionality has been migrated to:
    app.simulation_engine

Migration:
    from app.simulation_engine import StrategySimulator, SimulationCore

This module will be removed in a future version.
"""
# DEPRECATED: Import forwarding to canonical simulation_engine
from app.simulation_engine import (
    StrategySimulator,
    get_strategy_simulator,
    SimulationCore,
    get_simulation_core,
    SimulationConfig,
    SimulationResult,
    SimulationType,
    DomainState,
)

from app.simulation_engine.simulation_models import (
    SimulationStatus,
)

__all__ = [
    # Canonical imports (preferred)
    "StrategySimulator",
    "get_strategy_simulator",
    "SimulationCore",
    "get_simulation_core",
    "SimulationConfig",
    "SimulationResult",
    "SimulationType",
    "SimulationStatus",
    "DomainState",
]
