"""Recommendation scorer for evaluating recommendation effectiveness."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.learning.outcome_models import (
    OutcomeQuality,
    RecommendationEffectivenessScore,
)

logger = logging.getLogger(__name__)


class RecommendationScorer:
    """Scores recommendation effectiveness based on outcomes."""

    def __init__(self):
        self._scores: Dict[str, RecommendationEffectivenessScore] = {}

    def score_recommendation(
        self,
        recommendation_id: str,
        outcome_quality: OutcomeQuality,
        magnitude: float,
        urgency: str = "medium",
    ) -> RecommendationEffectivenessScore:
        """Score a single recommendation based on its outcome."""
        
        # Get existing or create new
        if recommendation_id in self._scores:
            score = self._scores[recommendation_id]
            score.total_evaluations += 1
        else:
            score = RecommendationEffectivenessScore(
                recommendation_id=recommendation_id,
                total_evaluations=1,
            )

        # Update outcome counts
        if outcome_quality == OutcomeQuality.IMPROVEMENT:
            score.positive_outcomes += 1
        elif outcome_quality in [OutcomeQuality.DETERIORATION, OutcomeQuality.MIXED]:
            score.negative_outcomes += 1
        else:
            score.neutral_outcomes += 1

        # Calculate average effectiveness
        total = score.total_evaluations
        score.average_effectiveness = (
            (score.positive_outcomes * 1.0 + 
             score.neutral_outcomes * 0.5 + 
             score.negative_outcomes * 0.0) 
            / total
        )

        # Calculate confidence impact
        score.confidence_impact = self._calculate_confidence_impact(
            outcome_quality, magnitude, urgency
        )

        # Identify pattern flags
        score.pattern_flags = self._identify_patterns(score)

        self._scores[recommendation_id] = score
        return score

    def _calculate_confidence_impact(
        self,
        outcome_quality: OutcomeQuality,
        magnitude: float,
        urgency: str,
    ) -> float:
        """Calculate how this outcome should impact future confidence."""
        
        # Base impact from outcome quality
        quality_impact = {
            OutcomeQuality.IMPROVEMENT: 0.1,
            OutcomeQuality.NO_CHANGE: 0.0,
            OutcomeQuality.DETERIORATION: -0.1,
            OutcomeQuality.MIXED: -0.05,
            OutcomeQuality.INSUFFICIENT_EVIDENCE: 0.0,
        }.get(outcome_quality, 0.0)

        # Adjust for magnitude
        magnitude_factor = magnitude * 0.05

        # Adjust for urgency (high urgency recommendations should have more impact)
        urgency_factor = {
            "critical": 1.5,
            "high": 1.2,
            "medium": 1.0,
            "low": 0.8,
        }.get(urgency, 1.0)

        impact = (quality_impact + magnitude_factor) * urgency_factor
        
        # Bound the impact
        return max(-0.2, min(0.2, impact))

    def _identify_patterns(
        self,
        score: RecommendationEffectivenessScore
    ) -> List[str]:
        """Identify patterns in recommendation effectiveness."""
        flags = []

        if score.total_evaluations >= 3:
            # Check for consistently positive
            if score.positive_outcomes / score.total_evaluations >= 0.8:
                flags.append("consistently_positive")
            
            # Check for consistently negative
            if score.negative_outcomes / score.total_evaluations >= 0.6:
                flags.append("consistently_negative")
            
            # Check for inconsistent
            if (score.positive_outcomes > 0 and score.negative_outcomes > 0):
                flags.append("inconsistent")

        # Check for high effectiveness
        if score.average_effectiveness >= 0.8:
            flags.append("high_effectiveness")
        
        # Check for low effectiveness
        if score.average_effectiveness < 0.4 and score.total_evaluations >= 2:
            flags.append("low_effectiveness")

        return flags

    def get_effectiveness_for_domain(
        self,
        domain_scores: Dict[str, RecommendationEffectivenessScore]
    ) -> Dict[str, float]:
        """Calculate aggregate effectiveness by domain."""
        
        domain_effectiveness = {}
        
        for rec_id, score in domain_scores.items():
            # Group by domain (would need domain in score)
            domain = "unknown"
            
            if domain not in domain_effectiveness:
                domain_effectiveness[domain] = []
            domain_effectiveness[domain].append(score.average_effectiveness)
        
        # Calculate averages
        result = {}
        for domain, scores in domain_effectiveness.items():
            if scores:
                result[domain] = sum(scores) / len(scores)
        
        return result

    def get_weak_recommendations(
        self,
        threshold: float = 0.4,
        min_evaluations: int = 2
    ) -> List[str]:
        """Get IDs of recommendations with low effectiveness."""
        return [
            rec_id for rec_id, score in self._scores.items()
            if score.average_effectiveness < threshold 
            and score.total_evaluations >= min_evaluations
        ]

    def get_strong_recommendations(
        self,
        threshold: float = 0.7,
        min_evaluations: int = 2
    ) -> List[str]:
        """Get IDs of recommendations with high effectiveness."""
        return [
            rec_id for rec_id, score in self._scores.items()
            if score.average_effectiveness >= threshold
            and score.total_evaluations >= min_evaluations
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get scorer statistics."""
        
        if not self._scores:
            return {
                "total_scored": 0,
                "avg_effectiveness": 0.0,
                "weak_count": 0,
                "strong_count": 0,
            }

        total = len(self._scores)
        avg_effectiveness = sum(
            s.average_effectiveness for s in self._scores.values()
        ) / total

        return {
            "total_scored": total,
            "avg_effectiveness": avg_effectiveness,
            "weak_count": len(self.get_weak_recommendations()),
            "strong_count": len(self.get_strong_recommendations()),
            "total_evaluations": sum(
                s.total_evaluations for s in self._scores.values()
            ),
        }


# Global scorer instance
_scorer: Optional[RecommendationScorer] = None


def get_recommendation_scorer() -> RecommendationScorer:
    """Get the global recommendation scorer instance."""
    global _scorer
    if _scorer is None:
        _scorer = RecommendationScorer()
    return _scorer
