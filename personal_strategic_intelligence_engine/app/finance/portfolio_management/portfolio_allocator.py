"""Portfolio Allocator.

This module determines how capital is distributed across different strategies.
"""
from decimal import Decimal
from typing import Optional

from app.finance.portfolio_management.portfolio_models import (
    AllocationTier,
    CapitalAllocation,
    PortfolioState,
)


class PortfolioAllocator:
    """Manages capital allocation across strategies."""
    
    # Default allocation targets
    DEFAULT_ALLOCATION = {
        AllocationTier.STABILITY: 20.0,    # Emergency capital
        AllocationTier.DEBT: 25.0,         # Liability reduction
        AllocationTier.INCOME: 15.0,        # Income strategies
        AllocationTier.INVESTMENT: 30.0,    # Long-term investing
        AllocationTier.TACTICAL: 10.0,      # Active trading (SPY 0DTE)
    }
    
    def __init__(
        self,
        total_capital: Decimal = Decimal("100000"),
        allocation_targets: Optional[dict[AllocationTier, float]] = None,
    ):
        """Initialize the portfolio allocator.
        
        Args:
            total_capital: Total capital available
            allocation_targets: Custom allocation targets
        """
        self.total_capital = total_capital
        self.allocation_targets = allocation_targets or self.DEFAULT_ALLOCATION
        
    def calculate_allocation(
        self,
        portfolio: PortfolioState,
        tier: AllocationTier,
    ) -> CapitalAllocation:
        """Calculate allocation for a specific tier.
        
        Args:
            portfolio: Current portfolio state
            tier: Allocation tier
            
        Returns:
            Capital allocation for the tier
        """
        target_percent = self.allocation_targets.get(tier, 0.0)
        target_amount = self.total_capital * Decimal(str(target_percent / 100))
        
        # Calculate current allocation
        tier_positions = [
            p for p in portfolio.open_positions
            if self._get_tier_for_ticker(p.ticker) == tier
        ]
        
        current_amount = sum(
            p.current_price * p.quantity for p in tier_positions
        )
        
        current_percent = 0.0
        if self.total_capital > 0:
            current_percent = float(current_amount / self.total_capital * 100)
        
        return CapitalAllocation(
            tier=tier,
            target_percent=target_percent,
            current_percent=current_percent,
            allocated_amount=current_amount,
            target_amount=target_amount,
        )
    
    def get_available_capital(
        self,
        portfolio: PortfolioState,
        tier: AllocationTier,
    ) -> Decimal:
        """Get available capital for a tier.
        
        Args:
            portfolio: Current portfolio state
            tier: Allocation tier
            
        Returns:
            Available capital for the tier
        """
        allocation = self.calculate_allocation(portfolio, tier)
        
        # Available = target - current
        available = allocation.target_amount - allocation.allocated_amount
        
        # Also consider cash
        if tier == AllocationTier.TACTICAL:
            # Tactical can use cash
            available = max(available, portfolio.cash_balance * Decimal("0.5"))
        
        return max(Decimal("0"), available)
    
    def can_allocate(
        self,
        portfolio: PortfolioState,
        tier: AllocationTier,
        amount: Decimal,
    ) -> tuple[bool, str]:
        """Check if allocation is possible.
        
        Args:
            portfolio: Current portfolio state
            tier: Allocation tier
            amount: Amount to allocate
            
        Returns:
            Tuple of (allowed, reason)
        """
        available = self.get_available_capital(portfolio, tier)
        
        if amount > available:
            return False, f"Insufficient capital in {tier.value} tier"
        
        # Check total portfolio exposure
        new_exposure = portfolio.exposure_percent + float(amount / self.total_capital * 100)
        if new_exposure > 80:
            return False, "Portfolio would be overexposed"
        
        return True, "Allocation approved"
    
    def adjust_allocation(
        self,
        portfolio: PortfolioState,
        tier: AllocationTier,
        adjustment_percent: float,
    ) -> CapitalAllocation:
        """Adjust allocation target for a tier.
        
        Args:
            portfolio: Current portfolio state
            tier: Allocation tier
            adjustment_percent: Percentage adjustment (+/-)
            
        Returns:
            Updated allocation
        """
        current_target = self.allocation_targets.get(tier, 0.0)
        new_target = max(0, min(100, current_target + adjustment_percent))
        
        self.allocation_targets[tier] = new_target
        
        return self.calculate_allocation(portfolio, tier)
    
    def get_allocation_report(self, portfolio: PortfolioState) -> dict:
        """Generate allocation report.
        
        Args:
            portfolio: Current portfolio state
            
        Returns:
            Allocation report
        """
        allocations = []
        
        for tier in AllocationTier:
            alloc = self.calculate_allocation(portfolio, tier)
            allocations.append({
                "tier": tier.value,
                "target_percent": alloc.target_percent,
                "current_percent": alloc.current_percent,
                "drift": alloc.current_percent - alloc.target_percent,
                "target_amount": float(alloc.target_amount),
                "allocated_amount": float(alloc.allocated_amount),
                "available": float(self.get_available_capital(portfolio, tier)),
            })
        
        return {
            "total_capital": float(self.total_capital),
            "total_equity": float(portfolio.total_equity),
            "cash_balance": float(portfolio.cash_balance),
            "allocations": allocations,
        }
    
    def _get_tier_for_ticker(self, ticker: str) -> AllocationTier:
        """Map ticker to allocation tier."""
        ticker_upper = ticker.upper()
        
        # SPY options go to tactical
        if "SPY" in ticker_upper or ticker_upper in ["QQQ", "IWM", "TLT"]:
            return AllocationTier.TACTICAL
        
        # Dividend stocks go to income
        if ticker_upper in ["SCHD", "VYM", "VNQ"]:
            return AllocationTier.INCOME
        
        # Default to investment
        return AllocationTier.INVESTMENT
    
    def rebalance_required(self, portfolio: PortfolioState) -> tuple[bool, str]:
        """Check if rebalancing is required.
        
        Args:
            portfolio: Current portfolio state
            
        Returns:
            Tuple of (rebalance_needed, reason)
        """
        for tier in AllocationTier:
            allocation = self.calculate_allocation(portfolio, tier)
            drift = abs(allocation.current_percent - allocation.target_percent)
            
            # Rebalance if drift > 5%
            if drift > 5.0:
                return True, f"{tier.value} tier drift: {drift:.1f}%"
        
        return False, "Allocations within targets"


# Global allocator
_allocator: Optional[PortfolioAllocator] = None


def get_allocator() -> PortfolioAllocator:
    """Get the global portfolio allocator."""
    global _allocator
    
    if _allocator is None:
        _allocator = PortfolioAllocator()
    
    return _allocator
