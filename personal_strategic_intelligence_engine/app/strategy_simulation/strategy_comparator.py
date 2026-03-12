"""Strategy Comparator - Compares multiple strategic options."""
import uuid
from typing import List, Dict, Any, Optional

from app.strategy_simulation.simulation_types import (
    StrategyDecision,
    SimulatedOutcome,
    StrategyComparison,
)


class StrategyComparator:
    """Compares multiple strategic options."""
    
    def __init__(self):
        pass
    
    def compare_strategies(
        self,
        baseline_outcome: SimulatedOutcome,
        strategy_outcomes: List[SimulatedOutcome],
    ) -> StrategyComparison:
        """Compare multiple strategy outcomes."""
        
        comparison_id = str(uuid.uuid4())[:8]
        
        # Sort by overall score
        sorted_outcomes = sorted(
            strategy_outcomes,
            key=lambda x: x.overall_score,
            reverse=True
        )
        
        best = sorted_outcomes[0] if sorted_outcomes else None
        worst = sorted_outcomes[-1] if sorted_outcomes else None
        
        # Generate recommendation
        recommended = None
        reason = ""
        
        if best:
            recommended = best.strategy_id
            
            # Generate reason
            if best.expected_performance_gain > 1:
                reason = f"Highest expected performance gain: +{best.expected_performance_gain:.1f}"
            elif best.risk_exposure_change > 0:
                reason = f"Best risk reduction: {best.risk_exposure_change:.1f}"
            else:
                reason = f"Best overall score: {best.overall_score:.1f}"
        
        return StrategyComparison(
            comparison_id=comparison_id,
            baseline_outcome=baseline_outcome,
            strategy_outcomes=strategy_outcomes,
            best_strategy=best.strategy_id if best else None,
            worst_strategy=worst.strategy_id if worst else None,
            recommended_strategy=recommended,
            recommendation_reason=reason,
        )
    
    def rank_strategies(
        self,
        outcomes: List[SimulatedOutcome],
    ) -> List[Dict[str, Any]]:
        """Rank strategies by various criteria."""
        
        rankings = []
        
        for outcome in outcomes:
            rankings.append({
                "strategy_id": outcome.strategy_id,
                "overall_score": outcome.overall_score,
                "performance_gain": outcome.expected_performance_gain,
                "risk_change": outcome.risk_exposure_change,
            })
        
        # Sort by overall score
        rankings.sort(key=lambda x: x["overall_score"], reverse=True)
        
        return rankings
    
    def get_detailed_comparison(
        self,
        outcomes: List[SimulatedOutcome],
    ) -> Dict[str, Any]:
        """Get detailed comparison of strategies."""
        
        if not outcomes:
            return {"strategies": []}
        
        # Get average metrics
        avg_gain = sum(o.expected_performance_gain for o in outcomes) / len(outcomes)
        avg_risk = sum(o.risk_exposure_change for o in outcomes) / len(outcomes)
        avg_score = sum(o.overall_score for o in outcomes) / len(outcomes)
        
        return {
            "average_performance_gain": avg_gain,
            "average_risk_change": avg_risk,
            "average_overall_score": avg_score,
            "strategies": [
                {
                    "id": o.strategy_id,
                    "score": o.overall_score,
                    "gain": o.expected_performance_gain,
                    "risk": o.risk_exposure_change,
                }
                for o in outcomes
            ],
            "rankings": self.rank_strategies(outcomes),
        }


# Global comparator
_strategy_comparator: Optional[StrategyComparator] = None


def get_strategy_comparator() -> StrategyComparator:
    """Get the global strategy comparator."""
    global _strategy_comparator
    if _strategy_comparator is None:
        _strategy_comparator = StrategyComparator()
    return _strategy_comparator
