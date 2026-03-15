"""Monte Carlo Engine - Monte Carlo simulation for probabilistic outcomes."""
import uuid
import random
import math
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict

from app.simulation_engine.simulation_models import (
    SimulationResult,
    SimulationStatus,
    DomainState,
)


class MonteCarloEngine:
    """Monte Carlo simulation engine for probabilistic analysis."""
    
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        if seed:
            random.seed(seed)
    
    def run_simulation(
        self,
        domains: Dict[str, DomainState],
        num_iterations: int = 10000,
        time_horizon_days: int = 365,
    ) -> SimulationResult:
        """Run Monte Carlo simulation."""
        
        result_id = str(uuid.uuid4())[:8]
        start_time = datetime.utcnow()
        
        # Store results per domain
        domain_results = {d: [] for d in domains}
        
        # Run iterations
        for _ in range(num_iterations):
            iteration = self._run_iteration(domains, time_horizon_days)
            for domain, score in iteration.items():
                domain_results[domain].append(score)
        
        # Calculate statistics
        projected_domains = {}
        percentiles = defaultdict(dict)
        
        for domain_name, scores in domain_results.items():
            if not scores:
                continue
            
            sorted_scores = sorted(scores)
            n = len(sorted_scores)
            
            # Mean
            mean_score = sum(scores) / n
            
            # Standard deviation
            variance = sum((s - mean_score) ** 2 for s in scores) / n
            std_dev = math.sqrt(variance)
            
            # Percentiles
            p10 = sorted_scores[int(n * 0.1)]
            p50 = sorted_scores[int(n * 0.5)]
            p90 = sorted_scores[int(n * 0.9)]
            
            # Confidence interval
            ci_low = mean_score - (1.96 * std_dev / math.sqrt(n))
            ci_high = mean_score + (1.96 * std_dev / math.sqrt(n))
            
            percentiles[domain_name] = {
                "p10": p10,
                "p50": p50,
                "p90": p90,
                "mean": mean_score,
                "std_dev": std_dev,
            }
            
            projected_domains[domain_name] = DomainState(
                domain=domain_name,
                current_score=domains.get(domain_name, DomainState(domain=domain_name)).current_score,
                target_score=domains.get(domain_name, DomainState(domain=domain_name)).target_score,
                risk_level=domains.get(domain_name, DomainState(domain=domain_name)).risk_level,
                momentum=p50 - domains.get(domain_name, DomainState(domain=domain_name)).current_score,
            )
        
        # Calculate overall metrics
        all_scores = [s for scores in domain_results.values() for s in scores]
        overall_mean = sum(all_scores) / len(all_scores) if all_scores else 0
        
        # Probability of achieving target
        target_achievement = 0
        for domain_name, domain in domains.items():
            if domain_name in domain_results:
                achieved = sum(1 for s in domain_results[domain_name] if s >= domain.target_score)
                target_achievement += achieved / len(domain_results[domain_name])
        
        goal_prob = target_achievement / len(domains) if domains else 0
        
        # Calculate confidence interval
        all_sorted = sorted(all_scores)
        n = len(all_sorted)
        ci_low = all_sorted[int(n * 0.025)] if n > 0 else 0
        ci_high = all_sorted[int(n * 0.975)] if n > 0 else 10
        
        result = SimulationResult(
            simulation_id=result_id,
            simulation_type="monte_carlo",
            status=SimulationStatus.COMPLETED,
            started_at=start_time,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - start_time).total_seconds(),
            initial_domains=domains,
            projected_domains=projected_domains,
            expected_performance=overall_mean,
            risk_exposure=sum(d.risk_level for d in projected_domains.values()) / len(projected_domains) if projected_domains else 0,
            goal_achievement_probability=goal_prob,
            confidence_interval_low=ci_low,
            confidence_interval_high=ci_high,
            percentile_results={k: v["p50"] for k, v in percentiles.items()},
        )
        
        return result
    
    def _run_iteration(
        self,
        domains: Dict[str, DomainState],
        time_horizon_days: int,
    ) -> Dict[str, float]:
        """Run a single Monte Carlo iteration."""
        
        results = {}
        
        for domain_name, domain in domains.items():
            # Base score
            base = domain.current_score
            
            # Time factor (less impact for longer horizons due to uncertainty)
            time_factor = math.sqrt(time_horizon_days / 365)
            
            # Random walk with drift based on momentum
            drift = domain.momentum * time_factor * random.uniform(-0.5, 1.5)
            
            # Noise based on risk
            noise = domain.risk_level * random.gauss(0, 1) * 0.5
            
            # Resource allocation effect
            resource_effect = (domain.resource_allocation - 1) * random.uniform(0, 0.5)
            
            result = base + drift + noise + resource_effect
            results[domain_name] = max(0, min(10, result))
        
        return results
    
    def calculate_value_at_risk(
        self,
        domains: Dict[str, DomainState],
        confidence: float = 0.95,
        iterations: int = 1000,
    ) -> Dict[str, float]:
        """Calculate Value at Risk (VaR) for domains."""
        
        results = {d: [] for d in domains}
        
        for _ in range(iterations):
            iteration = self._run_iteration(domains, 365)
            for domain, score in iteration.items():
                results[domain].append(score)
        
        var_results = {}
        for domain, scores in results.items():
            if scores:
                sorted_scores = sorted(scores)
                idx = int((1 - confidence) * len(sorted_scores))
                var_results[domain] = sorted_scores[idx] if idx < len(sorted_scores) else 0
        
        return var_results


# Singleton
_engine: Optional[MonteCarloEngine] = None


def get_monte_carlo_engine(seed: Optional[int] = None) -> MonteCarloEngine:
    """Get the Monte Carlo engine instance."""
    global _engine
    if _engine is None:
        _engine = MonteCarloEngine(seed)
    return _engine
