"""Confidence scoring engine for strategic recommendations."""
from typing import Dict, Any, List, Optional
from app.meta_cognition.meta_types import ConfidenceTier
from app.meta_cognition.meta_models import ConfidenceScoreComponents


class ConfidenceScorer:
    """Calculates confidence scores for strategic recommendations.
    
    Confidence scoring formula:
    confidence_score =
        forecast_weight +
        simulation_weight +
        monte_carlo_weight +
        doctrine_alignment_weight -
        contradiction_penalty
    """
    
    # Default weights for each component
    DEFAULT_WEIGHTS = {
        "forecast_reliability": 0.25,
        "simulation_stability": 0.25,
        "monte_carlo_confidence": 0.20,
        "doctrine_alignment": 0.15,
        "signal_agreement": 0.15,
    }
    
    # Minimum confidence thresholds for each tier
    CONFIDENCE_TIERS = {
        ConfidenceTier.VERY_HIGH: 0.85,
        ConfidenceTier.HIGH: 0.70,
        ConfidenceTier.MODERATE: 0.50,
        ConfidenceTier.LOW: 0.0,
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS
    
    def calculate_confidence(
        self,
        forecast_data: Optional[Dict[str, Any]] = None,
        simulation_data: Optional[Dict[str, Any]] = None,
        monte_carlo_data: Optional[Dict[str, Any]] = None,
        doctrine_alignment: float = 0.5,
        signals: Optional[List[Dict[str, Any]]] = None,
        contradiction_penalty: float = 0.0,
    ) -> tuple[float, ConfidenceTier]:
        """Calculate confidence score for a recommendation.
        
        Args:
            forecast_data: Forecast engine data (reliability, trend)
            simulation_data: Simulation engine data (stability, outcomes)
            monte_carlo_data: Monte Carlo data (distribution confidence)
            doctrine_alignment: Alignment with established doctrine (0-1)
            signals: List of supporting signals from various engines
            contradiction_penalty: Penalty for detected contradictions
            
        Returns:
            Tuple of (confidence_score, confidence_tier)
        """
        components = self._calculate_components(
            forecast_data=forecast_data,
            simulation_data=simulation_data,
            monte_carlo_data=monte_carlo_data,
            doctrine_alignment=doctrine_alignment,
            signals=signals,
            contradiction_penalty=contradiction_penalty,
        )
        
        score = components.total_score()
        tier = self._get_confidence_tier(score)
        
        return score, tier
    
    def _calculate_components(
        self,
        forecast_data: Optional[Dict[str, Any]],
        simulation_data: Optional[Dict[str, Any]],
        monte_carlo_data: Optional[Dict[str, Any]],
        doctrine_alignment: float,
        signals: Optional[List[Dict[str, Any]]],
        contradiction_penalty: float,
    ) -> ConfidenceScoreComponents:
        """Calculate individual components of confidence."""
        
        # Calculate forecast reliability (0-1)
        forecast_reliability = self._calculate_forecast_reliability(forecast_data)
        
        # Calculate simulation stability (0-1)
        simulation_stability = self._calculate_simulation_stability(simulation_data)
        
        # Calculate Monte Carlo confidence (0-1)
        monte_carlo_confidence = self._calculate_monte_carlo_confidence(monte_carlo_data)
        
        # Signal agreement (0-1)
        signal_agreement = self._calculate_signal_agreement(signals)
        
        # Apply weights
        weighted_forecast = forecast_reliability * self.weights["forecast_reliability"]
        weighted_simulation = simulation_stability * self.weights["simulation_stability"]
        weighted_monte_carlo = monte_carlo_confidence * self.weights["monte_carlo_confidence"]
        weighted_doctrine = doctrine_alignment * self.weights["doctrine_alignment"]
        weighted_signals = signal_agreement * self.weights["signal_agreement"]
        
        return ConfidenceScoreComponents(
            forecast_reliability=weighted_forecast,
            simulation_stability=weighted_simulation,
            monte_carlo_confidence=weighted_monte_carlo,
            doctrine_alignment=weighted_doctrine,
            signal_agreement=weighted_signals,
            contradiction_penalty=contradiction_penalty,
        )
    
    def _calculate_forecast_reliability(
        self, forecast_data: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate forecast reliability score."""
        if not forecast_data:
            return 0.3  # Default low score
        
        # Look for reliability indicators
        reliability = forecast_data.get("reliability", 0.5)
        trend_confidence = forecast_data.get("trend_confidence", 0.5)
        data_quality = forecast_data.get("data_quality", 0.5)
        
        # Weight the factors
        return (reliability * 0.4 + trend_confidence * 0.4 + data_quality * 0.2)
    
    def _calculate_simulation_stability(
        self, simulation_data: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate simulation stability score."""
        if not simulation_data:
            return 0.3  # Default low score
        
        # Look for stability indicators
        outcome_variance = simulation_data.get("outcome_variance", 0.5)
        success_rate = simulation_data.get("success_rate", 0.5)
        convergence = simulation_data.get("convergence", 0.5)
        
        # High variance = low stability
        stability = 1.0 - outcome_variance
        
        # Weight the factors
        return (stability * 0.4 + success_rate * 0.4 + convergence * 0.2)
    
    def _calculate_monte_carlo_confidence(
        self, monte_carlo_data: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate Monte Carlo confidence score."""
        if not monte_carlo_data:
            return 0.3  # Default low score
        
        # Look for confidence indicators
        distribution_confidence = monte_carlo_data.get("distribution_confidence", 0.5)
        sample_size = monte_carlo_data.get("sample_size", 100)
        convergence = monte_carlo_data.get("convergence", 0.5)
        
        # Adjust for sample size (more samples = more confidence)
        sample_factor = min(1.0, sample_size / 1000)
        
        # Weight the factors
        return (
            distribution_confidence * 0.4 +
            sample_factor * 0.3 +
            convergence * 0.3
        )
    
    def _calculate_signal_agreement(
        self, signals: Optional[List[Dict[str, Any]]]
    ) -> float:
        """Calculate signal agreement score."""
        if not signals or len(signals) == 0:
            return 0.3  # Default low score
        
        if len(signals) == 1:
            return 0.5  # Single signal, moderate confidence
        
        # Calculate agreement between signals
        positive_count = sum(1 for s in signals if s.get("direction", "neutral") == "positive")
        negative_count = sum(1 for s in signals if s.get("direction", "neutral") == "negative")
        
        total = len(signals)
        agreement = max(positive_count, negative_count) / total
        
        return agreement
    
    def _get_confidence_tier(self, score: float) -> ConfidenceTier:
        """Map confidence score to tier."""
        if score >= self.CONFIDENCE_TIERS[ConfidenceTier.VERY_HIGH]:
            return ConfidenceTier.VERY_HIGH
        elif score >= self.CONFIDENCE_TIERS[ConfidenceTier.HIGH]:
            return ConfidenceTier.HIGH
        elif score >= self.CONFIDENCE_TIERS[ConfidenceTier.MODERATE]:
            return ConfidenceTier.MODERATE
        else:
            return ConfidenceTier.LOW
    
    def get_minimum_confidence_for_approval(self) -> float:
        """Get minimum confidence score required for approval."""
        return self.CONFIDENCE_TIERS[ConfidenceTier.MODERATE]
    
    def update_weights(self, weights: Dict[str, float]):
        """Update scoring weights."""
        # Validate weights sum to approximately 1.0
        total = sum(weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError("Weights must sum to 1.0")
        self.weights = weights


def calculate_contradiction_penalty(
    contradictions: List[Dict[str, Any]]
) -> float:
    """Calculate penalty for detected contradictions.
    
    Args:
        contradictions: List of detected contradictions
        
    Returns:
        Penalty value (0-0.5)
    """
    if not contradictions:
        return 0.0
    
    penalty = 0.0
    
    for contradiction in contradictions:
        severity = contradiction.get("severity", "low")
        
        if severity == "critical":
            penalty += 0.15
        elif severity == "high":
            penalty += 0.10
        elif severity == "medium":
            penalty += 0.05
        elif severity == "low":
            penalty += 0.02
    
    # Cap penalty at 0.5
    return min(penalty, 0.5)
