"""Paper Trade Simulator for SPY 0DTE Options.

Simulates trade outcomes for performance evaluation without real money risk.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
import random

from app.agents.finance.options_0dte.options_signal_models import (
    OptionsSignal,
    SimulatedTrade,
    OptionType,
)


@dataclass
class SimulationConfig:
    """Configuration for paper trading simulation."""
    max_trade_duration_minutes: int = 30
    profit_target_percent: float = 50.0
    stop_loss_percent: float = -30.0
    trailing_stop_enabled: bool = True
    trailing_stop_percent: float = 20.0


@dataclass
class PaperTradeSimulator:
    """Simulates options trades for performance evaluation."""
    
    config: SimulationConfig = field(default_factory=SimulationConfig)
    trades: list[SimulatedTrade] = field(default_factory=list)
    closed_trades: list[SimulatedTrade] = field(default_factory=list)
    
    def simulate_entry(
        self,
        signal: OptionsSignal,
        entry_time: Optional[datetime] = None,
    ) -> SimulatedTrade:
        """
        Simulate trade entry based on signal.
        
        Args:
            signal: OptionsSignal to trade
            entry_time: Entry timestamp (default: now)
        
        Returns:
            SimulatedTrade object
        """
        if entry_time is None:
            entry_time = datetime.now()
        
        # Use mid price as entry price
        entry_price = signal.mid_price if signal.mid_price else signal.bid_price
        
        trade = SimulatedTrade(
            id=str(uuid.uuid4()),
            signal_id=signal.id,
            ticker=signal.ticker,
            expiration_date=signal.expiration_date,
            strike=signal.strike,
            option_type=signal.option_type,
            entry_time=entry_time,
            entry_price=entry_price,
            quantity=1,
            contract_multiplier=100,
            status="open",
        )
        
        self.trades.append(trade)
        return trade
    
    def simulate_exit(
        self,
        trade: SimulatedTrade,
        exit_price: float,
        exit_time: Optional[datetime] = None,
    ) -> SimulatedTrade:
        """
        Simulate trade exit.
        
        Args:
            trade: Trade to close
            exit_price: Exit price
            exit_time: Exit timestamp (default: now)
        
        Returns:
            Updated SimulatedTrade object
        """
        if exit_time is None:
            exit_time = datetime.now()
        
        trade.exit_price = exit_price
        trade.exit_time = exit_time
        
        # Calculate P&L
        trade.calculate_pnl()
        
        # Calculate time in trade
        if trade.exit_time and trade.entry_time:
            trade.time_in_trade_seconds = int(
                (trade.exit_time - trade.entry_time).total_seconds()
            )
        
        trade.status = "closed"
        
        # Move to closed trades
        if trade in self.trades:
            self.trades.remove(trade)
        self.closed_trades.append(trade)
        
        return trade
    
    def update_trade_mtm(
        self,
        trade: SimulatedTrade,
        current_price: float,
        timestamp: Optional[datetime] = None,
    ) -> SimulatedTrade:
        """
        Update mark-to-market for an open trade.
        
        Args:
            trade: Open trade to update
            current_price: Current option price
            timestamp: Current timestamp
        
        Returns:
            Updated trade
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Calculate current P&L
        current_pnl = (current_price - trade.entry_price) * trade.contract_multiplier * trade.quantity
        current_pnl_percent = ((current_price - trade.entry_price) / trade.entry_price * 100) if trade.entry_price > 0 else 0
        
        # Update max favorable/adverse excursion
        if current_pnl > 0:
            trade.max_favorable_excursion = max(trade.max_favorable_excursion, current_pnl)
        else:
            trade.max_adverse_excursion = min(trade.max_adverse_excursion, current_pnl)
        
        return trade
    
    def check_exit_conditions(
        self,
        trade: SimulatedTrade,
        current_price: float,
        current_time: datetime,
    ) -> Optional[str]:
        """
        Check if any exit conditions are met.
        
        Args:
            trade: Open trade to check
            current_price: Current option price
            current_time: Current timestamp
        
        Returns:
            Exit reason if conditions met, None otherwise
        """
        if trade.entry_price <= 0:
            return None
        
        pnl_percent = ((current_price - trade.entry_price) / trade.entry_price) * 100
        
        # Check max duration
        duration_minutes = (current_time - trade.entry_time).total_seconds() / 60
        if duration_minutes >= self.config.max_trade_duration_minutes:
            return "max_duration"
        
        # Check profit target
        if pnl_percent >= self.config.profit_target_percent:
            return "profit_target"
        
        # Check stop loss
        if pnl_percent <= self.config.stop_loss_percent:
            return "stop_loss"
        
        # Check trailing stop
        if self.config.trailing_stop_enabled:
            if trade.max_favorable_excursion > 0:
                # Trailing stop activates after some profit
                trailing_threshold = trade.max_favorable_excursion * (1 - self.config.trailing_stop_percent / 100)
                current_pnl = (current_price - trade.entry_price) * trade.contract_multiplier * trade.quantity
                if current_pnl < trailing_threshold and current_pnl > 0:
                    return "trailing_stop"
        
        return None
    
    def run_simulation(
        self,
        signal: OptionsSignal,
        price_series: list[tuple[datetime, float]],
    ) -> SimulatedTrade:
        """
        Run full simulation for a signal with price history.
        
        Args:
            signal: OptionsSignal to simulate
            price_series: List of (timestamp, price) tuples
        
        Returns:
            Final SimulatedTrade
        """
        # Enter trade at first price
        if not price_series:
            raise ValueError("Price series cannot be empty")
        
        entry_time, entry_price = price_series[0]
        trade = self.simulate_entry(signal, entry_time)
        
        # Process each price point
        for timestamp, price in price_series[1:]:
            # Update MTM
            self.update_trade_mtm(trade, price, timestamp)
            
            # Check exit conditions
            exit_reason = self.check_exit_conditions(trade, price, timestamp)
            if exit_reason:
                self.simulate_exit(trade, price, timestamp)
                return trade
        
        # If simulation ends without exit, close at last price
        if trade.status == "open":
            last_timestamp, last_price = price_series[-1]
            self.simulate_exit(trade, last_price, last_timestamp)
        
        return trade
    
    def generate_realistic_price_series(
        self,
        signal: OptionsSignal,
        duration_minutes: int = 30,
        volatility_percent: float = 20.0,
        trend_bias: float = 0.0,
    ) -> list[tuple[datetime, float]]:
        """
        Generate a realistic price series for simulation.
        
        This is a simplified simulation for testing purposes.
        
        Args:
            signal: OptionsSignal to generate prices for
            duration_minutes: Duration of simulation in minutes
            volatility_percent: Volatility of underlying
            trend_bias: Trend bias (-1 to 1)
        
        Returns:
            List of (timestamp, price) tuples
        """
        prices = []
        base_price = signal.mid_price if signal.mid_price else signal.bid_price
        start_time = signal.timestamp
        
        # Generate 1-minute bars
        num_bars = min(duration_minutes, 60)  # Max 60 bars
        minutes_per_bar = duration_minutes / num_bars
        
        current_price = base_price
        
        for i in range(num_bars + 1):
            timestamp = start_time + timedelta(minutes=i * minutes_per_bar)
            
            # Add some randomness
            random_change = random.gauss(trend_bias * volatility_percent / 100, volatility_percent / 100)
            price_change = current_price * random_change
            current_price = max(0.01, current_price + price_change)
            
            prices.append((timestamp, current_price))
        
        return prices
    
    def track_trade_metrics(self, trade: SimulatedTrade) -> dict:
        """
        Extract detailed metrics from a trade.
        
        Args:
            trade: Simulated trade
        
        Returns:
            Dictionary of metrics
        """
        return {
            "trade_id": trade.id,
            "signal_id": trade.signal_id,
            "ticker": trade.ticker,
            "strike": trade.strike,
            "option_type": trade.option_type.value,
            "entry_time": trade.entry_time.isoformat(),
            "exit_time": trade.exit_time.isoformat() if trade.exit_time else None,
            "entry_price": trade.entry_price,
            "exit_price": trade.exit_price,
            "quantity": trade.quantity,
            "profit_loss": trade.profit_loss,
            "profit_loss_percent": trade.profit_loss_percent,
            "max_adverse_excursion": trade.max_adverse_excursion,
            "max_favorable_excursion": trade.max_favorable_excursion,
            "time_in_trade_seconds": trade.time_in_trade_seconds,
            "status": trade.status,
        }
    
    def get_performance_summary(self) -> dict:
        """
        Get overall performance summary.
        
        Returns:
            Dictionary of performance metrics
        """
        if not self.closed_trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "average_pnl": 0.0,
                "average_duration_seconds": 0,
            }
        
        winning_trades = [t for t in self.closed_trades if t.profit_loss and t.profit_loss > 0]
        losing_trades = [t for t in self.closed_trades if t.profit_loss and t.profit_loss <= 0]
        
        total_pnl = sum(t.profit_loss for t in self.closed_trades if t.profit_loss)
        avg_pnl = total_pnl / len(self.closed_trades) if self.closed_trades else 0
        avg_duration = sum(t.time_in_trade_seconds for t in self.closed_trades) / len(self.closed_trades)
        
        return {
            "total_trades": len(self.closed_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": len(winning_trades) / len(self.closed_trades) * 100 if self.closed_trades else 0,
            "total_pnl": total_pnl,
            "average_pnl": avg_pnl,
            "average_duration_seconds": avg_duration,
            "average_duration_minutes": avg_duration / 60,
        }
    
    def store_simulation_result(self, trade: SimulatedTrade) -> dict:
        """
        Store simulation result for later analysis.
        
        Args:
            trade: Completed trade
        
        Returns:
            Dictionary of stored result
        """
        result = self.track_trade_metrics(trade)
        result["stored_at"] = datetime.now().isoformat()
        
        return result
