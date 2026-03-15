"""Strategy Ranker.

Ranks strategies by current opportunity quality.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass

from app.intelligence.alpha_engine.alpha_models import AlphaCandidate, StrategyRanking


class StrategyRanker:
    """Ranks strategies by opportunity quality."""
    
    def __init__(self):
        self.rankings = []
    
    def rank_strategies(
        self,
        candidates: List[AlphaCandidate],
        current_regime: str,
        recent_performance: Dict[str, List[Dict]],
    ) -> List[StrategyRanking]:
        """Rank strategies by current opportunity quality."""
        
        rankings = []
        
        for i, candidate in enumerate(candidates):
            # Calculate scores
            regime_fit = self._calculate_regime_fit(candidate, current_regime)
            perf_score = self._calculate_performance_score(candidate, recent_performance.get(candidate.id, []))
            confidence = candidate.confidence_score
            
            # Overall score (weighted)
            score = (
                0.4 * regime_fit +
                0.3 * perf_score +
                0.3 * confidence
            )
            
            ranking = StrategyRanking(
                rank=i + 1,
                alpha_id=candidate.id,
                name=candidate.name,
                score=score,
                regime_fit=regime_fit,
                recent_performance=perf_score,
                confidence=confidence,
                recommendation=self._get_recommendation(score, regime_fit, perf_score),
            )
            
            rankings.append(ranking)
        
        # Sort by score
        rankings.sort(key=lambda r: r.score, reverse=True)
        
        # Update ranks
        for i, r in enumerate(rankings):
            r.rank = i + 1
        
        self.rankings = rankings
        return rankings
    
    def _calculate_regime_fit(
        self,
        candidate: AlphaCandidate,
        current_regime: str,
    ) -> float:
        """Calculate how well candidate fits current regime."""
        
        requirements = candidate.regime_requirements
        
        if not requirements:
            return 0.5
        
        # Simple match scoring
        if "regime" in requirements:
            if requirements["regime"] == current_regime:
                return 1.0
            return 0.3
        
        if "time" in requirements:
            if requirements["time"] in current_regime:
                return 1.0
            return 0.3
        
        return 0.5
    
    def _calculate_performance_score(
        self,
        candidate: AlphaCandidate,
        recent_trades: List[Dict],
    ) -> float:
        """Calculate recent performance score."""
        
        if not recent_trades:
            return 0.5
        
        # Calculate expectancy
        pnls = [t.get("pnl", 0) for t in recent_trades]
        if not pnls:
            return 0.5
        
        expectancy = sum(pnls) / len(pnls)
        
        # Normalize to 0-1
        score = (expectancy + 50) / 100
        return max(0, min(1, score))
    
    def _get_recommendation(
        self,
        score: float,
        regime_fit: float,
        perf_score: float,
    ) -> str:
        """Get recommendation based on scores."""
        
        if score > 0.8 and regime_fit > 0.8:
            return "Strong opportunity - deploy"
        elif score > 0.6:
            return "Good opportunity - consider"
        elif score > 0.4:
            return "Moderate opportunity - monitor"
        else:
            return "Weak opportunity - avoid"
    
    def get_top_strategy(self) -> Optional[StrategyRanking]:
        """Get top ranked strategy."""
        
        if self.rankings:
            return self.rankings[0]
        return None
    
    def get_recommendations_by_regime(
        self,
        regime: str,
    ) -> List[StrategyRanking]:
        """Get recommendations filtered by regime."""
        
        return [r for r in self.rankings if r.regime_fit > 0.7]


def create_ranker() -> StrategyRanker:
    """Create strategy ranker."""
    return StrategyRanker()
