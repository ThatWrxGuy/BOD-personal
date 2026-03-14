"""Options Signal Models for SPY 0DTE Tactical Agent."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class OptionType(str, Enum):
    """Option type enumeration."""
    CALL = "call"
    PUT = "put"


@dataclass
class OptionsSignal:
    """
    Signal model for SPY 0DTE options.
    
    Represents a potential options contract with scoring and confidence metrics.
    Includes feature attribution and outcome tracking for learning.
    """
    id: str
    timestamp: datetime
    ticker: str
    expiration_date: datetime
    strike: float
    option_type: OptionType
    delta: float
    gamma: float
    vega: float
    theta: float
    spread: float
    volume: int
    open_interest: int
    signal_score: float
    confidence_score: float
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    mid_price: Optional[float] = None
    underlying_price: Optional[float] = None
    implied_volatility: Optional[float] = None
    reasoning_summary: str = ""
    
    # Feature attribution (new in V31-AUDIT-001)
    feature_scores: Optional[dict] = None  # Raw feature values
    score_contributions: Optional[dict] = None  # Weighted score contributions
    regime_label: Optional[str] = None  # Market regime at signal time
    volatility_regime: Optional[str] = None  # Volatility regime
    time_window: Optional[str] = None  # Trading window
    liquidity_context: Optional[dict] = None  # Liquidity details
    spread_context: Optional[dict] = None  # Spread details
    
    # Outcome tracking (new in V31-AUDIT-001)
    trade_outcome: Optional[str] = None  # "win", "loss", "pending"
    profit_loss: Optional[float] = None  # P&L if closed
    trade_exit_time: Optional[datetime] = None
    trade_duration_seconds: Optional[int] = None
    
    # Governance
    governance_status: str = "advisory_only"
    human_approval_required: bool = True
    suppression_reason: Optional[str] = None
    suppression_details: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "ticker": self.ticker,
            "expiration_date": self.expiration_date.isoformat(),
            "strike": self.strike,
            "option_type": self.option_type.value,
            "delta": self.delta,
            "gamma": self.gamma,
            "vega": self.vega,
            "theta": self.theta,
            "spread": self.spread,
            "volume": self.volume,
            "open_interest": self.open_interest,
            "signal_score": self.signal_score,
            "confidence_score": self.confidence_score,
            "bid_price": self.bid_price,
            "ask_price": self.ask_price,
            "mid_price": self.mid_price,
            "underlying_price": self.underlying_price,
            "implied_volatility": self.implied_volatility,
            "reasoning_summary": self.reasoning_summary,
            # Feature attribution
            "feature_scores": self.feature_scores,
            "score_contributions": self.score_contributions,
            "regime_label": self.regime_label,
            "volatility_regime": self.volatility_regime,
            "time_window": self.time_window,
            "liquidity_context": self.liquidity_context,
            "spread_context": self.spread_context,
            # Outcome tracking
            "trade_outcome": self.trade_outcome,
            "profit_loss": self.profit_loss,
            "trade_exit_time": self.trade_exit_time.isoformat() if self.trade_exit_time else None,
            "trade_duration_seconds": self.trade_duration_seconds,
            # Governance
            "governance_status": self.governance_status,
            "human_approval_required": self.human_approval_required,
            "suppression_reason": self.suppression_reason,
            "suppression_details": self.suppression_details,
        }


@dataclass
class MarketDataSnapshot:
    """Market data snapshot for SPY."""
    timestamp: datetime
    ticker: str
    current_price: float
    open_price: float
    high_price: float
    low_price: float
    volume: int
    change_percent: float
    
    # 1-minute bar data
    open: float
    high: float
    low: float
    close: float
    
    # Technical indicators
    rsi_14: Optional[float] = None
    ema_9: Optional[float] = None
    ema_21: Optional[float] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "ticker": self.ticker,
            "current_price": self.current_price,
            "open_price": self.open_price,
            "high_price": self.high_price,
            "low_price": self.low_price,
            "volume": self.volume,
            "change_percent": self.change_percent,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "rsi_14": self.rsi_14,
            "ema_9": self.ema_9,
            "ema_21": self.ema_21,
        }


@dataclass
class OptionContract:
    """Individual option contract data."""
    ticker: str
    expiration_date: datetime
    strike: float
    option_type: OptionType
    bid: float
    ask: float
    last: float
    volume: int
    open_interest: int
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float = 0.0
    implied_volatility: float = 0.0
    
    @property
    def spread(self) -> float:
        """Calculate bid-ask spread."""
        return self.ask - self.bid
    
    @property
    def mid_price(self) -> float:
        """Calculate mid price."""
        return (self.bid + self.ask) / 2
    
    @property
    def spread_percent(self) -> float:
        """Calculate spread as percentage of mid price."""
        if self.mid_price > 0:
            return (self.spread / self.mid_price) * 100
        return 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "ticker": self.ticker,
            "expiration_date": self.expiration_date.isoformat(),
            "strike": self.strike,
            "option_type": self.option_type.value,
            "bid": self.bid,
            "ask": self.ask,
            "last": self.last,
            "volume": self.volume,
            "open_interest": self.open_interest,
            "delta": self.delta,
            "gamma": self.gamma,
            "vega": self.vega,
            "theta": self.theta,
            "rho": self.rho,
            "implied_volatility": self.implied_volatility,
            "spread": self.spread,
            "mid_price": self.mid_price,
            "spread_percent": self.spread_percent,
        }


@dataclass
class OptionsChain:
    """SPY options chain for a specific expiration."""
    ticker: str
    expiration_date: datetime
    timestamp: datetime
    calls: list[OptionContract] = field(default_factory=list)
    puts: list[OptionContract] = field(default_factory=list)
    underlying_price: float = 0.0
    
    def get_atm_strike(self) -> float:
        """Get at-the-money strike."""
        if not self.underlying_price:
            return 0.0
        return round(self.underlying_price / 1)  # Round to nearest dollar
    
    def get_otm_calls(self, threshold: float = 0.0) -> list[OptionContract]:
        """Get out-of-the-money calls above threshold."""
        atm = self.get_atm_strike()
        return [c for c in self.calls if c.strike >= atm + threshold]
    
    def get_otm_puts(self, threshold: float = 0.0) -> list[OptionContract]:
        """Get out-of-the-money puts below threshold."""
        atm = self.get_atm_strike()
        return [p for p in self.puts if p.strike <= atm - threshold]
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "ticker": self.ticker,
            "expiration_date": self.expiration_date.isoformat(),
            "timestamp": self.timestamp.isoformat(),
            "underlying_price": self.underlying_price,
            "calls": [c.to_dict() for c in self.calls],
            "puts": [p.to_dict() for p in self.puts],
        }


@dataclass
class SimulatedTrade:
    """Simulated trade for paper trading."""
    id: str
    signal_id: str
    ticker: str
    expiration_date: datetime
    strike: float
    option_type: OptionType
    entry_time: datetime
    entry_price: float
    quantity: int = 1
    contract_multiplier: int = 100
    
    # Exit metrics (set after simulation)
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    
    # Trade metrics
    max_adverse_excursion: float = 0.0
    max_favorable_excursion: float = 0.0
    time_in_trade_seconds: int = 0
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None
    
    # Status
    status: str = "open"  # open, closed
    
    def calculate_pnl(self) -> None:
        """Calculate profit/loss if trade is closed."""
        if self.exit_price is not None:
            self.profit_loss = (self.exit_price - self.entry_price) * self.contract_multiplier * self.quantity
            if self.entry_price > 0:
                self.profit_loss_percent = ((self.exit_price - self.entry_price) / self.entry_price) * 100
            
            if self.exit_time and self.entry_time:
                self.time_in_trade_seconds = int((self.exit_time - self.entry_time).total_seconds())
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "signal_id": self.signal_id,
            "ticker": self.ticker,
            "expiration_date": self.expiration_date.isoformat(),
            "strike": self.strike,
            "option_type": self.option_type.value,
            "entry_time": self.entry_time.isoformat(),
            "entry_price": self.entry_price,
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "exit_price": self.exit_price,
            "quantity": self.quantity,
            "contract_multiplier": self.contract_multiplier,
            "max_adverse_excursion": self.max_adverse_excursion,
            "max_favorable_excursion": self.max_favorable_excursion,
            "time_in_trade_seconds": self.time_in_trade_seconds,
            "profit_loss": self.profit_loss,
            "profit_loss_percent": self.profit_loss_percent,
            "status": self.status,
        }
