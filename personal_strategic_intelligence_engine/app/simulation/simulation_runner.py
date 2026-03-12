"""Simulation Runner - Entry interface for launching simulations."""
import logging
import uuid
from datetime import datetime
from typing import Optional

from app.simulation.seed_manager import SeedManager, create_seed_manager
from app.simulation.mock_data_generator import MockDataGenerator
from app.simulation.scenario_builder import ScenarioBuilder
from app.simulation.simulation_engine_v2 import SimulationEngine
from app.simulation.simulation_types_v2 import (
    SimulationConfig,
    SimulationMetadata,
    SimulationResults,
    SimulationStatus,
    ScenarioType,
)

logger = logging.getLogger(__name__)


class SimulationRunner:
    """Entry point for running seeded simulations."""
    
    def __init__(self):
        self._history: dict[str, SimulationResults] = {}
    
    async def run_simulation(
        self,
        seed: str,
        scenario_type: ScenarioType = ScenarioType.BASELINE,
        duration_days: int = 30,
        enable_subsystems: bool = True,
    ) -> SimulationResults:
        """Run a full simulation."""
        
        # Create simulation ID
        sim_id = str(uuid.uuid4())[:8]
        
        logger.info(f"Starting simulation {sim_id} with seed {seed}")
        
        # Create configuration
        config = SimulationConfig(
            seed=seed,
            scenario_type=scenario_type,
            duration_days=duration_days,
            enable_subsystems=enable_subsystems,
        )
        
        # Create metadata
        metadata = SimulationMetadata(
            simulation_id=sim_id,
            seed=seed,
            scenario_type=scenario_type,
            duration_days=duration_days,
            start_time=datetime.utcnow(),
            status=SimulationStatus.RUNNING,
        )
        
        try:
            # Create components
            seed_manager = create_seed_manager(seed)
            mock_generator = MockDataGenerator(seed_manager)
            scenario_builder = ScenarioBuilder(seed_manager, mock_generator)
            
            # Build scenario
            scenario = scenario_builder.build_scenario(scenario_type)
            
            # Create results object
            results = SimulationResults(
                metadata=metadata,
                initial_profile=scenario["initial_state"]["personal_profile"],
                initial_financial=scenario["initial_state"]["financial_state"],
                initial_goals=scenario["initial_state"]["goals"],
                initial_habits=scenario["initial_state"]["habits"],
                initial_domains=scenario["initial_state"]["domain_states"],
            )
            
            # Run simulation engine
            engine = SimulationEngine(seed_manager, mock_generator, scenario)
            results = await engine.run_simulation(results, duration_days)
            
            # Update metadata
            results.metadata.status = SimulationStatus.COMPLETED
            results.metadata.end_time = datetime.utcnow()
            
            # Store in history
            self._history[sim_id] = results
            
            logger.info(f"Simulation {sim_id} completed successfully")
            
            return results
            
        except Exception as e:
            logger.error(f"Simulation {sim_id} failed: {e}")
            
            metadata.status = SimulationStatus.FAILED
            metadata.end_time = datetime.utcnow()
            
            results = SimulationResults(
                metadata=metadata,
                initial_profile=None,
                initial_financial=None,
                initial_goals=[],
                initial_habits=[],
                initial_domains=[],
            )
            
            return results
    
    def get_simulation(self, sim_id: str) -> Optional[SimulationResults]:
        """Get a simulation by ID."""
        return self._history.get(sim_id)
    
    def get_history(self) -> list[SimulationResults]:
        """Get simulation history."""
        return list(self._history.values())
    
    def clear_history(self) -> None:
        """Clear simulation history."""
        self._history.clear()


# Global runner instance
_simulation_runner: Optional[SimulationRunner] = None


def get_simulation_runner() -> SimulationRunner:
    """Get the global simulation runner."""
    global _simulation_runner
    if _simulation_runner is None:
        _simulation_runner = SimulationRunner()
    return _simulation_runner


async def run_seeded_simulation(
    seed: str,
    scenario_type: ScenarioType = ScenarioType.BASELINE,
    duration_days: int = 30,
) -> SimulationResults:
    """Convenience function to run a seeded simulation."""
    runner = get_simulation_runner()
    return await runner.run_simulation(seed, scenario_type, duration_days)
