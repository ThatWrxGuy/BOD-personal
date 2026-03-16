"""Strategy Ranker - BB-FIN-020

Ranks strategies based on composite performance scores.
"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.finance.strategy_lab.strategy_models import (
    StrategyDefinition,
    PerformanceMetrics,
    StrategyRobustnessProfile,
    StrategyRanking,
    StrategyLeaderboard,
)

logger = logging.getLogger(__name__)


class StrategyRanker:
    """Ranks strategies based on composite performance."""
    
    def __init__(self):
        pass
    
    def rank_strategies(
        self,
        strategies: List[StrategyDefinition],
        metrics_map: Dict[str, PerformanceMetrics],
        robustness_map: Optional[Dict[str, StrategyRobustnessProfile]] = None,
    ) -> StrategyLeaderboard:
        """Rank strategies and generate leaderboard."""
        
        rankings = []
        
        for strategy in strategies:
            metrics = metrics_map.get(strategy.strategy_id)
            
            if not metrics:
                continue
            
            ranking = self._create_ranking(strategy, metrics, robustness_map)
            rankings.append(ranking)
        
        # Sort by composite score
        rankings.sort(key=lambda x: x.composite_score, reverse=True)
        
        # Assign ranks
        for i, ranking in enumerate(rankings):
            ranking.rank = i + 1
        
        # Categorize strategies
        top = [r for r in rankings if r.composite_score >= 0.7]
        emerging = [r for r in rankings if 0.4 <= r.composite_score < 0.7]
        retired = []  # Would be populated from registry
        
        leaderboard = StrategyLeaderboard(
            timestamp=datetime.utcnow(),
            top_strategies=top[:10],
            emerging_strategies=emerging[:10],
            retired_strategies=retired,
            total_strategies=len(rankings),
            active_strategies=len([r for r in rankings if r.composite_score >= 0.4]),
            experimental_strategies=len(emerging),
        )
        
        logger.info(f"Generated leaderboard with {len(rankings)} ranked strategies")
        
        return leaderboard
    
    def _create_ranking(
        self,
        strategy: StrategyDefinition,
        metrics: PerformanceMetrics,
        robustness_map: Optional[Dict[str, StrategyRobustnessProfile]] = None,
    ) -> StrategyRanking:
        
        # Calculate component scores
        sharpe_score = self._score_sharpe(metrics.sharpe_ratio)
        consistency_score = self._score_consistency(metrics.win_rate, metrics.volatility)
        robustness_score = 0.5
        
        if robustness_map:
            robustness = robustness_map.get(strategy.strategy_id)
            if robustness:
                robustness_score = robustness.stability_score
        
        # Regime adaptation score
        regime_score = 0.5  # Default
        
        # Composite
        composite = (sharpe_score * 0.3 + consistency_score * 0.25 + 
                     robustness_score * 0.25 + regime_score * 0.2)
        
        # Summary
        summary = self._generate_summary(strategy, metrics, composite)
        
        return StrategyRanking(
            rank=0,  # Will be assigned later
            strategy_id=strategy.strategy_id,
            strategy_name=strategy.name,
            category=strategy.category,
            sharpe_score=sharpe_score,
            consistency_score=consistency_score,
            robustness_score=robustness_score,
            regime_adaptation_score=regime_score,
            composite_score=composite,
            performance_summary=summary,
        )
    
    def _score_sharpe(self, sharpe: float) -> float:
        if sharpe >= 2.0:
            return 1.0
        elif sharpe >= 1.5:
            return 0.85
        elif sharpe >= 1.0:
            return 0.7
        elif sharpe >= 0.5:
            return 0.5
        elif sharpe >= 0:
            return 0.3
        return 0.0
    
    def _score_consistency(self, win_rate: float, volatility: float) -> float:
        return win_rate * (1 - min(volatility, 1))
    
    def _generate_summary(
        self,
        strategy: StrategyDefinition,
        metrics: PerformanceMetrics,
        composite: float,
    ) -> str:
        
        if composite >= 0.8:
            verdict = "Excellent"
        elif composite >= 0.6:
            verdict = "Strong"
        elif composite >= 0.4:
            verdict = "Moderate"
        else:
            verdict = "Weak"
        
        return (
            f"{verdict} strategy with {metrics.total_trades} trades, "
            f"{metrics.win_rate:.0%} win rate, Sharpe {metrics.sharpe_ratio:.2f}"
        )
    
    def get_top_strategies(
        self,
        leaderboard: StrategyLeaderboard,
        n: int = 5,
    ) -> List[StrategyRanking]:
        """Get top N strategies from leaderboard."""
        return leaderboard.top_strategies[:n]
    
    def get_strategies_for_regime(
        self,
        leaderboard: StrategyLeaderboard,
        regime: str,
    ) -> List[StrategyRanking]:
        """Get strategies suitable for a specific regime."""
        # Would filter by regime compatibility
        return leaderboard.top_strategies


_strategy_ranker: Optional[StrategyRanker] = None


def get_strategy_ranker() -> StrategyRanker:
    global _strategy_ranker
    
    if _strategy_ranker is None:
        _strategy_ranker = StrategyRanker()
    
    return _strategy_ranker
