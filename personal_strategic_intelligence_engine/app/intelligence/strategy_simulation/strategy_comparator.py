"""Strategy Comparator.

Compares candidate strategies against baseline.
"""

from typing import List, Dict
import uuid

from app.intelligence.strategy_simulation.simulation_models import (
    SimulationResult,
    StrategyComparison,
)


class StrategyComparator:
    """Compares candidate strategies to baseline."""
    
    def __init__(self):
        self.baseline_id = "strat-baseline-001"
    
    def compare(
        self,
        baseline: SimulationResult,
        candidate: SimulationResult,
    ) -> StrategyComparison:
        """Compare candidate to baseline."""
        
        baseline_metrics = baseline.metrics
        candidate_metrics = candidate.metrics
        
        # Calculate improvements
        expectancy_improvement = candidate_metrics.expectancy - baseline_metrics.expectancy
        sharpe_improvement = candidate_metrics.sharpe_ratio - baseline_metrics.sharpe_ratio
        drawdown_improvement = baseline_metrics.max_drawdown - candidate_metrics.max_drawdown
        
        # Determine winner
        if expectancy_improvement > 0.1 and sharpe_improvement > 0:
            winner = "candidate"
        elif expectancy_improvement < -0.1:
            winner = "baseline"
        else:
            winner = "tie"
        
        # Generate recommendation
        if winner == "candidate":
            recommendation = (
                f"Candidate outperforms baseline by {expectancy_improvement:.2f} in expectancy. "
                f"Recommend adoption pending governance approval."
            )
        elif winner == "baseline":
            recommendation = (
                f"Baseline outperforms candidate by {abs(expectancy_improvement):.2f}. "
                f"Recommend keeping current strategy."
            )
        else:
            recommendation = (
                "Strategies perform similarly. Recommend further analysis "
                "before making changes."
            )
        
        return StrategyComparison(
            comparison_id=str(uuid.uuid4()),
            baseline_strategy=baseline.strategy_config,
            candidate_strategy=candidate.strategy_config,
            baseline_metrics=baseline_metrics,
            candidate_metrics=candidate_metrics,
            expectancy_improvement=expectancy_improvement,
            sharpe_improvement=sharpe_improvement,
            drawdown_improvement=drawdown_improvement,
            winner=winner,
            recommendation=recommendation,
        )
    
    def rank_candidates(
        self,
        baseline: SimulationResult,
        candidates: List[SimulationResult],
    ) -> List[StrategyComparison]:
        """Rank candidates against baseline."""
        
        comparisons = []
        
        for candidate in candidates:
            comparison = self.compare(baseline, candidate)
            comparisons.append(comparison)
        
        # Sort by expectancy improvement
        comparisons.sort(key=lambda c: c.expectancy_improvement, reverse=True)
        
        return comparisons


def create_comparator() -> StrategyComparator:
    """Create a new strategy comparator."""
    return StrategyComparator()
