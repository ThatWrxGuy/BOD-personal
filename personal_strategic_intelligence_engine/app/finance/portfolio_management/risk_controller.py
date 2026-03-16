"""Risk Controller.

This module ensures portfolio risk remains within acceptable limits.
"""
from decimal import Decimal
from typing import Optional

from app.finance.portfolio_management.portfolio_models import (
    Position,
    PortfolioState,
    RiskLimits,
    TradeProposal,
)


class RiskController:
    """Manages portfolio risk limits."""
    
    def __init__(self, limits: Optional[RiskLimits] = None):
        """Initialize the risk controller.
        
        Args:
            limits: Risk limits configuration
        """
        self.limits = limits or RiskLimits()
        
    def validate_trade(
        self,
        proposal: TradeProposal,
        portfolio: PortfolioState,
    ) -> tuple[bool, str]:
        """Validate a trade proposal against risk limits.
        
        Args:
            proposal: Trade proposal
            portfolio: Current portfolio state
            
        Returns:
            Tuple of (valid, reason)
        """
        # Check trade risk
        trade_risk = self._calculate_trade_risk(proposal)
        risk_percent = float(trade_risk / portfolio.total_equity * 100)
        
        if risk_percent > self.limits.max_trade_risk_percent:
            return False, f"Trade risk {risk_percent:.1f}% exceeds limit {self.limits.max_trade_risk_percent}%"
        
        # Check portfolio exposure
        new_exposure = portfolio.exposure_percent + risk_percent
        if new_exposure > self.limits.max_portfolio_exposure_percent:
            return False, f"Portfolio exposure {new_exposure:.1f}% would exceed limit"
        
        # Check position concentration
        position_value = proposal.entry_price * proposal.position_size
        concentration = float(position_value / portfolio.total_equity * 100)
        if concentration > self.limits.max_position_concentration_percent:
            return False, f"Position concentration {concentration:.1f}% exceeds limit"
        
        # Check daily loss limit
        if self._exceeds_daily_loss_limit(portfolio):
            return False, "Daily loss limit exceeded"
        
        return True, "Trade validated"
    
    def validate_position_size(
        self,
        proposal: TradeProposal,
        portfolio: PortfolioState,
    ) -> Decimal:
        """Validate and adjust position size.
        
        Args:
            proposal: Trade proposal
            portfolio: Current portfolio state
            
        Returns:
            Adjusted position size
        """
        max_position_value = (
            portfolio.total_equity 
            * Decimal(str(self.limits.max_position_concentration_percent / 100))
        )
        
        proposed_value = proposal.entry_price * proposal.position_size
        
        if proposed_value > max_position_value:
            adjusted_size = max_position_value / proposal.entry_price
            return adjusted_size
        
        return proposal.position_size
    
    def get_portfolio_risk(self, portfolio: PortfolioState) -> dict:
        """Calculate current portfolio risk metrics.
        
        Args:
            portfolio: Current portfolio state
            
        Returns:
            Risk metrics
        """
        # Calculate exposure
        exposure = portfolio.exposure_percent
        
        # Calculate concentration
        max_concentration = 0.0
        if portfolio.total_equity > 0:
            for position in portfolio.open_positions:
                value = position.current_price * position.quantity
                concentration = float(value / portfolio.total_equity * 100)
                max_concentration = max(max_concentration, concentration)
        
        # Calculate downside exposure
        downside_exposure = 0.0
        for position in portfolio.open_positions:
            if position.pnl < 0:
                exposure = abs(float(position.pnl))
                downside_exposure += exposure
        
        return {
            "exposure_percent": exposure,
            "max_concentration_percent": max_concentration,
            "downside_exposure": float(downside_exposure),
            "cash_percent": 100 - exposure,
            "within_limits": exposure <= self.limits.max_portfolio_exposure_percent,
        }
    
    def check_risk_limits(self, portfolio: PortfolioState) -> tuple[bool, list[str]]:
        """Check all risk limits.
        
        Args:
            portfolio: Current portfolio state
            
        Returns:
            Tuple of (all_within_limits, violations)
        """
        violations = []
        risk = self.get_portfolio_risk(portfolio)
        
        if risk["exposure_percent"] > self.limits.max_portfolio_exposure_percent:
            violations.append(
                f"Portfolio exposure {risk['exposure_percent']:.1f}% exceeds limit"
            )
        
        if risk["max_concentration_percent"] > self.limits.max_position_concentration_percent:
            violations.append(
                f"Position concentration {risk['max_concentration_percent']:.1f}% exceeds limit"
            )
        
        return len(violations) == 0, violations
    
    def calculate_var(
        self,
        portfolio: PortfolioState,
        confidence: float = 0.95,
    ) -> Decimal:
        """Calculate Value at Risk.
        
        Args:
            portfolio: Current portfolio state
            confidence: Confidence level
            
        Returns:
            VaR estimate
        """
        # Simplified VaR calculation
        # In production, would use historical returns
        
        total_risk = sum(
            abs(position.pnl) for position in portfolio.open_positions
            if position.pnl < 0
        )
        
        if confidence == 0.95:
            # 95% VaR - assume 2x worst case
            return total_risk * Decimal("2")
        
        return total_risk
    
    def should_reduce_risk(self, portfolio: PortfolioState) -> tuple[bool, str]:
        """Determine if risk should be reduced.
        
        Args:
            portfolio: Current portfolio state
            
        Returns:
            Tuple of (should_reduce, reason)
        """
        risk = self.get_portfolio_risk(portfolio)
        
        if risk["exposure_percent"] > 70:
            return True, "High portfolio exposure"
        
        if risk["max_concentration_percent"] > 15:
            return True, "High position concentration"
        
        if self._exceeds_daily_loss_limit(portfolio):
            return True, "Daily loss limit approaching"
        
        return False, "Risk within acceptable range"
    
    def _calculate_trade_risk(self, proposal: TradeProposal) -> Decimal:
        """Calculate risk for a trade proposal.
        
        Args:
            proposal: Trade proposal
            
        Returns:
            Risk amount
        """
        # Risk is the full position value (worst case)
        return proposal.entry_price * proposal.position_size
    
    def _exceeds_daily_loss_limit(self, portfolio: PortfolioState) -> bool:
        """Check if daily loss limit is exceeded.
        
        Args:
            portfolio: Current portfolio state
            
        Returns:
            True if limit exceeded
        """
        # Would track daily P&L in production
        # Simplified check
        total_pnl = sum(p.pnl for p in portfolio.open_positions)
        daily_loss = abs(float(total_pnl))
        daily_loss_percent = daily_loss / float(portfolio.total_equity) * 100
        
        return daily_loss_percent > self.limits.max_daily_loss_percent


# Global risk controller
_risk_controller: Optional[RiskController] = None


def get_risk_controller() -> RiskController:
    """Get the global risk controller."""
    global _risk_controller
    
    if _risk_controller is None:
        _risk_controller = RiskController()
    
    return _risk_controller
