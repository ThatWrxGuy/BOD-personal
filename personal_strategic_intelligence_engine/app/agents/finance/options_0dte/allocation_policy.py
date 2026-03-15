"""Tactical Allocation Policy Engine for SPY 0DTE Tactical Agent.

Determines signal eligibility, allocation limits, and disposition.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class AllocationEligibility(str, Enum):
    """Eligibility status for tactical allocation."""
    PAPER_TRADE_ONLY = "paper_trade_only"
    BOARD_REVIEWABLE = "board_reviewable"
    QUALIFIED = "qualified"
    DEFERRED = "deferred"
    BLOCKED = "blocked"


class DispositionAction(str, Enum):
    """Final disposition action for signal."""
    LOG_ONLY = "log_only"
    REVIEW = "review"
    APPROVE = "approve"
    DOWNGRADE = "downgrade"
    DEFER = "defer"
    BLOCK = "block"


@dataclass
class AllocationPolicy:
    """Allocation policy configuration."""
    max_paper_trade_notional: float = 50000.0
    max_board_review_notional: float = 25000.0
    max_qualified_notional: float = 10000.0
    
    min_confidence_for_paper: float = 30.0
    min_confidence_for_review: float = 50.0
    min_confidence_for_qualified: float = 70.0
    
    allow_defensive_reduction: bool = True
    reduction_factor_defensive: float = 0.5


@dataclass
class AllocationDecision:
    """Allocation decision for a tactical signal."""
    eligibility: AllocationEligibility
    disposition: DispositionAction
    max_notional: float
    recommended_notional: float
    reasons: list[str] = field(default_factory=list)
    policy_rules_applied: list[str] = field(default_factory=list)
    downgrade_reason: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "eligibility": self.eligibility.value,
            "disposition": self.disposition.value,
            "max_notional": self.max_notional,
            "recommended_notional": self.recommended_notional,
            "reasons": self.reasons,
            "policy_rules_applied": self.policy_rules_applied,
            "downgrade_reason": self.downgrade_reason,
        }


class TacticalAllocationEngine:
    """
    Determines signal eligibility and allocation limits.
    """
    
    def __init__(self, policy: Optional[AllocationPolicy] = None):
        self.policy = policy or AllocationPolicy()
    
    def evaluate(
        self,
        signal,
        portfolio_fit_result=None,
        review_decision=None,
        regime_context=None,
    ) -> AllocationDecision:
        """
        Evaluate allocation eligibility.
        
        Args:
            signal: OptionsSignal
            portfolio_fit_result: PortfolioFitResult
            review_decision: ReviewDecision
            regime_context: RegimeContext
        
        Returns:
            AllocationDecision
        """
        reasons = []
        rules_applied = []
        
        confidence = signal.confidence_score
        score = signal.signal_score
        
        # Check if rejected by review
        if review_decision and review_decision.should_reject:
            reasons.append("Signal rejected by review process")
            return AllocationDecision(
                eligibility=AllocationEligibility.BLOCKED,
                disposition=DispositionAction.BLOCK,
                max_notional=0,
                recommended_notional=0,
                reasons=reasons,
                policy_rules_applied=["review_rejection"],
            )
        
        # Check portfolio feasibility
        if portfolio_fit_result and not portfolio_fit_result.is_feasible:
            reasons.append("Portfolio infeasible")
            return AllocationDecision(
                eligibility=AllocationEligibility.BLOCKED,
                disposition=DispositionAction.BLOCK,
                max_notional=0,
                recommended_notional=0,
                reasons=reasons,
                policy_rules_applied=["portfolio_infeasibility"],
            )
        
        # Determine base eligibility by confidence
        eligibility = self._determine_eligibility(
            confidence, score, portfolio_fit_result
        )
        
        # Apply regime adjustments
        if regime_context:
            eligibility, downgrade_reason = self._apply_regime_adjustment(
                eligibility, regime_context
            )
            if downgrade_reason:
                reasons.append(downgrade_reason)
                rules_applied.append("regime_adjustment")
        
        # Apply portfolio adjustments
        if portfolio_fit_result:
            eligibility, max_notional = self._apply_portfolio_adjustment(
                eligibility, portfolio_fit_result
            )
            rules_applied.append("portfolio_adjustment")
        else:
            max_notional = self._get_max_notional(eligibility)
        
        # Determine disposition
        disposition = self._determine_disposition(
            eligibility, review_decision
        )
        
        # Calculate recommended notional
        recommended = self._calculate_recommended_notional(
            signal, eligibility, max_notional
        )
        
        return AllocationDecision(
            eligibility=eligibility,
            disposition=disposition,
            max_notional=max_notional,
            recommended_notional=recommended,
            reasons=reasons,
            policy_rules_applied=rules_applied,
        )
    
    def _determine_eligibility(
        self,
        confidence: float,
        score: float,
        portfolio_fit_result=None,
    ) -> AllocationEligibility:
        """Determine base eligibility by confidence."""
        
        if confidence >= self.policy.min_confidence_for_qualified:
            if portfolio_fit_result and portfolio_fit_result.is_feasible:
                return AllocationEligibility.QUALIFIED
        
        if confidence >= self.policy.min_confidence_for_review:
            return AllocationEligibility.BOARD_REVIEWABLE
        
        if confidence >= self.policy.min_confidence_for_paper:
            return AllocationEligibility.PAPER_TRADE_ONLY
        
        return AllocationEligibility.DEFERRED
    
    def _apply_regime_adjustment(
        self,
        eligibility: AllocationEligibility,
        regime_context,
    ) -> tuple[AllocationEligibility, Optional[str]]:
        """Apply regime-based adjustments."""
        
        regime = regime_context.regime.value
        
        if regime == "volatility_expansion":
            # Downgrade in volatile regime
            if eligibility == AllocationEligibility.QUALIFIED:
                return AllocationEligibility.BOARD_REVIEWABLE, "Downgraded: volatility expansion"
            elif eligibility == AllocationEligibility.BOARD_REVIEWABLE:
                return AllocationEligibility.PAPER_TRADE_ONLY, "Downgraded: volatility expansion"
        
        if regime == "range_chop":
            # Downgrade in chop
            if eligibility == AllocationEligibility.QUALIFIED:
                return AllocationEligibility.BOARD_REVIEWABLE, "Downgraded: range/chop regime"
        
        if regime == "low_participation":
            # Defer in low participation
            if eligibility in [AllocationEligibility.QUALIFIED, AllocationEligibility.BOARD_REVIEWABLE]:
                return AllocationEligibility.DEFERRED, "Deferred: low participation"
        
        return eligibility, None
    
    def _apply_portfolio_adjustment(
        self,
        eligibility: AllocationEligibility,
        portfolio_fit_result,
    ) -> tuple[AllocationEligibility, float]:
        """Apply portfolio-based adjustments."""
        
        max_notional = self._get_max_notional(eligibility)
        
        # Apply position size limit
        if portfolio_fit_result.max_recommended_notional > 0:
            max_notional = min(
                max_notional,
                portfolio_fit_result.max_recommended_notional
            )
        
        # Downgrade if budget exceeded
        if portfolio_fit_result.conflict_flags:
            if eligibility == AllocationEligibility.QUALIFIED:
                eligibility = AllocationEligibility.BOARD_REVIEWABLE
            elif eligibility == AllocationEligibility.BOARD_REVIEWABLE:
                eligibility = AllocationEligibility.PAPER_TRADE_ONLY
        
        return eligibility, max_notional
    
    def _get_max_notional(self, eligibility: AllocationEligibility) -> float:
        """Get max notional for eligibility level."""
        
        if eligibility == AllocationEligibility.QUALIFIED:
            return self.policy.max_qualified_notional
        elif eligibility == AllocationEligibility.BOARD_REVIEWABLE:
            return self.policy.max_board_review_notional
        elif eligibility == AllocationEligibility.PAPER_TRADE_ONLY:
            return self.policy.max_paper_trade_notional
        
        return 0
    
    def _determine_disposition(
        self,
        eligibility: AllocationEligibility,
        review_decision=None,
    ) -> DispositionAction:
        """Determine final disposition."""
        
        if eligibility == AllocationEligibility.BLOCKED:
            return DispositionAction.BLOCK
        
        if eligibility == AllocationEligibility.DEFERRED:
            return DispositionAction.DEFER
        
        if eligibility == AllocationEligibility.PAPER_TRADE_ONLY:
            return DispositionAction.LOG_ONLY
        
        if eligibility == AllocationEligibility.BOARD_REVIEWABLE:
            return DispositionAction.REVIEW
        
        if eligibility == AllocationEligibility.QUALIFIED:
            if review_decision and review_decision.requires_ceo_approval:
                return DispositionAction.REVIEW
            return DispositionAction.APPROVE
        
        return DispositionAction.LOG_ONLY
    
    def _calculate_recommended_notional(
        self,
        signal,
        eligibility: AllocationEligibility,
        max_notional: float,
    ) -> float:
        """Calculate recommended notional amount."""
        
        # Base recommended on confidence
        confidence_factor = signal.confidence_score / 100.0
        
        recommended = max_notional * confidence_factor
        
        # Minimum $1000 for any trade
        recommended = max(recommended, 1000)
        
        # Round to nearest $1000
        recommended = round(recommended / 1000) * 1000
        
        return min(recommended, max_notional)


def create_allocation_engine() -> TacticalAllocationEngine:
    """Factory function to create allocation engine."""
    return TacticalAllocationEngine()
