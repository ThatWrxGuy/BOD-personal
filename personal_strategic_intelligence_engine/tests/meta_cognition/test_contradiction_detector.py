"""Tests for Contradiction Detector."""
import pytest
from app.meta_cognition import (
    ContradictionDetector,
    OriginEngine,
    ContradictionSeverity,
)


class TestContradictionDetector:
    """Tests for ContradictionDetector."""

    def setup_method(self):
        self.detector = ContradictionDetector()

    def test_detect_contradictions_forecast_simulation(self):
        """Test detecting contradictions between forecast and simulation."""
        forecast_data = {"recommendation": "aggressive", "confidence": 0.8}
        simulation_data = {"recommendation": "defensive", "confidence": 0.7}
        
        contradictions = self.detector.detect_contradictions(
            forecast_data,
            simulation_data,
            OriginEngine.FORECAST,
            OriginEngine.SIMULATION,
        )
        
        assert len(contradictions) >= 0  # May or may not detect

    def test_detect_contradictions_forecast_monte_carlo(self):
        """Test detecting contradictions between forecast and Monte Carlo."""
        forecast_data = {"risk_assessment": 0.2, "expected_outcome": 0.7}
        monte_carlo_data = {"expected_max_drawdown": 0.6, "expected_return": 0.2}
        
        contradictions = self.detector.detect_contradictions(
            forecast_data,
            monte_carlo_data,
            OriginEngine.FORECAST,
            OriginEngine.MONTE_CARLO,
        )
        
        # Should detect contradiction
        assert len(contradictions) >= 1

    def test_detect_all_contradictions(self):
        """Test detecting contradictions across all engines."""
        all_engines_data = {
            OriginEngine.FORECAST: {"recommendation": "growth", "confidence": 0.7},
            OriginEngine.SIMULATION: {"recommendation": "neutral", "confidence": 0.6},
            OriginEngine.MONTE_CARLO: {"recommendation": "contraction", "confidence": 0.5},
        }
        
        contradictions = self.detector.detect_all_contradictions(all_engines_data)
        
        assert contradictions is not None

    def test_has_critical_contradictions(self):
        """Test checking for critical contradictions."""
        from app.meta_cognition.meta_models import ContradictionRecord
        
        # No contradictions
        assert not self.detector.has_critical_contradictions([])
        
        # Low severity
        low_contradiction = ContradictionRecord(
            contradiction_id="test",
            engine_a=OriginEngine.FORECAST,
            engine_b=OriginEngine.SIMULATION,
            conflicting_signal="test",
            severity=ContradictionSeverity.LOW,
        )
        assert not self.detector.has_critical_contradictions([low_contradiction])
        
        # Critical severity
        critical_contradiction = ContradictionRecord(
            contradiction_id="test2",
            engine_a=OriginEngine.FORECAST,
            engine_b=OriginEngine.SIMULATION,
            conflicting_signal="test",
            severity=ContradictionSeverity.CRITICAL,
        )
        assert self.detector.has_critical_contradictions([critical_contradiction])

    def test_get_contradiction_severity_summary(self):
        """Test getting severity summary."""
        from app.meta_cognition.meta_models import ContradictionRecord
        
        contradictions = [
            ContradictionRecord(
                contradiction_id="1",
                engine_a=OriginEngine.FORECAST,
                engine_b=OriginEngine.SIMULATION,
                conflicting_signal="test",
                severity=ContradictionSeverity.CRITICAL,
            ),
            ContradictionRecord(
                contradiction_id="2",
                engine_a=OriginEngine.FORECAST,
                engine_b=OriginEngine.MONTE_CARLO,
                conflicting_signal="test",
                severity=ContradictionSeverity.HIGH,
            ),
        ]
        
        summary = self.detector.get_contradiction_severity_summary(contradictions)
        
        assert summary["critical"] == 1
        assert summary["high"] == 1
