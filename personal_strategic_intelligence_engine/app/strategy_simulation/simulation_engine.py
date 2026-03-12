"""Simulation Engine - Main engine for strategic scenario simulation."""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.strategy_simulation.simulation_types import (
    SimulationCycle,
    SimulationPolicy,
    StrategyDecision,
    SimulatedOutcome,
    EnvironmentScenario,
    StrategyType,
)
from app.strategy_simulation.decision_model import DecisionModel, get_decision_model
from app.strategy_simulation.outcome_simulator import OutcomeSimulator, get_outcome_simulator
from app.strategy_simulation.strategy_comparator import StrategyComparator, get_strategy_comparator


class SimulationEngine:
    """Main simulation engine for strategic scenarios."""
    
    def __init__(self, policy: Optional[SimulationPolicy] = None):
        self.policy = policy or SimulationPolicy()
        self.decision_model = get_decision_model()
        self.outcome_simulator = get_outcome_simulator()
        self.comparator = get_strategy_comparator()
        self.cycles: List[SimulationCycle] = []
    
    def run_simulation_cycle(
        self,
        current_domains: Dict[str, float],
        strategies: Optional[List[StrategyDecision]] = None,
        environments: Optional[List[EnvironmentScenario]] = None,
    ) -> SimulationCycle:
        """Run a complete simulation cycle."""
        
        cycle_id = str(uuid.uuid4())[:8]
        
        # Get strategies to evaluate
        if strategies is None:
            strategies = self.decision_model.get_all_strategies()
        
        # Limit strategies
        strategies = strategies[:self.policy.max_strategies_to_compare]
        
        # Get environments
        if environments is None:
            environments = self._create_default_environments()
        
        # Get time horizons
        horizons = self.policy.time_horizons
        
        # Simulate baseline (no strategy change)
        baseline_outcome = self._simulate_baseline(
            current_domains, horizons[0], environments[0]
        )
        
        # Simulate each strategy
        outcomes = []
        
        for strategy in strategies:
            # Simulate in each environment
            for env in environments[:self.policy.scenarios_to_test]:
                outcome = self.outcome_simulator.simulate_outcome(
                    strategy, current_domains, horizons[0], env
                )
                outcomes.append(outcome)
        
        # Compare strategies
        comparison = self.comparator.compare_strategies(baseline_outcome, outcomes)
        
        # Determine best strategy
        best = comparison.recommended_strategy
        
        # Determine if execution recommended
        execution_recommended = False
        if best and comparison.baseline_outcome:
            best_outcome = next(
                (o for o in outcomes if o.strategy_id == best), None
            )
            if best_outcome:
                execution_recommended = (
                    best_outcome.overall_score > comparison.baseline_outcome.overall_score
                )
        
        cycle = SimulationCycle(
            cycle_id=cycle_id,
            current_domains=current_domains,
            strategies=strategies,
            outcomes=outcomes,
            comparison=comparison,
            best_strategy=best,
            execution_recommended=execution_recommended,
        )
        
        self.cycles.append(cycle)
        
        return cycle
    
    def _simulate_baseline(
        self,
        current_domains: Dict[str, float],
        days: int,
        environment: EnvironmentScenario,
    ) -> SimulatedOutcome:
        """Simulate baseline (no strategic change)."""
        
        # Use minimal resource change
        baseline_strategy = StrategyDecision(
            decision_id="baseline",
            name="Baseline",
            description="Continue current approach",
            strategy_type=StrategyType.FOCUS_SHIFT,
            resource_changes={},
            priority=0.5,
        )
        
        return self.outcome_simulator.simulate_outcome(
            baseline_strategy, current_domains, days, environment
        )
    
    def _create_default_environments(self) -> List[EnvironmentScenario]:
        """Create default environment scenarios."""
        
        return [
            EnvironmentScenario(
                scenario_id="baseline",
                name="Baseline",
                description="Normal conditions",
                economic_conditions=0.5,
                market_volatility=0.5,
                health_factors=0.5,
                opportunity_availability=0.5,
                probability=0.5,
            ),
            EnvironmentScenario(
                scenario_id="boom",
                name="Economic Boom",
                description="Favorable economic conditions",
                economic_conditions=0.8,
                market_volatility=0.3,
                health_factors=0.6,
                opportunity_availability=0.8,
                probability=0.2,
            ),
            EnvironmentScenario(
                scenario_id="recession",
                name="Economic Recession",
                description="Challenging economic conditions",
                economic_conditions=0.2,
                market_volatility=0.8,
                health_factors=0.4,
                opportunity_availability=0.3,
                probability=0.2,
            ),
            EnvironmentScenario(
                scenario_id="opportunity",
                name="Unexpected Opportunity",
                description="Major opportunity emerges",
                economic_conditions=0.6,
                market_volatility=0.4,
                health_factors=0.7,
                opportunity_availability=0.9,
                probability=0.1,
            ),
        ]
    
    def get_strategy_report(self) -> Dict[str, Any]:
        """Get strategy report."""
        
        if not self.cycles:
            return {"cycles": 0}
        
        latest = self.cycles[-1]
        
        return {
            "cycle_id": latest.cycle_id,
            "strategies_count": len(latest.strategies),
            "best_strategy": latest.best_strategy,
            "execution_recommended": latest.execution_recommended,
        }
    
    def get_comparison_report(self) -> Dict[str, Any]:
        """Get detailed comparison report."""
        
        if not self.cycles or not self.cycles[-1].comparison:
            return {}
        
        comp = self.cycles[-1].comparison
        
        return {
            "comparison_id": comp.comparison_id,
            "best_strategy": comp.best_strategy,
            "worst_strategy": comp.worst_strategy,
            "recommended": comp.recommended_strategy,
            "reason": comp.recommendation_reason,
            "strategies": [
                {
                    "id": o.strategy_id,
                    "score": o.overall_score,
                    "gain": o.expected_performance_gain,
                    "risk_change": o.risk_exposure_change,
                }
                for o in comp.strategy_outcomes
            ],
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get simulation statistics."""
        
        return {
            "total_cycles": len(self.cycles),
            "strategies_evaluated": sum(len(c.strategies) for c in self.cycles),
        }


# Global engine
_simulation_engine: Optional[SimulationEngine] = None


def get_simulation_engine() -> SimulationEngine:
    """Get the global simulation engine."""
    global _simulation_engine
    if _simulation_engine is None:
        _simulation_engine = SimulationEngine()
    return _simulation_engine
