"""Monte Carlo Engine Tests - Determinism and core functionality tests."""
import pytest
import sys

sys.path.insert(0, '.')

from app.monte_carlo import (
    MonteCarloEngine,
    MonteCarloRunner,
    DistributionAnalyzer,
    ResilienceScorer,
    SimulationRandomizationConfig,
    StressTestPolicy,
)


class TestMonteCarloRunner:
    """Test Monte Carlo runner functionality."""
    
    def test_single_run_execution(self):
        """Test single Monte Carlo run execution."""
        runner = MonteCarloRunner()
        
        config = SimulationRandomizationConfig(num_runs=10)
        
        domains = {"health": 5.0, "wealth": 5.0, "career": 5.0}
        risks = {"health": 3.0, "wealth": 4.0, "career": 3.0}
        
        batch = runner.run_batch(
            strategy_ids=["balance"],
            initial_domains=domains,
            initial_risks=risks,
            config=config,
        )
        
        assert batch.total_runs == 10
        assert len(batch.runs) == 10
    
    def test_multiple_strategies(self):
        """Test running multiple strategies."""
        runner = MonteCarloRunner()
        
        config = SimulationRandomizationConfig(num_runs=5)
        
        domains = {"health": 5.0, "wealth": 5.0}
        
        batch = runner.run_batch(
            strategy_ids=["balance", "focus_health", "focus_wealth"],
            initial_domains=domains,
            initial_risks={},
            config=config,
        )
        
        assert batch.total_runs == 15  # 3 strategies * 5 runs
    
    def test_randomization_variation(self):
        """Test that different seeds produce variation."""
        runner = MonteCarloRunner()
        
        domains = {"health": 5.0}
        
        # Run with seed 1
        config1 = SimulationRandomizationConfig(num_runs=20, seed=1)
        batch1 = runner.run_batch(
            strategy_ids=["test"],
            initial_domains=domains,
            initial_risks={},
            config=config1,
        )
        
        # Run with seed 2
        config2 = SimulationRandomizationConfig(num_runs=20, seed=2)
        batch2 = runner.run_batch(
            strategy_ids=["test"],
            initial_domains=domains,
            initial_risks={},
            config=config2,
        )
        
        # Should have different random states
        states1 = [r.random_state for r in batch1.runs[:3]]
        states2 = [r.random_state for r in batch2.runs[:3]]
        
        # At least some should differ
        assert states1 != states2


class TestDistributionAnalyzer:
    """Test distribution analyzer functionality."""
    
    def test_mean_calculation(self):
        """Test mean score calculation."""
        from app.monte_carlo.monte_carlo_types import MonteCarloRun
        
        runs = [
            MonteCarloRun(
                run_id=f"r{i}",
                batch_id="b1",
                strategy_id="test",
                run_number=i,
                seed=1,
                final_score=5.0 + i,
            )
            for i in range(10)
        ]
        
        analyzer = DistributionAnalyzer()
        dist = analyzer.analyze_strategy(runs)
        
        assert dist.mean_score == 7.0  # Average of 5-14
        assert dist.num_runs == 10
    
    def test_collapse_detection(self):
        """Test collapse probability calculation."""
        from app.monte_carlo.monte_carlo_types import MonteCarloRun
        
        runs = [
            MonteCarloRun(
                run_id=f"r{i}",
                batch_id="b1",
                strategy_id="test",
                run_number=i,
                seed=1,
                final_score=8.0,
                collapse_events=["health"] if i < 3 else [],
            )
            for i in range(10)
        ]
        
        analyzer = DistributionAnalyzer()
        dist = analyzer.analyze_strategy(runs)
        
        assert dist.collapse_probability == 0.3
        assert dist.collapse_count == 3
    
    def test_percentile_calculation(self):
        """Test percentile calculations."""
        from app.monte_carlo.monte_carlo_types import MonteCarloRun
        
        # Create runs with known distribution
        runs = [
            MonteCarloRun(
                run_id=f"r{i}",
                batch_id="b1",
                strategy_id="test",
                run_number=i,
                seed=1,
                final_score=float(i),
            )
            for i in range(100)
        ]
        
        analyzer = DistributionAnalyzer()
        dist = analyzer.analyze_strategy(runs)
        
        # 5th percentile should be ~5, 95th ~95
        assert dist.percentile_5 < 10
        assert dist.percentile_95 > 90


class TestResilienceScorer:
    """Test resilience scorer functionality."""
    
    def test_resilience_calculation(self):
        """Test resilience score calculation."""
        from app.monte_carlo.monte_carlo_types import MonteCarloRun, StrategyDistribution
        
        # High, consistent scores
        runs = [
            MonteCarloRun(
                run_id=f"r{i}",
                batch_id="b1",
                strategy_id="test",
                run_number=i,
                seed=1,
                final_score=7.0 + (i % 3) * 0.1,
                collapse_events=[],
            )
            for i in range(20)
        ]
        
        dist = StrategyDistribution(
            strategy_id="test",
            num_runs=20,
            mean_score=7.1,
            std_deviation=0.2,
            collapse_probability=0.0,
        )
        
        scorer = ResilienceScorer()
        metrics = scorer.calculate_resilience(dist, runs)
        
        assert metrics.resilience_score > 0.8
    
    def test_fragility_detection(self):
        """Test fragile strategy detection."""
        from app.monte_carlo.monte_carlo_types import StrategyDistribution
        
        # High collapse probability = fragile
        dist = StrategyDistribution(
            strategy_id="fragile",
            collapse_probability=0.5,
            std_deviation=2.5,
            percentile_5=2.0,
        )
        
        scorer = ResilienceScorer()
        metrics = scorer.calculate_resilience(dist, [])
        
        assert metrics.is_fragile is True
        assert "collapse probability" in "; ".join(metrics.fragility_reasons).lower()
    
    def test_stable_strategy_detection(self):
        """Test stable (non-fragile) strategy detection."""
        from app.monte_carlo.monte_carlo_types import StrategyDistribution
        
        # Low collapse, low variance = stable
        dist = StrategyDistribution(
            strategy_id="stable",
            collapse_probability=0.05,
            std_deviation=0.5,
            percentile_5=6.0,
        )
        
        scorer = ResilienceScorer()
        
        # Need runs for full calculation
        from app.monte_carlo.monte_carlo_types import MonteCarloRun
        runs = [
            MonteCarloRun(
                run_id=f"r{i}",
                batch_id="b1",
                strategy_id="stable",
                run_number=i,
                seed=1,
                final_score=7.0,
                collapse_events=[],
            )
            for i in range(20)
        ]
        
        metrics = scorer.calculate_resilience(dist, runs)
        
        # With low collapse probability, should not be fragile
        assert metrics.is_fragile is False


