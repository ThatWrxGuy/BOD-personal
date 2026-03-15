"""Tests for canonical forecasting engine."""
import pytest
from datetime import date, datetime, timedelta

from app.forecasting import (
    ForecastEngine,
    TrendAnalyzer,
    RiskProjector,
    GoalProbabilityEngine,
    TrendDirection,
    RiskLevel,
)


class TestTrendAnalyzer:
    """Tests for TrendAnalyzer."""

    def test_initialization(self):
        """Test TrendAnalyzer initializes correctly."""
        analyzer = TrendAnalyzer()
        assert analyzer.history == {}

    def test_add_data_point(self):
        """Test adding data points."""
        analyzer = TrendAnalyzer()
        analyzer.add_data_point("health", 7.0, 3.0)
        assert "health" in analyzer.history
        assert len(analyzer.history["health"]) == 1

    def test_analyze_trend_no_data(self):
        """Test analyze_trend returns default when no data."""
        analyzer = TrendAnalyzer()
        trend = analyzer.analyze_trend("health")
        assert trend is not None
        assert trend.domain == "health"

    def test_analyze_trend_with_data(self):
        """Test analyze_trend with data points."""
        analyzer = TrendAnalyzer()
        analyzer.add_data_point("health", 5.0, 3.0)
        analyzer.add_data_point("health", 6.0, 2.5)
        analyzer.add_data_point("health", 7.0, 2.0)
        trend = analyzer.analyze_trend("health")
        assert trend.domain == "health"
        assert trend.direction in [TrendDirection.UP, TrendDirection.STABLE, TrendDirection.DOWN]


class TestRiskProjector:
    """Tests for RiskProjector."""

    def test_initialization(self):
        """Test RiskProjector initializes correctly."""
        analyzer = TrendAnalyzer()
        projector = RiskProjector(analyzer)
        assert projector.trend_analyzer is analyzer

    def test_project_risk_no_data(self):
        """Test risk projection with no data."""
        analyzer = TrendAnalyzer()
        projector = RiskProjector(analyzer)
        risk = projector.project_risk("health", "operational", 3.0, days_ahead=7)
        assert risk.domain == "health"
        assert risk.projected_risk_30d is not None


class TestGoalProbabilityEngine:
    """Tests for GoalProbabilityEngine."""

    def test_initialization(self):
        """Test GoalProbabilityEngine initializes correctly."""
        engine = GoalProbabilityEngine()
        assert engine.goals == {}

    def test_register_goal(self):
        """Test registering a goal."""
        engine = GoalProbabilityEngine()
        target = date.today() + timedelta(days=30)
        engine.register_goal("goal1", "Test Goal", target, 0.0, 1.0)
        assert "goal1" in engine.goals

    def test_calculate_probability_no_goal(self):
        """Test probability calculation for unregistered goal."""
        engine = GoalProbabilityEngine()
        prob = engine.calculate_probability("nonexistent")
        assert prob.goal_id == "nonexistent"
        assert prob.probability_of_success == 0.0

    def test_calculate_probability_with_goal(self):
        """Test probability calculation for registered goal."""
        engine = GoalProbabilityEngine()
        target = date.today() + timedelta(days=30)
        engine.register_goal("goal1", "Test Goal", target, 0.5, 1.0)
        prob = engine.calculate_probability("goal1")
        assert prob.goal_id == "goal1"
        assert 0.0 <= prob.probability_of_success <= 1.0


class TestForecastEngine:
    """Tests for ForecastEngine."""

    def test_initialization(self):
        """Test ForecastEngine initializes correctly."""
        engine = ForecastEngine()
        assert engine.trend_analyzer is not None
        assert engine.risk_projector is not None

    def test_generate_forecast(self):
        """Test forecast generation."""
        engine = ForecastEngine()
        # Add some data
        engine.add_domain_data("health", 6.0, 3.0)
        engine.add_domain_data("wealth", 5.0, 4.0)
        
        cycle = engine.run_forecast_cycle()
        assert cycle.cycle_id is not None
        assert cycle.timestamp is not None
