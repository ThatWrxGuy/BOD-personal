"""Decision Fusion Engine - BB-CORE-021

Combines outputs from multiple engines into unified strategic decisions.
"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.core.orchestration.orchestration_models import (
    SystemStateSnapshot,
    ActivationDecision,
    FusedDecision,
    TacticalOpportunity,
    CapitalPosture,
)

logger = logging.get_logger(__name__)


class DecisionFusionEngine:
    """Fuses outputs from multiple engines into unified decisions."""
    
    def __init__(self):
        pass
    
    def fuse_decisions(
        self,
        snapshot: SystemStateSnapshot,
        activation: ActivationDecision,
    ) -> FusedDecision:
        """Fuse all engine outputs into a single strategic decision."""
        
        decision = FusedDecision()
        
        # Collect inputs
        regime_input = self._evaluate_regime_input(snapshot)
        strategy_input = self._evaluate_strategy_input(snapshot)
        portfolio_input = self._evaluate_portfolio_input(snapshot)
        tactical_input = self._evaluate_tactical_input(snapshot)
        risk_input = self._evaluate_risk_input(snapshot)
        
        decision.regime_input = regime_input
        decision.strategy_input = strategy_input
        decision.portfolio_input = portfolio_input
        decision.tactical_input = tactical_input
        decision.risk_input = risk_input
        
        # Identify conflicts
        conflicts = self._identify_conflicts(
            regime_input, strategy_input, portfolio_input, tactical_input, risk_input
        )
        decision.conflicts = conflicts
        
        # Resolve conflicts
        resolution, action, conviction = self._resolve_conflicts(
            conflicts, regime_input, strategy_input, portfolio_input, tactical_input, risk_input, snapshot
        )
        
        decision.resolution = resolution
        decision.action = action
        decision.conviction = conviction
        
        # Build reasoning
        reasoning = []
        supporting = []
        opposing = []
        
        # Add regime input
        if regime_input:
            reasoning.append(f"Regime: {regime_input}")
            if "favorable" in regime_input.lower() or "risk-on" in regime_input.lower():
                supporting.append("Regime favors deployment")
            else:
                opposing.append("Regime is hostile")
        
        # Add strategy input
        if strategy_input:
            reasoning.append(f"Strategies: {strategy_input}")
        
        # Add portfolio input
        if portfolio_input:
            reasoning.append(f"Portfolio: {portfolio_input}")
            if "low" in portfolio_input.lower() or "moderate" in portfolio_input.lower():
                supporting.append("Portfolio has capacity")
            else:
                opposing.append("Portfolio is near capacity")
        
        # Add tactical input
        if tactical_input:
            reasoning.append(f"Tactical: {tactical_input}")
            if "high" in tactical_input.lower() or "strong" in tactical_input.lower():
                supporting.append("Strong tactical opportunities")
        
        # Add risk input
        if risk_input:
            reasoning.append(f"Risk: {risk_input}")
            if "normal" in risk_input.lower():
                supporting.append("Risk is manageable")
            else:
                opposing.append("Risk is elevated")
        
        # Handle conflicts
        if conflicts:
            reasoning.append(f"Conflicts resolved: {resolution}")
        
        decision.reasoning = reasoning
        decision.supporting_factors = supporting
        decision.opposing_factors = opposing
        
        logger.info(f"Fused decision: {action} (conviction: {conviction:.0%})")
        
        return decision
    
    def _evaluate_regime_input(self, snapshot: SystemStateSnapshot) -> str:
        """Evaluate regime engine input."""
        
        regime = snapshot.current_regime
        
        if not regime:
            return "Unknown regime"
        
        favorable_regimes = ["RISK_ON_TREND", "RISK_ON_MOMENTUM"]
        neutral_regimes = ["NEUTRAL_MIXED", "RANGE_COMPRESSION", "MEAN_REVERSION"]
        hostile_regimes = ["RISK_OFF_DEFENSIVE", "VOLATILITY_STRESS", "LIQUIDITY_DISLOCATION"]
        
        if regime.value in favorable_regimes:
            return f"Favorable: {regime.value}"
        elif regime.value in neutral_regimes:
            return f"Neutral: {regime.value}"
        elif regime.value in hostile_regimes:
            return f"Hostile: {regime.value}"
        
        return f"Unknown: {regime.value}"
    
    def _evaluate_strategy_input(self, snapshot: SystemStateSnapshot) -> str:
        """Evaluate strategy lab input."""
        
        active = snapshot.active_strategies
        approved = snapshot.approved_strategies
        restricted = snapshot.restricted_strategies
        
        if len(active) >= 3 and len(approved) >= 2:
            return f"Strong - {len(active)} active, {len(approved)} approved"
        elif len(active) >= 1:
            return f"Moderate - {len(active)} active"
        else:
            return "Weak - No active strategies"
    
    def _evaluate_portfolio_input(self, snapshot: SystemStateSnapshot) -> str:
        """Evaluate portfolio engine input."""
        
        if not snapshot.portfolio:
            return "No portfolio data"
        
        exposure = snapshot.portfolio.total_exposure
        cash = snapshot.portfolio.cash_position
        drawdown = snapshot.portfolio.drawdown_percent
        
        if exposure > 0.8:
            return f"High exposure ({exposure:.0%}), low capacity"
        elif exposure > 0.6:
            return f"Moderate exposure ({exposure:.0%})"
        else:
            return f"Low exposure ({exposure:.0%}), capacity available"
    
    def _evaluate_tactical_input(self, snapshot: SystemStateSnapshot) -> str:
        """Evaluate tactical opportunities input."""
        
        opportunities = snapshot.tactical_opportunities
        
        if not opportunities:
            return "No tactical opportunities"
        
        # Find highest confidence
        best = max(opportunities, key=lambda x: x.confidence)
        
        if best.confidence >= 0.7:
            return f"Strong - {len(opportunities)} opportunities, best confidence {best.confidence:.0%}"
        elif best.confidence >= 0.5:
            return f"Moderate - {len(opportunities)} opportunities"
        else:
            return f"Weak - Low confidence ({best.confidence:.0%})"
    
    def _evaluate_risk_input(self, snapshot: SystemStateSnapshot) -> str:
        """Evaluate risk controller input."""
        
        if snapshot.drawdown_breach:
            return "EMERGENCY - Drawdown breach"
        
        if snapshot.risk_status == "emergency":
            return "Emergency risk status"
        elif snapshot.risk_status == "elevated":
            return "Elevated risk"
        else:
            return "Normal risk"
    
    def _identify_conflicts(
        self,
        regime_input: str,
        strategy_input: str,
        portfolio_input: str,
        tactical_input: str,
        risk_input: str,
    ) -> List[str]:
        """Identify conflicts between engine outputs."""
        
        conflicts = []
        
        # Regime vs Tactical
        if "Hostile" in regime_input and "Strong" in tactical_input:
            conflicts.append("Regime hostile but strong tactical opportunities")
        
        # Regime vs Strategy
        if "Hostile" in regime_input and "Strong" in strategy_input:
            conflicts.append("Regime hostile but strong strategy signals")
        
        # Portfolio vs Tactical
        if "High exposure" in portfolio_input and "Strong" in tactical_input:
            conflicts.append("High portfolio exposure but strong tactical opportunities")
        
        # Risk vs Everything
        if "EMERGENCY" in risk_input or "Emergency" in risk_input:
            conflicts.append("Risk emergency overrides all other signals")
        
        return conflicts
    
    def _resolve_conflicts(
        self,
        conflicts: List[str],
        regime_input: str,
        strategy_input: str,
        portfolio_input: str,
        tactical_input: str,
        risk_input: str,
        snapshot: SystemStateSnapshot,
    ) -> tuple:
        """Resolve conflicts and determine final action."""
        
        # Emergency always wins
        if "EMERGENCY" in risk_input or "Emergency" in risk_input:
            return ("Risk emergency override", "SUPPRESS", 0.95)
        
        # Hostile regime overrides positive tactical/strategy signals
        if "Hostile" in regime_input:
            # Check if portfolio is already low - might allow selective
            if snapshot.portfolio and snapshot.portfolio.total_exposure < 0.3:
                return ("Hostile regime but low exposure - selective", "HOLD", 0.7)
            return ("Hostile regime override", "WITHDRAW", 0.85)
        
        # High exposure with strong tactical
        if "High exposure" in portfolio_input and "Strong" in tactical_input:
            return ("High exposure limit - hold new positions", "HOLD", 0.75)
        
        # Favorable conditions
        if "Favorable" in regime_input or "Strong" in strategy_input:
            if "Moderate" in portfolio_input or "Low" in portfolio_input:
                return ("Favorable conditions - deploy", "DEPLOY", 0.75)
            else:
                return ("Favorable but fully invested", "HOLD", 0.6)
        
        # Neutral conditions
        if "Neutral" in regime_input or "Moderate" in tactical_input:
            return ("Neutral conditions - hold", "HOLD", 0.55)
        
        # Default to hold
        return ("Default hold", "HOLD", 0.5)


_decision_fusion_engine: Optional[DecisionFusionEngine] = None


def get_decision_fusion_engine() -> DecisionFusionEngine:
    """Get the decision fusion engine."""
    global _decision_fusion_engine
    
    if _decision_fusion_engine is None:
        _decision_fusion_engine = DecisionFusionEngine()
    
    return _decision_fusion_engine
