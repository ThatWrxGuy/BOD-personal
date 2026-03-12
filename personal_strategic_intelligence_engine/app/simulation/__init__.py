"""DEPRECATED: Legacy Simulation Module.

This module is DEPRECATED. All simulation functionality has been migrated to:
    app.simulation_engine

Migration:
    from app.simulation_engine import SimulationCore, StrategySimulator, MonteCarloEngine

This module will be removed in a future version.
"""
# DEPRECATED: Import forwarding to canonical simulation_engine
# This is a thin compatibility wrapper - all logic is in app.simulation_engine

from app.simulation_engine import (
    SimulationCore,
    get_simulation_core,
    StrategySimulator,
    get_strategy_simulator,
    MonteCarloEngine,
    get_monte_carlo_engine,
    SimulationConfig,
    SimulationResult,
    SimulationType,
    DomainState,
)

# Keep some legacy exports for backward compatibility
# These are mapped to the canonical implementation
from app.simulation_engine.simulation_models import (
    SimulationStatus,
)

__all__ = [
    # Canonical imports (preferred)
    "SimulationCore",
    "get_simulation_core",
    "StrategySimulator",
    "get_strategy_simulator",
    "MonteCarloEngine", 
    "get_monte_carlo_engine",
    "SimulationConfig",
    "SimulationResult",
    "SimulationType",
    "SimulationStatus",
    "DomainState",
]
