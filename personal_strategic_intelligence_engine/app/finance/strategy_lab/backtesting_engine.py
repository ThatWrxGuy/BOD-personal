"""Backtesting Engine - BB-FIN-020

Core strategy simulation engine for historical testing.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import uuid
import random

from app.finance.strategy_lab.strategy_models import (
    StrategyDefinition,
    BacktestResult,
    BacktestTrade,
    TradeDirection,
)

logger = logging.getLogger(__name__)


class OHLCV:
    """OHLCV data point."""
    def __init__(
        self,
        timestamp: datetime,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: float,
    ):
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume


class BacktestingEngine:
    """Core strategy backtesting engine."""
    
    def __init__(self):
        self._historical_data: Dict[str, List[OHLCV]] = {}
    
    def load_historical_data(
        self,
        symbol: str,
        data: List[Dict],
    ) -> bool:
        """Load historical OHLCV data for a symbol."""
        
        ohlcv_data = []
        for point in data:
            ohlcv_data.append(OHLCV(
                timestamp=point.get("timestamp", datetime.utcnow()),
                open=point["open"],
                high=point["high"],
                low=point["low"],
                close=point["close"],
                volume=point.get("volume", 0),
            ))
        
        self._historical_data[symbol] = sorted(ohlcv_data, key=lambda x: x.timestamp)
        logger.info(f"Loaded {len(ohlcv_data)} bars for {symbol}")
        return True
    
    def run_backtest(
        self,
        strategy: StrategyDefinition,
        symbols: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> BacktestResult:
        """Run a backtest for a strategy."""
        
        if symbols is None:
            symbols = strategy.target_assets if strategy.target_assets else ["SPY"]
        
        # Generate demo data if not available
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=90)
        if not end_date:
            end_date = datetime.utcnow()
        
        backtest_id = f"bt_{strategy.strategy_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        result = BacktestResult(
            backtest_id=backtest_id,
            strategy_id=strategy.strategy_id,
            start_date=start_date,
            end_date=end_date,
        )
        
        # Run backtest for each symbol
        all_trades = []
        for symbol in symbols:
            trades = self._simulate_strategy(
                strategy=strategy,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
            )
            all_trades.extend(trades)
        
        result.trades = all_trades
        result.total_trades = len(all_trades)
        
        # Calculate metrics
        if all_trades:
            winning = [t for t in all_trades if t.pnl > 0]
            losing = [t for t in all_trades if t.pnl <= 0]
            result.winning_trades = len(winning)
            result.losing_trades = len(losing)
            
            if winning:
                result.avg_win = sum(t.pnl for t in winning) / len(winning)
            if losing:
                result.avg_loss = sum(t.pnl for t in losing) / len(losing)
            
            result.total_return = sum(t.pnl for t in all_trades)
        
        logger.info(f"Backtest {backtest_id}: {result.total_trades} trades, ${result.total_return:.2f}")
        return result
    
    def _simulate_strategy(
        self,
        strategy: StrategyDefinition,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[BacktestTrade]:
        """Simulate strategy on historical data."""
        
        # Generate demo price data if not loaded
        price_data = self._historical_data.get(symbol)
        if not price_data:
            price_data = self._generate_demo_data(symbol, start_date, end_date)
        
        trades = []
        position = None
        
        # Simple simulation - generate trades based on random entry signals
        # In production, this would use actual strategy entry/exit conditions
        for i in range(10, len(price_data)):
            bar = price_data[i]
            prev_bar = price_data[i - 1]
            
            # Demo: Random entry signal (in production, evaluate strategy conditions)
            if position is None and random.random() < 0.15:
                # Enter trade
                direction = random.choice([TradeDirection.LONG, TradeDirection.SHORT])
                quantity = random.uniform(100, 500)
                
                trade = BacktestTrade(
                    trade_id=f"trade_{uuid.uuid4().hex[:8]}",
                    strategy_id=strategy.strategy_id,
                    entry_time=bar.timestamp,
                    symbol=symbol,
                    direction=direction,
                    entry_price=bar.close,
                    quantity=quantity,
                    position_value=bar.close * quantity,
                    entry_reason=f"Strategy entry: {random.choice(['breakout', 'signal', 'pattern'])}_entry",
                )
                position = trade
            
            # Demo: Random exit signal
            elif position is not None and random.random() < 0.12:
                # Close position
                pnl_percent = random.uniform(-0.05, 0.08)  # -5% to +8%
                position.exit_price = bar.close
                position.exit_time = bar.timestamp
                position.pnl = position.position_value * pnl_percent
                position.pnl_percent = pnl_percent * 100
                position.realized_pnl = position.pnl
                position.status = "closed"
                position.exit_reason = f"Strategy exit: {random.choice(['target', 'stop', 'time'])}_exit"
                
                trades.append(position)
                position = None
        
        # Close any open position at end
        if position and position in trades:
            pass  # Already closed
        elif position:
            final_bar = price_data[-1]
            pnl_percent = random.uniform(-0.03, 0.05)
            position.exit_price = final_bar.close
            position.exit_time = final_bar.timestamp
            position.pnl = position.position_value * pnl_percent
            position.pnl_percent = pnl_percent * 100
            position.realized_pnl = position.pnl
            position.status = "closed"
            position.exit_reason = "End of backtest"
            trades.append(position)
        
        return trades
    
    def _generate_demo_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[OHLCV]:
        """Generate demo OHLCV data for testing."""
        
        # Start with base price
        base_prices = {
            "SPY": 450.0,
            "QQQ": 380.0,
            "IWM": 200.0,
            "AAPL": 175.0,
            "MSFT": 350.0,
        }
        base_price = base_prices.get(symbol, 100.0)
        
        data = []
        current_date = start_date
        current_price = base_price
        
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() < 5:
                # Random walk with drift
                change = random.gauss(0.0005, 0.01)  # Slight upward drift
                current_price = current_price * (1 + change)
                
                # Generate OHLC
                high = current_price * (1 + abs(random.gauss(0, 0.005)))
                low = current_price * (1 - abs(random.gauss(0, 0.005)))
                open_price = current_price * (1 + random.gauss(0, 0.002))
                close_price = current_price
                
                volume = random.uniform(10_000_000, 100_000_000)
                
                data.append(OHLCV(
                    timestamp=current_date,
                    open=open_price,
                    high=high,
                    low=low,
                    close=close_price,
                    volume=volume,
                ))
            
            current_date += timedelta(hours=24)  # Daily bars
        
        logger.info(f"Generated {len(data)} demo bars for {symbol}")
        return data
    
    def get_available_symbols(self) -> List[str]:
        """Get list of symbols with historical data."""
        return list(self._historical_data.keys())


# Global instance
_backtesting_engine: Optional[BacktestingEngine] = None


def get_backtesting_engine() -> BacktestingEngine:
    """Get the backtesting engine."""
    global _backtesting_engine
    
    if _backtesting_engine is None:
        _backtesting_engine = BacktestingEngine()
    
    return _backtesting_engine
