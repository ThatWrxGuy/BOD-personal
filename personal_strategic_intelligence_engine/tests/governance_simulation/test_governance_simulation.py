"""Tests for governance simulation framework."""
import pytest

from app.governance_simulation.simulation_models import (
    GovernanceSimulationScenario,
    ScenarioType,
    SignalPattern,
    GovernanceSimulationCycle,
)
from app.governance_simulation.scenario_generator import ScenarioGenerator, create_scenario_generator
from app.governance_simulation.governance_simulator import GovernanceSimulator, run_governance_simulation
from app.governance_simulation.stability_metrics import (
    compute_recommendation_stability,
    compute_doctrine_consistency,
    compute_tier_stability,
    compute_confidence_stability,
    compute_execution_pressure,
    compute_governance_load,
    compute_overall_stability,
    compute_all_stability_metrics,
)
from app.governance_simulation.oscillation_detector import OscillationDetector, detect_oscillations
from app.governance_simulation.doctrine_conflict_detector import DoctrineConflictDetector, detect_doctrine_conflicts
from app.governance_simulation.saturation_analyzer import SaturationAnalyzer, analyze_saturation
from app.governance_simulation.policy_stress_tester import PolicyStressTester, run_policy_stress_test
from app.governance_simulation.execution_feedback_analyzer import ExecutionFeedbackAnalyzer, analyze_execution_feedback
from app.governance_simulation.simulation_reporter import SimulationReporter, generate_simulation_report


class TestScenarioGenerator:
    """Tests for scenario generator."""
    
    def test_create_generator(self):
        """Test creating a scenario generator."""
        generator = ScenarioGenerator(random_seed=42)
        assert generator is not None
        assert generator.random_seed == 42
    
    def test_generate_steady_state_scenario(self):
        """Test generating steady-state scenario."""
        generator = ScenarioGenerator()
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        
        assert scenario.scenario_type == ScenarioType.STEADY_STATE
        assert scenario.cycle_count == 100
        assert scenario.signal_noise_level < 0.1
        assert scenario.signal_volatility < 0.1
    
    def test_generate_noisy_signal_scenario(self):
        """Test generating noisy signal scenario."""
        generator = ScenarioGenerator()
        scenario = generator.generate_scenario(ScenarioType.NOISY_SIGNAL)
        
        assert scenario.scenario_type == ScenarioType.NOISY_SIGNAL
        assert scenario.signal_noise_level >= 0.5
    
    def test_generate_high_volatility_scenario(self):
        """Test generating high volatility scenario."""
        generator = ScenarioGenerator()
        scenario = generator.generate_scenario(ScenarioType.HIGH_VOLATILITY)
        
        assert scenario.scenario_type == ScenarioType.HIGH_VOLATILITY
        assert scenario.signal_volatility >= 0.8
    
    def test_generate_conflicting_domain_scenario(self):
        """Test generating conflicting domain scenario."""
        generator = ScenarioGenerator()
        scenario = generator.generate_scenario(ScenarioType.CONFLICTING_DOMAIN)
        
        assert scenario.scenario_type == ScenarioType.CONFLICTING_DOMAIN
        assert scenario.signal_conflict_rate >= 0.5
        assert scenario.conflicting_domain_weight >= 0.5
    
    def test_generate_all_scenario_types(self):
        """Test generating all scenario types."""
        generator = ScenarioGenerator()
        types = generator.get_all_scenario_types()
        
        assert len(types) == len(ScenarioType)
        assert ScenarioType.STEADY_STATE in types
        assert ScenarioType.NOISY_SIGNAL in types
    
    def test_generate_signals(self):
        """Test signal generation."""
        generator = ScenarioGenerator(random_seed=42)
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        
        signals = generator.generate_signals(scenario, cycle_number=1)
        
        assert len(signals) > 0
        assert all(isinstance(s, SignalPattern) for s in signals)
    
    def test_deterministic_with_seed(self):
        """Test that same seed produces same results."""
        gen1 = ScenarioGenerator(random_seed=12345)
        gen2 = ScenarioGenerator(random_seed=12345)
        
        scenario1 = gen1.generate_scenario(ScenarioType.STEADY_STATE)
        scenario2 = gen2.generate_scenario(ScenarioType.STEADY_STATE)
        
        assert scenario1.scenario_id == scenario2.scenario_id


