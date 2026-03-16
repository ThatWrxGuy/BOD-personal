"""Strategy Scoring Engine - BB-FIN-020

Computes comprehensive strategy quality metrics.
"""

from typing import Dict, List, Optional
import logging
import statistics

from app.finance.strategy_lab.strategy_models import (
    BacktestResult,
    MonteCarloSimulation,
    PerformanceMetrics,
    RegimePerformance,
)

logger = logging.getLogger(__name__)


class StrategyScoringEngine:
    """Computes strategy quality metrics and scores."""
    
    def __init__(self):
        pass
    
    def compute_metrics(
        self,
        backtest_result: BacktestResult,
    ) -> PerformanceMetrics:
        """Compute comprehensive performance metrics from backtest results."""
        
        trades = backtest_result.trades
        if not trades:
            return PerformanceMetrics()
        
        # Extract trade data
        pnls = [t.pnl for t in trades]
        pct_returns = [t.pnl_percent for t in trades]
        
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]
        
        metrics = PerformanceMetrics()
        
        # Basic counts
        metrics.total_trades = len(trades)
        metrics.winning_trades = len(winning_trades)
        metrics.losing_trades = len(losing_trades)
        
        if not trades:
            return metrics
        
        # Win rate
        metrics.win_rate = len(winning_trades) / len(trades) if trades else 0
        metrics.loss_rate = 1 - metrics.win_rate
        
        # Returns
        metrics.total_return = sum(pnls)
        metrics.total_return_percent = sum(pct_returns)
        
        # Average trade
        metrics.avg_trade = statistics.mean(pnls) if pnls else 0
        
        # Win/Loss stats
        if winning_trades:
            metrics.avg_win = statistics.mean([t.pnl for t in winning_trades])
            metrics.largest_win = max([t.pnl for t in winning_trades])
        else:
            metrics.avg_win = 0
            metrics.largest_win = 0
        
        if losing_trades:
            metrics.avg_loss = statistics.mean([t.pnl for t in losing_trades])
            metrics.largest_loss = min([t.pnl for t in losing_trades])
        else:
            metrics.avg_loss = 0
            metrics.largest_loss = 0
        
        # Profit factor
        gross_profit = sum(t.pnl for t in winning_trades) if winning_trades else 0
        gross_loss = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 0
        metrics.profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Expectancy
        if winning_trades and losing_trades:
            avg_win_rate = metrics.win_rate
            avg_loss_rate = 1 - avg_win_rate
            win_loss_ratio = abs(metrics.avg_win / metrics.avg_loss) if metrics.avg_loss != 0 else 0
            metrics.expectancy = (avg_win_rate * win_loss_ratio) - avg_loss_rate
        else:
            metrics.expectancy = 0
        
        # Volatility and drawdown
        if len(pct_returns) > 1:
            metrics.volatility = statistics.stdev(pct_returns)
            metrics.return_std_dev = statistics.stdev(pct_returns)
            metrics.max_drawdown_percent = self._calculate_max_drawdown(pct_returns)
        
        # Risk-adjusted metrics
        if metrics.volatility > 0:
            risk_free_annual = 0.02 / 252
            excess_return = (metrics.total_return_percent / 100) - risk_free_annual
            metrics.sharpe_ratio = (excess_return / metrics.volatility) * (252 ** 0.5) if metrics.volatility else 0
        
        # Sortino ratio
        downside_returns = [r for r in pct_returns if r < 0]
        if downside_returns and len(downside_returns) > 1:
            downside_dev = statistics.stdev(downside_returns)
            if downside_dev > 0:
                risk_free_annual = 0.02 / 252
                metrics.sortino_ratio = (metrics.total_return_percent / 100 - risk_free_annual) / downside_dev * (252 ** 0.5)
        
        # Calmar ratio
        if metrics.max_drawdown_percent != 0:
            metrics.calmar_ratio = (metrics.total_return_percent / 100) / abs(metrics.max_drawdown_percent / 100)
        
        # Annualized return
        if backtest_result.start_date and backtest_result.end_date:
            days = (backtest_result.end_date - backtest_result.start_date).days
            if days > 0:
                metrics.annualized_return = (metrics.total_return_percent / days) * 252
        
        # Trades per month
        if backtest_result.start_date and backtest_result.end_date:
            months = (backtest_result.end_date - backtest_result.start_date).days / 30
            if months > 0:
                metrics.trades_per_month = len(trades) / months
        
        metrics.monthly_hit_rate = metrics.win_rate
        
        logger.info(f"Computed metrics for {metrics.total_trades} trades: Sharpe={metrics.sharpe_ratio:.2f}, WinRate={metrics.win_rate:.1%}")
        
        return metrics
    
    def _calculate_max_drawdown(self, returns: List[float]) -> float:
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
    
    def calculate_composite_score(
        self,
        metrics: PerformanceMetrics,
        monte_carlo: Optional[MonteCarloSimulation] = None,
        regime_performance: Optional[List[RegimePerformance]] = None,
    ) -> Dict[str, float]:
        
        scores = {
            "sharpe_score": 0.0,
            "consistency_score": 0.0,
            "risk_score": 0.0,
            "regime_score": 0.0,
            "composite": 0.0,
        }
        
        # Sharpe score
        if metrics.sharpe_ratio >= 2.0:
            scores["sharpe_score"] = 1.0
        elif metrics.sharpe_ratio >= 1.0:
            scores["sharpe_score"] = 0.7
        elif metrics.sharpe_ratio >= 0.5:
            scores["sharpe_score"] = 0.5
        elif metrics.sharpe_ratio >= 0:
            scores["sharpe_score"] = 0.3
        
        # Consistency
        consistency = metrics.win_rate * (1 - min(metrics.volatility, 1))
        scores["consistency_score"] = consistency
        
        # Risk
        if metrics.max_drawdown_percent > 0:
            scores["risk_score"] = max(0, 1 - abs(metrics.max_drawdown_percent) / 20)
        else:
            scores["risk_score"] = 1.0
        
        # Regime
        if regime_performance:
            regime_scores = []
            for perf in regime_performance:
                if perf.sample_size_adequate and perf.num_trades >= 10:
                    regime_scores.append(perf.return_percent / 10)
            if regime_scores:
                scores["regime_score"] = min(1.0, statistics.mean(regime_scores))
        
        # Monte Carlo
        if monte_carlo:
            mc_score = 0
            if monte_carlo.prob_ruin < 0.05:
                mc_score += 0.4
            if monte_carlo.percentile_10 > -0.15:
                mc_score += 0.3
            if monte_carlo.std_deviation < 0.3:
                mc_score += 0.3
            scores["monte_carlo_score"] = mc_score
        
        # Composite
        weights = {"sharpe_score": 0.30, "consistency_score": 0.25, "risk_score": 0.25, "regime_score": 0.20}
        
        if "monte_carlo_score" in scores:
            weights["monte_carlo_score"] = 0.20
            del weights["regime_score"]
        
        total_weight = sum(weights.values())
        scores["composite"] = sum(scores[k] * w for k, w in weights.items()) / total_weight
        
        return scores


_strategy_scoring_engine: Optional[StrategyScoringEngine] = None


def get_strategy_scoring_engine() -> StrategyScoringEngine:
    global _strategy_scoring_engine
    
    if _strategy_scoring_engine is None:
        _strategy_scoring_engine = StrategyScoringEngine()
    
    return _strategy_scoring_engine
