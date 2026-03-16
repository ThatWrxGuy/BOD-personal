"""Performance Tracker.

This module measures and tracks strategy performance.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.finance.portfolio_management.portfolio_models import (
    Position,
    PortfolioMetrics,
    PortfolioState,
)


class PerformanceTracker:
    """Tracks portfolio performance metrics."""
    
    def __init__(self):
        """Initialize the performance tracker."""
        self.trade_history: list[Position] = []
        self.equity_curve: list[dict] = []
        
    def record_trade(self, position: Position):
        """Record a completed trade.
        
        Args:
            position: Closed position
        """
        self.trade_history.append(position)
        
    def update_equity_curve(self, portfolio: PortfolioState):
        """Update equity curve.
        
        Args:
            portfolio: Current portfolio state
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "equity": float(portfolio.total_equity),
            "cash": float(portfolio.cash_balance),
            "exposure": portfolio.exposure_percent,
        }
        self.equity_curve.append(entry)
    
    def calculate_metrics(self, portfolio: PortfolioState) -> PortfolioMetrics:
        """Calculate performance metrics.
        
        Args:
            portfolio: Current portfolio state
            
        Returns:
            Performance metrics
        """
        metrics = PortfolioMetrics()
        
        # Count trades
        closed_positions = [
            p for p in self.trade_history
            if p.status.value == "closed"
        ]
        
        metrics.total_trades = len(closed_positions)
        metrics.winning_trades = len([p for p in closed_positions if p.pnl > 0])
        metrics.losing_trades = len([p for p in closed_positions if p.pnl < 0])
        
        # Calculate P&L
        metrics.total_pnl = sum(p.pnl for p in closed_positions)
        
        # Calculate derived metrics
        metrics.calculate_metrics()
        
        # Calculate drawdown
        if self.equity_curve:
            metrics.max_drawdown = self._calculate_max_drawdown()
            metrics.current_drawdown = self._calculate_current_drawdown(portfolio.total_equity)
        
        # Calculate Sharpe ratio
        if len(self.equity_curve) > 1:
            metrics.sharpe_ratio = self._calculate_sharpe_ratio()
        
        return metrics
    
    def get_win_rate(self) -> float:
        """Get current win rate.
        
        Returns:
            Win rate percentage
        """
        if not self.trade_history:
            return 0.0
        
        winning = len([p for p in self.trade_history if p.pnl > 0])
        return (winning / len(self.trade_history)) * 100
    
    def get_expectancy(self) -> float:
        """Calculate trade expectancy.
        
        Returns:
            Expectancy per trade
        """
        if not self.trade_history:
            return 0.0
        
        wins = [p for p in self.trade_history if p.pnl > 0]
        losses = [p for p in self.trade_history if p.pnl < 0]
        
        if not wins or not losses:
            return 0.0
        
        avg_win = sum(float(p.pnl) for p in wins) / len(wins)
        avg_loss = abs(sum(float(p.pnl) for p in losses) / len(losses))
        
        win_rate = len(wins) / len(self.trade_history)
        
        return (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
    
    def get_profit_factor(self) -> float:
        """Calculate profit factor.
        
        Returns:
            Profit factor
        """
        if not self.trade_history:
            return 0.0
        
        gross_wins = sum(p.pnl for p in self.trade_history if p.pnl > 0)
        gross_losses = abs(sum(p.pnl for p in self.trade_history if p.pnl < 0))
        
        if gross_losses == 0:
            return float('inf') if gross_wins > 0 else 0.0
        
        return float(gross_wins / gross_losses)
    
    def get_average_win(self) -> Decimal:
        """Get average winning trade amount.
        
        Returns:
            Average win
        """
        wins = [p for p in self.trade_history if p.pnl > 0]
        
        if not wins:
            return Decimal("0")
        
        return sum(p.pnl for p in wins) / Decimal(str(len(wins)))
    
    def get_average_loss(self) -> Decimal:
        """Get average losing trade amount.
        
        Returns:
            Average loss
        """
        losses = [p for p in self.trade_history if p.pnl < 0]
        
        if not losses:
            return Decimal("0")
        
        return sum(abs(p.pnl) for p in losses) / Decimal(str(len(losses)))
    
    def get_performance_summary(self) -> dict:
        """Get comprehensive performance summary.
        
        Returns:
            Performance summary
        """
        return {
            "total_trades": len(self.trade_history),
            "win_rate": self.get_win_rate(),
            "expectancy": self.get_expectancy(),
            "profit_factor": self.get_profit_factor(),
            "average_win": float(self.get_average_win()),
            "average_loss": float(self.get_average_loss()),
            "max_drawdown": self._calculate_max_drawdown(),
            "sharpe_ratio": self._calculate_sharpe_ratio() if len(self.equity_curve) > 1 else 0.0,
        }
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown from equity curve.
        
        Returns:
            Maximum drawdown percentage
        """
        if not self.equity_curve:
            return 0.0
        
        peak = float('-inf')
        max_dd = 0.0
        
        for entry in self.equity_curve:
            equity = entry["equity"]
            
            if equity > peak:
                peak = equity
            
            drawdown = (peak - equity) / peak * 100
            
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd
    
    def _calculate_current_drawdown(self, current_equity: Decimal) -> float:
        """Calculate current drawdown.
        
        Args:
            current_equity: Current equity
            
        Returns:
            Current drawdown percentage
        """
        if not self.equity_curve:
            return 0.0
        
        peak = max(e["equity"] for e in self.equity_curve)
        current = float(current_equity)
        
        if peak == 0:
            return 0.0
        
        return (peak - current) / peak * 100
    
    def _calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio.
        
        Returns:
            Sharpe ratio
        """
        if len(self.equity_curve) < 2:
            return 0.0
        
        returns = []
        for i in range(1, len(self.equity_curve)):
            prev = self.equity_curve[i-1]["equity"]
            curr = self.equity_curve[i]["equity"]
            
            if prev > 0:
                ret = (curr - prev) / prev
                returns.append(ret)
        
        if not returns:
            return 0.0
        
        # Calculate average return
        avg_return = sum(returns) / len(returns)
        
        # Calculate standard deviation
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return 0.0
        
        # Assume risk-free rate of 2%
        risk_free = 0.02 / 252  # Daily
        
        sharpe = (avg_return - risk_free) / std_dev
        
        # Annualize
        return sharpe * (252 ** 0.5)
    
    def get_trade_history(self, limit: int = 100) -> list[dict]:
        """Get recent trade history.
        
        Args:
            limit: Number of trades to return
            
        Returns:
            List of trade records
        """
        trades = sorted(
            self.trade_history,
            key=lambda p: p.exit_time or datetime.now(),
            reverse=True
        )[:limit]
        
        return [
            {
                "id": p.id,
                "ticker": p.ticker,
                "entry_price": float(p.entry_price),
                "exit_price": float(p.current_price),
                "quantity": float(p.quantity),
                "pnl": float(p.pnl),
                "pnl_percent": p.pnl_percent,
                "entry_time": p.entry_time.isoformat() if p.entry_time else None,
                "exit_time": p.exit_time.isoformat() if p.exit_time else None,
            }
            for p in trades
        ]


# Global performance tracker
_performance_tracker: Optional[PerformanceTracker] = None


def get_performance_tracker() -> PerformanceTracker:
    """Get the global performance tracker."""
    global _performance_tracker
    
    if _performance_tracker is None:
        _performance_tracker = PerformanceTracker()
    
    return _performance_tracker
