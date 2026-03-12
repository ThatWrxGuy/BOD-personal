"""Synthesizer Tests - Tests for strategic intelligence synthesizer."""
import pytest
import sys

sys.path.insert(0, '.')

from app.intelligence.synthesizer import (
    SynthesizerService,
    get_synthesizer_service,
    SignalExtractor,
    get_signal_extractor,
    ConflictDetector,
    get_conflict_detector,
    InsightRanker,
    get_insight_ranker,
    StrategyAdvisor,
    get_strategy_advisor,
)
from app.intelligence.synthesizer.insight_models import (
    StrategicInsight,
    InsightCategory,
    UrgencyLevel,
    RiskSeverity,
)


class TestSignalExtractor:
    """Test signal extraction functionality."""
    
    def test_extract_from_forecast(self):
        """Test extraction from forecast data."""
        from app.intelligence.synthesizer.insight_models import PredictionSnapshot
        
        extractor = SignalExtractor()
        
        forecast = PredictionSnapshot(
            engine_name="forecast",
            domain_predictions={
                "health": 3.5,  # Low - risk
                "wealth": 7.5,  # High - strength
            },
            risk_predictions={
                "health": 7.0,
                "wealth": 3.0,
            },
            goal_probabilities={
                "retire_early": 0.4,
            },
        )
        
        insights = extractor.extract_from_forecast(forecast)
        
        assert len(insights) >= 2
        
        # Should detect health risk
        health_insights = [i for i in insights if "health" in i.title.lower()]
        assert len(health_insights) > 0
        
        # Should detect wealth strength
        wealth_insights = [i for i in insights if "wealth" in i.title.lower()]
        assert len(wealth_insights) > 0
    
    def test_extract_from_simulation(self):
        """Test extraction from simulation data."""
        from app.intelligence.synthesizer.insight_models import PredictionSnapshot
        
        extractor = SignalExtractor()
        
        simulation = PredictionSnapshot(
            engine_name="simulation",
            strategy_rankings={
                "balance": 6.0,
                "focus_health": 5.5,
            },
        )
        
        insights = extractor.extract_from_simulation(simulation)
        
        assert len(insights) > 0
    
    def test_extract_all(self):
        """Test extracting from multiple sources."""
        from app.intelligence.synthesizer.insight_models import PredictionSnapshot
        
        extractor = SignalExtractor()
        
        forecast = PredictionSnapshot(
            engine_name="forecast",
            domain_predictions={"health": 4.0},
            risk_predictions={},
            goal_probabilities={},
        )
        
        simulation = PredictionSnapshot(
            engine_name="simulation",
            strategy_rankings={"balance": 5.5},
        )
        
        insights = extractor.extract_all(forecast, simulation)
        
        assert len(insights) >= 2


class TestConflictDetector:
    """Test conflict detection."""
    
    def test_detect_forecast_simulation_conflict(self):
        """Test detection of forecast vs simulation conflicts."""
        from app.intelligence.synthesizer.insight_models import PredictionSnapshot
        
        detector = ConflictDetector()
        
        forecast = PredictionSnapshot(
            engine_name="forecast",
            domain_predictions={"health": 8.0},  # High
            risk_predictions={},
            goal_probabilities={},
        )
        
        simulation = PredictionSnapshot(
            engine_name="simulation",
            domain_predictions={"health": 2.0},  # Low - conflict!
            risk_predictions={},
            goal_probabilities={},
        )
        
        conflicts = detector.check_forecast_simulation_conflict(forecast, simulation)
        
        assert len(conflicts) > 0
    
    def test_no_conflict_when_aligned(self):
        """Test no conflicts when predictions align."""
        from app.intelligence.synthesizer.insight_models import PredictionSnapshot
        
        detector = ConflictDetector()
        
        forecast = PredictionSnapshot(
            engine_name="forecast",
            domain_predictions={"health": 6.0},
            risk_predictions={},
            goal_probabilities={},
        )
        
        simulation = PredictionSnapshot(
            engine_name="simulation",
            domain_predictions={"health": 6.5},
            risk_predictions={},
            goal_probabilities={},
        )
        
        conflicts = detector.check_forecast_simulation_conflict(forecast, simulation)
        
        # Should have minimal or no conflicts
        assert len(conflicts) <= 1
    
    def test_confidence_adjustment(self):
        """Test confidence adjustment based on conflicts."""
        detector = ConflictDetector()
        
        conflicts = [
            type('Obj', (), {
                'severity': RiskSeverity.HIGH,
            })(),
        ]
        
        adjusted = detector.adjust_confidence_for_conflict(0.8, conflicts)
        
        assert adjusted < 0.8


