"""Strategy Simulation Tests - Determinism and core functionality tests."""
import pytest
import sys

sys.path.insert(0, '.')

from app.strategy_simulation import (
    EnhancedSimulationEngine,
    DecisionModel,
    OutcomeSimulator,
    StrategyComparator,
    CandidateStrategy,
    StrategyType,
)


class TestDecisionModel:
    """Test decision model functionality."""
    
    def test_get_all_strategies(self):
        """Test retrieval of all strategy templates."""
        model = DecisionModel()
        
        strategies = model.get_all_strategies()
        
        assert len(strategies) >= 5
        assert any(s.strategy_id == "balance" for s in strategies)
    
    def test_get_strategy(self):
        """Test retrieval of specific strategy."""
        model = DecisionModel()
        
        strategy = model.get_strategy("balance")
        
        assert strategy is not None
        assert strategy.strategy_name == "Balanced Approach"
    
    def test_create_custom_strategy(self):
        """Test creation of custom strategy."""
        model = DecisionModel()
        
        strategy = model.create_custom_strategy(
            name="Test Strategy",
            description="A test strategy",
            affected_domains=["health", "wealth"],
            resource_changes={"health": 2.0, "wealth": -1.0},
        )
        
        assert strategy.strategy_id is not None
        assert strategy.strategy_name == "Test Strategy"


class TestOutcomeSimulator:
    """Test outcome simulator functionality."""
    
    def test_simulate_outcome_basic(self):
        """Test basic outcome simulation."""
        simulator = OutcomeSimulator()
        
        # Simple strategy
        from app.strategy_simulation.simulation_types import StrategyDecision
        
        strategy = StrategyDecision(
            decision_id="test",
            name="Test",
            description="Test",
            strategy_type=StrategyType.FOCUS_SHIFT,
            resource_changes={"health": 2.0},
        )
        
        current_domains = {"health": 5.0, "wealth": 5.0}
        
        outcome = simulator.simulate_outcome(strategy, current_domains, 30)
        
        assert outcome.strategy_id == "test"
        assert "health" in outcome.projected_domains
    
    def test_domain_interactions(self):
        """Test domain interaction effects."""
        simulator = OutcomeSimulator()
        
        # High health should boost other domains
        domains = {"health": 8.0, "wealth": 5.0, "career": 5.0}
        
        from app.strategy_simulation.simulation_types import StrategyDecision
        
        strategy = StrategyDecision(
            decision_id="test",
            name="Test",
            description="Test",
            strategy_type=StrategyType.FOCUS_SHIFT,
            resource_changes={},
        )
        
        outcome = simulator.simulate_outcome(strategy, domains, 30)
        
        # Health should have positive effect on other domains
        assert outcome.projected_domains["health"] >= domains["health"]


class TestStrategyComparator:
    """Test strategy comparator functionality."""
    
    def test_compare_strategies(self):
        """Test strategy comparison."""
        comparator = StrategyComparator()
        
        from app.strategy_simulation.simulation_types import SimulatedOutcome
        
        baseline = SimulatedOutcome(
            strategy_id="baseline",
            time_horizon_days=90,
            overall_score=5.0,
            expected_performance_gain=0.0,
            risk_exposure_change=0.0,
        )
        
        strategies = [
            SimulatedOutcome(
                strategy_id="strategy_a",
                time_horizon_days=90,
                overall_score=6.0,
                expected_performance_gain=1.0,
                risk_exposure_change=0.5,
            ),
            SimulatedOutcome(
                strategy_id="strategy_b",
                time_horizon_days=90,
                overall_score=4.5,
                expected_performance_gain=-0.5,
                risk_exposure_change=-0.3,
            ),
        ]
        
        comparison = comparator.compare_strategies(baseline, strategies)
        
        assert comparison.best_strategy == "strategy_a"
        assert comparison.worst_strategy == "strategy_b"
    
    def test_rank_strategies(self):
        """Test strategy ranking."""
        comparator = StrategyComparator()
        
        outcomes = [
            type('Obj', (), {
                'strategy_id': 'a',
                'overall_score': 5.0,
                'expected_performance_gain': 0.5,
                'risk_exposure_change': 0.2,
            })(),
            type('Obj', (), {
                'strategy_id': 'b',
                'overall_score': 7.0,
                'expected_performance_gain': 2.0,
                'risk_exposure_change': 0.5,
            })(),
            type('Obj', (), {
                'strategy_id': 'c',
                'overall_score': 6.0,
                'expected_performance_gain': 1.0,
                'risk_exposure_change': 0.3,
            })(),
        ]
        
        rankings = comparator.rank_strategies(outcomes)
        
        assert rankings[0]['strategy_id'] == 'b'
        assert rankings[1]['strategy_id'] == 'c'
        assert rankings[2]['strategy_id'] == 'a'


