"""Activation Policy Engine - BB-CORE-021

Determines which subsystems are allowed to activate under current conditions.
"""

from datetime import datetime
from typing import Dict, List
import logging

from app.core.orchestration.orchestration_models import (
    SystemStateSnapshot,
    ActivationDecision,
    ActivationStatus,
    RegimeType,
)

logger = logging.getLogger(__name__)


class ActivationPolicyEngine:
    """Determines which engines and subsystems should be active."""
    
    def __init__(self):
        self._policy_rules = self._initialize_rules()
    
    def _initialize_rules(self) -> Dict:
        """Initialize activation policy rules."""
        return {
            # Regime-based rules
            "regime_rules": {
                RegimeType.RISK_ON_TREND: {
                    "allow_tactical": True,
                    "allow_aggressive": True,
                    "allow_momentum": True,
                },
                RegimeType.RISK_ON_MOMENTUM: {
                    "allow_tactical": True,
                    "allow_aggressive": True,
                    "allow_momentum": True,
                },
                RegimeType.NEUTRAL_MIXED: {
                    "allow_tactical": False,
                    "allow_aggressive": False,
                    "allow_momentum": False,
                },
                RegimeType.ROTATION_TRANSITION: {
                    "allow_tactical": False,
                    "allow_aggressive": False,
                    "allow_momentum": False,
                },
                RegimeType.RISK_OFF_DEFENSIVE: {
                    "allow_tactical": False,
                    "allow_aggressive": False,
                    "allow_momentum": False,
                },
                RegimeType.VOLATILITY_STRESS: {
                    "allow_tactical": False,
                    "allow_aggressive": False,
                    "allow_momentum": False,
                },
                RegimeType.LIQUIDITY_DISLOCATION: {
                    "allow_tactical": False,
                    "allow_aggressive": False,
                    "allow_momentum": False,
                },
                RegimeType.RANGE_COMPRESSION: {
                    "allow_tactical": False,
                    "allow_aggressive": False,
                    "allow_momentum": False,
                },
                RegimeType.MEAN_REVERSION: {
                    "allow_tactical": True,
                    "allow_aggressive": False,
                    "allow_momentum": False,
                },
                RegimeType.MACRO_EVENT_UNCERTAINTY: {
                    "allow_tactical": False,
                    "allow_aggressive": False,
                    "allow_momentum": False,
                },
            },
        }
    
    def determine_activation(
        self,
        snapshot: SystemStateSnapshot,
    ) -> ActivationDecision:
        """Determine which engines should be active based on current state."""
        
        decision = ActivationDecision()
        engines = {}
        reasoning = []
        
        # Get regime rules
        regime = snapshot.current_regime or RegimeType.NEUTRAL_MIXED
        regime_rules = self._policy_rules["regime_rules"].get(regime, {})
        
        # Determine regime factor
        regime_factor = f"Regime={regime.value}"
        decision.regime_factor = regime_factor
        reasoning.append(f"Current regime: {regime.value}")
        
        # === Market Regime Engine ===
        engines["market_regime"] = ActivationStatus.ACTIVE
        reasoning.append("Market Regime Engine: Always active")
        
        # === Strategy Lab ===
        if regime_rules.get("allow_momentum", False):
            engines["strategy_lab"] = ActivationStatus.ACTIVE
            reasoning.append("Strategy Lab: Allowed in current regime")
        else:
            engines["strategy_lab"] = ActivationStatus.RESTRICTED
            reasoning.append("Strategy Lab: Restricted in current regime")
        
        # === Security Selection ===
        if regime_rules.get("allow_aggressive", False):
            engines["security_selection"] = ActivationStatus.ACTIVE
            reasoning.append("Security Selection: Full activation")
        else:
            engines["security_selection"] = ActivationStatus.ACTIVE
            reasoning.append("Security Selection: Conservative mode")
        
        # === SPY 0DTE Tactical Agent ===
        if snapshot.risk_status == "emergency" or snapshot.drawdown_breach:
            engines["spy_0dte"] = ActivationStatus.SUPPRESSED
            engines["tactical"] = ActivationStatus.SUPPRESSED
            decision.risk_factor = "Emergency drawdown"
            reasoning.append("SPY 0DTE: SUPPRESSED - Emergency drawdown")
        elif regime_rules.get("allow_tactical", False):
            engines["spy_0dte"] = ActivationStatus.ACTIVE
            engines["tactical"] = ActivationStatus.ACTIVE
            reasoning.append("SPY 0DTE: Active - Favorable regime")
        else:
            engines["spy_0dte"] = ActivationStatus.SUPPRESSED
            engines["tactical"] = ActivationStatus.SUPPRESSED
            reasoning.append("SPY 0DTE: Suppressed - Hostile regime")
        
        # === Portfolio Engine ===
        engines["portfolio"] = ActivationStatus.ACTIVE
        reasoning.append("Portfolio Engine: Always active")
        
        # === Risk Controller ===
        if snapshot.risk_status == "elevated":
            engines["risk_controller"] = ActivationStatus.RESTRICTED
            decision.risk_factor = "Elevated risk"
            reasoning.append("Risk Controller: Elevated mode")
        else:
            engines["risk_controller"] = ActivationStatus.ACTIVE
            reasoning.append("Risk Controller: Normal mode")
        
        # === External Intelligence ===
        engines["external_intelligence"] = ActivationStatus.ACTIVE
        reasoning.append("External Intelligence: Active")
        
        # Check exposure factor
        if snapshot.portfolio:
            exposure = snapshot.portfolio.total_exposure
            if exposure > 0.8:
                decision.exposure_factor = "High exposure"
                reasoning.append(f"Exposure factor: High ({exposure:.0%})")
            elif exposure > 0.6:
                decision.exposure_factor = "Moderate exposure"
                reasoning.append(f"Exposure factor: Moderate ({exposure:.0%})")
        
        decision.engines = engines
        decision.reasoning = reasoning
        
        logger.info(f"Activation decision: {sum(1 for s in engines.values() if s == ActivationStatus.ACTIVE)} active engines")
        
        return decision
    
    def get_allowed_activities(
        self,
        activation: ActivationDecision,
    ) -> Dict[str, bool]:
        """Get dictionary of allowed activities."""
        
        allowed = {}
        
        for engine, status in activation.engines.items():
            allowed[engine] = (status == ActivationStatus.ACTIVE)
        
        return allowed


_activation_policy_engine: ActivationPolicyEngine = None


def get_activation_policy_engine() -> ActivationPolicyEngine:
    """Get the activation policy engine."""
    global _activation_policy_engine
    
    if _activation_policy_engine is None:
        _activation_policy_engine = ActivationPolicyEngine()
    
    return _activation_policy_engine
