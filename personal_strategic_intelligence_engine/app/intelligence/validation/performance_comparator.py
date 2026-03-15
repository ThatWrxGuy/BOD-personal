"""Performance Comparator - Compares baseline vs system results."""
from typing import List

from app.intelligence.validation.simulation_models import (
    SimulationResult,
    PerformanceComparison,
)


class PerformanceComparator:
    """Compares baseline and system simulation results."""
    
    def __init__(self):
        self.comparisons: List[PerformanceComparison] = []
    
    def compare(
        self,
        baseline_result: SimulationResult,
        system_result: SimulationResult,
    ) -> PerformanceComparison:
        """Compare baseline vs system results."""
        
        # Calculate deltas
        improvement_delta = system_result.outcome_score - baseline_result.outcome_score
        goal_improvement = system_result.goal_completion - baseline_result.goal_completion
        risk_reduction = baseline_result.risk_exposure - system_result.risk_exposure
        efficiency_gain = system_result.execution_efficiency - baseline_result.execution_efficiency
        decision_quality_improvement = system_result.decision_quality - baseline_result.decision_quality
        
        # Determine winner
        system_wins = improvement_delta > 0
        margin = abs(improvement_delta)
        
        comparison = PerformanceComparison(
            scenario_id=baseline_result.scenario_id,
            scenario_name="",  # Would be filled in
            baseline_score=baseline_result.outcome_score,
            system_score=system_result.outcome_score,
            improvement_delta=improvement_delta,
            goal_improvement=goal_improvement,
            risk_reduction=risk_reduction,
            efficiency_gain=efficiency_gain,
            decision_quality_improvement=decision_quality_improvement,
            system_wins=system_wins,
            margin=margin,
        )
        
        self.comparisons.append(comparison)
        
        return comparison
    
    def compare_batch(
        self,
        baseline_results: List[SimulationResult],
        system_results: List[SimulationResult],
    ) -> List[PerformanceComparison]:
        """Compare multiple results."""
        
        comparisons = []
        
        # Match by scenario ID
        baseline_by_id = {r.scenario_id: r for r in baseline_results}
        system_by_id = {r.scenario_id: r for r in system_results}
        
        for scenario_id in baseline_by_id:
            if scenario_id in system_by_id:
                comparison = self.compare(
                    baseline_by_id[scenario_id],
                    system_by_id[scenario_id],
                )
                comparisons.append(comparison)
        
        return comparisons
    
    def get_summary(self) -> dict:
        """Get summary statistics."""
        
        if not self.comparisons:
            return {
                "total_comparisons": 0,
                "system_wins": 0,
                "baseline_wins": 0,
                "average_improvement": 0,
            }
        
        system_wins = sum(1 for c in self.comparisons if c.system_wins)
        baseline_wins = len(self.comparisons) - system_wins
        
        avg_improvement = sum(c.improvement_delta for c in self.comparisons) / len(self.comparisons)
        avg_risk_reduction = sum(c.risk_reduction for c in self.comparisons) / len(self.comparisons)
        
        return {
            "total_comparisons": len(self.comparisons),
            "system_wins": system_wins,
            "baseline_wins": baseline_wins,
            "average_improvement": avg_improvement,
            "average_risk_reduction": avg_risk_reduction,
        }


_comparator: PerformanceComparator = None


def get_performance_comparator() -> PerformanceComparator:
    """Get the global performance comparator."""
    global _comparator
    if _comparator is None:
        _comparator = PerformanceComparator()
    return _comparator