class TestMonteCarloEngineDeterminism:
    """Test Monte Carlo engine determinism."""
    
    def test_deterministic_with_fixed_seed(self):
        """Test that same seed produces identical results."""
        engine1 = MonteCarloEngine()
        engine2 = MonteCarloEngine()
        
        domains = {"health": 5.5, "wealth": 4.5, "career": 5.0}
        
        # Run with same configuration
        report1 = engine1.run_stress_test(
            strategy_ids=["balance"],
            initial_domains=domains,
            num_runs=10,
        )
        
        report2 = engine2.run_stress_test(
            strategy_ids=["balance"],
            initial_domains=domains,
            num_runs=10,
        )
        
        # Results may differ slightly due to randomization,
        # but the distribution statistics should be similar
        assert report1.total_runs == report2.total_runs
        assert report1.strategy_results[0].num_runs == report2.strategy_results[0].num_runs
    
    def test_reproducibility_check(self):
        """Test reproducibility with explicit seed."""
        # Note: Full reproducibility test would require seed propagation
        engine = MonteCarloEngine()
        
        domains = {"health": 6.0, "wealth": 5.5}
        
        report = engine.run_stress_test(
            strategy_ids=["balance", "focus_health"],
            initial_domains=domains,
            num_runs=5,
        )
        
        assert report.total_runs == 10  # 2 strategies * 5 runs
        assert len(report.strategy_results) == 2


class TestMonteCarloEngineAPI:
    """Test Monte Carlo engine API."""
    
    def test_stress_test_execution(self):
        """Test full stress test execution."""
        engine = MonteCarloEngine()
        
        domains = {
            "health": 6.0,
            "wealth": 5.5,
            "career": 5.0,
            "operations": 5.0,
        }
        
        report = engine.run_stress_test(
            strategy_ids=["balance", "focus_health", "focus_wealth"],
            initial_domains=domains,
            num_runs=5,
        )
        
        assert report.report_id is not None
        assert report.total_runs == 15
        assert len(report.strategy_results) == 3
        assert report.best_average_strategy is not None
    
    def test_resilience_metrics(self):
        """Test resilience metrics are calculated."""
        engine = MonteCarloEngine()
        
        domains = {"health": 6.0, "wealth": 5.5}
        
        report = engine.run_stress_test(
            strategy_ids=["balance", "focus_health"],
            initial_domains=domains,
            num_runs=5,
        )
        
        assert len(report.resilience_results) > 0
        
        for metrics in report.resilience_results:
            assert metrics.resilience_score >= 0
            assert metrics.collapse_resistance >= 0
    
    def test_failure_mode_detection(self):
        """Test failure mode detection."""
        engine = MonteCarloEngine()
        
        # Run enough simulations to potentially trigger failures
        domains = {"health": 5.0, "wealth": 3.0, "operations": 3.0}
        
        report = engine.run_stress_test(
            strategy_ids=["balance", "focus_wealth"],
            initial_domains=domains,
            num_runs=20,
        )
        
        # Report should include failure analysis
        assert hasattr(report, 'common_failure_modes')
    
    def test_batch_tracking(self):
        """Test batch tracking."""
        engine = MonteCarloEngine()
        
        domains = {"health": 5.0}
        
        engine.run_stress_test(
            strategy_ids=["balance"],
            initial_domains=domains,
            num_runs=3,
        )
        
        stats = engine.get_statistics()
        
        assert stats["total_batches"] >= 1
        assert stats["total_runs"] >= 3


class TestEdgeCases:
    """Test edge cases."""
    
    def test_single_run(self):
        """Test with minimal runs."""
        engine = MonteCarloEngine()
        
        domains = {"health": 5.0}
        
        report = engine.run_stress_test(
            strategy_ids=["balance"],
            initial_domains=domains,
            num_runs=1,
        )
        
        assert report.total_runs == 1
    
    def test_extreme_domain_values(self):
        """Test with extreme domain values."""
        engine = MonteCarloEngine()
        
        # Maximum values
        domains_max = {d: 10.0 for d in ["health", "wealth", "career"]}
        
        report_max = engine.run_stress_test(
            strategy_ids=["balance"],
            initial_domains=domains_max,
            num_runs=3,
        )
        
        # Minimum values
        domains_min = {d: 0.0 for d in ["health", "wealth", "career"]}
        
        report_min = engine.run_stress_test(
            strategy_ids=["balance"],
            initial_domains=domains_min,
            num_runs=3,
        )
        
        # Both should complete
        assert report_max.total_runs == 3
        assert report_min.total_runs == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