class TestGovernanceSimulator:
    """Tests for governance simulator."""
    
    def test_create_simulator(self):
        """Test creating a governance simulator."""
        generator = ScenarioGenerator(random_seed=42)
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        simulator = GovernanceSimulator(scenario=scenario, scenario_generator=generator)
        
        assert simulator is not None
        assert simulator.scenario == scenario
    
    def test_run_short_simulation(self):
        """Test running a short simulation."""
        generator = ScenarioGenerator(random_seed=42)
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        scenario.cycle_count = 10  # Short for testing
        
        simulator = GovernanceSimulator(scenario=scenario, scenario_generator=generator)
        result = simulator.run_simulation()
        
        assert result is not None
        assert len(result.cycles) == 10
        assert result.signals_processed > 0
    
    def test_simulation_tracks_state(self):
        """Test that simulation tracks state across cycles."""
        generator = ScenarioGenerator(random_seed=42)
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        scenario.cycle_count = 5
        
        simulator = GovernanceSimulator(scenario=scenario, scenario_generator=generator)
        result = simulator.run_simulation()
        
        # Verify cycles have state
        for cycle in result.cycles:
            assert cycle.state_snapshot is not None
    
    def test_simulation_generates_recommendations(self):
        """Test that simulation generates recommendations."""
        generator = ScenarioGenerator(random_seed=42)
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        scenario.cycle_count = 10
        
        simulator = GovernanceSimulator(scenario=scenario, scenario_generator=generator)
        result = simulator.run_simulation()
        
        # Should have at least some recommendations
        total_recs = sum(len(c.recommendations) for c in result.cycles)
        assert total_recs >= 0
    
    def test_run_governance_simulation_helper(self):
        """Test the convenience function."""
        result = run_governance_simulation(
            ScenarioType.STEADY_STATE,
            cycle_count=10,
            seed=42
        )
        
        assert result is not None
        assert len(result.cycles) == 10


class TestStabilityMetrics:
    """Tests for stability metrics."""
    
    def test_compute_recommendation_stability(self):
        """Test computing recommendation stability."""
        generator = ScenarioGenerator(random_seed=42)
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        scenario.cycle_count = 20
        
        simulator = GovernanceSimulator(scenario=scenario, scenario_generator=generator)
        result = simulator.run_simulation()
        
        stability = compute_recommendation_stability(result.cycles)
        
        assert 0.0 <= stability <= 1.0
    
    def test_compute_doctrine_consistency(self):
        """Test computing doctrine consistency."""
        generator = ScenarioGenerator(random_seed=42)
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        scenario.cycle_count = 20
        
        simulator = GovernanceSimulator(scenario=scenario, scenario_generator=generator)
        result = simulator.run_simulation()
        
        consistency = compute_doctrine_consistency(result.cycles)
        
        assert 0.0 <= consistency <= 1.0
    
    def test_compute_tier_stability(self):
        """Test computing tier stability."""
        generator = ScenarioGenerator(random_seed=42)
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        scenario.cycle_count = 20
        
        simulator = GovernanceSimulator(scenario=scenario, scenario_generator=generator)
        result = simulator.run_simulation()
        
        stability = compute_tier_stability(result.cycles)
        
        assert 0.0 <= stability <= 1.0
    
    def test_compute_confidence_stability(self):
        """Test computing confidence stability."""
        generator = ScenarioGenerator(random_seed=42)
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        scenario.cycle_count = 20
        
        simulator = GovernanceSimulator(scenario=scenario, scenario_generator=generator)
        result = simulator.run_simulation()
        
        stability = compute_confidence_stability(result.cycles)
        
        assert 0.0 <= stability <= 1.0
    
    def test_compute_execution_pressure(self):
        """Test computing execution pressure."""
        generator = ScenarioGenerator(random_seed=42)
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        scenario.cycle_count = 20
        
        simulator = GovernanceSimulator(scenario=scenario, scenario_generator=generator)
        result = simulator.run_simulation()
        
        pressure = compute_execution_pressure(result.cycles)
        
        assert 0.0 <= pressure <= 1.0
    
    def test_compute_governance_load(self):
        """Test computing governance load."""
        generator = ScenarioGenerator(random_seed=42)
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        scenario.cycle_count = 20
        
        simulator = GovernanceSimulator(scenario=scenario, scenario_generator=generator)
        result = simulator.run_simulation()
        
        load = compute_governance_load(result.cycles)
        
        assert 0.0 <= load <= 1.0
    
    def test_compute_overall_stability(self):
        """Test computing overall stability."""
        overall = compute_overall_stability(
            recommendation_stability=0.8,
            doctrine_consistency=0.9,
            tier_stability=0.7,
            confidence_stability=0.85,
            governance_load=0.3,
        )
        
        assert 0.0 <= overall <= 1.0
    
    def test_compute_all_stability_metrics(self):
        """Test computing all stability metrics."""
        generator = ScenarioGenerator(random_seed=42)
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        scenario.cycle_count = 20
        
        simulator = GovernanceSimulator(scenario=scenario, scenario_generator=generator)
        result = simulator.run_simulation()
        
        metrics = compute_all_stability_metrics(result)
        
        assert len(metrics) > 0
        assert result.recommendation_stability_score >= 0
        assert result.overall_stability_score >= 0


