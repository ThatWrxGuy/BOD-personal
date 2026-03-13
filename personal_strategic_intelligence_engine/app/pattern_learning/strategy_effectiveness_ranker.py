"""Strategy Effectiveness Ranker.

Ranks strategy families by historical effectiveness.
"""
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

from app.pattern_learning.pattern_models import (
    ContextCluster,
    DecisionPattern,
    StrategyEffectivenessScore,
    StrategyFamily,
)


class StrategyEffectivenessRanker:
    """Ranks strategy families by historical effectiveness."""
    
    # Minimum sample size for ranking
    MIN_SAMPLE_FOR_RANKING = 3
    
    # Score weights
    SUCCESS_RATE_WEIGHT = 0.6
    SAMPLE_SIZE_WEIGHT = 0.3
    RECENCY_WEIGHT = 0.1
    
    def __init__(self):
        self._rankings: Dict[str, List[StrategyEffectivenessScore]] = {}
    
    def rank_strategies_for_context(
        self,
        context_cluster: ContextCluster,
        patterns: List[DecisionPattern],
    ) -> List[StrategyEffectivenessScore]:
        """Rank strategy families for a specific context."""
        
        # Filter patterns in this context
        context_patterns = [
            p for p in patterns
            if p.pattern_id in context_cluster.pattern_ids
        ]
        
        # Group by strategy family
        family_results = defaultdict(lambda: {"successes": 0, "total": 0, "last_outcome": None})
        
        for pattern in context_patterns:
            family = pattern.recommendation_family
            family_results[family]["total"] += pattern.total_count
            family_results[family]["successes"] += pattern.success_count
        
        # Calculate scores
        scores = []
        
        for family, results in family_results.items():
            total = results["total"]
            
            if total >= self.MIN_SAMPLE_FOR_RANKING:
                success_rate = results["successes"] / total if total > 0 else 0.0
                
                score = self._calculate_effectiveness_score(
                    success_rate=success_rate,
                    sample_size=total,
                )
                
                scores.append(StrategyEffectivenessScore(
                    strategy_family=family,
                    context_cluster_id=context_cluster.cluster_id,
                    rank=0,  # Will be set after sorting
                    score=score,
                    success_rate=success_rate,
                    sample_size=total,
                    contextual_adjustment=0.0,
                    final_score=score,
                    confidence=self._calculate_confidence(total),
                    is_reliable=total >= 10,
                ))
        
        # Sort by score
        scores.sort(key=lambda s: s.score, reverse=True)
        
        # Assign ranks
        for i, score in enumerate(scores):
            score.rank = i + 1
        
        # Store rankings
        self._rankings[context_cluster.cluster_id] = scores
        
        return scores
    
    def rank_strategies_global(
        self,
        patterns: List[DecisionPattern],
    ) -> List[StrategyEffectivenessScore]:
        """Rank strategy families globally (across all contexts)."""
        
        # Group by strategy family
        family_results = defaultdict(lambda: {"successes": 0, "total": 0})
        
        for pattern in patterns:
            family = pattern.recommendation_family
            family_results[family]["total"] += pattern.total_count
            family_results[family]["successes"] += pattern.success_count
        
        # Calculate scores
        scores = []
        
        for family, results in family_results.items():
            total = results["total"]
            
            if total >= self.MIN_SAMPLE_FOR_RANKING:
                success_rate = results["successes"] / total if total > 0 else 0.0
                
                score = self._calculate_effectiveness_score(
                    success_rate=success_rate,
                    sample_size=total,
                )
                
                scores.append(StrategyEffectivenessScore(
                    strategy_family=family,
                    context_cluster_id="global",
                    rank=0,
                    score=score,
                    success_rate=success_rate,
                    sample_size=total,
                    contextual_adjustment=0.0,
                    final_score=score,
                    confidence=self._calculate_confidence(total),
                    is_reliable=total >= 10,
                ))
        
        # Sort and rank
        scores.sort(key=lambda s: s.score, reverse=True)
        
        for i, score in enumerate(scores):
            score.rank = i + 1
        
        self._rankings["global"] = scores
        
        return scores
    
    def get_recommended_strategies(
        self,
        context_cluster_id: str,
        limit: int = 3,
    ) -> List[StrategyFamily]:
        """Get top recommended strategies for a context."""
        
        rankings = self._rankings.get(context_cluster_id, [])
        
        return [s.strategy_family for s in rankings[:limit]]
    
    def get_suppressed_strategies(
        self,
        context_cluster_id: str,
        threshold: float = 0.4,
    ) -> List[StrategyFamily]:
        """Get strategies that should be suppressed in a context."""
        
        rankings = self._rankings.get(context_cluster_id, [])
        
        return [
            s.strategy_family for s in rankings
            if s.success_rate < threshold
        ]
    
    def _calculate_effectiveness_score(
        self,
        success_rate: float,
        sample_size: int,
    ) -> float:
        """Calculate overall effectiveness score."""
        
        # Success rate component
        success_component = success_rate * self.SUCCESS_RATE_WEIGHT
        
        # Sample size component (diminishing returns)
        sample_component = min(1.0, sample_size / 20.0) * self.SAMPLE_SIZE_WEIGHT
        
        return success_component + sample_component
    
    def _calculate_confidence(self, sample_size: int) -> float:
        """Calculate confidence based on sample size."""
        
        if sample_size >= 20:
            return 0.9
        elif sample_size >= 10:
            return 0.7
        elif sample_size >= 5:
            return 0.5
        else:
            return 0.3


# Global ranker instance
_strategy_effectiveness_ranker: Optional[StrategyEffectivenessRanker] = None


def get_strategy_effectiveness_ranker() -> StrategyEffectivenessRanker:
    """Get the global strategy effectiveness ranker instance."""
    global _strategy_effectiveness_ranker
    if _strategy_effectiveness_ranker is None:
        _strategy_effectiveness_ranker = StrategyEffectivenessRanker()
    return _strategy_effectiveness_ranker