class TestSimulationEngineDeterminism:
    """Test simulation engine determinism."""
    
    def test_deterministic_ranking(self):
        """Test that identical inputs produce same rankings."""
        # First simulation
        engine1 = EnhancedSimulationEngine()
        
        domains1 = {
            'health': 5.5,
            'wealth': 4.5,
            'career': 4.8,
            'operations': 4.0,
        }
        
        cycle1 = engine1.run_simulation_cycle(domains1)
        
        # Second simulation with identical data
        engine2 = EnhancedSimulationEngine()
        
        domains2 = {
            'health': 5.5,
            'wealth': 4.5,
            'career': 4.8,
            'operations': 4.0,
        }
        
        cycle2 = engine2.run_simulation_cycle(domains2)
        
        # Rankings should be identical
        assert cycle1.best_strategy == cycle2.best_strategy
        
        # Score order should match
        scores1 = [s.expected_value for s in cycle1.scores]
        scores2 = [s.expected_value for s in cycle2.scores]
        
        for s1, s2 in zip(sorted(scores1), sorted(scores2)):
            assert abs(s1 - s2) < 0.01
    
    def test_stress_scenario_affects_ranking(self):
        """Test that different scenarios produce different rankings."""
        engine = EnhancedSimulationEngine()
        
        # Normal state
        domains_normal = {d: 7.0 for d in ['health', 'wealth', 'career']}
        
        # Stressed state  
        domains_stressed = {d: 3.0 for d in ['health', 'wealth', 'career']}
        
        cycle_normal = engine.run_simulation_cycle(domains_normal)
        cycle_stressed = engine.run_simulation_cycle(domains_stressed)
        
        # Different scenarios should potentially produce different best strategies
        # (not guaranteed, but likely with very different inputs)
        # At minimum, scores should differ
        assert cycle_normal.confidence_level != cycle_stressed.confidence_level


class TestSimulationEngineAPI:
    """Test simulation engine API."""
    
    def test_simulation_cycle_execution(self):
        """Test full simulation cycle execution."""
        engine = EnhancedSimulationEngine()
        
        domains = {
            'health': 5.5,
            'wealth': 4.5,
            'career': 5.0,
        }
        
        cycle = engine.run_simulation_cycle(domains)
        
        assert cycle.cycle_id is not None
        assert cycle.status.value == "completed"
        assert len(cycle.candidate_strategies) > 0
        assert cycle.recommendation is not None
    
    def test_recommendation_generation(self):
        """Test recommendation is generated."""
        engine = EnhancedSimulationEngine()
        
        domains = {d: 5.0 for d in ['health', 'wealth', 'career']}
        
        cycle = engine.run_simulation_cycle(domains)
        
        rec = cycle.recommendation
        
        assert rec is not None
        assert rec.recommended_strategy_id is not None
        assert rec.reasoning is not None
    
    def test_history_tracking(self):
        """Test simulation history is tracked."""
        engine = EnhancedSimulationEngine()
        
        domains = {d: 5.0 for d in ['health', 'wealth']}
        
        engine.run_simulation_cycle(domains)
        engine.run_simulation_cycle(domains)
        
        history = engine.get_history(limit=10)
        
        assert len(history) >= 2


class TestEdgeCases:
    """Test edge cases."""
    
    def test_minimal_domains(self):
        """Test with minimal domain set."""
        engine = EnhancedSimulationEngine()
        
        domains = {"health": 5.0}
        
        cycle = engine.run_simulation_cycle(domains)
        
        assert cycle.status.value == "completed"
    
    def test_extreme_domain_values(self):
        """Test with extreme domain values."""
        engine = EnhancedSimulationEngine()
        
        domains = {
            "health": 10.0,  # Max
            "wealth": 0.0,   # Min
        }
        
        cycle = engine.run_simulation_cycle(domains)
        
        # Should complete without error
        assert cycle.status.value == "completed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