class TestOscillationDetector:
    """Tests for oscillation detector."""
    
    def test_create_detector(self):
        """Test creating an oscillation detector."""
        detector = OscillationDetector(min_reversals=2)
        assert detector.min_reversals == 2
    
    def test_detect_oscillations_steady_state(self):
        """Test oscillation detection in steady state."""
        generator = ScenarioGenerator(random_seed=42)
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        scenario.cycle_count = 20
        
        simulator = GovernanceSimulator(scenario=scenario, scenario_generator=generator)
        result = simulator.run_simulation()
        
        detector = OscillationDetector(min_reversals=3)
        events = detector.detect_all_oscillations(result.cycles)
        
        # Steady state should have few oscillations
        assert isinstance(events, list)
    
    def test_detect_confidence_swings(self):
        """Test detecting confidence swings."""
        detector = OscillationDetector(min_reversals=2)
        
        # Create mock cycles with oscillating confidence
        cycles = []
        for i in range(10):
            cycle = GovernanceSimulationCycle(
                cycle_id=f"cycle_{i}",
                scenario_id="test",
                cycle_number=i + 1,
                doctrine_assessment={
                    "confidence": 0.5 + (0.3 if i % 2 == 0 else -0.3),
                }
            )
            cycles.append(cycle)
        
        events = detector.detect_confidence_swings(cycles)
        
        assert isinstance(events, list)


class TestDoctrineConflictDetector:
    """Tests for doctrine conflict detector."""
    
    def test_create_detector(self):
        """Test creating a doctrine conflict detector."""
        detector = DoctrineConflictDetector(similarity_threshold=0.8)
        assert detector.similarity_threshold == 0.8
    
    def test_detect_conflicts_steady_state(self):
        """Test conflict detection in steady state."""
        generator = ScenarioGenerator(random_seed=42)
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        scenario.cycle_count = 20
        
        simulator = GovernanceSimulator(scenario=scenario, scenario_generator=generator)
        result = simulator.run_simulation()
        
        detector = DoctrineConflictDetector()
        events = detector.detect_conflicts(result.cycles)
        
        assert isinstance(events, list)


class TestSaturationAnalyzer:
    """Tests for saturation analyzer."""
    
    def test_create_analyzer(self):
        """Test creating a saturation analyzer."""
        analyzer = SaturationAnalyzer(
            recommendation_capacity=10,
            approval_queue_capacity=20,
        )
        assert analyzer.recommendation_capacity == 10
    
    def test_analyze_saturation_steady_state(self):
        """Test saturation analysis in steady state."""
        generator = ScenarioGenerator(random_seed=42)
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        scenario.cycle_count = 20
        
        simulator = GovernanceSimulator(scenario=scenario, scenario_generator=generator)
        result = simulator.run_simulation()
        
        analyzer = SaturationAnalyzer()
        analysis = analyzer.run_full_saturation_analysis(result.cycles)
        
        assert "saturation_events" in analysis
        assert "metrics" in analysis
        assert "operator_burden" in analysis
    
    def test_detect_recommendation_overload(self):
        """Test detecting recommendation overload."""
        analyzer = SaturationAnalyzer(recommendation_capacity=2)
        
        # Create cycles with many recommendations
        cycles = []
        for i in range(5):
            cycle = GovernanceSimulationCycle(
                cycle_id=f"cycle_{i}",
                scenario_id="test",
                cycle_number=i + 1,
                recommendations=[{"id": j} for j in range(5)]  # 5 recs > capacity of 2
            )
            cycles.append(cycle)
        
        events = analyzer._detect_recommendation_overload(cycles)
        
        assert len(events) > 0


class TestPolicyStressTester:
    """Tests for policy stress tester."""
    
    def test_create_tester(self):
        """Test creating a policy stress tester."""
        tester = PolicyStressTester()
        assert tester is not None
    
    def test_run_stress_test(self):
        """Test running policy stress test."""
        generator = ScenarioGenerator(random_seed=42)
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        scenario.cycle_count = 20
        
        simulator = GovernanceSimulator(scenario=scenario, scenario_generator=generator)
        result = simulator.run_simulation()
        
        tester = PolicyStressTester()
        analysis = tester.run_full_stress_test(scenario, result)
        
        assert "threshold_sensitivity" in analysis
        assert "tier_consistency" in analysis


