"""Portfolio Risk Adapter for SPY 0DTE Tactical Agent.

Evaluates tactical signals against portfolio risk constraints.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalPath(str, Enum):
    """Approval path for signals."""
    AUTO_LOG_ONLY = "auto_log_only"
    FINANCE_REVIEW = "finance_review"
    CEO_APPROVAL = "ceo_approval"
    REJECT = "reject"


@dataclass
class PortfolioContext:
    """Portfolio context at time of signal evaluation."""
    timestamp: datetime
    total_portfolio_value: float
    available_cash: float
    daily_loss_limit: float
    weekly_loss_limit: float
    current_daily_pnl: float
    current_weekly_pnl: float
    existing_tactical_positions: int
    tactical_exposure_notional: float
    speculative_risk_budget: float
    speculative_risk_used: float
    
    @property
    def daily_loss_remaining(self) -> float:
        """Remaining daily loss allowance."""
        return self.daily_loss_limit + self.current_daily_pnl
    
    @property
    def weekly_loss_remaining(self) -> float:
        """Remaining weekly loss allowance."""
        return self.weekly_loss_limit + self.current_weekly_pnl
    
    @property
    def speculative_budget_remaining(self) -> float:
        """Remaining speculative risk budget."""
        return self.speculative_risk_budget - self.speculative_risk_used
    
    @property
    def speculative_budget_pct(self) -> float:
        """Percentage of speculative budget used."""
        if self.speculative_risk_budget > 0:
            return (self.speculative_risk_used / self.speculative_risk_budget) * 100
        return 0.0


@dataclass
class PortfolioFitResult:
    """Result of portfolio fit evaluation."""
    is_feasible: bool
    risk_level: RiskLevel
    approval_path: ApprovalPath
    capital_feasibility: bool
    risk_budget_impact: float
    exposure_classification: str
    conflict_flags: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    portfolio_context: Optional[PortfolioContext] = None
    max_recommended_notional: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "is_feasible": self.is_feasible,
            "risk_level": self.risk_level.value,
            "approval_path": self.approval_path.value,
            "capital_feasibility": self.capital_feasibility,
            "risk_budget_impact": self.risk_budget_impact,
            "exposure_classification": self.exposure_classification,
            "conflict_flags": self.conflict_flags,
            "warnings": self.warnings,
            "max_recommended_notional": self.max_recommended_notional,
        }


class PortfolioRiskAdapter:
    """
    Evaluates tactical signals against portfolio risk constraints.
    """
    
    def __init__(
        self,
        default_cash: float = 100000.0,
        default_daily_loss_limit: float = 2000.0,
        default_weekly_loss_limit: float = 5000.0,
        default_speculative_budget: float = 10000.0,
        max_position_size_pct: float = 2.0,
    ):
        """
        Initialize portfolio risk adapter.
        
        Args:
            default_cash: Default available cash
            default_daily_loss_limit: Maximum daily loss allowed
            default_weekly_loss_limit: Maximum weekly loss allowed
            default_speculative_budget: Budget for speculative trades
            max_position_size_pct: Max position size as % of portfolio
        """
        self.default_cash = default_cash
        self.default_daily_loss_limit = default_daily_loss_limit
        self.default_weekly_loss_limit = default_weekly_loss_limit
        self.default_speculative_budget = default_speculative_budget
        self.max_position_size_pct = max_position_size_pct
        
        # Current portfolio context
        self.current_context: Optional[PortfolioContext] = None
    
    def get_default_context(self) -> PortfolioContext:
        """Get default portfolio context."""
        return PortfolioContext(
            timestamp=datetime.now(),
            total_portfolio_value=self.default_cash,
            available_cash=self.default_cash,
            daily_loss_limit=self.default_daily_loss_limit,
            weekly_loss_limit=self.default_weekly_loss_limit,
            current_daily_pnl=0.0,
            current_weekly_pnl=0.0,
            existing_tactical_positions=0,
            tactical_exposure_notional=0.0,
            speculative_risk_budget=self.default_speculative_budget,
            speculative_risk_used=0.0,
        )
    
    def set_portfolio_context(self, context: PortfolioContext) -> None:
        """Set current portfolio context."""
        self.current_context = context
    
    def evaluate_signal(
        self,
        signal,
        option_price: float = 5.0,
        contract_multiplier: int = 100,
    ) -> PortfolioFitResult:
        """
        Evaluate a tactical signal against portfolio constraints.
        
        Args:
            signal: OptionsSignal to evaluate
            option_price: Price of the option contract
            contract_multiplier: Options contract multiplier
        
        Returns:
            PortfolioFitResult with feasibility assessment
        """
        # Get portfolio context
        context = self.current_context or self.get_default_context()
        
        # Calculate required capital
        required_capital = option_price * contract_multiplier
        
        # Calculate notional exposure
        notional_exposure = signal.strike * contract_multiplier
        
        # Check capital feasibility
        capital_feasible = context.available_cash >= required_capital
        
        # Check max position size
        max_notional = context.total_portfolio_value * (self.max_position_size_pct / 100)
        position_too_large = notional_exposure > max_notional
        
        # Check daily loss limit
        at_daily_loss_limit = context.daily_loss_remaining <= 0
        
        # Check weekly loss limit
        at_weekly_loss_limit = context.weekly_loss_remaining <= 0
        
        # Check speculative budget
        budget_exceeded = context.speculative_budget_remaining < required_capital
        budget_pct = context.speculative_budget_pct
        
        # Check existing positions
        too_many_positions = context.existing_tactical_positions >= 3
        
        # Build conflict flags
        conflict_flags = []
        warnings = []
        
        if not capital_feasible:
            conflict_flags.append("insufficient_cash")
        
        if position_too_large:
            conflict_flags.append("position_too_large")
            warnings.append(f"Position exceeds {self.max_position_size_pct}% of portfolio")
        
        if at_daily_loss_limit:
            conflict_flags.append("daily_loss_limit_reached")
        
        if at_weekly_loss_limit:
            conflict_flags.append("weekly_loss_limit_reached")
        
        if budget_exceeded:
            conflict_flags.append("speculative_budget_exceeded")
        
        if budget_pct > 80:
            warnings.append(f"Speculative budget {budget_pct:.0f}% utilized")
        
        if too_many_positions:
            warnings.append("Maximum tactical positions reached")
        
        # Determine feasibility
        is_feasible = (
            capital_feasible and 
            not position_too_large and
            not at_daily_loss_limit and
            not conflict_flags  # No critical conflicts
        )
        
        # Determine risk level
        if conflict_flags:
            risk_level = RiskLevel.CRITICAL
        elif warnings:
            risk_level = RiskLevel.HIGH
        elif budget_pct > 50:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        # Determine approval path
        approval_path = self._determine_approval_path(
            risk_level, is_feasible, conflict_flags
        )
        
        # Calculate risk budget impact
        risk_budget_impact = (required_capital / context.speculative_risk_budget * 100) if context.speculative_risk_budget > 0 else 0
        
        # Determine exposure classification
        if signal.signal_score >= 70:
            exposure_class = "high_confidence"
        elif signal.signal_score >= 50:
            exposure_class = "medium_confidence"
        else:
            exposure_class = "low_confidence"
        
        # Calculate max recommended notional
        max_recommended = min(
            context.available_cash,
            max_notional,
            context.speculative_budget_remaining,
        )
        
        return PortfolioFitResult(
            is_feasible=is_feasible,
            risk_level=risk_level,
            approval_path=approval_path,
            capital_feasibility=capital_feasible,
            risk_budget_impact=risk_budget_impact,
            exposure_classification=exposure_class,
            conflict_flags=conflict_flags,
            warnings=warnings,
            portfolio_context=context,
            max_recommended_notional=max_recommended,
        )
    
    def _determine_approval_path(
        self,
        risk_level: RiskLevel,
        is_feasible: bool,
        conflict_flags: list[str],
    ) -> ApprovalPath:
        """Determine approval path based on risk level and conflicts."""
        
        if not is_feasible:
            return ApprovalPath.REJECT
        
        if conflict_flags:
            return ApprovalPath.CEO_APPROVAL
        
        if risk_level == RiskLevel.CRITICAL:
            return ApprovalPath.CEO_APPROVAL
        
        if risk_level == RiskLevel.HIGH:
            return ApprovalPath.CEO_APPROVAL
        
        if risk_level == RiskLevel.MEDIUM:
            return ApprovalPath.FINANCE_REVIEW
        
        # Low risk - auto log
        return ApprovalPath.AUTO_LOG_ONLY
    
    def check_conflicts(
        self,
        signal,
        portfolio_context: Optional[PortfolioContext] = None,
    ) -> list[str]:
        """
        Check for conflicts with portfolio strategy.
        
        Args:
            signal: OptionsSignal to check
            portfolio_context: Current portfolio context
        
        Returns:
            List of conflict descriptions
        """
        context = portfolio_context or self.current_context or self.get_default_context()
        conflicts = []
        
        # Check if at loss limits
        if context.daily_loss_remaining <= 0:
            conflicts.append("Daily loss limit already reached")
        
        if context.weekly_loss_remaining <= 0:
            conflicts.append("Weekly loss limit already reached")
        
        # Check speculative budget
        if context.speculative_budget_pct >= 90:
            conflicts.append("Speculative budget nearly exhausted")
        
        # Check position concentration
        if context.existing_tactical_positions >= 3:
            conflicts.append("Maximum tactical positions already open")
        
        return conflicts


def create_default_adapter() -> PortfolioRiskAdapter:
    """Factory function to create default adapter."""
    return PortfolioRiskAdapter()