class TestInsightRanker:
    """Test insight ranking."""
    
    def test_rank_insights(self):
        """Test insight ranking by priority."""
        ranker = InsightRanker()
        
        insights = [
            StrategicInsight(
                id="1",
                category=InsightCategory.RISK,
                title="Test 1",
                description="Test",
                impact_score=8.0,
                confidence_score=0.9,
                urgency=UrgencyLevel.HIGH,
                source_engine="test",
            ),
            StrategicInsight(
                id="2",
                category=InsightCategory.STRENGTH,
                title="Test 2",
                description="Test",
                impact_score=5.0,
                confidence_score=0.5,
                urgency=UrgencyLevel.LOW,
                source_engine="test",
            ),
        ]
        
        ranked = ranker.rank_insights(insights)
        
        # First should have higher priority
        assert ranked[0].priority_score >= ranked[1].priority_score
    
    def test_get_top_insights(self):
        """Test getting top N insights."""
        ranker = InsightRanker()
        
        insights = [
            StrategicInsight(
                id=str(i),
                category=InsightCategory.RISK,
                title=f"Test {i}",
                description="Test",
                impact_score=float(i),
                confidence_score=0.5,
                urgency=UrgencyLevel.MEDIUM,
                source_engine="test",
            )
            for i in range(10)
        ]
        
        top = ranker.get_top_insights(insights, limit=3)
        
        assert len(top) == 3


class TestStrategyAdvisor:
    """Test strategy advisor."""
    
    def test_generate_recommendation(self):
        """Test recommendation generation."""
        advisor = StrategyAdvisor()
        
        insight = StrategicInsight(
            id="1",
            category=InsightCategory.RISK,
            title="High Risk",
            description="Operations at risk",
            impact_score=8.0,
            confidence_score=0.8,
            urgency=UrgencyLevel.HIGH,
            source_engine="test",
            domains_affected=["operations"],
        )
        
        recommendation = advisor.generate_recommendation(insight)
        
        assert recommendation is not None
        assert recommendation.recommended_action is not None
    
    def test_generate_multiple_recommendations(self):
        """Test generating multiple recommendations."""
        advisor = StrategyAdvisor()
        
        insights = [
            StrategicInsight(
                id=str(i),
                category=InsightCategory.RISK,
                title=f"Risk {i}",
                description="Test",
                impact_score=float(10 - i),
                confidence_score=0.7,
                urgency=UrgencyLevel.HIGH,
                source_engine="test",
            )
            for i in range(5)
        ]
        
        # All have low priority score, so may get filtered
        for i in insights:
            i.priority_score = 5.0
        
        recommendations = advisor.generate_recommendations(insights)
        
        assert isinstance(recommendations, list)


class TestSynthesizerService:
    """Test synthesizer service."""
    
    def test_generate_report(self):
        """Test full report generation."""
        service = SynthesizerService()
        
        forecast = {
            "domain_predictions": {"health": 4.0, "wealth": 7.0},
            "risk_predictions": {"health": 6.5, "wealth": 3.0},
            "goal_probabilities": {"goal1": 0.6},
        }
        
        simulation = {
            "strategy_rankings": {"balance": 5.5, "focus_health": 5.0},
        }
        
        report = service.generate_report(
            forecast_data=forecast,
            simulation_data=simulation,
        )
        
        assert report.report_id is not None
        assert report.timestamp is not None
        assert report.total_insights >= 0
        assert "forecast" in report.engines_used
    
    def test_report_stored(self):
        """Test that reports are stored."""
        service = SynthesizerService()
        
        service.generate_report(
            forecast_data={"domain_predictions": {"health": 5.0}},
        )
        
        history = service.get_report_history(limit=5)
        
        assert len(history) >= 1
    
    def test_get_latest_report(self):
        """Test getting latest report."""
        service = SynthesizerService()
        
        service.generate_report(forecast_data={"domain_predictions": {}})
        
        latest = service.get_latest_report()
        
        assert latest is not None


class TestDeterminism:
    """Test determinism of synthesizer."""
    
    def test_deterministic_output(self):
        """Test that same input produces same output."""
        service1 = SynthesizerService()
        service2 = SynthesizerService()
        
        data = {
            "domain_predictions": {"health": 5.0, "wealth": 6.0},
            "risk_predictions": {"health": 4.0, "wealth": 3.0},
            "goal_probabilities": {},
        }
        
        report1 = service1.generate_report(forecast_data=data)
        report2 = service2.generate_report(forecast_data=data)
        
        # Same number of insights
        assert report1.total_insights == report2.total_insights


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
