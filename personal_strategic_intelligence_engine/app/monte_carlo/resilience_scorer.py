"""Resilience Scorer - Calculates resilience and stability metrics."""
from typing import List, Dict, Any

from app.monte_carlo.monte_carlo_types import (
    MonteCarloRun,
    ResilienceMetrics,
    StrategyDistribution,
    FailureEvent,
)


class ResilienceScorer:
    """Calculates resilience metrics for strategies."""
    
    def __init__(self):
        self.collapse_threshold = 3.0
    
    def calculate_resilience(
        self,
        distribution: StrategyDistribution,
        runs: List[MonteCarloRun],
    ) -> ResilienceMetrics:
        """Calculate resilience metrics for a strategy."""
        
        if not runs:
            return ResilienceMetrics(strategy_id=distribution.strategy_id)
        
        strategy_id = distribution.strategy_id
        
        # Extract data
        scores = [r.final_score for r in runs]
        collapse_counts = [len(r.collapse_events) for r in runs]
        
        # Resilience score: how well it maintains performance
        resilience = self._calculate_resilience_score(scores)
        
        # Collapse resistance: probability of no collapse
        collapse_resistance = 1 - distribution.collapse_probability
        
        # Recovery rate: how often it recovers from issues
        recovery_rate = self._calculate_recovery_rate(runs)
        
        # Intervention success rate
        intervention_success = self._calculate_intervention_success(runs)
        
        # Domain balance stability
        balance_stability = self._calculate_balance_stability(runs)
        
        # Variance in stability
        stability_variance = self._calculate_stability_variance(scores)
        
        # Worst case
        worst_case = min(scores) if scores else 0
        
        # Recovery probability
        recovery_prob = self._calculate_recovery_probability(runs)
        
        # Fragility detection
        is_fragile, reasons = self._detect_fragility(
            distribution, resilience, collapse_resistance
        )
        
        return ResilienceMetrics(
            strategy_id=strategy_id,
            resilience_score=resilience,
            collapse_resistance=collapse_resistance,
            recovery_rate=recovery_rate,
            intervention_success_rate=intervention_success,
            domain_balance_stability=balance_stability,
            stability_variance=stability_variance,
            worst_case_score=worst_case,
            recovery_probability=recovery_prob,
            is_fragile=is_fragile,
            fragility_reasons=reasons,
        )
    
    def _calculate_resilience_score(self, scores: List[float]) -> float:
        """Calculate resilience score (0-1)."""
        
        if not scores:
            return 0.0
        
        # Based on consistency of scores
        mean_score = sum(scores) / len(scores)
        
        # Calculate how many runs are above threshold
        stable_runs = sum(1 for s in scores if s >= mean_score * 0.8)
        
        return stable_runs / len(scores) if scores else 0
    
    def _calculate_recovery_rate(self, runs: List[MonteCarloRun]) -> float:
        """Calculate recovery rate."""
        
        if not runs:
            return 0.0
        
        # Count runs that had issues but recovered
        recovered = 0
        for run in runs:
            if run.collapse_events and run.final_score > 4.0:
                recovered += 1
        
        # Only count runs with collapses
        runs_with_collapse = sum(1 for r in runs if r.collapse_events)
        
        if runs_with_collapse == 0:
            return 1.0  # No collapses = perfect recovery
        
        return recovered / runs_with_collapse
    
    def _calculate_intervention_success(self, runs: List[MonteCarloRun]) -> float:
        """Calculate intervention success rate."""
        
        runs_with_intervention = [r for r in runs if r.intervention_events > 0]
        
        if not runs_with_intervention:
            return 0.5  # Neutral if no interventions
        
        # Success = improvement after intervention
        successful = 0
        for run in runs_with_intervention:
            if run.performance_gain > 0:
                successful += 1
        
        return successful / len(runs_with_intervention)
    
    def _calculate_balance_stability(self, runs: List[MonteCarloRun]) -> float:
        """Calculate domain balance stability."""
        
        if not runs:
            return 0.0
        
        # Look at variance of domain outcomes
        balance_scores = []
        
        for run in runs:
            domains = run.domain_outcomes
            if domains:
                domain_vals = list(domains.values())
                mean = sum(domain_vals) / len(domain_vals)
                variance = sum((x - mean) ** 2 for x in domain_vals) / len(domain_vals)
                
                # Lower variance = better balance
                balance = 1.0 - min(1.0, (variance ** 0.5) / 3)
                balance_scores.append(balance)
        
        return sum(balance_scores) / len(balance_scores) if balance_scores else 0
    
    def _calculate_stability_variance(self, scores: List[float]) -> float:
        """Calculate stability variance."""
        
        if len(scores) < 2:
            return 0.0
        
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        
        return variance
    
    def _calculate_recovery_probability(self, runs: List[MonteCarloRun]) -> float:
        """Calculate probability of recovery after collapse."""
        
        collapsed_runs = [r for r in runs if r.collapse_events]
        
        if not collapsed_runs:
            return 1.0
        
        recovered = sum(1 for r in collapsed_runs if r.final_score >= 4.0)
        
        return recovered / len(collapsed_runs)
    
    def _detect_fragility(
        self,
        distribution: StrategyDistribution,
        resilience: float,
        collapse_resistance: float,
    ) -> tuple[bool, List[str]]:
        """Detect if strategy is fragile."""
        
        reasons = []
        is_fragile = False
        
        # High collapse probability
        if distribution.collapse_probability > 0.3:
            is_fragile = True
            reasons.append(f"High collapse probability: {distribution.collapse_probability:.1%}")
        
        # Low resilience
        if resilience < 0.5:
            is_fragile = True
            reasons.append(f"Low resilience score: {resilience:.2f}")
        
        # High variance
        if distribution.std_deviation > 2.0:
            is_fragile = True
            reasons.append(f"High outcome variance: {distribution.std_deviation:.2f}")
        
        # Poor worst case
        if distribution.percentile_5 < 3.0:
            is_fragile = True
            reasons.append(f"Poor worst-case outcome: {distribution.percentile_5:.1f}")
        
        return is_fragile, reasons
    
    def rank_by_resilience(
        self,
        metrics: List[ResilienceMetrics],
    ) -> List[ResilienceMetrics]:
        """Rank strategies by resilience."""
        
        return sorted(
            metrics,
            key=lambda m: m.resilience_score,
            reverse=True
        )


# Global scorer
_scorer = None


def get_resilience_scorer() -> ResilienceScorer:
    """Get the global resilience scorer."""
    global _scorer
    if _scorer is None:
        _scorer = ResilienceScorer()
    return _scorer
