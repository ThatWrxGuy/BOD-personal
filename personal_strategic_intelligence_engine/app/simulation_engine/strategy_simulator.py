"""Strategy Simulator - Unified strategy simulation capability."""
import uuid
import random
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.simulation_engine.simulation_models import (
    SimulationResult,
    SimulationStatus,
    StrategyOutcome,
    DomainState,
)


class StrategySimulator:
    """Unified strategy simulation engine."""
    
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        if seed:
            random.seed(seed)
    
    def simulate_strategy(
        self,
        strategy_name: str,
        domains: Dict[str, DomainState],
        iterations: int = 1000,
    ) -> SimulationResult:
        """Simulate a strategy and return projected outcomes."""
        
        result_id = str(uuid.uuid4())[:8]
        start_time = datetime.utcnow()
        
        # Initialize results storage
        domain_totals = {d: [] for d in domains}
        
        # Run simulation iterations
        for _ in range(iterations):
            iteration_result = self._simulate_iteration(domains)
            for domain, score in iteration_result.items():
                domain_totals[domain].append(score)
        
        # Calculate statistics
        projected_domains = {}
        for domain, scores in domain_totals.items():
            avg = sum(scores) / len(scores) if scores else 5.0
            projected_domains[domain] = DomainState(
                domain=domain,
                current_score=domains.get(domain, DomainState(domain=domain)).current_score,
                target_score=domains.get(domain, DomainState(domain=domain)).target_score,
                risk_level=domains.get(domain, DomainState(domain=domain)).risk_level,
                momentum=avg - domains.get(domain, DomainState(domain=domain)).current_score,
            )
        
        # Build result
        result = SimulationResult(
            simulation_id=result_id,
            simulation_type="strategy",
            status=SimulationStatus.COMPLETED,
            started_at=start_time,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - start_time).total_seconds(),
            initial_domains=domains,
            projected_domains=projected_domains,
            expected_performance=sum(
                d.current_score for d in projected_domains.values()
            ) / len(projected_domains) if projected_domains else 0,
            risk_exposure=sum(
                d.risk_level for d in projected_domains.values()
            ) / len(projected_domains) if projected_domains else 0,
            goal_achievement_probability=0.75,
        )
        
        return result
    
    def _simulate_iteration(self, domains: Dict[str, DomainState]) -> Dict[str, float]:
        """Simulate a single iteration."""
        
        results = {}
        
        for domain_name, domain in domains.items():
            # Base score with some randomness
            base = domain.current_score
            
            # Add momentum effect
            momentum_effect = domain.momentum * 0.1
            
            # Add randomness (-1 to +1)
            noise = random.uniform(-1, 1)
            
            # Risk affects volatility
            risk_factor = domain.risk_level * 0.05
            
            result = base + momentum_effect + noise + risk_factor
            results[domain_name] = max(0, min(10, result))
        
        return results
    
    def compare_strategies(
        self,
        strategies: List[Dict[str, Any]],
        domains: Dict[str, DomainState],
    ) -> List[StrategyOutcome]:
        """Compare multiple strategies."""
        
        outcomes = []
        
        for i, strategy in enumerate(strategies):
            result = self.simulate_strategy(
                strategy.get("name", f"Strategy {i}"),
                domains,
                iterations=500,
            )
            
            outcome = StrategyOutcome(
                strategy_id=str(uuid.uuid4())[:8],
                strategy_name=strategy.get("name", f"Strategy {i}"),
                domain_impacts={
                    d: result.projected_domains.get(d, DomainState(domain=d)).momentum
                    for d in domains
                },
                expected_value=result.expected_performance,
                probability_of_success=result.goal_achievement_probability,
                rank=i + 1,
            )
            outcomes.append(outcome)
        
        # Sort by expected value
        outcomes.sort(key=lambda x: x.expected_value, reverse=True)
        
        # Update ranks
        for i, outcome in enumerate(outcomes):
            outcome.rank = i + 1
        
        return outcomes


# Singleton
_simulator: Optional[StrategySimulator] = None


def get_strategy_simulator(seed: Optional[int] = None) -> StrategySimulator:
    """Get the strategy simulator instance."""
    global _simulator
    if _simulator is None:
        _simulator = StrategySimulator(seed)
    return _simulator
