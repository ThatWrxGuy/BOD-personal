"""Confidence Engine - assigns confidence scores to recommendations."""
from typing import Any, Dict, List

from app.finance.intelligence.models.financial_recommendation import FinancialRecommendation


class ConfidenceEngine:
    """
    Assigns a confidence score to each recommendation.
    
    Score Range: 0.0 - 1.0
    
    Example interpretation:
    0.90+ → High confidence
    0.70–0.89 → Moderate confidence
    <0.70 → Low confidence
    """

    # Confidence factors weights
    DATA_COMPLETENESS_WEIGHT = 0.30
    METRIC_RELIABILITY_WEIGHT = 0.25
    VOLATILITY_WEIGHT = 0.25
    SCENARIO_UNCERTAINTY_WEIGHT = 0.20

    @staticmethod
    def score(
        recommendations: List[FinancialRecommendation],
        financial_state: Dict[str, Any],
    ) -> List[FinancialRecommendation]:
        """
        Score confidence for each recommendation.

        Args:
            recommendations: List of recommendations to score
            financial_state: The canonical financial state

        Returns:
            List of recommendations with updated confidence scores
        """
        scored_recommendations = []

        for recommendation in recommendations:
            confidence = ConfidenceEngine._calculate_confidence(
                recommendation, financial_state
            )
            recommendation.confidence_score = confidence
            scored_recommendations.append(recommendation)

        return scored_recommendations

    @staticmethod
    def _calculate_confidence(
        recommendation: FinancialRecommendation,
        financial_state: Dict[str, Any],
    ) -> float:
        """Calculate confidence score for a recommendation."""
        
        # Start with recommendation's existing confidence
        base_confidence = recommendation.confidence_score
        
        # Adjust based on data completeness
        completeness = ConfidenceEngine._assess_data_completeness(financial_state)
        
        # Adjust based on metric reliability
        reliability = ConfidenceEngine._assess_metric_reliability(financial_state)
        
        # Adjust based on volatility
        volatility = ConfidenceEngine._assess_volatility(financial_state)
        
        # Adjust based on scenario uncertainty
        uncertainty = ConfidenceEngine._assess_scenario_uncertainty(financial_state, recommendation)
        
        # Calculate weighted confidence
        confidence = (
            completeness * ConfidenceEngine.DATA_COMPLETENESS_WEIGHT +
            reliability * ConfidenceEngine.METRIC_RELIABILITY_WEIGHT +
            volatility * ConfidenceEngine.VOLATILITY_WEIGHT +
            uncertainty * ConfidenceEngine.SCENARIO_UNCERTAINTY_WEIGHT
        )
        
        # Blend with base confidence (favor base but allow adjustments)
        final_confidence = (base_confidence * 0.5) + (confidence * 0.5)
        
        # Ensure within bounds
        return max(0.0, min(1.0, final_confidence))

    @staticmethod
    def _assess_data_completeness(financial_state: Dict[str, Any]) -> float:
        """Assess completeness of financial data (0-1)."""
        required_fields = [
            "net_worth", "monthly_income", "monthly_expenses",
            "free_cash_flow", "total_assets", "total_liabilities",
            "liquid_assets", "emergency_fund_months"
        ]
        
        present = sum(1 for field in required_fields if field in financial_state and financial_state.get(field) is not None)
        return present / len(required_fields)

    @staticmethod
    def _assess_metric_reliability(financial_state: Dict[str, Any]) -> float:
        """Assess reliability of financial metrics (0-1)."""
        # If we have detailed breakdowns, metrics are more reliable
        has_assets_by_category = bool(financial_state.get("assets_by_category"))
        has_liabilities_by_category = bool(financial_state.get("liabilities_by_category"))
        
        reliability = 0.6  # Base reliability
        
        if has_assets_by_category:
            reliability += 0.2
        if has_liabilities_by_category:
            reliability += 0.2
            
        return min(1.0, reliability)

    @staticmethod
    def _assess_volatility(financial_state: Dict[str, Any]) -> float:
        """Assess volatility/exposure (0-1, higher = more volatile = lower confidence)."""
        # Get volatility-related metrics
        # This is simplified - full implementation would analyze actual asset volatility
        
        # Check for negative net worth (high uncertainty)
        net_worth = financial_state.get("net_worth", 0)
        if net_worth < 0:
            return 0.5  # Lower confidence due to debt
            
        # Check emergency fund stability
        emergency_months = financial_state.get("emergency_fund_months", 0)
        if emergency_months < 3:
            return 0.6  # Lower confidence due to low reserves
            
        return 0.8  # Default reasonable confidence

    @staticmethod
    def _assess_scenario_uncertainty(
        financial_state: Dict[str, Any],
        recommendation: FinancialRecommendation,
    ) -> float:
        """Assess scenario uncertainty (0-1, higher = more certain)."""
        uncertainty = 0.7  # Base uncertainty
        
        # Cash flow certainty
        fcf = financial_state.get("free_cash_flow", 0)
        monthly_income = financial_state.get("monthly_income", 0)
        
        if monthly_income > 0:
            fcf_ratio = abs(fcf) / monthly_income
            if fcf_ratio > 0.2:
                # Large positive or negative relative to income
                uncertainty = 0.8
            elif abs(fcf_ratio) < 0.05:
                # Near break-even
                uncertainty = 0.6
        
        # Priority affects confidence - critical items typically more certain
        if recommendation.priority.value in ["critical", "high"]:
            uncertainty += 0.1
            
        return min(1.0, uncertainty)

    @staticmethod
    def get_confidence_label(confidence: float) -> str:
        """Get human-readable confidence label."""
        if confidence >= 0.90:
            return "High"
        elif confidence >= 0.70:
            return "Moderate"
        else:
            return "Low"
