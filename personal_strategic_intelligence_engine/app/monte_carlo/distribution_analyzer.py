"""Distribution Analyzer - Analyzes distributions of Monte Carlo outcomes."""
from typing import List, Dict, Any
import statistics

from app.monte_carlo.monte_carlo_types import (
    MonteCarloRun,
    StrategyDistribution,
    MonteCarloBatch,
)


class DistributionAnalyzer:
    """Analyzes outcome distributions from Monte Carlo runs."""
    
    def analyze_strategy(self, runs: List[MonteCarloRun]) -> StrategyDistribution:
        """Analyze distribution for a single strategy."""
        
        if not runs:
            return StrategyDistribution(strategy_id="unknown")
        
        strategy_id = runs[0].strategy_id
        
        # Extract scores
        scores = [r.final_score for r in runs]
        
        if not scores:
            return StrategyDistribution(strategy_id=strategy_id)
        
        # Basic statistics
        mean_score = statistics.mean(scores)
        median_score = statistics.median(scores)
        std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
        
        # Percentiles
        sorted_scores = sorted(scores)
        n = len(sorted_scores)
        
        def percentile(p):
            idx = int(n * p)
            return sorted_scores[min(idx, n - 1)]
        
        p5 = percentile(0.05)
        p25 = percentile(0.25)
        p75 = percentile(0.75)
        p95 = percentile(0.95)
        
        # Collapse analysis
        collapse_count = sum(1 for r in runs if r.collapse_events)
        collapse_prob = collapse_count / len(runs) if runs else 0
        
        # Domain collapse frequency
        domain_collapse: Dict[str, int] = {}
        for run in runs:
            for domain in run.collapse_events:
                domain_collapse[domain] = domain_collapse.get(domain, 0) + 1
        
        domain_freq = {
            d: count / len(runs) 
            for d, count in domain_collapse.items()
        }
        
        return StrategyDistribution(
            strategy_id=strategy_id,
            num_runs=len(runs),
            mean_score=mean_score,
            median_score=median_score,
            std_deviation=std_dev,
            min_score=min(scores),
            max_score=max(scores),
            percentile_5=p5,
            percentile_25=p25,
            percentile_75=p75,
            percentile_95=p95,
            collapse_count=collapse_count,
            collapse_probability=collapse_prob,
            domain_collapse_frequency=domain_freq,
        )
    
    def analyze_batch(self, batch: MonteCarloBatch) -> List[StrategyDistribution]:
        """Analyze distributions for all strategies in a batch."""
        
        # Group runs by strategy
        by_strategy: Dict[str, List[MonteCarloRun]] = {}
        
        for run in batch.runs:
            if run.strategy_id not in by_strategy:
                by_strategy[run.strategy_id] = []
            by_strategy[run.strategy_id].append(run)
        
        # Analyze each strategy
        distributions = []
        for strategy_id, runs in by_strategy.items():
            dist = self.analyze_strategy(runs)
            distributions.append(dist)
        
        # Sort by mean score
        distributions.sort(key=lambda d: d.mean_score, reverse=True)
        
        return distributions
    
    def get_summary_stats(self, batch: MonteCarloBatch) -> Dict[str, Any]:
        """Get summary statistics for a batch."""
        
        if not batch.runs:
            return {"total_runs": 0}
        
        all_scores = [r.final_score for r in batch.runs]
        
        return {
            "total_runs": len(batch.runs),
            "strategies_tested": len(set(r.strategy_id for r in batch.runs)),
            "overall_mean": statistics.mean(all_scores),
            "overall_std": statistics.stdev(all_scores) if len(all_scores) > 1 else 0,
            "total_collapses": sum(1 for r in batch.runs if r.collapse_events),
            "total_interventions": sum(r.intervention_events for r in batch.runs),
        }


# Global analyzer
_analyzer = None


def get_distribution_analyzer() -> DistributionAnalyzer:
    """Get the global distribution analyzer."""
    global _analyzer
    if _analyzer is None:
        _analyzer = DistributionAnalyzer()
    return _analyzer
