"""Forecasting Engine Tests - Determinism and core functionality tests."""
import pytest
import sys
from datetime import datetime, date, timedelta

sys.path.insert(0, '.')

from app.forecasting import (
    ForecastEngine,
    get_forecast_engine,
    TrendAnalyzer,
    get_trend_analyzer,
    RiskProjector,
    get_risk_projector,
    GoalProbabilityEngine,
    get_goal_probability_engine,
)


class TestTrendAnalyzer:
    """Test trend analyzer functionality."""
    
    def test_trend_detection_improving(self):
        """Test detection of improving trend."""
        analyzer = TrendAnalyzer()
        
        # Add improving data
        for i in range(10):
            analyzer.add_data_point("test_domain", 5.0 + i * 0.3, 4.0)
        
        trend = analyzer.analyze_trend("test_domain")
        
        assert trend.trend_direction.value == "improving"
        assert trend.projected_performance_90d > trend.current_performance
    
    def test_trend_detection_declining(self):
        """Test detection of declining trend."""
        analyzer = TrendAnalyzer()
        
        # Add declining data
        for i in range(10):
            analyzer.add_data_point("test_domain", 8.0 - i * 0.3, 4.0)
        
        trend = analyzer.analyze_trend("test_domain")
        
        assert trend.trend_direction.value == "declining"
        assert trend.projected_performance_90d < trend.current_performance
    
    def test_trend_detection_stable(self):
        """Test detection of stable trend."""
        analyzer = TrendAnalyzer()
        
        # Add stable data
        for i in range(10):
            analyzer.add_data_point("test_domain", 5.0 + (i % 3 - 1) * 0.1, 4.0)
        
        trend = analyzer.analyze_trend("test_domain")
        
        assert trend.trend_direction.value == "stable"
    
    def test_confidence_increases_with_data(self):
        """Test that confidence increases with more data points."""
        analyzer = TrendAnalyzer()
        
        # Few data points
        for i in range(3):
            analyzer.add_data_point("test", 5.0, 4.0)
        
        trend_few = analyzer.analyze_trend("test")
        
        # More data points
        for i in range(20):
            analyzer.add_data_point("test2", 5.0, 4.0)
        
        trend_more = analyzer.analyze_trend("test2")
        
        assert trend_more.trend_confidence > trend_few.trend_confidence


class TestRiskProjector:
    """Test risk projection functionality."""
    
    def test_risk_projection_basic(self):
        """Test basic risk projection."""
        analyzer = TrendAnalyzer()
        projector = RiskProjector(analyzer)
        
        # Add data with increasing risk
        for i in range(10):
            analyzer.add_data_point("wealth", 5.0, 3.0 + i * 0.3)
        
        projection = projector.project_risk("wealth", "financial", 6.5, 30)
        
        assert projection.current_risk == 6.5
        assert projection.projected_risk_30d >= projection.current_risk
    
    def test_risk_severity_levels(self):
        """Test severity level determination."""
        analyzer = TrendAnalyzer()
        projector = RiskProjector(analyzer)
        
        # Low risk
        proj_low = projector.project_risk("test", "type", 2.0)
        assert proj_low.severity.value == "low"
        
        # High risk
        proj_high = projector.project_risk("test", "type", 8.0)
        assert proj_high.severity.value == "critical"


class TestGoalProbabilityEngine:
    """Test goal probability calculation."""
    
    def test_goal_registration(self):
        """Test goal registration."""
        engine = GoalProbabilityEngine()
        
        target = date.today() + timedelta(days=180)
        
        engine.register_goal(
            goal_id="test-goal",
            goal_name="Test Goal",
            target_date=target,
            current_progress=0.3,
            target_value=1.0,
            priority=0.7,
        )
        
        assert "test-goal" in engine.goals
    
    def test_probability_calculation(self):
        """Test probability calculation."""
        engine = GoalProbabilityEngine()
        
        target = date.today() + timedelta(days=365)
        
        engine.register_goal(
            goal_id="test-goal",
            goal_name="Test Goal",
            target_date=target,
            current_progress=0.5,
            target_value=1.0,
            priority=0.8,
        )
        
        prob = engine.calculate_probability("test-goal")
        
        assert 0 <= prob.probability_of_success <= 1
        assert prob.confidence > 0


class TestForecastEngineDeterminism:
    """Test forecast engine determinism."""
    
    def test_deterministic_with_same_data(self):
        """Test that identical inputs produce identical outputs."""
        # First run
        engine1 = ForecastEngine()
        
        for i in range(30):
            engine1.add_domain_data("health", 5.0 + i * 0.05, 4.0)
            engine1.add_domain_data("wealth", 5.0 + i * 0.03, 4.0)
        
        engine1.register_goal(
            goal_id="g1",
            goal_name="Test",
            target_date=date.today() + timedelta(days=180),
            current_progress=0.4,
        )
        
        cycle1 = engine1.run_forecast_cycle()
        
        # Second run with same data
        engine2 = ForecastEngine()
        
        for i in range(30):
            engine2.add_domain_data("health", 5.0 + i * 0.05, 4.0)
            engine2.add_domain_data("wealth", 5.0 + i * 0.03, 4.0)
        
        engine2.register_goal(
            goal_id="g1",
            goal_name="Test",
            target_date=date.today() + timedelta(days=180),
            current_progress=0.4,
        )
        
        cycle2 = engine2.run_forecast_cycle()
        
        # Should produce same trends
        for t1, t2 in zip(cycle1.domain_trends, cycle2.domain_trends):
            assert abs(t1.projected_performance_90d - t2.projected_performance_90d) < 0.01


class TestForecastEngineAPI:
    """Test forecast engine API endpoints."""
    
    def test_trend_report(self):
        """Test trend report generation."""
        engine = ForecastEngine()
        
        engine.add_domain_data("health", 6.0, 3.0)
        engine.add_domain_data("wealth", 5.0, 4.0)
        
        report = engine.get_trend_report()
        
        assert "trends" in report
        assert len(report["trends"]) >= 2
    
    def test_risk_report(self):
        """Test risk report generation."""
        engine = ForecastEngine()
        
        engine.add_domain_data("health", 6.0, 3.0)
        
        report = engine.get_risk_report()
        
        assert "projections" in report
    
    def test_goal_report(self):
        """Test goal probability report."""
        engine = ForecastEngine()
        
        engine.register_goal(
            goal_id="test",
            goal_name="Test",
            target_date=date.today() + timedelta(days=180),
        )
        
        report = engine.get_goal_report()
        
        assert "goals" in report


class TestEdgeCases:
    """Test edge cases."""
    
    def test_empty_domain_history(self):
        """Test handling of domain with no history."""
        analyzer = TrendAnalyzer()
        
        trend = analyzer.analyze_trend("unknown_domain")
        
        assert trend.current_performance == 5.0
        assert trend.trend_confidence == 0.0
    
    def test_single_data_point(self):
        """Test handling of single data point."""
        analyzer = TrendAnalyzer()
        
        analyzer.add_domain_data("test", 7.0, 3.0)
        
        trend = analyzer.analyze_trend("test")
        
        assert trend.current_performance == 7.0
        assert trend.trend_confidence < 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
