"""Signal Logger for SPY 0DTE Options.

Records generated signals and simulated trades for analysis and strategic memory.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.agents.finance.options_0dte.options_signal_models import (
    OptionsSignal,
    SimulatedTrade,
)


class SignalLogger:
    """Logs signals and simulated trades to storage."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize signal logger.
        
        Args:
            storage_path: Path to store log files. Defaults to ./data/options_signals
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path(__file__).parent / "data"
        
        # Ensure directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.signals_file = self.storage_path / "signals.jsonl"
        self.trades_file = self.storage_path / "simulated_trades.jsonl"
        self.history_file = self.storage_path / "history.jsonl"
    
    def log_signal(self, signal: OptionsSignal) -> dict:
        """
        Log a generated signal.
        
        Args:
            signal: OptionsSignal to log
        
        Returns:
            Logged signal data
        """
        log_entry = {
            "id": signal.id,
            "timestamp": signal.timestamp.isoformat(),
            "ticker": signal.ticker,
            "expiration_date": signal.expiration_date.isoformat(),
            "strike": signal.strike,
            "option_type": signal.option_type.value,
            "delta": signal.delta,
            "gamma": signal.gamma,
            "vega": signal.vega,
            "theta": signal.theta,
            "spread": signal.spread,
            "volume": signal.volume,
            "open_interest": signal.open_interest,
            "signal_score": signal.signal_score,
            "confidence_score": signal.confidence_score,
            "bid_price": signal.bid_price,
            "ask_price": signal.ask_price,
            "mid_price": signal.mid_price,
            "underlying_price": signal.underlying_price,
            "implied_volatility": signal.implied_volatility,
            "reasoning_summary": signal.reasoning_summary,
            "logged_at": datetime.now().isoformat(),
        }
        
        # Append to signals file
        with open(self.signals_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        return log_entry
    
    def log_simulated_trade(self, trade: SimulatedTrade) -> dict:
        """
        Log a simulated trade.
        
        Args:
            trade: SimulatedTrade to log
        
        Returns:
            Logged trade data
        """
        log_entry = {
            "id": trade.id,
            "signal_id": trade.signal_id,
            "ticker": trade.ticker,
            "expiration_date": trade.expiration_date.isoformat(),
            "strike": trade.strike,
            "option_type": trade.option_type.value,
            "entry_time": trade.entry_time.isoformat(),
            "entry_price": trade.entry_price,
            "exit_time": trade.exit_time.isoformat() if trade.exit_time else None,
            "exit_price": trade.exit_price,
            "quantity": trade.quantity,
            "contract_multiplier": trade.contract_multiplier,
            "max_adverse_excursion": trade.max_adverse_excursion,
            "max_favorable_excursion": trade.max_favorable_excursion,
            "time_in_trade_seconds": trade.time_in_trade_seconds,
            "profit_loss": trade.profit_loss,
            "profit_loss_percent": trade.profit_loss_percent,
            "status": trade.status,
            "logged_at": datetime.now().isoformat(),
        }
        
        # Append to trades file
        with open(self.trades_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        return log_entry
    
    def store_signal_history(self, signal: OptionsSignal) -> dict:
        """
        Store signal in history file for long-term analysis.
        
        Args:
            signal: OptionsSignal to store
        
        Returns:
            Stored history entry
        """
        history_entry = {
            "id": str(uuid.uuid4()),
            "signal_id": signal.id,
            "timestamp": signal.timestamp.isoformat(),
            "signal_score": signal.signal_score,
            "confidence_score": signal.confidence_score,
            "strike": signal.strike,
            "option_type": signal.option_type.value,
            "profit_loss": None,  # Will be updated when trade completes
            "status": "generated",
            "stored_at": datetime.now().isoformat(),
        }
        
        # Append to history file
        with open(self.history_file, "a") as f:
            f.write(json.dumps(history_entry) + "\n")
        
        return history_entry
    
    def get_signals(self, limit: int = 100) -> list[dict]:
        """
        Get recent signals.
        
        Args:
            limit: Maximum number of signals to retrieve
        
        Returns:
            List of signal dictionaries
        """
        if not self.signals_file.exists():
            return []
        
        signals = []
        with open(self.signals_file, "r") as f:
            for line in f:
                try:
                    signals.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        return signals[-limit:]
    
    def get_simulated_trades(self, limit: int = 100) -> list[dict]:
        """
        Get recent simulated trades.
        
        Args:
            limit: Maximum number of trades to retrieve
        
        Returns:
            List of trade dictionaries
        """
        if not self.trades_file.exists():
            return []
        
        trades = []
        with open(self.trades_file, "r") as f:
            for line in f:
                try:
                    trades.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        return trades[-limit:]
    
    def get_signal_history(self, limit: int = 100) -> list[dict]:
        """
        Get signal history.
        
        Args:
            limit: Maximum number of entries to retrieve
        
        Returns:
            List of history entries
        """
        if not self.history_file.exists():
            return []
        
        history = []
        with open(self.history_file, "r") as f:
            for line in f:
                try:
                    history.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        return history[-limit:]
    
    def get_performance_metrics(self) -> dict:
        """
        Calculate performance metrics from logged trades.
        
        Returns:
            Dictionary of performance metrics
        """
        trades = self.get_simulated_trades(limit=1000)
        
        if not trades:
            return {
                "total_signals": len(self.get_signals(limit=10000)),
                "total_simulated_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "average_pnl": 0.0,
                "average_win": 0.0,
                "average_loss": 0.0,
                "largest_win": 0.0,
                "largest_loss": 0.0,
            }
        
        closed_trades = [t for t in trades if t.get("status") == "closed" and t.get("profit_loss") is not None]
        winning_trades = [t for t in closed_trades if t.get("profit_loss", 0) > 0]
        losing_trades = [t for t in closed_trades if t.get("profit_loss", 0) <= 0]
        
        total_pnl = sum(t.get("profit_loss", 0) for t in closed_trades)
        avg_pnl = total_pnl / len(closed_trades) if closed_trades else 0
        
        avg_win = sum(t.get("profit_loss", 0) for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.get("profit_loss", 0) for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        largest_win = max((t.get("profit_loss", 0) for t in winning_trades), default=0)
        largest_loss = min((t.get("profit_loss", 0) for t in losing_trades), default=0)
        
        return {
            "total_signals": len(self.get_signals(limit=10000)),
            "total_simulated_trades": len(closed_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": len(winning_trades) / len(closed_trades) * 100 if closed_trades else 0,
            "total_pnl": total_pnl,
            "average_pnl": avg_pnl,
            "average_win": avg_win,
            "average_loss": avg_loss,
            "largest_win": largest_win,
            "largest_loss": largest_loss,
        }
    
    def clear_logs(self) -> None:
        """Clear all log files."""
        for file_path in [self.signals_file, self.trades_file, self.history_file]:
            if file_path.exists():
                file_path.unlink()
