"""Tactical Board Brief Generator for SPY 0DTE Tactical Agent.

Generates executive-ready briefs for tactical signals.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class TacticalBoardBrief:
    """Executive-ready tactical board brief."""
    brief_id: str
    timestamp: datetime
    
    # Signal summary
    signal_id: str
    ticker: str
    strike: float
    option_type: str
    direction: str
    expiration: str
    
    # Performance metrics
    signal_score: float
    confidence_score: float
    
    # Context
    regime: str
    regime_confidence: float
    time_window: str
    
    # Risk assessment
    risk_level: str
    approval_path: str
    requires_ceo_approval: bool
    requires_finance_approval: bool
    
    # Portfolio context
    portfolio_fit: str
    capital_required: float
    risk_budget_impact_pct: float
    position_size_appropriate: bool
    
    # Thesis and rationale
    thesis: str
    rationale: str
    suppression_risks: list[str] = field(default_factory=list)
    
    # Conflicts
    conflict_flags: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    
    # Status
    status: str = "pending_review"
    
    def to_dict(self) -> dict:
        return {
            "brief_id": self.brief_id,
            "timestamp": self.timestamp.isoformat(),
            "signal_id": self.signal_id,
            "ticker": self.ticker,
            "strike": self.strike,
            "option_type": self.option_type,
            "direction": self.direction,
            "expiration": self.expiration,
            "signal_score": self.signal_score,
            "confidence_score": self.confidence_score,
            "regime": self.regime,
            "regime_confidence": self.regime_confidence,
            "time_window": self.time_window,
            "risk_level": self.risk_level,
            "approval_path": self.approval_path,
            "requires_ceo_approval": self.requires_ceo_approval,
            "requires_finance_approval": self.requires_finance_approval,
            "portfolio_fit": self.portfolio_fit,
            "capital_required": self.capital_required,
            "risk_budget_impact_pct": self.risk_budget_impact_pct,
            "position_size_appropriate": self.position_size_appropriate,
            "thesis": self.thesis,
            "rationale": self.rationale,
            "suppression_risks": self.suppression_risks,
            "conflict_flags": self.conflict_flags,
            "warnings": self.warnings,
            "status": self.status,
        }
    
    def to_executive_summary(self) -> str:
        """Generate executive summary text."""
        lines = []
        lines.append(f"TACTICAL SIGNAL BRIEF - {self.ticker}")
        lines.append("=" * 50)
        lines.append(f"Strike: ${self.strike} {self.option_type.upper()}")
        lines.append(f"Direction: {self.direction.upper()}")
        lines.append(f"Confidence: {self.confidence_score:.0f}% | Score: {self.signal_score:.0f}")
        lines.append("")
        lines.append(f"REGIME: {self.regime.upper()} ({self.regime_confidence:.0%} confidence)")
        lines.append(f"Time Window: {self.time_window}")
        lines.append("")
        lines.append(f"RISK LEVEL: {self.risk_level.upper()}")
        lines.append(f"Approval Required: {'CEO' if self.requires_ceo_approval else ('Finance' if self.requires_finance_approval else 'None')}")
        lines.append("")
        lines.append("THESIS:")
        lines.append(self.thesis)
        lines.append("")
        
        if self.conflict_flags:
            lines.append("CONFLICTS:")
            for flag in self.conflict_flags:
                lines.append(f"  - {flag}")
            lines.append("")
        
        if self.warnings:
            lines.append("WARNINGS:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
            lines.append("")
        
        lines.append("-" * 50)
        lines.append(f"Status: {self.status.upper()}")
        
        return "\n".join(lines)


class BoardBriefGenerator:
    """
    Generates executive-ready tactical board briefs.
    """
    
    def __init__(self):
        self.briefs: list[TacticalBoardBrief] = []
        self.brief_counter: int = 0
    
    def generate(
        self,
        signal,
        regime_context=None,
        portfolio_fit_result=None,
        review_decision=None,
    ) -> TacticalBoardBrief:
        """
        Generate a tactical board brief.
        
        Args:
            signal: OptionsSignal
            regime_context: RegimeContext from classification
            portfolio_fit_result: PortfolioFitResult
            review_decision: ReviewDecision
        
        Returns:
            TacticalBoardBrief
        """
        self.brief_counter += 1
        brief_id = f"BRIEF-{self.brief_counter:06d}"
        
        # Determine direction
        direction = "call" if signal.option_type.value == "call" else "put" if hasattr(signal.option_type, 'value') else str(signal.option_type)
        
        # Get values with fallbacks
        regime = regime_context.regime.value if regime_context else (signal.regime_label or "unknown")
        regime_confidence = regime_context.confidence if regime_context else (signal.confidence_score / 100)
        time_window = regime_context.timestamp.strftime("%H:%M") if regime_context else "unknown"
        
        # Portfolio fit
        portfolio_fit = "FEASIBLE" if (portfolio_fit_result and portfolio_fit_result.is_feasible) else "INFEASIBLE"
        capital_required = signal.mid_price * 100 if signal.mid_price else 500
        risk_budget_pct = portfolio_fit_result.risk_budget_impact if portfolio_fit_result else 0
        position_appropriate = portfolio_fit_result.is_feasible if portfolio_fit_result else True
        
        # Approval
        requires_ceo = review_decision.requires_ceo_approval if review_decision else False
        requires_finance = review_decision.requires_finance_approval if review_decision else False
        
        # Risk level
        risk_level = review_decision.review_level.value if review_decision else "unknown"
        
        # Generate thesis
        thesis = self._generate_thesis(signal, regime, direction)
        
        # Generate rationale
        rationale = signal.reasoning_summary or "Signal generated based on delta velocity, gamma exposure, and momentum alignment."
        
        # Suppression risks
        suppression_risks = self._identify_suppression_risks(signal, regime_context)
        
        # Conflicts and warnings
        conflicts = portfolio_fit_result.conflict_flags if portfolio_fit_result else []
        warnings = portfolio_fit_result.warnings if portfolio_fit_result else []
        
        brief = TacticalBoardBrief(
            brief_id=brief_id,
            timestamp=datetime.now(),
            signal_id=signal.id,
            ticker=signal.ticker,
            strike=signal.strike,
            option_type=direction,
            direction=direction,
            expiration=signal.expiration_date.strftime("%Y-%m-%d"),
            signal_score=signal.signal_score,
            confidence_score=signal.confidence_score,
            regime=regime,
            regime_confidence=regime_confidence,
            time_window=time_window,
            risk_level=risk_level,
            approval_path=review_decision.review_level.value if review_decision else "unknown",
            requires_ceo_approval=requires_ceo,
            requires_finance_approval=requires_finance,
            portfolio_fit=portfolio_fit,
            capital_required=capital_required,
            risk_budget_impact_pct=risk_budget_pct,
            position_size_appropriate=position_appropriate,
            thesis=thesis,
            rationale=rationale,
            suppression_risks=suppression_risks,
            conflict_flags=conflicts,
            warnings=warnings,
        )
        
        self.briefs.append(brief)
        return brief
    
    def _generate_thesis(self, signal, regime: str, direction: str) -> str:
        """Generate trading thesis."""
        theses = []
        
        # Direction thesis
        if direction == "call":
            theses.append(f"Bullish SPY 0DTE based on {regime} regime")
        else:
            theses.append(f"Bearish SPY 0DTE based on {regime} regime")
        
        # Confidence thesis
        if signal.confidence_score >= 70:
            theses.append("high confidence in directional move")
        elif signal.confidence_score >= 50:
            theses.append("moderate confidence in directional move")
        else:
            theses.append("speculative directional play")
        
        # Score thesis
        if signal.signal_score >= 70:
            theses.append("strong technical signal")
        elif signal.signal_score >= 50:
            theses.append("moderate technical signal")
        
        return "; ".join(theses)
    
    def _identify_suppression_risks(self, signal, regime_context) -> list[str]:
        """Identify potential suppression risks."""
        risks = []
        
        if signal.confidence_score < 50:
            risks.append("Low confidence may suppress signal")
        
        if signal.signal_score < 60:
            risks.append("Below-threshold score may suppress signal")
        
        if regime_context:
            if regime_context.volatility_regime.value == "extreme":
                risks.append("Extreme volatility regime may suppress")
            
            if regime_context.regime.value == "low_participation":
                risks.append("Low participation regime may suppress")
        
        return risks
    
    def get_pending_briefs(self) -> list[TacticalBoardBrief]:
        """Get briefs awaiting review."""
        return [b for b in self.briefs if b.status == "pending_review"]
    
    def get_ceo_briefs(self) -> list[TacticalBoardBrief]:
        """Get briefs requiring CEO approval."""
        return [b for b in self.briefs if b.requires_ceo_approval]
    
    def get_finance_briefs(self) -> list[TacticalBoardBrief]:
        """Get briefs requiring finance approval."""
        return [b for b in self.briefs if b.requires_finance_approval and not b.requires_ceo_approval]
    
    def get_brief_by_id(self, brief_id: str) -> Optional[TacticalBoardBrief]:
        """Get brief by ID."""
        for brief in self.briefs:
            if brief.brief_id == brief_id:
                return brief
        return None
    
    def update_brief_status(self, brief_id: str, status: str) -> bool:
        """Update brief status."""
        for brief in self.briefs:
            if brief.brief_id == brief_id:
                brief.status = status
                return True
        return False


def create_brief_generator() -> BoardBriefGenerator:
    """Factory function to create brief generator."""
    return BoardBriefGenerator()
