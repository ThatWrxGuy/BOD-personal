"""Result Aggregator.

Summarizes experiment outputs and compares variants.
"""

from typing import List, Dict
from dataclasses import dataclass

from app.intelligence.autonomous_strategy_lab.lab_models import VariantPerformance


@dataclass
class LeaderboardEntry:
    """Leaderboard entry."""
    rank: int
    variant_id: str
    score: float
    expectancy: float
    stability: float


class ResultAggregator:
    """Aggregates and compares experiment results."""
    
    def __init__(self):
        self.leaderboards = {}
    
    def generate_leaderboard(
        self,
        results: Dict[str, VariantPerformance],
        sort_by: str = "expectancy",
        limit: int = 10,
    ) -> List[LeaderboardEntry]:
        """Generate variant leaderboard."""
        
        entries = []
        
        for variant_id, perf in results.items():
            if sort_by == "expectancy":
                score = perf.expectancy
            elif sort_by == "stability":
                score = perf.stability_score
            elif sort_by == "confidence":
                score = perf.confidence_score
            elif sort_by == "regime_fit":
                score = max(perf.regime_fit.values()) if perf.regime_fit else 0
            else:
                score = perf.expectancy
            
            entries.append(LeaderboardEntry(
                rank=0,
                variant_id=variant_id,
                score=score,
                expectancy=perf.expectancy,
                stability=perf.stability_score,
            ))
        
        # Sort and rank
        entries.sort(key=lambda e: e.score, reverse=True)
        
        for i, entry in enumerate(entries[:limit]):
            entry.rank = i + 1
        
        return entries[:limit]
    
    def generate_research_report(
        self,
        template_name: str,
        results: Dict[str, VariantPerformance],
    ) -> Dict:
        """Generate research report for a template."""
        
        leaderboard = self.generate_leaderboard(results, sort_by="expectancy")
        
        # Find best variant
        best = leaderboard[0] if leaderboard else None
        
        # Analyze regime performance
        regime_performance = {}
        for variant_id, perf in results.items():
            for regime, fit in perf.regime_fit.items():
                if regime not in regime_performance:
                    regime_performance[regime] = []
                regime_performance[regime].append(fit)
        
        avg_regime_perf = {
            regime: sum(fits) / len(fits) if fits else 0
            for regime, fits in regime_performance.items()
        }
        
        best_regime = max(avg_regime_perf.items(), key=lambda x: x[1])[0] if avg_regime_perf else "unknown"
        worst_regime = min(avg_regime_perf.items(), key=lambda x: x[1])[0] if avg_regime_perf else "unknown"
        
        return {
            "template": template_name,
            "total_variants": len(results),
            "best_variant": best.variant_id if best else None,
            "best_expectancy": best.expectancy if best else 0,
            "best_regime": best_regime,
            "worst_regime": worst_regime,
            "leaderboard": [e.to_dict() for e in leaderboard[:5]],
        }


def create_aggregator() -> ResultAggregator:
    """Create result aggregator."""
    return ResultAggregator()
