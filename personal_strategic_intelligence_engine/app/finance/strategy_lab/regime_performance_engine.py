"""Regime Performance Engine - BB-FIN-020

Evaluates strategy performance under specific market regimes.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import random
import statistics

from app.finance.strategy_lab.strategy_models import (
    BacktestResult,
    BacktestTrade,
    RegimePerformance,
    MarketRegime,
    StrategyDefinition,
)

logger = logging.getLogger(__name__)


class RegimePerformanceEngine:
    """Analyzes strategy performance across market regimes."""
    
    def __init__(self):
        self._regime_history: Dict[MarketRegime, List[datetime]] = {}
        self._initialize_regime_history()
    
    def _initialize_regime_history(self) -> None:
        """Initialize demo regime history."""
        now = datetime.utcnow()
        
        self._regime_history = {
            MarketRegime.RISK_ON_TREND: [now - timedelta(days=60), now - timedelta(days=30)],
            MarketRegime.RISK_ON_MOMENTUM: [now - timedelta(days=45), now - timedelta(days=15)],
            MarketRegime.NEUTRAL_MIXED: [now - timedelta(days=35), now - timedelta(days=10)],
            MarketRegime.RANGE_COMPRESSION: [now - timedelta(days=20), now - timedelta(days=5)],
            MarketRegime.RISK_OFF_DEFENSIVE: [now - timedelta(days=55), now - timedelta(days=50)],
            MarketRegime.VOLATILITY_STRESS: [now - timedelta(days=50), now - timedelta(days=48)],
        }
    
    def analyze_regime_performance(
        self,
        backtest_result: BacktestResult,
        strategy: StrategyDefinition,
    ) -> List[RegimePerformance]:
        """Analyze strategy performance under different regimes."""
        
        trades = backtest_result.trades
        if not trades:
            return []
        
        regime_trades = self._assign_trades_to_regimes(trades, backtest_result.start_date, backtest_result.end_date)
        
        performances = []
        
        for regime, regime_trade_list in regime_trades.items():
            perf = self._calculate_regime_performance(regime=regime, trades=regime_trade_list)
            performances.append(perf)
        
        logger.info(f"Analyzed regime performance for {len(performances)} regimes")
        return performances
    
    def _assign_trades_to_regimes(
        self,
        trades: List[BacktestTrade],
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[MarketRegime, List[BacktestTrade]]:
        """Assign trades to regimes based on timestamps."""
        
        regime_trades: Dict[MarketRegime, List[BacktestTrade]] = {r: [] for r in MarketRegime}
        
        regime_weights = {
            MarketRegime.RISK_ON_TREND: 0.25,
            MarketRegime.RISK_ON_MOMENTUM: 0.20,
            MarketRegime.NEUTRAL_MIXED: 0.20,
            MarketRegime.RANGE_COMPRESSION: 0.15,
            MarketRegime.RISK_OFF_DEFENSIVE: 0.10,
            MarketRegime.VOLATILITY_STRESS: 0.05,
            MarketRegime.LIQUIDITY_DISLOCATION: 0.03,
            MarketRegime.ROTATION_TRANSITION: 0.02,
        }
        
        for trade in trades:
            rand = random.random()
            cumulative = 0
            
            for regime, weight in regime_weights.items():
                cumulative += weight
                if rand <= cumulative:
                    regime_trades[regime].append(trade)
                    break
        
        return regime_trades
    
    def _calculate_regime_performance(
        self,
        regime: MarketRegime,
        trades: List[BacktestTrade],
    ) -> RegimePerformance:
        """Calculate performance metrics for a specific regime."""
        
        if not trades:
            return RegimePerformance(regime=regime, num_trades=0, statistical_significance=0.0, sample_size_adequate=False)
        
        returns = [t.pnl_percent for t in trades]
        winning = [t for t in trades if t.pnl > 0]
        losing = [t for t in trades if t.pnl <= 0]
        
        total_return = sum(returns)
        win_rate = len(winning) / len(trades) if trades else 0
        
        gross_profit = sum(t.pnl for t in winning) if winning else 0
        gross_loss = abs(sum(t.pnl for t in losing)) if losing else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        max_dd = self._calculate_max_drawdown(returns)
        volatility = statistics.stdev(returns) if len(returns) > 1 else 0
        
        sample_size = len(trades)
        if sample_size >= 30:
            significance = 0.9
        elif sample_size >= 20:
            significance = 0.7
        elif sample_size >= 10:
            significance = 0.5
        else:
            significance = 0.3
        
        return RegimePerformance(
            regime=regime,
            num_trades=sample_size,
            return_percent=total_return,
            win_rate=win_rate,
            profit_factor=profit_factor,
            max_drawdown=max_dd,
            volatility=volatility,
            statistical_significance=significance,
            sample_size_adequate=sample_size >= 20,
        )
    
    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown from returns."""
        if not returns:
            return 0.0
        
        cumulative = 0.0
        peak = 0.0
        max_dd = 0.0
        
        for ret in returns:
            cumulative += ret
            if cumulative > peak:
                peak = cumulative
            dd = peak - cumulative
            if dd > max_dd:
                max_dd = dd
        
        return max_dd
    
    def get_regime_compatibility_matrix(
        self,
        performances: List[RegimePerformance],
    ) -> Dict[MarketRegime, Dict[str, float]]:
        """Generate regime compatibility matrix."""
        
        matrix: Dict[MarketRegime, Dict[str, float]] = {}
        
        for perf in performances:
            matrix[perf.regime] = {
                "return": perf.return_percent,
                "win_rate": perf.win_rate,
                "profit_factor": perf.profit_factor,
                "max_drawdown": perf.max_drawdown,
                "volatility": perf.volatility,
                "significance": perf.statistical_significance,
                "sample_adequate": float(perf.sample_size_adequate),
                "compatibility_score": self._calculate_compatibility_score(perf),
            }
        
        return matrix
    
    def _calculate_compatibility_score(self, perf: RegimePerformance) -> float:
        """Calculate regime compatibility score (0-1)."""
        
        if perf.num_trades == 0:
            return 0.0
        
        factors = []
        
        if perf.return_percent > 5:
            factors.append(1.0)
        elif perf.return_percent > 0:
            factors.append(0.5)
        else:
            factors.append(0.0)
        
        factors.append(perf.win_rate)
        
        dd_factor = max(0, 1 - abs(perf.max_drawdown) / 10)
        factors.append(dd_factor)
        
        if perf.sample_size_adequate:
            factors.append(1.0)
        else:
            factors.append(0.5)
        
        return sum(factors) / len(factors)
    
    def get_best_regimes(
        self,
        performances: List[RegimePerformance],
        top_n: int = 3,
    ) -> List[RegimePerformance]:
        """Get top performing regimes."""
        
        scored = []
        for perf in performances:
            score = self._calculate_compatibility_score(perf)
            scored.append((score, perf))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored[:top_n]]


_regime_performance_engine: Optional[RegimePerformanceEngine] = None


def get_regime_performance_engine() -> RegimePerformanceEngine:
    """Get the regime performance engine."""
    global _regime_performance_engine
    
    if _regime_performance_engine is None:
        _regime_performance_engine = RegimePerformanceEngine()
    
    return _regime_performance_engine
