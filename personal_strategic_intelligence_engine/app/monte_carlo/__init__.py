"""DEPRECATED: Legacy Monte Carlo Module.

This module is DEPRECATED. All Monte Carlo functionality has been migrated to:
    app.simulation_engine

Migration:
    from app.simulation_engine import MonteCarloEngine, get_monte_carlo_engine

This module will be removed in a future version.
"""
# DEPRECATED: Import forwarding to canonical simulation_engine
from app.simulation_engine import (
    MonteCarloEngine,
    get_monte_carlo_engine,
    SimulationConfig,
    SimulationResult,
    DomainState,
)

from app.simulation_engine.simulation_models import (
    SimulationType,
    SimulationStatus,
)

__all__ = [
    # Canonical imports (preferred)
    "MonteCarloEngine",
    "get_monte_carlo_engine",
    "SimulationConfig",
    "SimulationResult",
    "SimulationType",
    "SimulationStatus",
    "DomainState",
]
