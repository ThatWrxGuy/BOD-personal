"""Tests for canonical simulation engine."""
import pytest

from app.simulation_engine import (
    SimulationCore,
    SimulationConfig,
    SimulationType,
    DomainState,
    SimulationStatus,
)


class TestSimulationCore:
    """Tests for SimulationCore."""

    def test_initialization(self):
        """Test SimulationCore initializes correctly."""
        core = SimulationCore()
        assert core is not None

    def test_run_simulation_basic(self):
        """Test basic simulation execution."""
        core = SimulationCore()
        config = SimulationConfig(
            simulation_type=SimulationType.STRATEGY,
            num_iterations=10,
            time_horizon_days=7,
        )
        domains = {
            "health": DomainState(domain="health", current_score=6.0, target_score=7.0),
        }
        
        result = core.run_simulation(config, domains)
        
        assert result.simulation_id is not None
        assert result.status == SimulationStatus.COMPLETED
        assert result.expected_performance is not None
        assert 0 <= result.expected_performance <= 10

    def test_run_simulation_monte_carlo(self):
        """Test Monte Carlo simulation."""
        core = SimulationCore()
        config = SimulationConfig(
            simulation_type=SimulationType.MONTE_CARLO,
            num_iterations=50,
            time_horizon_days=14,
        )
        domains = {
            "wealth": DomainState(domain="wealth", current_score=5.0, target_score=8.0),
            "career": DomainState(domain="career", current_score=6.0, target_score=8.0),
        }
        
        result = core.run_simulation(config, domains)
        
        assert result.simulation_id is not None
        assert result.status == SimulationStatus.COMPLETED
        assert result.expected_performance is not None

    def test_run_simulation_multiple_domains(self):
        """Test simulation with multiple domains."""
        core = SimulationCore()
        config = SimulationConfig(
            simulation_type=SimulationType.STRATEGY,
            num_iterations=20,
            time_horizon_days=30,
        )
        domains = {
            "health": DomainState(domain="health", current_score=5.0, target_score=7.0),
            "wealth": DomainState(domain="wealth", current_score=5.0, target_score=7.0),
            "career": DomainState(domain="career", current_score=5.0, target_score=7.0),
            "learning": DomainState(domain="learning", current_score=5.0, target_score=7.0),
        }
        
        result = core.run_simulation(config, domains)
        
        assert len(result.projected_domains) == 4
        assert result.goal_achievement_probability is not None


class TestSimulationConfig:
    """Tests for SimulationConfig."""

    def test_config_defaults(self):
        """Test default configuration values."""
        config = SimulationConfig(simulation_type=SimulationType.STRATEGY)
        
        assert config.simulation_type == SimulationType.STRATEGY
        assert config.num_iterations == 1000
        assert config.time_horizon_days == 365

    def test_config_custom_values(self):
        """Test custom configuration values."""
        config = SimulationConfig(
            simulation_type=SimulationType.MONTE_CARLO,
            num_iterations=500,
            time_horizon_days=90,
        )
        
        assert config.simulation_type == SimulationType.MONTE_CARLO
        assert config.num_iterations == 500
        assert config.time_horizon_days == 90


class TestDomainState:
    """Tests for DomainState."""

    def test_domain_state_creation(self):
        """Test DomainState creation."""
        state = DomainState(
            domain="health",
            current_score=6.5,
            target_score=8.0,
        )
        
        assert state.domain == "health"
        assert state.current_score == 6.5
        assert state.target_score == 8.0
        assert state.momentum == 0.0  # Default

    def test_domain_state_with_momentum(self):
        """Test DomainState with momentum."""
        state = DomainState(
            domain="career",
            current_score=7.0,
            target_score=9.0,
            momentum=0.5,
        )
        
        assert state.momentum == 0.5
