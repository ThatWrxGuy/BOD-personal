"""Monte Carlo Engine - Main engine for Monte Carlo stress testing."""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.monte_carlo.monte_carlo_types import (
    MonteCarloBatch,
    StressTestReport,
    SimulationRandomizationConfig,
    StressTestPolicy,
    MonteCarloStatus,
    FailureEvent,
)
from app.monte_carlo.monte_carlo_runner import get_monte_carlo_runner
from app.monte_carlo.distribution_analyzer import get_distribution_analyzer
from app.monte_carlo.resilience_scorer import get_resilience_scorer


class MonteCarloEngine:
    """Main Monte Carlo stress testing engine."""
    
    def __init__(self, policy: Optional[StressTestPolicy] = None):
        self.policy = policy or StressTestPolicy()
        self.runner = get_monte_carlo_runner()
        self.analyzer = get_distribution_analyzer()
        self.scorer = get_resilience_scorer()
        self.batches: List[MonteCarloBatch] = []
    
    def run_stress_test(
        self,
        strategy_ids: List[str],
        initial_domains: Dict[str, float],
        initial_risks: Optional[Dict[str, float]] = None,
        num_runs: Optional[int] = None,
    ) -> StressTestReport:
        """Run a complete stress test."""
        
        # Validate inputs
        num_runs = num_runs or self.policy.default_num_runs
        num_runs = min(num_runs, self.policy.max_num_runs)
        
        # Create config
        config = SimulationRandomizationConfig(
            num_runs=num_runs,
        )
        
        # Run batch
        batch = self.runner.run_batch(
            strategy_ids=strategy_ids,
            initial_domains=initial_domains,
            initial_risks=initial_risks or {d: 5.0 for d in initial_domains},
            config=config,
        )
        
        self.batches.append(batch)
        
        # Analyze distributions
        distributions = self.analyzer.analyze_batch(batch)
        batch.distributions = distributions
        
        # Calculate resilience metrics
        resilience_metrics = []
        for dist in distributions:
            runs = [r for r in batch.runs if r.strategy_id == dist.strategy_id]
            metrics = self.scorer.calculate_resilience(dist, runs)
            resilience_metrics.append(metrics)
        
        batch.resilience_metrics = resilience_metrics
        
        # Generate report
        report = self._generate_report(batch, resilience_metrics)
        
        return report
    
    def _generate_report(
        self,
        batch: MonteCarloBatch,
        resilience_metrics,
    ) -> StressTestReport:
        """Generate stress test report."""
        
        report_id = str(uuid.uuid4())[:8]
        
        # Rankings
        best_avg = None
        most_resilient = None
        most_fragile = None
        
        if batch.distributions:
            # Best average
            best_avg = max(batch.distributions, key=lambda d: d.mean_score)
            best_avg = best_avg.strategy_id
        
        if resilience_metrics:
            # Most resilient
            most_resilient = max(resilience_metrics, key=lambda m: m.resilience_score)
            most_resilient = most_resilient.strategy_id
            
            # Most fragile
            fragile = [m for m in resilience_metrics if m.is_fragile]
            if fragile:
                most_fragile = fragile[0].strategy_id
        
        # Common failure modes
        failure_modes = self._identify_failure_modes(batch)
        
        # Recommendations
        recommendations = self._generate_recommendations(
            batch.distributions, resilience_metrics
        )
        
        # Calculate overall metrics
        all_scores = [r.final_score for r in batch.runs]
        overall_collapse = sum(1 for r in batch.runs if r.collapse_events) / len(batch.runs) if batch.runs else 0
        avg_resilience = sum(m.resilience_score for m in resilience_metrics) / len(resilience_metrics) if resilience_metrics else 0
        
        report = StressTestReport(
            report_id=report_id,
            batch_id=batch.batch_id,
            timestamp=datetime.utcnow(),
            strategy_results=batch.distributions,
            resilience_results=resilience_metrics,
            best_average_strategy=best_avg,
            most_resilient_strategy=most_resilient,
            most_fragile_strategy=most_fragile,
            failure_events=batch.failure_events,
            common_failure_modes=failure_modes,
            recommended_strategy=best_avg,
            strategy_adjustments=recommendations,
            total_runs=batch.total_runs,
            overall_collapse_probability=overall_collapse,
            average_resilience_score=avg_resilience,
        )
        
        return report
    
    def _identify_failure_modes(self, batch: MonteCarloBatch) -> List[str]:
        """Identify common failure modes."""
        
        modes = []
        
        # Count collapse by domain
        domain_collapses: Dict[str, int] = {}
        for run in batch.runs:
            for domain in run.collapse_events:
                domain_collapses[domain] = domain_collapses.get(domain, 0) + 1
        
        # Add common failures
        for domain, count in sorted(domain_collapses.items(), key=lambda x: x[1], reverse=True)[:3]:
            if count > batch.total_runs * 0.1:
                modes.append(f"{domain} collapse ({count} times)")
        
        return modes
    
    def _generate_recommendations(
        self,
        distributions,
        resilience_metrics,
    ) -> Dict[str, str]:
        """Generate strategy adjustment recommendations."""
        
        recommendations = {}
        
        for metrics in resilience_metrics:
            if metrics.is_fragile:
                recommendations[metrics.strategy_id] = f"Fragile: {'; '.join(metrics.fragility_reasons)}"
            elif metrics.resilience_score > 0.7:
                recommendations[metrics.strategy_id] = "Robust - maintain current approach"
            else:
                recommendations[metrics.strategy_id] = "Moderate - consider improvements"
        
        return recommendations
    
    def get_batch(self, batch_id: str) -> Optional[MonteCarloBatch]:
        """Get a specific batch."""
        for batch in self.batches:
            if batch.batch_id == batch_id:
                return batch
        return None
    
    def get_recent_batches(self, limit: int = 10) -> List[MonteCarloBatch]:
        """Get recent batches."""
        return self.batches[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics."""
        
        return {
            "total_batches": len(self.batches),
            "total_runs": sum(b.total_runs for b in self.batches),
            "recent_batches": len(self.batches[-10:]) if self.batches else 0,
        }


# Global engine
_engine: Optional[MonteCarloEngine] = None


def get_monte_carlo_engine() -> MonteCarloEngine:
    """Get the global Monte Carlo engine."""
    global _engine
    if _engine is None:
        _engine = MonteCarloEngine()
    return _engine
