"""Portfolio Engine.

This is the main portfolio management engine that coordinates all components.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.finance.portfolio_management.portfolio_allocator import (
    PortfolioAllocator,
    get_allocator,
)
from app.finance.portfolio_management.portfolio_models import (
    AllocationTier,
    PortfolioMetrics,
    PortfolioSignal,
    PortfolioState,
    PositionStatus,
    RiskLimits,
    TradeProposal,
)
from app.finance.portfolio_management.portfolio_models import (
    PortfolioState,
    TradeProposal,
)
from app.finance.portfolio_management.position_manager import (
    PositionManager,
    get_position_manager,
)
from app.finance.portfolio_management.performance_tracker import (
    PerformanceTracker,
    get_performance_tracker,
)
from app.finance.portfolio_management.risk_controller import (
    RiskController,
    get_risk_controller,
)
from app.finance.portfolio_management.rebalancer import (
    PortfolioRebalancer,
    get_rebalancer,
)


class PortfolioEngine:
    """Main portfolio management engine."""
    
    def __init__(
        self,
        initial_capital: Decimal = Decimal("100000"),
        risk_limits: Optional[RiskLimits] = None,
    ):
        """Initialize the portfolio engine.
        
        Args:
            initial_capital: Starting capital
            risk_limits: Risk limits configuration
        """
        self.initial_capital = initial_capital
        
        # Initialize components
        self.allocator = PortfolioAllocator(total_capital=initial_capital)
        self.position_manager = PositionManager()
        self.performance_tracker = PerformanceTracker()
        self.risk_controller = RiskController(limits=risk_limits)
        self.rebalancer = PortfolioRebalancer(
            allocator=self.allocator,
            risk_controller=self.risk_controller,
        )
        
        # Signals
        self.active_signals: list[PortfolioSignal] = []
        
    def get_portfolio_state(self) -> PortfolioState:
        """Get current portfolio state.
        
        Returns:
            Current portfolio state
        """
        positions = self.position_manager.get_open_positions()
        
        # Calculate allocations
        allocations = []
        for tier in AllocationTier:
            alloc = self.allocator.calculate_allocation(
                self._create_portfolio_state(positions),
                tier,
            )
            allocations.append(alloc)
        
        return PortfolioState(
            timestamp=datetime.now(),
            total_equity=self._calculate_equity(positions),
            cash_balance=self._calculate_cash(positions),
            open_positions=positions,
            allocations=allocations,
        )
    
    def _create_portfolio_state(self, positions) -> PortfolioState:
        """Create a portfolio state for calculations."""
        return PortfolioState(
            timestamp=datetime.now(),
            total_equity=self.initial_capital,
            cash_balance=self.initial_capital,
            open_positions=positions,
        )
    
    def _calculate_equity(self, positions) -> Decimal:
        """Calculate total equity."""
        position_value = sum(
            p.current_price * p.quantity for p in positions
        )
        return self.initial_capital + self.position_manager.get_unrealized_pnl() + position_value
    
    def _calculate_cash(self, positions) -> Decimal:
        """Calculate available cash."""
        position_value = sum(
            p.entry_price * p.quantity for p in positions
        )
        return max(Decimal("0"), self.initial_capital - position_value)
    
    async def evaluate_proposal(
        self,
        proposal: TradeProposal,
    ) -> dict:
        """Evaluate a trade proposal through the portfolio engine.
        
        Args:
            proposal: Trade proposal from an agent
            
        Returns:
            Evaluation result
        """
        portfolio = self.get_portfolio_state()
        
        # Step 1: Check risk limits
        is_valid, risk_reason = self.risk_controller.validate_trade(
            proposal, portfolio
        )
        
        if not is_valid:
            proposal.status = "rejected"
            return {
                "approved": False,
                "reason": risk_reason,
                "proposal": proposal,
            }
        
        # Step 2: Check allocation
        tier = AllocationTier.TACTICAL  # SPY 0DTE goes to tactical
        can_allocate, alloc_reason = self.allocator.can_allocate(
            portfolio, tier, proposal.position_size * proposal.entry_price
        )
        
        if not can_allocate:
            proposal.status = "rejected"
            return {
                "approved": False,
                "reason": alloc_reason,
                "proposal": proposal,
            }
        
        # Step 3: Validate position size
        adjusted_size = self.risk_controller.validate_position_size(
            proposal, portfolio
        )
        
        # All checks passed
        proposal.status = "approved"
        
        return {
            "approved": True,
            "adjusted_position_size": adjusted_size,
            "proposal": proposal,
            "allocation": self.allocator.get_allocation_report(portfolio),
        }
    
    async def execute_trade(
        self,
        proposal: TradeProposal,
        current_price: Decimal,
    ) -> dict:
        """Execute an approved trade.
        
        Args:
            proposal: Approved trade proposal
            current_price: Current market price
            
        Returns:
            Execution result
        """
        portfolio = self.get_portfolio_state()
        
        # Validate again
        is_valid, reason = self.risk_controller.validate_trade(proposal, portfolio)
        
        if not is_valid:
            return {
                "success": False,
                "reason": reason,
            }
        
        # Open position
        position = self.position_manager.open_position(proposal, current_price)
        proposal.status = "executed"
        
        # Update equity curve
        self.performance_tracker.update_equity_curve(self.get_portfolio_state())
        
        return {
            "success": True,
            "position_id": position.id,
            "position": position,
        }
    
    async def close_position(
        self,
        position_id: str,
        exit_price: Decimal,
    ) -> dict:
        """Close an existing position.
        
        Args:
            position_id: Position ID
            exit_price: Exit price
            
        Returns:
            Close result
        """
        position = self.position_manager.close_position(position_id, exit_price)
        
        if not position:
            return {
                "success": False,
                "reason": "Position not found",
            }
        
        # Record trade in performance tracker
        self.performance_tracker.record_trade(position)
        
        # Update equity curve
        self.performance_tracker.update_equity_curve(self.get_portfolio_state())
        
        return {
            "success": True,
            "position": position,
            "pnl": float(position.pnl),
            "pnl_percent": position.pnl_percent,
        }
    
    def get_portfolio_report(self) -> dict:
        """Generate comprehensive portfolio report.
        
        Returns:
            Portfolio report
        """
        portfolio = self.get_portfolio_state()
        metrics = self.performance_tracker.calculate_metrics(portfolio)
        
        # Check for signals
        self._update_signals(portfolio)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "portfolio": {
                "total_equity": float(portfolio.total_equity),
                "cash_balance": float(portfolio.cash_balance),
                "total_exposure": float(portfolio.total_exposure),
                "exposure_percent": portfolio.exposure_percent,
                "open_positions": portfolio.open_position_count,
            },
            "allocation": self.allocator.get_allocation_report(portfolio),
            "risk": self.risk_controller.get_portfolio_risk(portfolio),
            "performance": {
                "total_trades": metrics.total_trades,
                "win_rate": metrics.win_rate,
                "expectancy": float(metrics.expectancy),
                "profit_factor": metrics.profit_factor,
                "sharpe_ratio": metrics.sharpe_ratio,
                "max_drawdown": metrics.max_drawdown,
            },
            "signals": [s.message for s in self.active_signals],
            "rebalancing": self.rebalancer.get_rebalance_report(portfolio),
        }
    
    def _update_signals(self, portfolio: PortfolioState):
        """Update portfolio signals."""
        self.active_signals = []
        
        # Check exposure
        exposure = portfolio.exposure_percent
        if exposure > 70:
            self.active_signals.append(PortfolioSignal(
                type="overexposed",
                severity="high",
                message=f"Portfolio exposure at {exposure:.1f}%",
            ))
        elif exposure < 30:
            self.active_signals.append(PortfolioSignal(
                type="underutilized",
                severity="medium",
                message=f"Portfolio utilization at {exposure:.1f}%",
            ))
        
        # Check allocation drift
        should_rebalance, reason = self.rebalancer.should_rebalance(portfolio)
        if should_rebalance:
            self.active_signals.append(PortfolioSignal(
                type="strategy_degradation",
                severity="low",
                message=reason,
            ))
        
        # Check risk
        should_reduce, risk_reason = self.risk_controller.should_reduce_risk(portfolio)
        if should_reduce:
            self.active_signals.append(PortfolioSignal(
                type="risk_spike",
                severity="high",
                message=risk_reason,
            ))
    
    def check_and_close_positions(self, market_prices: dict[str, Decimal]) -> list[dict]:
        """Check positions and close if necessary.
        
        Args:
            market_prices: Current market prices
            
        Returns:
            List of closed positions
        """
        self.position_manager.update_positions(market_prices)
        
        closed = []
        
        # Check stop losses and take profits
        for position in self.position_manager.get_open_positions():
            # Check stop loss (5%)
            if self.position_manager.check_stop_loss(position.id, 5.0):
                result = self.position_manager.close_position(
                    position.id,
                    position.current_price,
                )
                if result:
                    closed.append({
                        "position_id": position.id,
                        "reason": "stop_loss",
                        "pnl": float(result.pnl),
                    })
            
            # Check take profit (15%)
            elif self.position_manager.check_take_profit(position.id, 15.0):
                result = self.position_manager.close_position(
                    position.id,
                    position.current_price,
                )
                if result:
                    closed.append({
                        "position_id": position.id,
                        "reason": "take_profit",
                        "pnl": float(result.pnl),
                    })
        
        return closed


# Global portfolio engine
_portfolio_engine: Optional[PortfolioEngine] = None


def get_portfolio_engine() -> PortfolioEngine:
    """Get the global portfolio engine."""
    global _portfolio_engine
    
    if _portfolio_engine is None:
        _portfolio_engine = PortfolioEngine()
    
    return _portfolio_engine
