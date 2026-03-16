"""Portfolio Rebalancer.

This module maintains allocation targets by rebalancing the portfolio.
"""
from decimal import Decimal
from typing import Optional

from app.finance.portfolio_management.portfolio_allocator import PortfolioAllocator
from app.finance.portfolio_management.portfolio_models import (
    AllocationTier,
    PortfolioSignal,
    PortfolioState,
)
from app.finance.portfolio_management.risk_controller import RiskController


class PortfolioRebalancer:
    """Manages portfolio rebalancing."""
    
    # Rebalance when drift exceeds this percentage
    REBALANCE_THRESHOLD = 5.0
    
    def __init__(
        self,
        allocator: Optional[PortfolioAllocator] = None,
        risk_controller: Optional[RiskController] = None,
    ):
        """Initialize the rebalancer.
        
        Args:
            allocator: Portfolio allocator
            risk_controller: Risk controller
        """
        self.allocator = allocator or PortfolioAllocator()
        self.risk_controller = risk_controller or RiskController()
        
    def should_rebalance(self, portfolio: PortfolioState) -> tuple[bool, str]:
        """Determine if rebalancing is needed.
        
        Args:
            portfolio: Current portfolio state
            
        Returns:
            Tuple of (should_rebalance, reason)
        """
        # Check allocation drift
        can_rebalance, reason = self.allocator.rebalance_required(portfolio)
        
        if can_rebalance:
            return True, reason
        
        # Check risk conditions
        should_reduce, risk_reason = self.risk_controller.should_reduce_risk(portfolio)
        
        if should_reduce:
            return True, f"Risk reduction: {risk_reason}"
        
        return False, "No rebalancing needed"
    
    def get_rebalance_actions(self, portfolio: PortfolioState) -> list[dict]:
        """Get recommended rebalancing actions.
        
        Args:
            portfolio: Current portfolio state
            
        Returns:
            List of rebalance actions
        """
        actions = []
        
        for tier in AllocationTier:
            allocation = self.allocator.calculate_allocation(portfolio, tier)
            drift = allocation.current_percent - allocation.target_percent
            
            if abs(drift) > self.REBALANCE_THRESHOLD:
                action = {
                    "tier": tier.value,
                    "current_percent": allocation.current_percent,
                    "target_percent": allocation.target_percent,
                    "drift": drift,
                }
                
                if drift > 0:
                    # Over-allocated - need to reduce
                    action["action"] = "reduce"
                    action["amount"] = abs(float(allocation.allocated_amount - allocation.target_amount))
                else:
                    # Under-allocated - can add
                    action["action"] = "add"
                    action["amount"] = abs(float(allocation.allocated_amount - allocation.target_amount))
                
                actions.append(action)
        
        return actions
    
    def execute_rebalance(
        self,
        portfolio: PortfolioState,
        market_prices: dict[str, Decimal],
    ) -> tuple[PortfolioState, list[dict]]:
        """Execute portfolio rebalancing.
        
        Args:
            portfolio: Current portfolio state
            market_prices: Current market prices
            
        Returns:
            Tuple of (new portfolio state, actions taken)
        """
        # Get rebalance actions
        actions = self.get_rebalance_actions(portfolio)
        
        # Would execute trades here in production
        
        return portfolio, actions
    
    def reduce_risk(
        self,
        portfolio: PortfolioState,
    ) -> list[PortfolioSignal]:
        """Reduce portfolio risk by closing positions.
        
        Args:
            portfolio: Current portfolio state
            
        Returns:
            List of signals generated
        """
        signals = []
        
        # Find positions to close
        losing_positions = [
            p for p in portfolio.open_positions
            if p.pnl < 0
        ]
        
        # Sort by worst loss
        losing_positions.sort(key=lambda p: p.pnl)
        
        # Check if we need to reduce
        should_reduce, reason = self.risk_controller.should_reduce_risk(portfolio)
        
        if not should_reduce:
            return signals
        
        # Generate signal
        risk = self.risk_controller.get_portfolio_risk(portfolio)
        
        if risk["exposure_percent"] > 70:
            signals.append(PortfolioSignal(
                type="risk_spike",
                severity="high",
                message=f"Reducing exposure from {risk['exposure_percent']:.1f}%",
                details={"positions_to_close": len(losing_positions)},
            ))
        
        return signals
    
    def get_rebalance_report(self, portfolio: PortfolioState) -> dict:
        """Generate rebalancing report.
        
        Args:
            portfolio: Current portfolio state
            
        Returns:
            Rebalancing report
        """
        should_rebalance, reason = self.should_rebalance(portfolio)
        
        return {
            "should_rebalance": should_rebalance,
            "reason": reason,
            "actions": self.get_rebalance_actions(portfolio),
            "allocator_report": self.allocator.get_allocation_report(portfolio),
        }


# Global rebalancer
_rebalancer: Optional[PortfolioRebalancer] = None


def get_rebalancer() -> PortfolioRebalancer:
    """Get the global rebalancer."""
    global _rebalancer
    
    if _rebalancer is None:
        _rebalancer = PortfolioRebalancer()
    
    return _rebalancer
