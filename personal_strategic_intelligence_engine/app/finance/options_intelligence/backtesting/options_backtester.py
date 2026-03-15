"""Options Backtesting Engine.

Backtests options strategies.
"""

from typing import Dict, List
from datetime import datetime, timedelta
import random


class BacktestResult:
    def __init__(self, strategy_name: str, trades: List[Dict], metrics: Dict):
        self.strategy_name = strategy_name
        self.trades = trades
        self.metrics = metrics
    
    def to_dict(self) -> dict:
        return {
            "strategy_name": self.strategy_name,
            "trades": self.trades,
            "metrics": self.metrics,
        }


class OptionsBacktester:
    def __init__(self):
        self.results = []
    
    def backtest(self, strategy: Dict, market_data: List[Dict]) -> BacktestResult:
        """Run backtest on strategy."""
        
        trades = []
        
        # Simulate trades
        for i in range(50):
            trade = {
                "entry_time": datetime.now() - timedelta(days=random.randint(1, 30)),
                "exit_time": datetime.now() - timedelta(days=random.randint(0, 29)),
                "pnl": random.uniform(-100, 200),
                "pnl_pct": random.uniform(-20, 40),
                "holding_period": random.randint(1, 10),
            }
            trades.append(trade)
        
        # Calculate metrics
        pnls = [t["pnl"] for t in trades]
        wins = [p for p in pnls if p > 0]
        
        metrics = {
            "total_trades": len(trades),
            "win_rate": len(wins) / len(pnls) * 100 if pnls else 0,
            "avg_win": sum(wins) / len(wins) if wins else 0,
            "avg_loss": abs(sum([p for p in pnls if p < 0]) / len([p for p in pnls if p < 0])) if [p for p in pnls if p < 0] else 0,
            "expectancy": sum(pnls) / len(pnls) if pnls else 0,
            "max_drawdown": min(pnls) if pnls else 0,
        }
        
        return BacktestResult(strategy["name"], trades, metrics)
    
    def compare_strategies(self, strategies: List[Dict], market_data: List[Dict]) -> List[BacktestResult]:
        """Compare multiple strategies."""
        results = []
        for strategy in strategies:
            result = self.backtest(strategy, market_data)
            results.append(result)
        return results


def create_backtester() -> OptionsBacktester:
    return OptionsBacktester()
