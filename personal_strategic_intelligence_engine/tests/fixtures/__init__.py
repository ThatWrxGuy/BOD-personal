"""Test fixtures for canonical subsystems."""
import pytest
from datetime import date, timedelta

from app.forecasting import (
    ForecastEngine,
    TrendAnalyzer,
    RiskProjector,
    GoalProbabilityEngine,
    DomainTrend,
    RiskProjection,
    GoalProbability,
)
from app.simulation_engine import (
    SimulationCore,
    SimulationConfig,
    SimulationType,
    DomainState,
)


@pytest.fixture
def trend_analyzer():
    """Create a TrendAnalyzer with sample data."""
    analyzer = TrendAnalyzer()
    # Add sample data for health domain
    for i in range(5):
        day = date.today() - timedelta(days=4-i)
        analyzer.add_data_point("health", 5.0 + i * 0.5, day)
    # Add sample data for wealth domain
    for i in range(5):
        day = date.today() - timedelta(days=4-i)
        analyzer.add_data_point("wealth", 6.0 - i * 0.2, day)
    return analyzer


@pytest.fixture
def risk_projector(trend_analyzer):
    """Create a RiskProjector with trend analyzer."""
    return RiskProjector(trend_analyzer)


@pytest.fixture
def goal_engine():
    """Create a GoalProbabilityEngine with registered goals."""
    engine = GoalProbabilityEngine()
    # Register some test goals
    engine.register_goal(
        "goal_health",
        "Improve Health",
        date.today() + timedelta(days=30),
        current_progress=0.4,
        target_value=1.0,
    )
    engine.register_goal(
        "goal_wealth",
        "Build Wealth",
        date.today() + timedelta(days=90),
        current_progress=0.2,
        target_value=1.0,
    )
    return engine


@pytest.fixture
def forecast_engine(trend_analyzer, risk_projector, goal_engine):
    """Create a ForecastEngine with components."""
    engine = ForecastEngine()
    return engine


@pytest.fixture
def simulation_core():
    """Create a SimulationCore."""
    return SimulationCore()


@pytest.fixture
def basic_simulation_config():
    """Create a basic simulation configuration."""
    return SimulationConfig(
        simulation_type=SimulationType.STRATEGY,
        num_iterations=50,
        time_horizon_days=30,
    )


@pytest.fixture
def monte_carlo_config():
    """Create a Monte Carlo simulation configuration."""
    return SimulationConfig(
        simulation_type=SimulationType.MONTE_CARLO,
        num_iterations=100,
        time_horizon_days=90,
    )


@pytest.fixture
def sample_domains():
    """Create sample domain states."""
    return {
        "health": DomainState(domain="health", current_score=6.0, target_score=8.0, momentum=0.1),
        "wealth": DomainState(domain="wealth", current_score=5.5, target_score=7.5, momentum=0.0),
        "career": DomainState(domain="career", current_score=7.0, target_score=9.0, momentum=0.2),
        "learning": DomainState(domain="learning", current_score=5.0, target_score=7.0, momentum=-0.1),
    }


@pytest.fixture
def stressed_domains():
    """Create domain states with declining trends."""
    return {
        "health": DomainState(domain="health", current_score=3.0, target_score=7.0, momentum=-0.5),
        "wealth": DomainState(domain="wealth", current_score=4.0, target_score=8.0, momentum=-0.3),
        "career": DomainState(domain="career", current_score=8.0, target_score=9.0, momentum=0.1),
    }
