"""Recommendation Engine.

This module converts ranked opportunities into structured recommendations.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.finance.security_selection.selection_models import (
    ConvictionLevel,
    RankedOpportunity,
    SecurityCategory,
    SecurityRecommendation,
)


class RecommendationEngine:
    """Generates security recommendations."""
    
    # Default weights for allocation buckets
    BUCKET_WEIGHTS = {
        "Investment": 0.04,  # 4% max
        "Tactical": 0.02,    # 2% max
        "Income": 0.03,      # 3% max
        "Stability": 0.01,   # 1% max
    }
    
    def __init__(self):
        """Initialize the recommendation engine."""
        self.recommendations: list[SecurityRecommendation] = []
    
    def create_recommendation(
        self,
        opportunity: RankedOpportunity,
        name: Optional[str] = None,
        market_data: Optional[dict] = None,
    ) -> SecurityRecommendation:
        """Create a recommendation from a ranked opportunity.
        
        Args:
            opportunity: Ranked opportunity
            name: Company name
            market_data: Additional market data
            
        Returns:
            Security recommendation
        """
        # Determine suggested weight
        weight = self._calculate_weight(
            opportunity.score,
            opportunity.conviction,
            opportunity.allocation_bucket,
        )
        
        # Build rationale
        rationale = self._build_rationale(opportunity, market_data)
        
        # Determine positive and risk factors
        positive, risks = self._categorize_factors(opportunity)
        
        recommendation = SecurityRecommendation(
            id=str(uuid.uuid4()),
            symbol=opportunity.symbol,
            name=name or opportunity.symbol,
            category=opportunity.category,
            score=opportunity.score,
            conviction=opportunity.conviction,
            allocation_bucket=opportunity.allocation_bucket,
            suggested_weight=weight,
            rationale=rationale,
            positive_factors=positive,
            risk_factors=risks,
            timestamp=datetime.now(),
        )
        
        return recommendation
    
    def create_recommendations(
        self,
        opportunities: list[RankedOpportunity],
        market_data: Optional[dict] = None,
    ) -> list[SecurityRecommendation]:
        """Create recommendations from multiple opportunities.
        
        Args:
            opportunities: Ranked opportunities
            market_data: Additional market data
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        for opp in opportunities:
            rec = self.create_recommendation(opp, market_data=market_data)
            recommendations.append(rec)
            self.recommendations.append(rec)
        
        return recommendations
    
    def get_top_recommendations(
        self,
        n: int = 5,
        bucket: Optional[str] = None,
    ) -> list[SecurityRecommendation]:
        """Get top N recommendations.
        
        Args:
            n: Number to return
            bucket: Optional bucket filter
            
        Returns:
            Top recommendations
        """
        filtered = self.recommendations
        
        if bucket:
            filtered = [r for r in filtered if r.allocation_bucket == bucket]
        
        # Sort by score
        sorted_recs = sorted(filtered, key=lambda r: r.score, reverse=True)
        
        return sorted_recs[:n]
    
    def get_high_conviction_recommendations(self) -> list[SecurityRecommendation]:
        """Get all high conviction recommendations."""
        return [
            r for r in self.recommendations
            if r.conviction in [ConvictionLevel.HIGH, ConvictionLevel.EXCEPTIONAL]
        ]
    
    def _calculate_weight(
        self,
        score: float,
        conviction: ConvictionLevel,
        bucket: str,
    ) -> float:
        """Calculate suggested weight for a recommendation."""
        base_weight = self.BUCKET_WEIGHTS.get(bucket, 0.02)
        
        # Adjust by conviction
        conviction_multiplier = {
            ConvictionLevel.EXCEPTIONAL: 1.0,
            ConvictionLevel.HIGH: 0.85,
            ConvictionLevel.MODERATE: 0.65,
            ConvictionLevel.LOW: 0.40,
        }
        
        multiplier = conviction_multiplier.get(conviction, 0.5)
        
        return base_weight * multiplier
    
    def _build_rationale(
        self,
        opportunity: RankedOpportunity,
        market_data: Optional[dict],
    ) -> list[str]:
        """Build rationale from opportunity."""
        rationale = opportunity.rationale.copy()
        
        # Add allocation context
        rationale.append(f"Recommended for {opportunity.allocation_bucket} allocation")
        
        return rationale
    
    def _categorize_factors(
        self,
        opportunity: RankedOpportunity,
    ) -> tuple[list[str], list[str]]:
        """Categorize factors into positive and risks."""
        positive = []
        risks = []
        
        breakdown = opportunity.score_breakdown
        
        # Positive factors (high contributions)
        for factor, contribution in breakdown.items():
            if contribution > 10:
                positive.append(f"Strong {factor.replace('_', ' ')}")
            elif contribution > 5:
                positive.append(f"Good {factor.replace('_', ' ')}")
        
        # Risks (low scores)
        if opportunity.score < 60:
            risks.append("Below average overall score")
        
        if opportunity.conviction == ConvictionLevel.LOW:
            risks.append("Low conviction")
        
        return positive, risks


# Global instance
_recommendation_engine: Optional[RecommendationEngine] = None


def get_recommendation_engine() -> RecommendationEngine:
    """Get the global recommendation engine."""
    global _recommendation_engine
    
    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine()
    
    return _recommendation_engine
