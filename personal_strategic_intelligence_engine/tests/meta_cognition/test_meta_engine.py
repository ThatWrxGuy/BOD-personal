"""Tests for Meta Engine."""
import pytest
from app.meta_cognition import (
    MetaEngine,
    StrategicDecision,
    OriginEngine,
    ValidationStatus,
    ConfidenceTier,
    PolicyComplianceStatus,
    reset_meta_engine,
)


class TestMetaEngine:
    """Tests for MetaEngine."""

    def setup_method(self):
        reset_meta_engine()
        self.engine = MetaEngine()

    def test_create_decision(self):
        """Test creating a strategic decision."""
        decision = self.engine.create_decision(
            origin_engine=OriginEngine.FORECAST,
            recommendation_type="growth",
            recommendation_summary="Increase allocation to growth assets",
            supporting_signals=[
                {"source": "forecast", "direction": "positive", "confidence": 0.8}
            ],
        )
        assert decision.decision_id is not None
        assert decision.origin_engine == OriginEngine.FORECAST
        assert decision.recommendation_type == "growth"

    def test_evaluate_decision_approved(self):
        """Test evaluating a decision that should be approved."""
        decision = self.engine.create_decision(
            origin_engine=OriginEngine.FORECAST,
            recommendation_type="growth",
            recommendation_summary="Increase allocation",
            supporting_signals=[
                {"source": "forecast", "direction": "positive", "confidence": 0.8},
                {"source": "simulation", "direction": "positive", "confidence": 0.7},
            ],
            context={
                "forecast_data": {"reliability": 0.8},
                "simulation_data": {"success_rate": 0.75},
                "monte_carlo_data": {"distribution_confidence": 0.7},
                "doctrine_alignment": 0.8,
            },
        )
        
        result = self.engine.evaluate_decision(decision)
        
        assert result.validation_status == ValidationStatus.APPROVED
        assert result.confidence_score > 0

    def test_evaluate_decision_rejected_policy_violation(self):
        """Test evaluating a decision with policy violation."""
        decision = self.engine.create_decision(
            origin_engine=OriginEngine.SYNTHESIZER,
            recommendation_type="aggressive",
            recommendation_summary="High leverage strategy",
            supporting_signals=[],
            context={
                "leverage": 5.0,  # Exceeds max leverage
                "expected_drawdown": 0.3,
            },
        )
        
        result = self.engine.evaluate_decision(decision)
        
        # Should be rejected due to policy violation
        assert result.validation_status == ValidationStatus.REJECTED

    def test_evaluate_decision_requires_review_low_confidence(self):
        """Test evaluating a decision with low confidence."""
        decision = self.engine.create_decision(
            origin_engine=OriginEngine.SIMULATION,
            recommendation_type="maintain",
            recommendation_summary="Maintain current strategy",
            supporting_signals=[],  # No supporting signals
            context={
                "doctrine_alignment": 0.3,
            },
        )
        
        result = self.engine.evaluate_decision(decision)
        
        # Should require review due to low confidence
        assert result.validation_status in [
            ValidationStatus.REQUIRES_REVIEW,
            ValidationStatus.REJECTED,
        ]

    def test_get_audit_statistics(self):
        """Test getting audit statistics."""
        stats = self.engine.get_audit_statistics()
        assert "total_audits" in stats


class TestMetaEngineWithEngineOutputs:
    """Tests with engine outputs for contradiction detection."""

    def setup_method(self):
        reset_meta_engine()
        self.engine = MetaEngine()

    def test_contradiction_detection(self):
        """Test contradiction detection between engines."""
        engine_outputs = {
            OriginEngine.FORECAST: {"recommendation": "aggressive", "confidence": 0.8},
            OriginEngine.SIMULATION: {"recommendation": "defensive", "confidence": 0.7},
        }
        
        decision = self.engine.create_decision(
            origin_engine=OriginEngine.SYNTHESIZER,
            recommendation_type="growth",
            recommendation_summary="Test",
            supporting_signals=[],
            context={},
        )
        
        result = self.engine.evaluate_decision(decision, engine_outputs)
        
        # Check that contradictions were detected
        assert result.contradictions is not None
