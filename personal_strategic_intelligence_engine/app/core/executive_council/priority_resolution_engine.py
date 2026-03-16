"""Priority Resolution Engine - BB-CORE-022

Ranks recommendations by strategic importance.
"""

from datetime import datetime
from typing import List
import logging

from app.core.executive_council.council_models import (
    PriorityLevel,
    DomainRecommendation,
    RankedRecommendation,
    PriorityLevel,
)

logger = logging.getLogger(__name__)


class PriorityResolutionEngine:
    """Ranks recommendations by strategic importance."""
    
    def __init__(self):
        # Priority weights for different factors
        self._priority_weights = {
            PriorityLevel.CRITICAL: 1.0,
            PriorityLevel.HIGH: 0.75,
            PriorityLevel.MEDIUM: 0.5,
            PriorityLevel.LOW: 0.25,
        }
        
        # Domain importance factors
        self._domain_weights = {
            Domain.HEALTH: 1.0,  # Health always comes first
            Domain.FINANCE: 0.85,
            Domain.CAREER: 0.7,
            Domain.LIFESTYLE: 0.6,
            Domain.RELATIONSHIPS: 0.55,
            Domain.INTELLIGENCE: 0.5,
        }
    
    def resolve_priorities(
        self,
        recommendations: List[DomainRecommendation],
    ) -> List[RankedRecommendation]:
        """Rank recommendations by priority."""
        
        if not recommendations:
            return []
        
        # Calculate priority scores
        scored = []
        for rec in recommendations:
            score = self._calculate_priority_score(rec)
            reasoning = self._generate_reasoning(rec, score)
            
            scored.append({
                "recommendation": rec,
                "score": score,
                "reasoning": reasoning,
            })
        
        # Sort by score (descending)
        scored.sort(key=lambda x: x["score"], reverse=True)
        
        # Create ranked recommendations
        ranked = []
        for i, item in enumerate(scored):
            ranked.append(RankedRecommendation(
                rank=i + 1,
                recommendation=item["recommendation"],
                priority_score=item["score"],
                reasoning=item["reasoning"],
            ))
        
        logger.info(f"Resolved priorities for {len(recommendations)} recommendations")
        
        return ranked
    
    def _calculate_priority_score(self, rec: DomainRecommendation) -> float:
        """Calculate priority score for a recommendation."""
        
        # Base priority score
        priority_score = self._priority_weights.get(rec.priority, 0.5)
        
        # Confidence factor
        confidence_factor = rec.confidence
        
        # Domain importance
        domain_weight = self._domain_weights.get(rec.domain, 0.5)
        
        # Signal strength (average of signal strengths)
        signal_strength = 0.5
        if rec.signals:
            signal_strength = sum(s.strength for s in rec.signals) / len(rec.signals)
        
        # Calculate combined score
        score = (
            priority_score * 0.35 +
            confidence_factor * 0.25 +
            domain_weight * 0.25 +
            signal_strength * 0.15
        )
        
        return score
    
    def _generate_reasoning(self, rec: DomainRecommendation, score: float) -> str:
        """Generate reasoning for the priority ranking."""
        
        reasons = []
        
        # Priority reason
        if rec.priority == PriorityLevel.CRITICAL:
            reasons.append(f"Critical priority ({rec.priority.value})")
        elif rec.priority == PriorityLevel.HIGH:
            reasons.append(f"High priority ({rec.priority.value})")
        
        # Domain reason
        reasons.append(f"Domain: {rec.domain.value}")
        
        # Confidence reason
        if rec.confidence >= 0.8:
            reasons.append(f"High confidence ({rec.confidence:.0%})")
        elif rec.confidence >= 0.6:
            reasons.append(f"Moderate confidence ({rec.confidence:.0%})")
        
        # Signal reason
        if rec.signals:
            reasons.append(f"{len(rec.signals)} supporting signals")
        
        # Score summary
        reasons.append(f"Priority score: {score:.2f}")
        
        return "; ".join(reasons)
    
    def get_top_n(
        self,
        ranked: List[RankedRecommendation],
        n: int = 5,
    ) -> List[RankedRecommendation]:
        """Get top N recommendations."""
        return ranked[:n]
    
    def get_by_level(
        self,
        ranked: List[RankedRecommendation],
        level: PriorityLevel,
    ) -> List[RankedRecommendation]:
        """Get recommendations by priority level."""
        return [r for r in ranked if r.recommendation.priority == level]


_priority_engine: PriorityResolutionEngine = None


def get_priority_resolution_engine() -> PriorityResolutionEngine:
    """Get the priority resolution engine."""
    global _priority_engine
    
    if _priority_engine is None:
        _priority_engine = PriorityResolutionEngine()
    
    return _priority_engine
