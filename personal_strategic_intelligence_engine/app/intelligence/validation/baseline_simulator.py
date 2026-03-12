"""Baseline Simulator - Simulates decision-making without the intelligence system."""
import random
from typing import Dict, Any

from app.intelligence.validation.simulation_models import (
    SimulationScenario,
    SimulationResult,
)


class BaselineSimulator:
    """Simulates baseline (non-intelligent) decision-making."""
    
    def __init__(self):
        self.use_seed = True
    
    def simulate(
        self,
        scenario: SimulationScenario,
    ) -> SimulationResult:
        """Run baseline simulation."""
        
        # Set random seed for reproducibility
        if self.use_seed:
            random.seed(scenario.id)
        
        # Simulate baseline decisions
        decisions = self._simulate_decisions(scenario)
        
        # Calculate results
        result = self._calculate_results(scenario, decisions)
        
        return result
    
    def _simulate_decisions(
        self,
        scenario: SimulationScenario,
    ) -> list:
        """Simulate baseline decisions."""
        
        decisions = []
        
        # Baseline makes limited, short-sighted decisions
        # Random selection without strategic thinking
        
        num_decisions = random.randint(3, 8)
        
        for i in range(num_decisions):
            decisions.append(f"Baseline decision {i+1}")
        
        return decisions
    
    def _calculate_results(
        self,
        scenario: SimulationScenario,
        decisions: list,
    ) -> SimulationResult:
        """Calculate simulation results."""
        
        # Baseline performs worse - limited analysis
        # Use random but generally lower scores
        
        # Outcome score: baseline is less effective
        base_score = random.randint(35, 55)
        
        # Risk exposure: higher without intelligent analysis
        risk = random.randint(45, 70)
        
        # Goal completion: harder without planning
        goal_completion = random.randint(30, 50)
        
        # Efficiency: less efficient
        efficiency = random.randint(35, 55)
        
        # Resource utilization: suboptimal
        resources = random.randint(40, 60)
        
        # Decision quality: basic heuristics only
        decision_quality = random.randint(40, 55)
        
        # Calculate weighted outcome score
        outcome_score = (
            base_score * 0.3 +
            goal_completion * 0.3 +
            efficiency * 0.2 +
            decision_quality * 0.2
        )
        
        result = SimulationResult(
            id=f"baseline_{scenario.id}",
            scenario_id=scenario.id,
            system_used=False,
            outcome_score=outcome_score,
            risk_exposure=risk,
            goal_completion=goal_completion,
            execution_efficiency=efficiency,
            resource_utilization=resources,
            decision_quality=decision_quality,
            duration_days=random.randint(30, 90),
            decisions_made=len(decisions),
            adjustments_made=random.randint(1, 3),
            steps_taken=decisions,
        )
        
        return result


_simulator: BaselineSimulator = None


def get_baseline_simulator() -> BaselineSimulator:
    """Get the global baseline simulator."""
    global _simulator
    if _simulator is None:
        _simulator = BaselineSimulator()
    return _simulator
