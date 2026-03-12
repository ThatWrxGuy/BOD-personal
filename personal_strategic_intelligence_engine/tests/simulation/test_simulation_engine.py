"""Tests for simulation engine."""
import pytest
from app.simulation_engine import (
    SimulationCore,
    StrategySimulator,
    MonteCarloEngine,
    SimulationConfig,
    SimulationType,
    DomainState,
)


class TestSimulationModels:
    """Test simulation model creation."""
    
    def test_domain_state_creation(self):
        """Test DomainState model."""
        domain = DomainState(
            domain="health",
            current_score=6.0,
            target_score=8.0,
            risk_level=3.0,
            momentum=0.5,
        )
        
        assert domain.domain == "health"
        assert domain.current_score == 6.0
        assert domain.target_score == 8.0
    
    def test_simulation_config(self):
        """Test SimulationConfig."""
        config = SimulationConfig(
            simulation_type=SimulationType.STRATEGY,
            num_iterations=100,
            time_horizon_days=90,
        )
        
        assert config.num_iterations == 100
        assert config.simulation_type == SimulationType.STRATEGY


class TestStrategySimulator:
    """Test strategy simulator."""
    
    def test_simulator_creation(self):
        """Test simulator instantiation."""
        sim = StrategySimulator(seed=42)
        assert sim is not None
    
    def test_simulate_strategy(self):
        """Test basic strategy simulation."""
        sim = StrategySimulator(seed=42)
        
        domains = {
            "health": DomainState(domain="health", current_score=6.0, target_score=8.0),
            "wealth": DomainState(domain="wealth", current_score=5.0, target_score=7.0),
        }
        
        result = sim.simulate_strategy("Test Strategy", domains, iterations=10)
        
        assert result is not None
        assert result.status.value == "completed"
        assert len(result.projected_domains) == 2
    
    def test_compare_strategies(self):
        """Test strategy comparison."""
        sim = StrategySimulator(seed=42)
        
        domains = {
            "health": DomainState(domain="health", current_score=6.0),
        }
        
        strategies = [
            {"name": "Strategy A"},
            {"name": "Strategy B"},
        ]
        
        outcomes = sim.compare_strategies(strategies, domains)
        
        assert len(outcomes) == 2
        assert all(o.rank is not None for o in outcomes)


class TestMonteCarloEngine:
    """Test Monte Carlo engine."""
    
    def test_engine_creation(self):
        """Test engine instantiation."""
        engine = MonteCarloEngine(seed=42)
        assert engine is not None
    
    def test_run_simulation(self):
        """Test Monte Carlo simulation."""
        engine = MonteCarloEngine(seed=42)
        
        domains = {
            "health": DomainState(
                domain="health",
                current_score=6.0,
                target_score=8.0,
                risk_level=3.0,
            ),
        }
        
        result = engine.run_simulation(domains, num_iterations=100)
        
        assert result is not None
        assert result.simulation_type.value == "monte_carlo"
        assert result.goal_achievement_probability > 0
    
    def test_value_at_risk(self):
        """Test VaR calculation."""
        engine = MonteCarloEngine(seed=42)
        
        domains = {
            "wealth": DomainState(domain="wealth", current_score=5.0, risk_level=4.0),
        }
        
        var = engine.calculate_value_at_risk(domains, confidence=0.95, iterations=50)
        
        assert "wealth" in var
        assert 0 <= var["wealth"] <= 10


class TestSimulationCore:
    """Test simulation core."""
    
    def test_core_creation(self):
        """Test core instantiation."""
        core = SimulationCore()
        assert core is not None
    
    def test_run_strategy_simulation(self):
        """Test running strategy simulation through core."""
        core = SimulationCore()
        
        config = SimulationConfig(
            simulation_type=SimulationType.STRATEGY,
            num_iterations=10,
        )
        
        domains = {
            "career": DomainState(domain="career", current_score=5.0),
        }
        
        result = core.run_simulation(config, domains)
        
        assert result is not None
        assert result.status.value == "completed"
    
    def test_run_monte_carlo(self):
        """Test running Monte Carlo through core."""
        core = SimulationCore()
        
        config = SimulationConfig(
            simulation_type=SimulationType.MONTE_CARLO,
            num_iterations=50,
        )
        
        domains = {
            "health": DomainState(domain="health", current_score=6.0),
        }
        
        result = core.run_simulation(config, domains)
        
        assert result is not None
        assert result.simulation_type.value == "monte_carlo"
    
    def test_get_simulation(self):
        """Test retrieving simulation results."""
        core = SimulationCore()
        
        config = SimulationConfig(simulation_type=SimulationType.STRATEGY, num_iterations=5)
        domains = {"test": DomainState(domain="test", current_score=5.0)}
        
        result = core.run_simulation(config, domains)
        
        retrieved = core.get_simulation(result.simulation_id)
        
        assert retrieved is not None
        assert retrieved.simulation_id == result.simulation_id


class TestFailureHandling:
    """Test failure scenarios."""
    
    def test_invalid_simulation_type(self):
        """Test handling of invalid simulation type."""
        core = SimulationCore()
        
        config = SimulationConfig(
            simulation_type="invalid_type",  # type: ignore
            num_iterations=10,
        )
        
        domains = {"test": DomainState(domain="test", current_score=5.0)}
        
        # Should raise ValueError
        with pytest.raises(ValueError):
            core.run_simulation(config, domains)
    
    def test_empty_domains(self):
        """Test simulation with no domains."""
        sim = StrategySimulator(seed=42)
        
        result = sim.simulate_strategy("Empty Test", {}, iterations=5)
        
        assert result is not None
        assert result.expected_performance == 0