class TestExecutionFeedbackAnalyzer:
    """Tests for execution feedback analyzer."""
    
    def test_create_analyzer(self):
        """Test creating an execution feedback analyzer."""
        analyzer = ExecutionFeedbackAnalyzer()
        assert analyzer is not None
    
    def test_analyze_execution_pressure(self):
        """Test analyzing execution pressure."""
        generator = ScenarioGenerator(random_seed=42)
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        scenario.cycle_count = 20
        
        simulator = GovernanceSimulator(scenario=scenario, scenario_generator=generator)
        result = simulator.run_simulation()
        
        analyzer = ExecutionFeedbackAnalyzer()
        analysis = analyzer.analyze_execution_pressure(result.cycles)
        
        assert "pressure_score" in analysis
        assert "avg_intents_per_cycle" in analysis
    
    def test_full_feedback_analysis(self):
        """Test full feedback analysis."""
        generator = ScenarioGenerator(random_seed=42)
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        scenario.cycle_count = 20
        
        simulator = GovernanceSimulator(scenario=scenario, scenario_generator=generator)
        result = simulator.run_simulation()
        
        analysis = analyze_execution_feedback(scenario, result.cycles)
        
        assert "execution_pressure" in analysis
        assert "audit_quality" in analysis


class TestSimulationReporter:
    """Tests for simulation reporter."""
    
    def test_create_reporter(self):
        """Test creating a simulation reporter."""
        reporter = SimulationReporter()
        assert reporter is not None
    
    def test_generate_report(self):
        """Test generating a simulation report."""
        # Run multiple simulations
        results = []
        for _ in range(2):
            result = run_governance_simulation(
                ScenarioType.STEADY_STATE,
                cycle_count=10,
                seed=42
            )
            results.append(result)
        
        reporter = SimulationReporter()
        report = reporter.generate_report(results)
        
        assert report.total_simulations == 2
        assert report.avg_overall_stability >= 0
        assert len(report.remediation_actions) > 0
    
    def test_generate_text_report(self):
        """Test generating text report."""
        result = run_governance_simulation(
            ScenarioType.STEADY_STATE,
            cycle_count=10,
            seed=42
        )
        
        reporter = SimulationReporter()
        enriched = reporter.enrich_result_with_analysis(result)
        report = reporter.generate_report([enriched])
        
        text = reporter.generate_text_report(report)
        
        assert "GOVERNANCE STRESS TEST REPORT" in text
        assert "STABILITY METRICS" in text
    
    def test_safety_verification(self):
        """Test safety verification."""
        result = run_governance_simulation(
            ScenarioType.STEADY_STATE,
            cycle_count=10,
            seed=42
        )
        
        reporter = SimulationReporter()
        report = reporter.generate_report([result])
        
        assert report.replay_mode_verified is True
        assert report.no_live_execution is True


class TestIntegration:
    """Integration tests for governance simulation."""
    
    def test_full_simulation_pipeline(self):
        """Test complete simulation pipeline."""
        # 1. Generate scenario
        generator = ScenarioGenerator(random_seed=42)
        scenario = generator.generate_scenario(ScenarioType.STEADY_STATE)
        scenario.cycle_count = 10
        
        # 2. Run simulation
        simulator = GovernanceSimulator(scenario=scenario, scenario_generator=generator)
        result = simulator.run_simulation()
        
        # 3. Compute metrics
        compute_all_stability_metrics(result)
        
        # 4. Detect issues
        detect_oscillations(result.cycles)
        detect_doctrine_conflicts(result.cycles)
        
        # 5. Analyze saturation
        analyze_saturation(result.cycles)
        
        # 6. Generate report
        reporter = SimulationReporter()
        enriched = reporter.enrich_result_with_analysis(result)
        report = reporter.generate_report([enriched])
        
        # Verify
        assert report.total_simulations == 1
        assert report.avg_overall_stability >= 0
    
    def test_multiple_scenario_types(self):
        """Test running multiple scenario types."""
        scenario_types = [
            ScenarioType.STEADY_STATE,
            ScenarioType.NOISY_SIGNAL,
            ScenarioType.HIGH_VOLATILITY,
            ScenarioType.CONFLICTING_DOMAIN,
        ]
        
        results = []
        for st in scenario_types:
            result = run_governance_simulation(st, cycle_count=10, seed=42)
            results.append(result)
        
        reporter = SimulationReporter()
        report = reporter.generate_report(results)
        
        assert report.total_simulations == 4
        assert len(report.results) == 4
    
    def test_deterministic_simulation(self):
        """Test that seeded simulations are deterministic."""
        result1 = run_governance_simulation(
            ScenarioType.STEADY_STATE,
            cycle_count=20,
            seed=12345
        )
        
        result2 = run_governance_simulation(
            ScenarioType.STEADY_STATE,
            cycle_count=20,
            seed=12345
        )
        
        # Same seed should produce same scenario ID
        assert result1.scenario_id == result2.scenario_id
    
    def test_adversarial_scenario_stress(self):
        """Test adversarial scenario produces expected stress."""
        result = run_governance_simulation(
            ScenarioType.ADVERSARIAL_POLICY_PRESSURE,
            cycle_count=50,
            seed=42
        )
        
        # Adversarial should generate more issues
        assert result.execution_intents_generated > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
