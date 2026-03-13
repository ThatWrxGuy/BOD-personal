"""Contextual Strategy Scorer.

Integrates pattern learning into recommendation scoring.
"""
from typing import Any, Dict, List, Optional

from app.pattern_learning.pattern_models import (
    ContextualStrategyScore,
    StrategyFamily,
)


class ContextualStrategyScorer:
    """Integrates pattern learning into recommendation scoring."""
    
    # Maximum adjustment from pattern learning
    MAX_PATTERN_ADJUSTMENT = 0.15
    
    # Exploration bonus for low-confidence contexts
    EXPLORATION_BONUS = 0.05
    
    # Minimum sample for reliable patterns
    MIN_RELIABLE_SAMPLE = 10
    
    def __init__(self):
        self._strategy_rankings: Dict[str, List] = {}
        self._global_rankings: List = []
    
    def set_rankings(
        self,
        cluster_rankings: Dict[str, List],
        global_rankings: List,
    ) -> None:
        """Set strategy rankings from the ranker."""
        self._strategy_rankings = cluster_rankings
        self._global_rankings = global_rankings
    
    def score_recommendation(
        self,
        recommendation_id: str,
        recommendation_type: str,
        base_score: float,
        context_cluster_id: Optional[str] = None,
    ) -> ContextualStrategyScore:
        """Score a recommendation with contextual pattern learning."""
        
        # Get strategy family
        from app.pattern_learning.recommendation_family_classifier import (
            get_recommendation_family_classifier,
        )
        
        classifier = get_recommendation_family_classifier()
        strategy_family = classifier.classify(recommendation_type)
        
        # Calculate pattern adjustment
        pattern_adjustment, justification = self._calculate_pattern_adjustment(
            strategy_family=strategy_family,
            context_cluster_id=context_cluster_id,
        )
        
        # Calculate exploration bonus
        exploration_bonus = self._calculate_exploration_bonus(
            strategy_family=strategy_family,
            context_cluster_id=context_cluster_id,
        )
        
        # Calculate final score
        final_score = base_score + pattern_adjustment + exploration_bonus
        final_score = max(0.0, min(1.0, final_score))
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            strategy_family=strategy_family,
            context_cluster_id=context_cluster_id,
        )
        
        return ContextualStrategyScore(
            recommendation_id=recommendation_id,
            recommendation_type=recommendation_type,
            strategy_family=strategy_family,
            base_score=base_score,
            pattern_adjustment=pattern_adjustment,
            exploration_bonus=exploration_bonus,
            final_score=final_score,
            confidence=confidence,
            justification=justification,
            context_cluster_id=context_cluster_id,
        )
    
    def _calculate_pattern_adjustment(
        self,
        strategy_family: StrategyFamily,
        context_cluster_id: Optional[str],
    ) -> tuple:
        """Calculate adjustment based on historical pattern effectiveness."""
        
        # Get rankings for context or use global
        rankings = None
        
        if context_cluster_id and context_cluster_id in self._strategy_rankings:
            rankings = self._strategy_rankings[context_cluster_id]
        elif self._global_rankings:
            rankings = self._global_rankings
        else:
            return 0.0, "No historical data available"
        
        # Find this strategy in rankings
        for ranking in rankings:
            if ranking.strategy_family == strategy_family:
                # Calculate adjustment based on rank
                rank = ranking.rank
                success_rate = ranking.success_rate
                
                if rank <= 2 and success_rate >= 0.7:
                    # Top performer - boost
                    adjustment = self.MAX_PATTERN_ADJUSTMENT * success_rate
                    return adjustment, f"Historical success in context (rank #{rank}, {success_rate:.0%} success)"
                elif rank >= 5 or success_rate < 0.4:
                    # Poor performer - suppress
                    adjustment = -self.MAX_PATTERN_ADJUSTMENT * (1 - success_rate)
                    return adjustment, f"Historical underperformance in context (rank #{rank}, {success_rate:.0%} success)"
                else:
                    return 0.0, f"Mixed historical results (rank #{rank}, {success_rate:.0%} success)"
        
        return 0.0, "Strategy not in historical rankings"
    
    def _calculate_exploration_bonus(
        self,
        strategy_family: StrategyFamily,
        context_cluster_id: Optional[str],
    ) -> float:
        """Calculate bonus for exploring less-tested strategies."""
        
        # Get rankings
        rankings = None
        
        if context_cluster_id and context_cluster_id in self._strategy_rankings:
            rankings = self._strategy_rankings[context_cluster_id]
        elif self._global_rankings:
            rankings = self._global_rankings
        
        if not rankings:
            return self.EXPLORATION_BONUS
        
        # Find this strategy
        for ranking in rankings:
            if ranking.strategy_family == strategy_family:
                # Low sample size = exploration bonus
                if ranking.sample_size < self.MIN_RELIABLE_SAMPLE:
                    return self.EXPLORATION_BONUS
        
        return 0.0
    
    def _calculate_confidence(
        self,
        strategy_family: StrategyFamily,
        context_cluster_id: Optional[str],
    ) -> float:
        """Calculate confidence in the scoring."""
        
        rankings = None
        
        if context_cluster_id and context_cluster_id in self._strategy_rankings:
            rankings = self._strategy_rankings[context_cluster_id]
        elif self._global_rankings:
            rankings = self._global_rankings
        
        if not rankings:
            return 0.3  # Low confidence with no data
        
        # Find this strategy
        for ranking in rankings:
            if ranking.strategy_family == strategy_family:
                return ranking.confidence
        
        return 0.3  # Unknown strategy
    
    def score_batch(
        self,
        recommendations: List[Dict[str, Any]],
        context_cluster_id: Optional[str] = None,
    ) -> List[ContextualStrategyScore]:
        """Score multiple recommendations."""
        
        scored = []
        
        for rec in recommendations:
            score = self.score_recommendation(
                recommendation_id=rec.get("recommendation_id", ""),
                recommendation_type=rec.get("action_type", ""),
                base_score=rec.get("base_score", 0.5),
                context_cluster_id=context_cluster_id,
            )
            scored.append(score)
        
        # Sort by final score
        scored.sort(key=lambda s: s.final_score, reverse=True)
        
        return scored


# Global scorer instance
_contextual_strategy_scorer: Optional[ContextualStrategyScorer] = None


def get_contextual_strategy_scorer() -> ContextualStrategyScorer:
    """Get the global contextual strategy scorer instance."""
    global _contextual_strategy_scorer
    if _contextual_strategy_scorer is None:
        _contextual_strategy_scorer = ContextualStrategyScorer()
    return _contextual_strategy_scorer
