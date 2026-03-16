"""Portfolio Management Models.

This module defines the core data models for portfolio management.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from dataclasses import dataclass, field


class PositionStatus(Enum):
    """Status of a position."""
    OPEN = "open"
    CLOSED = "closed"
    PENDING = "pending"


class AllocationTier(Enum):
    """Capital allocation tiers."""
    STABILITY = "stability"      # Emergency capital
    DEBT = "debt"                # Liability reduction
    INCOME = "income"            # Income strategies
    INVESTMENT = "investment"     # Long-term investing
    TACTICAL = "tactical"        # Active trading


@dataclass
class Position:
    """Represents an individual position."""
    id: str
    ticker: str
    entry_price: Decimal
    quantity: Decimal
    current_price: Decimal
    status: PositionStatus
    entry_time: datetime
    exit_time: Optional[datetime] = None
    pnl: Decimal = field(default_factory=Decimal)
    pnl_percent: float = 0.0
    
    def calculate_pnl(self):
        """Calculate current P&L."""
        self.pnl = (self.current_price - self.entry_price) * self.quantity
        if self.entry_price > 0:
            self.pnl_percent = float((self.current_price - self.entry_price) / self.entry_price * 100)
        return self.pnl


@dataclass
class CapitalAllocation:
    """Capital allocation across tiers."""
    tier: AllocationTier
    target_percent: float
    current_percent: float = 0.0
    allocated_amount: Decimal = field(default_factory=Decimal)
    target_amount: Decimal = field(default_factory=Decimal)


@dataclass
class PortfolioMetrics:
    """Portfolio performance metrics."""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    total_pnl: Decimal = field(default_factory=Decimal)
    average_win: Decimal = field(default_factory=Decimal)
    average_loss: Decimal = field(default_factory=Decimal)
    expectancy: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    current_drawdown: float = 0.0
    
    def calculate_metrics(self):
        """Calculate derived metrics."""
        if self.total_trades > 0:
            self.win_rate = (self.winning_trades / self.total_trades) * 100
        
        if self.winning_trades > 0:
            self.average_win = self.total_pnl / Decimal(str(self.winning_trades))
        
        if self.losing_trades > 0:
            self.average_loss = abs(self.total_pnl) / Decimal(str(self.losing_trades))
        
        # Expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
        win_rate_decimal = self.win_rate / 100
        loss_rate_decimal = 1 - win_rate_decimal
        if self.average_loss > 0:
            self.expectancy = (win_rate_decimal * float(self.average_win)) - (loss_rate_decimal * float(self.average_loss))
        
        # Profit factor
        if self.average_loss > 0:
            gross_wins = self.average_win * Decimal(str(self.winning_trades))
            gross_losses = self.average_loss * Decimal(str(self.losing_trades))
            if gross_losses > 0:
                self.profit_factor = float(gross_wins / gross_losses)


@dataclass
class PortfolioState:
    """Snapshot of portfolio state."""
    timestamp: datetime
    total_equity: Decimal
    cash_balance: Decimal
    open_positions: list[Position] = field(default_factory=list)
    closed_positions: list[Position] = field(default_factory=list)
    allocations: list[CapitalAllocation] = field(default_factory=list)
    metrics: Optional[PortfolioMetrics] = None
    
    @property
    def total_exposure(self) -> Decimal:
        """Calculate total portfolio exposure."""
        return self.total_equity - self.cash_balance
    
    @property
    def exposure_percent(self) -> float:
        """Calculate exposure as percentage."""
        if self.total_equity > 0:
            return float(self.total_exposure / self.total_equity * 100)
        return 0.0
    
    @property
    def open_position_count(self) -> int:
        """Count of open positions."""
        return len([p for p in self.open_positions if p.status == PositionStatus.OPEN])


@dataclass
class TradeProposal:
    """Proposed trade from an investment agent."""
    id: str
    ticker: str
    option_type: str  # call/put
    strike: float
    expiration: datetime
    entry_price: Decimal
    position_size: Decimal
    confidence: float
    signal_score: float
    rationale: str
    agent_source: str
    timestamp: datetime
    status: str = "pending"  # pending, approved, rejected, executed


@dataclass
class RiskLimits:
    """Risk limits configuration."""
    max_trade_risk_percent: float = 2.0
    max_portfolio_exposure_percent: float = 50.0
    max_drawdown_percent: float = 10.0
    max_position_concentration_percent: float = 20.0
    max_daily_loss_percent: float = 5.0


@dataclass
class PortfolioSignal:
    """Signal generated by portfolio engine."""
    type: str  # overexposed, underutilized, strategy_degradation, risk_spike
    severity: str  # low, medium, high, critical
    message: str
    details: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
