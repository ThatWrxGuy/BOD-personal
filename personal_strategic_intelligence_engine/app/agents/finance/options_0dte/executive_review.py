"""Executive Review Thresholds for SPY 0DTE Tactical Agent.

Defines canonical review rules for tactical options signals.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class ReviewLevel(str, Enum):
    """Review level classification."""
    AUTO_LOG = "auto_log"
    FINANCE_REVIEW = "finance_review"
    CEO_REVIEW = "ceo_review"
    REJECT = "reject"


class ReviewReason(str, Enum):
    """Reasons for review level assignment."""
    SIGNAL_STRENGTH = "signal_strength"
    POSITION_SIZE = "position_size"
    RISK_BUDGET = "risk_budget"
    CONFLICT = "conflict"
    REGIME = "regime"
    CONCENTRATION = "concentration"
    REPEATED_SUPPRESSION = "repeated_suppression"


@dataclass
class ReviewRule:
    """A single review rule definition."""
    name: str
    condition: str
    review_level: ReviewLevel
    priority: int = 0


@dataclass
class ReviewThreshold:
    """Review threshold configuration."""
    min_confidence_for_auto_log: float = 60.0
    min_score_for_auto_log: float = 70.0
    max_position_pct_for_auto_log: float = 0.5
    max_risk_budget_pct_for_auto_log: float = 10.0
    
    # Finance review thresholds
    min_confidence_for_finance: float = 40.0
    min_score_for_finance: float = 50.0
    max_position_pct_for_finance: float = 1.0
    max_risk_budget_pct_for_finance: float = 25.0
    
    # CEO review thresholds (anything above these)
    min_confidence_for_ceo: float = 0.0
    min_score_for_ceo: float = 0.0
    
    # Rejection thresholds
    min_confidence_to_proceed: float = 30.0
    min_score_to_proceed: float = 40.0


@dataclass
class ReviewDecision:
    """Review decision for a signal."""
    review_level: ReviewLevel
    requires_ceo_approval: bool
    requires_finance_approval: bool
    can_auto_log: bool
    should_reject: bool
    reasons: list[str] = field(default_factory=list)
    rule_applied: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "review_level": self.review_level.value,
            "requires_ceo_approval": self.requires_ceo_approval,
            "requires_finance_approval": self.requires_finance_approval,
            "can_auto_log": self.can_auto_log,
            "should_reject": self.should_reject,
            "reasons": self.reasons,
            "rule_applied": self.rule_applied,
            "timestamp": self.timestamp.isoformat(),
        }


class ExecutiveReviewEngine:
    """
    Executive review threshold engine for tactical signals.
    
    Determines the appropriate approval path for each signal based on:
    - Signal confidence and score
    - Position size relative to portfolio
    - Risk budget utilization
    - Conflict flags
    - Regulatory constraints
    """
    
    def __init__(self, thresholds: Optional[ReviewThreshold] = None):
        self.thresholds = thresholds or ReviewThreshold()
        self.suppression_history: dict[str, int] = {}
    
    def evaluate(
        self,
        signal,
        portfolio_fit_result=None,
        conflict_flags: Optional[list[str]] = None,
    ) -> ReviewDecision:
        """
        Evaluate a signal and determine review level.
        
        Args:
            signal: OptionsSignal to evaluate
            portfolio_fit_result: Portfolio risk evaluation result
            conflict_flags: List of conflict descriptions
        
        Returns:
            ReviewDecision with approval path
        """
        reasons = []
        conflict_flags = conflict_flags or []
        
        # Extract metrics
        confidence = signal.confidence_score
        score = signal.signal_score
        
        # Extract portfolio metrics if available
        position_pct = 0.0
        risk_budget_pct = 0.0
        
        if portfolio_fit_result:
            position_pct = portfolio_fit_result.risk_budget_impact
            risk_budget_pct = portfolio_fit_result.risk_budget_impact
        
        # Check rejection first (low confidence/score)
        if confidence < self.thresholds.min_confidence_to_proceed:
            reasons.append(f"Confidence too low: {confidence:.1f}%")
            return ReviewDecision(
                review_level=ReviewLevel.REJECT,
                requires_ceo_approval=False,
                requires_finance_approval=False,
                can_auto_log=False,
                should_reject=True,
                reasons=reasons,
                rule_applied="confidence_rejection",
            )
        
        if score < self.thresholds.min_score_to_proceed:
            reasons.append(f"Score too low: {score:.1f}")
            return ReviewDecision(
                review_level=ReviewLevel.REJECT,
                requires_ceo_approval=False,
                requires_finance_approval=False,
                can_auto_log=False,
                should_reject=True,
                reasons=reasons,
                rule_applied="score_rejection",
            )
        
        # Check conflicts (critical)
        if conflict_flags:
            reasons.append(f"Conflicts detected: {', '.join(conflict_flags)}")
            return ReviewDecision(
                review_level=ReviewLevel.CEO_REVIEW,
                requires_ceo_approval=True,
                requires_finance_approval=False,
                can_auto_log=False,
                should_reject=False,
                reasons=reasons,
                rule_applied="conflict_override",
            )
        
        # Check portfolio fit for rejection
        if portfolio_fit_result and not portfolio_fit_result.is_feasible:
            reasons.append(f"Portfolio infeasible: {', '.join(portfolio_fit_result.conflict_flags)}")
            return ReviewDecision(
                review_level=ReviewLevel.REJECT,
                requires_ceo_approval=False,
                requires_finance_approval=False,
                can_auto_log=False,
                should_reject=True,
                reasons=reasons,
                rule_applied="portfolio_rejection",
            )
        
        # CEO Review conditions
        if (confidence < self.thresholds.min_confidence_for_finance or
            score < self.thresholds.min_score_for_finance or
            position_pct > self.thresholds.max_position_pct_for_finance or
            risk_budget_pct > self.thresholds.max_risk_budget_pct_for_finance):
            
            reasons.append(f"High risk: conf={confidence:.0f}%, score={score:.0f}%, pos={position_pct:.1f}%")
            return ReviewDecision(
                review_level=ReviewLevel.CEO_REVIEW,
                requires_ceo_approval=True,
                requires_finance_approval=True,
                can_auto_log=False,
                should_reject=False,
                reasons=reasons,
                rule_applied="ceo_review_threshold",
            )
        
        # Finance Review conditions
        if (confidence < self.thresholds.min_confidence_for_auto_log or
            score < self.thresholds.min_score_for_auto_log or
            position_pct > self.thresholds.max_position_pct_for_auto_log or
            risk_budget_pct > self.thresholds.max_risk_budget_pct_for_auto_log):
            
            reasons.append(f"Medium risk: conf={confidence:.0f}%, score={score:.0f}%, pos={position_pct:.1f}%")
            return ReviewDecision(
                review_level=ReviewLevel.FINANCE_REVIEW,
                requires_ceo_approval=False,
                requires_finance_approval=True,
                can_auto_log=False,
                should_reject=False,
                reasons=reasons,
                rule_applied="finance_review_threshold",
            )
        
        # Auto-log (low risk)
        reasons.append(f"Low risk: conf={confidence:.0f}%, score={score:.0f}%, pos={position_pct:.1f}%")
        return ReviewDecision(
            review_level=ReviewLevel.AUTO_LOG,
            requires_ceo_approval=False,
            requires_finance_approval=False,
            can_auto_log=True,
            should_reject=False,
            reasons=reasons,
            rule_applied="auto_log_threshold",
        )
    
    def track_suppression(self, signal_id: str) -> None:
        """Track suppressed signals for pattern detection."""
        self.suppression_history[signal_id] = self.suppression_history.get(signal_id, 0) + 1
    
    def get_suppression_count(self, signal_id: str) -> int:
        """Get suppression count for a signal."""
        return self.suppression_history.get(signal_id, 0)
    
    def should_escalate_repeated_suppressions(self, regime: str, count: int = 5) -> bool:
        """
        Check if repeated suppressions should trigger escalation.
        
        Args:
            regime: Market regime
            count: Threshold for escalation
        
        Returns:
            True if should escalate
        """
        # Could be implemented to track by regime
        return count >= 10  # Only escalate after 10+ suppressions


def create_default_engine() -> ExecutiveReviewEngine:
    """Factory function to create default review engine."""
    return ExecutiveReviewEngine()
