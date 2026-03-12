"""Simulation Core - Main interface for unified simulation engine."""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.simulation_engine.simulation_models import (
    SimulationResult,
    SimulationStatus,
    SimulationConfig,
    SimulationType,
    DomainState,
)
from app.simulation_engine.strategy_simulator import get_strategy_simulator
from app.simulation_engine.monte_carlo_engine import get_monte_carlo_engine


class SimulationCore:
    """Central simulation interface - unified entry point for all simulations."""
    
    def __init__(self):
        self.strategy_sim = get_strategy_simulator()
        self.monte_carlo = get_monte_carlo_engine()
        
        self.active_simulations: Dict[str, SimulationResult] = {}
    
    def run_simulation(
        self,
        config: SimulationConfig,
        domains: Dict[str, DomainState],
    ) -> SimulationResult:
        """Run simulation based on configuration."""
        
        if config.simulation_type == SimulationType.STRATEGY:
            return self._run_strategy_simulation(config, domains)
        elif config.simulation_type == SimulationType.MONTE_CARLO:
            return self._run_monte_carlo(config, domains)
        elif config.simulation_type == SimulationType.SCENARIO:
            return self._run_scenario(config, domains)
        else:
            raise ValueError(f"Unknown simulation type: {config.simulation_type}")
    
    def _run_strategy_simulation(
        self,
        config: SimulationConfig,
        domains: Dict[str, DomainState],
    ) -> SimulationResult:
        """Run strategy simulation."""
        
        # Use strategy simulator with specified iterations
        result = self.strategy_sim.simulate_strategy(
            strategy_name="Strategy Simulation",
            domains=domains,
            iterations=config.num_iterations,
        )
        
        self.active_simulations[result.simulation_id] = result
        return result
    
    def _run_monte_carlo(
        self,
        config: SimulationConfig,
        domains: Dict[str, DomainState],
    ) -> SimulationResult:
        """Run Monte Carlo simulation."""
        
        result = self.monte_carlo.run_simulation(
            domains=domains,
            num_iterations=config.num_iterations,
            time_horizon_days=config.time_horizon_days,
        )
        
        self.active_simulations[result.simulation_id] = result
        return result
    
    def _run_scenario(
        self,
        config: SimulationConfig,
        domains: Dict[str, DomainState],
    ) -> SimulationResult:
        """Run scenario-based simulation."""
        
        # Scenario is essentially a constrained strategy simulation
        result = self.strategy_sim.simulate_strategy(
            strategy_name="Scenario Simulation",
            domains=domains,
            iterations=config.num_iterations // 10,  # Fewer for scenarios
        )
        
        self.active_simulations[result.simulation_id] = result
        return result
    
    def get_simulation(self, simulation_id: str) -> Optional[SimulationResult]:
        """Get a specific simulation result."""
        return self.active_simulations.get(simulation_id)
    
    def get_active_simulations(self) -> List[SimulationResult]:
        """Get all active simulations."""
        return list(self.active_simulations.values())
    
    def clear_completed(self) -> None:
        """Clear completed simulations from memory."""
        completed = [
            sid for sid, sim in self.active_simulations.items()
            if sim.status == SimulationStatus.COMPLETED
        ]
        for sid in completed:
            del self.active_simulations[sid]


# Singleton
_core: Optional[SimulationCore] = None


def get_simulation_core() -> SimulationCore:
    """Get the simulation core instance."""
    global _core
    if _core is None:
        _core = SimulationCore()
    return _core
