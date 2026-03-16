"""Position Manager.

This module manages open positions, tracks P&L, and handles position lifecycle.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.finance.portfolio_management.portfolio_models import (
    Position,
    PositionStatus,
    PortfolioState,
    TradeProposal,
)


class PositionManager:
    """Manages portfolio positions."""
    
    def __init__(self):
        """Initialize the position manager."""
        self.positions: dict[str, Position] = {}
        
    def open_position(
        self,
        proposal: TradeProposal,
        current_price: Decimal,
    ) -> Position:
        """Open a new position.
        
        Args:
            proposal: Trade proposal
            current_price: Current market price
            
        Returns:
            Opened position
        """
        position = Position(
            id=str(uuid.uuid4()),
            ticker=proposal.ticker,
            entry_price=proposal.entry_price,
            quantity=proposal.position_size,
            current_price=current_price,
            status=PositionStatus.OPEN,
            entry_time=datetime.now(),
        )
        position.calculate_pnl()
        
        self.positions[position.id] = position
        
        return position
    
    def close_position(
        self,
        position_id: str,
        exit_price: Decimal,
    ) -> Optional[Position]:
        """Close an existing position.
        
        Args:
            position_id: Position ID
            exit_price: Exit price
            
        Returns:
            Closed position or None
        """
        position = self.positions.get(position_id)
        
        if not position:
            return None
        
        position.current_price = exit_price
        position.status = PositionStatus.CLOSED
        position.exit_time = datetime.now()
        position.calculate_pnl()
        
        return position
    
    def update_positions(
        self,
        market_prices: dict[str, Decimal],
    ) -> list[Position]:
        """Update positions with current market prices.
        
        Args:
            market_prices: Dictionary of ticker -> current price
            
        Returns:
            Updated positions
        """
        updated = []
        
        for position in self.positions.values():
            if position.status == PositionStatus.OPEN:
                if position.ticker in market_prices:
                    position.current_price = market_prices[position.ticker]
                    position.calculate_pnl()
                    updated.append(position)
        
        return updated
    
    def get_open_positions(self) -> list[Position]:
        """Get all open positions."""
        return [
            p for p in self.positions.values()
            if p.status == PositionStatus.OPEN
        ]
    
    def get_position(self, position_id: str) -> Optional[Position]:
        """Get a position by ID."""
        return self.positions.get(position_id)
    
    def get_positions_by_ticker(self, ticker: str) -> list[Position]:
        """Get all positions for a ticker."""
        return [
            p for p in self.positions.values()
            if p.ticker == ticker
        ]
    
    def get_total_exposure(self) -> Decimal:
        """Calculate total portfolio exposure."""
        return sum(
            p.current_price * p.quantity
            for p in self.get_open_positions()
        )
    
    def get_position_count(self) -> dict:
        """Get position counts."""
        open_count = len(self.get_open_positions())
        closed_count = len([
            p for p in self.positions.values()
            if p.status == PositionStatus.CLOSED
        ])
        
        return {
            "open": open_count,
            "closed": closed_count,
            "total": len(self.positions),
        }
    
    def get_unrealized_pnl(self) -> Decimal:
        """Calculate unrealized P&L."""
        return sum(p.pnl for p in self.get_open_positions())
    
    def get_realized_pnl(self) -> Decimal:
        """Calculate realized P&L."""
        return sum(
            p.pnl for p in self.positions.values()
            if p.status == PositionStatus.CLOSED
        )
    
    def get_losing_positions(self) -> list[Position]:
        """Get positions with losses."""
        return [
            p for p in self.get_open_positions()
            if p.pnl < 0
        ]
    
    def get_winning_positions(self) -> list[Position]:
        """Get positions with gains."""
        return [
            p for p in self.get_open_positions()
            if p.pnl > 0
        ]
    
    def check_stop_loss(self, position_id: str, stop_loss_percent: float) -> bool:
        """Check if position hit stop loss.
        
        Args:
            position_id: Position ID
            stop_loss_percent: Stop loss percentage
            
        Returns:
            True if stop loss triggered
        """
        position = self.get_position(position_id)
        
        if not position:
            return False
        
        loss_percent = abs(position.pnl_percent)
        
        return loss_percent >= stop_loss_percent
    
    def check_take_profit(self, position_id: str, take_profit_percent: float) -> bool:
        """Check if position hit take profit target.
        
        Args:
            position_id: Position ID
            take_profit_percent: Take profit percentage
            
        Returns:
            True if take profit triggered
        """
        position = self.get_position(position_id)
        
        if not position:
            return False
        
        return position.pnl_percent >= take_profit_percent


# Global position manager
_position_manager: Optional[PositionManager] = None


def get_position_manager() -> PositionManager:
    """Get the global position manager."""
    global _position_manager
    
    if _position_manager is None:
        _position_manager = PositionManager()
    
    return _position_manager
