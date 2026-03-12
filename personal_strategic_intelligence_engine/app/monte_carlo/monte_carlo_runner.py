"""Monte Carlo Runner - Runs randomized strategic simulations."""
import uuid
import random
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.monte_carlo.monte_carlo_types import (
    MonteCarloRun,
    MonteCarloBatch,
    SimulationRandomizationConfig,
    MonteCarloStatus,
)


class MonteCarloRunner:
    """Runs Monte Carlo simulation batches."""
    
    def __init__(self):
        self.default_domains = [
            "health", "wealth", "career", "relationships",
            "learning", "operations", "personal_development", "strategic_projects"
        ]
    
    def run_batch(
        self,
        strategy_ids: List[str],
        initial_domains: Dict[str, float],
        initial_risks: Dict[str, float],
        config: Optional[SimulationRandomizationConfig] = None,
    ) -> MonteCarloBatch:
        """Run a batch of Monte Carlo simulations."""
        
        config = config or SimulationRandomizationConfig()
        batch_id = str(uuid.uuid4())[:8]
        
        batch = MonteCarloBatch(
            batch_id=batch_id,
            status=MonteCarloStatus.RUNNING,
            config=config,
            strategy_ids=strategy_ids,
            created_at=datetime.utcnow(),
        )
        
        # Run simulations for each strategy
        for strategy_id in strategy_ids:
            for run_num in range(config.num_runs):
                # Create unique seed for this run
                run_seed = config.seed + run_num * 1000 + hash(strategy_id) % 1000
                
                # Run simulation
                run = self._run_single_simulation(
                    batch_id=batch_id,
                    strategy_id=strategy_id,
                    run_number=run_num,
                    initial_domains=initial_domains,
                    initial_risks=initial_risks,
                    config=config,
                    seed=run_seed,
                )
                
                batch.runs.append(run)
        
        batch.total_runs = len(batch.runs)
        batch.completed_at = datetime.utcnow()
        batch.status = MonteCarloStatus.COMPLETED
        
        return batch
    
    def _run_single_simulation(
        self,
        batch_id: str,
        strategy_id: str,
        run_number: int,
        initial_domains: Dict[str, float],
        initial_risks: Dict[str, float],
        config: SimulationRandomizationConfig,
        seed: int,
    ) -> MonteCarloRun:
        """Run a single Monte Carlo simulation."""
        
        rng = random.Random(seed)
        
        run_id = str(uuid.uuid4())[:8]
        
        # Create random state
        random_state = {
            "economic": rng.random(),
            "opportunity": rng.random(),
            "disruption": rng.random(),
            "volatility": rng.random(),
            "intervention_variance": rng.random() * config.intervention_success_variance,
        }
        
        # Copy initial state
        domains = initial_domains.copy()
        risks = initial_risks.copy()
        
        # Track events
        collapse_events = []
        intervention_count = 0
        
        # Apply randomization factors
        economic = random_state["economic"]
        opportunity = random_state["opportunity"]
        disruption = random_state["disruption"]
        
        # Simulate 90-day horizon
        for day in range(90):
            # Random events based on probabilities
            if rng.random() < config.disruption_probability * disruption:
                # Health disruption
                target = rng.choice(list(domains.keys()))
                domains[target] = max(0, domains[target] - rng.random() * 2)
                if domains[target] < 3:
                    collapse_events.append(target)
            
            if rng.random() < config.opportunity_frequency * opportunity:
                # Positive opportunity
                target = rng.choice(list(domains.keys()))
                domains[target] = min(10, domains[target] + rng.random() * 1.5)
            
            # Economic effects on wealth
            if "wealth" in domains:
                wealth_change = (economic - 0.5) * 0.3
                domains["wealth"] = max(0, min(10, domains["wealth"] + wealth_change))
            
            # Intervention if domain is struggling
            for domain in list(domains.keys()):
                if domains[domain] < 4 and rng.random() < 0.1:
                    # Simulate intervention
                    recovery = rng.random() * 1.5 * (1 + random_state["intervention_variance"])
                    domains[domain] = min(10, domains[domain] + recovery)
                    intervention_count += 1
        
        # Calculate final metrics
        final_score = sum(domains.values()) / len(domains)
        performance_gain = final_score - (sum(initial_domains.values()) / len(initial_domains))
        
        # Calculate risk exposure
        final_risks = {d: max(0, 6 - domains.get(d, 5)) for d in domains}
        risk_exposure = sum(final_risks.values()) / len(final_risks)
        
        # Stability score
        stability = 1.0
        if collapse_events:
            stability = max(0, 1 - len(collapse_events) / len(domains))
        
        return MonteCarloRun(
            run_id=run_id,
            batch_id=batch_id,
            strategy_id=strategy_id,
            run_number=run_number,
            seed=seed,
            random_state=random_state,
            domain_outcomes=domains,
            risk_outcomes=final_risks,
            collapse_events=collapse_events,
            intervention_events=intervention_count,
            final_score=final_score,
            performance_gain=performance_gain,
            risk_exposure=risk_exposure,
            stability_score=stability,
        )


# Global runner
_runner: Optional[MonteCarloRunner] = None


def get_monte_carlo_runner() -> MonteCarloRunner:
    """Get the global Monte Carlo runner."""
    global _runner
    if _runner is None:
        _runner = MonteCarloRunner()
    return _runner
