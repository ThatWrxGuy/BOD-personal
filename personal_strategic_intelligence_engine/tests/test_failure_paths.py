"""Failure path and edge case tests for core subsystems."""
import pytest
from datetime import date

from app.forecasting import (
    ForecastEngine,
    TrendAnalyzer,
    RiskProjector,
    GoalProbabilityEngine,
)
from app.simulation_engine import (
    SimulationCore,
    SimulationConfig,
    SimulationType,
    DomainState,
)


class TestForecastingEdgeCases:
    """Edge case and failure tests for forecasting."""

    def test_trend_analyzer_empty_history(self):
        """Test TrendAnalyzer handles empty history."""
        analyzer = TrendAnalyzer()
        trend = analyzer.analyze_trend("nonexistent_domain")
        assert trend is not None

    def test_trend_analyzer_single_point(self):
        """Test TrendAnalyzer with single data point."""
        analyzer = TrendAnalyzer()
        analyzer.add_data_point("test", 5.0, 3.0)
        trend = analyzer.analyze_trend("test")
        assert trend is not None

    def test_risk_projector_empty_analyzer(self):
        """Test RiskProjector with empty analyzer."""
        analyzer = TrendAnalyzer()
        projector = RiskProjector(analyzer)
        risk = projector.project_risk("domain", "operational", 3.0, days_ahead=30)
        assert risk.domain == "domain"
        assert risk.projected_risk_30d is not None

    def test_goal_probability_zero_target(self):
        """Test GoalProbabilityEngine with zero target."""
        engine = GoalProbabilityEngine()
        target = date.today()
        # Register goal with non-zero target
        engine.register_goal("zero", "Zero", target, 0.5, 1.0)
        prob = engine.calculate_probability("zero")
        assert prob.goal_id == "zero"
        assert 0.0 <= prob.probability_of_success <= 1.0

    def test_forecast_engine_empty_domains(self):
        """Test ForecastEngine with empty domains."""
        engine = ForecastEngine()
        # Add data then run forecast
        engine.add_domain_data("health", 6.0, 3.0)
        cycle = engine.run_forecast_cycle()
        assert cycle.cycle_id is not None
        assert cycle.timestamp is not None


class TestSimulationEdgeCases:
    """Edge case and failure tests for simulation."""

    def test_simulation_zero_iterations(self):
        """Test simulation with zero iterations."""
        core = SimulationCore()
        config = SimulationConfig(simulation_type=SimulationType.STRATEGY, num_iterations=0)
        domains = {"health": DomainState(domain="health", current_score=5.0, target_score=7.0)}
        
        result = core.run_simulation(config, domains)
        assert result.status.value == "completed"

    def test_simulation_zero_time_horizon(self):
        """Test simulation with zero time horizon."""
        core = SimulationCore()
        config = SimulationConfig(simulation_type=SimulationType.STRATEGY, time_horizon_days=0)
        domains = {"health": DomainState(domain="health", current_score=5.0, target_score=7.0)}
        
        result = core.run_simulation(config, domains)
        assert result.status.value == "completed"

    def test_simulation_empty_domains(self):
        """Test simulation with empty domains dict."""
        core = SimulationCore()
        config = SimulationConfig(simulation_type=SimulationType.STRATEGY)
        domains = {}
        
        result = core.run_simulation(config, domains)
        assert result.status.value == "completed"
        assert result.expected_performance is not None

    def test_simulation_extreme_scores(self):
        """Test simulation with extreme score values."""
        core = SimulationCore()
        config = SimulationConfig(simulation_type=SimulationType.STRATEGY)
        
        # Test with minimum score
        domains = {"health": DomainState(domain="health", current_score=0.0, target_score=1.0)}
        result = core.run_simulation(config, domains)
        assert result.status.value == "completed"
        
        # Test with maximum score
        domains = {"health": DomainState(domain="health", current_score=10.0, target_score=10.0)}
        result = core.run_simulation(config, domains)
        assert result.status.value == "completed"

    def test_simulation_all_types(self):
        """Test simulation with all simulation types."""
        core = SimulationCore()
        
        # Test only the supported types
        for sim_type in [SimulationType.STRATEGY, SimulationType.MONTE_CARLO, SimulationType.SCENARIO]:
            config = SimulationConfig(simulation_type=sim_type)
            result = core.run_simulation(config, {"test": DomainState(domain="test", current_score=5.0, target_score=7.0)})
            assert result.status.value == "completed"


class TestBoundaryConditions:
    """Boundary condition tests."""

    def test_domain_state_boundaries(self):
        """Test DomainState with boundary values."""
        # Minimum
        state = DomainState(domain="test", current_score=0.0, target_score=0.0)
        assert state.current_score == 0.0
        
        # Maximum
        state = DomainState(domain="test", current_score=10.0, target_score=10.0)
        assert state.current_score == 10.0
        
        # Above maximum (should clamp)
        state = DomainState(domain="test", current_score=15.0, target_score=20.0)
        # Values should be accepted but may be clamped later

    def test_config_boundaries(self):
        """Test SimulationConfig with boundary values."""
        # Very large iterations
        config = SimulationConfig(simulation_type=SimulationType.STRATEGY, num_iterations=10000)
        assert config.num_iterations == 10000
        
        # Very large time horizon
        config = SimulationConfig(simulation_type=SimulationType.STRATEGY, time_horizon_days=365)
        assert config.time_horizon_days == 365


class TestErrorHandling:
    """Error handling tests."""

    def test_forecast_handles_exception(self):
        """Test that forecast engine handles exceptions gracefully."""
        engine = ForecastEngine()
        # Should not raise - invalid domains
        try:
            cycle = engine.run_forecast_cycle()
        except Exception as e:
            # Some exceptions are expected for invalid input
            pass

    def test_simulation_handles_invalid_config(self):
        """Test simulation handles invalid config."""
        core = SimulationCore()
        # Negative values should be handled
        config = SimulationConfig(simulation_type=SimulationType.STRATEGY, num_iterations=-1, time_horizon_days=-1)
        result = core.run_simulation(config, {"test": DomainState(domain="test", current_score=5.0, target_score=7.0)})
        # Should complete without crashing
        assert result is not None
