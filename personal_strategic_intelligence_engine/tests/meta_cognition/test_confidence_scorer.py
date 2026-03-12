"""Tests for Confidence Scorer."""
import pytest
from app.meta_cognition import (
    ConfidenceScorer,
    ConfidenceTier,
)


class TestConfidenceScorer:
    """Tests for ConfidenceScorer."""

    def test_calculate_confidence_with_all_data(self):
        """Test confidence calculation with all data provided."""
        scorer = ConfidenceScorer()
        
        forecast_data = {"reliability": 0.8, "trend_confidence": 0.7}
        simulation_data = {"success_rate": 0.75, "outcome_variance": 0.2}
        monte_carlo_data = {"distribution_confidence": 0.8, "sample_size": 1000}
        
        score, tier = scorer.calculate_confidence(
            forecast_data=forecast_data,
            simulation_data=simulation_data,
            monte_carlo_data=monte_carlo_data,
            doctrine_alignment=0.7,
            signals=[
                {"direction": "positive"},
                {"direction": "positive"},
            ],
            contradiction_penalty=0.0,
        )
        
        assert 0 <= score <= 1
        assert tier in ConfidenceTier

    def test_calculate_confidence_no_data(self):
        """Test confidence calculation with no data."""
        scorer = ConfidenceScorer()
        
        score, tier = scorer.calculate_confidence()
        
        # Should return default low score
        assert score > 0
        assert tier == ConfidenceTier.LOW

    def test_calculate_confidence_with_signals(self):
        """Test confidence with signal agreement."""
        scorer = ConfidenceScorer()
        
        # All positive signals
        score_pos, _ = scorer.calculate_confidence(
            signals=[
                {"direction": "positive"},
                {"direction": "positive"},
            ]
        )
        
        # Mixed signals
        score_mixed, _ = scorer.calculate_confidence(
            signals=[
                {"direction": "positive"},
                {"direction": "negative"},
            ]
        )
        
        # Positive agreement should be higher
        assert score_pos >= score_mixed

    def test_contradiction_penalty(self):
        """Test contradiction penalty calculation."""
        from app.meta_cognition.confidence_scorer import calculate_contradiction_penalty
        
        # No contradictions
        penalty = calculate_contradiction_penalty([])
        assert penalty == 0.0
        
        # Low severity contradiction
        penalty = calculate_contradiction_penalty([{"severity": "low"}])
        assert penalty > 0
        
        # Critical severity contradiction
        penalty = calculate_contradiction_penalty([{"severity": "critical"}])
        assert penalty > 0.1
        
        # Penalty is capped
        penalty = calculate_contradiction_penalty([{"severity": "critical"}] * 10)
        assert penalty <= 0.5

    def test_confidence_tier_mapping(self):
        """Test confidence tier mapping."""
        scorer = ConfidenceScorer()
        
        # Test threshold mapping
        assert scorer._get_confidence_tier(0.9) == ConfidenceTier.VERY_HIGH
        assert scorer._get_confidence_tier(0.75) == ConfidenceTier.HIGH
        assert scorer._get_confidence_tier(0.55) == ConfidenceTier.MODERATE
        assert scorer._get_confidence_tier(0.3) == ConfidenceTier.LOW

    def test_minimum_confidence_for_approval(self):
        """Test getting minimum confidence for approval."""
        scorer = ConfidenceScorer()
        
        min_conf = scorer.get_minimum_confidence_for_approval()
        assert min_conf == 0.5  # MODERATE threshold
