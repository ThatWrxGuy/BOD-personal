"""Governance Integration for SPY 0DTE Options Tactical Agent.

Integrates agent with PSIE governance layer, decision journaling, and compliance.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class SignalAction(str, Enum):
    """Signal action types."""
    GENERATED = "generated"
    SUPPRESSED = "suppressed"
    EXECUTED = "executed"  # Future - not currently used
    EXPIRED = "expired"


class SuppressionReason(str, Enum):
    """Signal suppression reasons."""
    LIQUIDITY = "liquidity"
    SPREAD = "spread"
    VOLATILITY = "volatility"
    CONFIDENCE = "confidence"
    REGIME = "regime"
    TIME_WINDOW = "time_window"
    COOLDOWN = "cooldown"
    DUPLICATE = "duplicate"


class GovernanceStatus(str, Enum):
    """Governance status for agent."""
    ADVISORY_ONLY = "advisory_only"
    APPROVAL_REQUIRED = "approval_required"
    AUTONOMOUS = "autonomous"


@dataclass
class DecisionJournalEntry:
    """Decision journal entry for governance tracking."""
    id: str
    timestamp: datetime
    signal_id: str
    action: SignalAction
    
    # Signal details
    ticker: str
    strike: float
    option_type: str
    direction: str
    signal_score: float
    confidence_score: float
    
    # Suppression details (if applicable)
    suppression_reason: Optional[SuppressionReason] = None
    suppression_detail: Optional[str] = None
    
    # Trade details (if applicable)
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    profit_loss: Optional[float] = None
    trade_status: Optional[str] = None
    
    # Governance
    governance_status: GovernanceStatus = GovernanceStatus.ADVISORY_ONLY
    human_approval_required: bool = False
    approved_by: Optional[str] = None
    
    # Metadata
    regime_label: Optional[str] = None
    time_window: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "signal_id": self.signal_id,
            "action": self.action.value,
            "ticker": self.ticker,
            "strike": self.strike,
            "option_type": self.option_type,
            "direction": self.direction,
            "signal_score": self.signal_score,
            "confidence_score": self.confidence_score,
            "suppression_reason": self.suppression_reason.value if self.suppression_reason else None,
            "suppression_detail": self.suppression_detail,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "profit_loss": self.profit_loss,
            "trade_status": self.trade_status,
            "governance_status": self.governance_status.value,
            "human_approval_required": self.human_approval_required,
            "approved_by": self.approved_by,
            "regime_label": self.regime_label,
            "time_window": self.time_window,
        }


class GovernanceIntegrator:
    """
    Integrates SPY 0DTE agent with PSIE governance layer.
    
    Tracks all signals, suppressions, and trade outcomes for
    compliance and audit purposes.
    """
    
    def __init__(self):
        self.journal_entries: list[DecisionJournalEntry] = []
        self.governance_status = GovernanceStatus.ADVISORY_ONLY
        
        # Configuration
        self.action_threshold = 60.0  # Score above this requires journal entry
        self.confidence_threshold = 40.0  # Min confidence for action
    
    def log_signal_generated(
        self,
        signal,
        regime_label: Optional[str] = None,
        time_window: Optional[str] = None,
    ) -> DecisionJournalEntry:
        """
        Log a generated signal.
        
        Args:
            signal: OptionsSignal object
            regime_label: Market regime label
            time_window: Trading window label
        
        Returns:
            DecisionJournalEntry
        """
        entry = DecisionJournalEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            signal_id=signal.id,
            action=SignalAction.GENERATED,
            ticker=signal.ticker,
            strike=signal.strike,
            option_type=signal.option_type.value if hasattr(signal.option_type, 'value') else str(signal.option_type),
            direction="call" if (hasattr(signal.option_type, 'value') and signal.option_type.value == "call") else "put",
            signal_score=signal.signal_score,
            confidence_score=signal.confidence_score,
            governance_status=self.governance_status,
            human_approval_required=True,  # Always required in advisory mode
            regime_label=regime_label,
            time_window=time_window,
        )
        
        self.journal_entries.append(entry)
        return entry
    
    def log_signal_suppressed(
        self,
        signal,
        reason: SuppressionReason,
        detail: str,
        regime_label: Optional[str] = None,
        time_window: Optional[str] = None,
    ) -> DecisionJournalEntry:
        """
        Log a suppressed signal.
        
        Args:
            signal: OptionsSignal object (or mock with required fields)
            reason: SuppressionReason
            detail: Detailed suppression reason
            regime_label: Market regime label
            time_window: Trading window label
        
        Returns:
            DecisionJournalEntry
        """
        entry = DecisionJournalEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            signal_id=signal.get('id', 'unknown'),
            action=SignalAction.SUPPRESSED,
            ticker=signal.get('ticker', 'SPY'),
            strike=signal.get('strike', 0),
            option_type=signal.get('option_type', 'call'),
            direction=signal.get('direction', 'call'),
            signal_score=signal.get('signal_score', 0),
            confidence_score=signal.get('confidence_score', 0),
            suppression_reason=reason,
            suppression_detail=detail,
            governance_status=self.governance_status,
            human_approval_required=False,
            regime_label=regime_label,
            time_window=time_window,
        )
        
        self.journal_entries.append(entry)
        return entry
    
    def log_trade_result(
        self,
        signal_id: str,
        entry_price: float,
        exit_price: float,
        profit_loss: float,
        trade_status: str,
    ) -> DecisionJournalEntry:
        """
        Log a trade result.
        
        Args:
            signal_id: Original signal ID
            entry_price: Entry price
            exit_price: Exit price
            profit_loss: Profit/loss amount
            trade_status: Trade status (closed, stopped, expired)
        
        Returns:
            DecisionJournalEntry
        """
        # Find original signal entry
        original_entry = None
        for entry in self.journal_entries:
            if entry.signal_id == signal_id:
                original_entry = entry
                break
        
        entry = DecisionJournalEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            signal_id=signal_id,
            action=SignalAction.EXPIRED if trade_status == "expired" else SignalAction.EXECUTED,
            ticker=original_entry.ticker if original_entry else "SPY",
            strike=original_entry.strike if original_entry else 0,
            option_type=original_entry.option_type if original_entry else "call",
            direction=original_entry.direction if original_entry else "call",
            signal_score=original_entry.signal_score if original_entry else 0,
            confidence_score=original_entry.confidence_score if original_entry else 0,
            entry_price=entry_price,
            exit_price=exit_price,
            profit_loss=profit_loss,
            trade_status=trade_status,
            governance_status=self.governance_status,
            human_approval_required=False,
            regime_label=original_entry.regime_label if original_entry else None,
            time_window=original_entry.time_window if original_entry else None,
        )
        
        self.journal_entries.append(entry)
        return entry
    
    def get_journal_entries(
        self,
        limit: int = 100,
        action: Optional[SignalAction] = None,
    ) -> list[DecisionJournalEntry]:
        """
        Get journal entries.
        
        Args:
            limit: Max entries to return
            action: Filter by action type
        
        Returns:
            List of DecisionJournalEntry
        """
        entries = self.journal_entries
        
        if action:
            entries = [e for e in entries if e.action == action]
        
        return entries[-limit:]
    
    def get_suppression_summary(self) -> dict:
        """Get summary of suppressions by reason."""
        suppressions = [e for e in self.journal_entries if e.action == SignalAction.SUPPRESSED]
        
        if not suppressions:
            return {"total": 0, "by_reason": {}}
        
        by_reason: dict[str, int] = {}
        for entry in suppressions:
            reason = entry.suppression_reason.value if entry.suppression_reason else "unknown"
            by_reason[reason] = by_reason.get(reason, 0) + 1
        
        return {
            "total": len(suppressions),
            "by_reason": by_reason,
        }
    
    def get_performance_by_regime(self) -> dict:
        """Get performance breakdown by regime."""
        trades = [e for e in self.journal_entries if e.action == SignalAction.EXPIRED]
        
        if not trades:
            return {}
        
        by_regime: dict[str, dict] = {}
        for trade in trades:
            regime = trade.regime_label or "unknown"
            if regime not in by_regime:
                by_regime[regime] = {
                    "count": 0,
                    "total_pnl": 0.0,
                    "wins": 0,
                    "losses": 0,
                }
            
            by_regime[regime]["count"] += 1
            by_regime[regime]["total_pnl"] += trade.profit_loss or 0
            
            if (trade.profit_loss or 0) > 0:
                by_regime[regime]["wins"] += 1
            else:
                by_regime[regime]["losses"] += 1
        
        # Calculate win rates
        for regime, stats in by_regime.items():
            if stats["count"] > 0:
                stats["win_rate"] = (stats["wins"] / stats["count"]) * 100
                stats["avg_pnl"] = stats["total_pnl"] / stats["count"]
        
        return by_regime
    
    def is_advisory_only(self) -> bool:
        """Check if agent is in advisory-only mode."""
        return self.governance_status == GovernanceStatus.ADVISORY_ONLY
    
    def requires_human_approval(self, signal_score: float) -> bool:
        """
        Check if signal requires human approval.
        
        In advisory-only mode, all signals require approval.
        """
        return self.is_advisory_only() or signal_score < self.action_threshold


# Global governance integrator instance
_governance_integrator: Optional[GovernanceIntegrator] = None


def get_governance_integrator() -> GovernanceIntegrator:
    """Get global governance integrator instance."""
    global _governance_integrator
    if _governance_integrator is None:
        _governance_integrator = GovernanceIntegrator()
    return _governance_integrator


def set_governance_status(status: GovernanceStatus) -> None:
    """Set governance status."""
    integrator = get_governance_integrator()
    integrator.governance_status = status
