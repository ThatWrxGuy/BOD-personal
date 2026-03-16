"""Capital Deployment Coordinator - BB-CORE-021

Converts fused decisions into capital posture recommendations.
"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.core.orchestration.orchestration_models import (
    SystemStateSnapshot,
    ActivationDecision,
    FusedDecision,
    CapitalPosture,
    CapitalPositionRecommendation,
)

logger = logging.get_logger(__name__)


class CapitalDeploymentCoordinator:
    """Determines capital deployment posture based on system state."""
    
    def __init__(self):
        self._posture_thresholds = self._initialize_thresholds()
    
    def _initialize_thresholds(self) -> Dict:
        """Initialize capital posture thresholds."""
        return {
            "defensive": {
                "max_exposure": 0.30,
                "max_tactical": 0.01,
                "max_strategy": 0.20,
            },
            "selective": {
                "max_exposure": 0.50,
                "max_tactical": 0.03,
                "max_strategy": 0.35,
            },
            "neutral": {
                "max_exposure": 0.70,
                "max_tactical": 0.05,
                "max_strategy": 0.50,
            },
            "offensive": {
                "max_exposure": 0.90,
                "max_tactical": 0.08,
                "max_strategy": 0.70,
            },
            "restricted": {
                "max_exposure": 0.10,
                "max_tactical": 0.00,
                "max_strategy": 0.05,
            },
        }
    
    def determine_posture(
        self,
        snapshot: SystemStateSnapshot,
        activation: ActivationDecision,
        fused_decision: FusedDecision,
    ) -> CapitalPositionRecommendation:
        """Determine capital deployment posture."""
        
        reasoning = []
        key_factors = {}
        
        # Start with neutral, then adjust
        posture = CapitalPosture.NEUTRAL
        confidence = 0.5
        
        # === Factor 1: System Status ===
        if snapshot.system_status.value == "emergency":
            posture = CapitalPosture.RESTRICTED
            reasoning.append("Emergency status: Capital restricted")
            key_factors["system_status"] = "emergency"
            confidence = 0.95
        elif snapshot.system_status.value == "restricted":
            posture = CapitalPosture.DEFENSIVE
            reasoning.append("Restricted status: Defensive posture")
            key_factors["system_status"] = "restricted"
            confidence = 0.80
        
        # === Factor 2: Risk Status ===
        if snapshot.drawdown_breach:
            posture = CapitalPosture.RESTRICTED
            reasoning.append("Drawdown breach: Maximum protection")
            key_factors["drawdown"] = "breach"
            confidence = 0.95
        elif snapshot.risk_status == "elevated":
            posture = CapitalPosture.DEFENSIVE
            reasoning.append("Elevated risk: Defensive")
            key_factors["risk"] = "elevated"
            confidence = max(confidence, 0.75)
        
        # === Factor 3: Regime ===
        regime = snapshot.current_regime
        if regime:
            regime_value = regime.value
            if regime_value in ["RISK_ON_TREND", "RISK_ON_MOMENTUM"]:
                if posture not in [CapitalPosture.RESTRICTED, CapitalPosture.DEFENSIVE]:
                    posture = CapitalPosture.OFFENSIVE
                    reasoning.append(f"Favorable regime: {regime_value}")
                    key_factors["regime"] = "favorable"
                    confidence = max(confidence, 0.70)
            elif regime_value in ["RISK_OFF_DEFENSIVE", "VOLATILITY_STRESS", "LIQUIDITY_DISLOCATION"]:
                posture = CapitalPosture.DEFENSIVE
                reasoning.append(f"Hostile regime: {regime_value}")
                key_factors["regime"] = "hostile"
                confidence = max(confidence, 0.80)
            elif regime_value in ["NEUTRAL_MIXED", "RANGE_COMPRESSION"]:
                if posture not in [CapitalPosture.RESTRICTED, CapitalPosture.DEFENSIVE]:
                    posture = CapitalPosture.SELECTIVE
                    reasoning.append(f"Neutral regime: {regime_value}")
                    key_factors["regime"] = "neutral"
                    confidence = max(confidence, 0.60)
        
        # === Factor 4: Portfolio Exposure ===
        if snapshot.portfolio:
            exposure = snapshot.portfolio.total_exposure
            if exposure > 0.80:
                posture = CapitalPosture.DEFENSIVE
                reasoning.append(f"High exposure: {exposure:.0%}")
                key_factors["exposure"] = "high"
                confidence = max(confidence, 0.75)
            elif exposure < 0.30 and posture != CapitalPosture.RESTRICTED:
                if posture == CapitalPosture.OFFENSIVE:
                    pass  # Keep offensive
                else:
                    posture = CapitalPosture.SELECTIVE
                    reasoning.append(f"Low exposure: {exposure:.0%} - room to deploy")
                    key_factors["exposure"] = "low"
        
        # === Factor 5: Fused Decision ===
        action = fused_decision.action
        if action == "SUPPRESS" or action == "WITHDRAW":
            posture = CapitalPosture.RESTRICTED if posture == CapitalPosture.RESTRICTED else CapitalPosture.DEFENSIVE
            reasoning.append(f"Fused decision: {action}")
            key_factors["decision"] = action.lower()
        elif action == "DEPLOY" and posture != CapitalPosture.RESTRICTED:
            if posture == CapitalPosture.DEFENSIVE:
                posture = CapitalPosture.SELECTIVE
                reasoning.append("Fused decision: Upgrade to selective")
                key_factors["decision"] = "deploy"
        
        # Get thresholds for posture
        thresholds = self._posture_thresholds.get(posture.value, self._posture_thresholds["neutral"])
        
        # Build recommendation
        recommendation = CapitalPositionRecommendation(
            posture=posture,
            confidence=confidence,
            max_tactical_allocation=thresholds["max_tactical"],
            max_strategy_allocation=thresholds["max_strategy"],
            new_capital_available=(posture not in [CapitalPosture.RESTRICTED, CapitalPosture.DEFENSIVE]),
            reasoning=reasoning,
            key_factors=key_factors,
        )
        
        # Set specific allocations based on posture
        if posture == CapitalPosture.DEFENSIVE:
            recommendation.investment_allocation = "limited"
            recommendation.tactical_allocation = "restricted"
            recommendation.income_allocation = "allowed"
            recommendation.leverage_allocation = "prohibited"
        elif posture == CapitalPosture.SELECTIVE:
            recommendation.investment_allocation = "allowed"
            recommendation.tactical_allocation = "limited"
            recommendation.income_allocation = "allowed"
            recommendation.leverage_allocation = "restricted"
        elif posture == CapitalPosture.OFFENSIVE:
            recommendation.investment_allocation = "active"
            recommendation.tactical_allocation = "allowed"
            recommendation.income_allocation = "allowed"
            recommendation.leverage_allocation = "limited"
        elif posture == CapitalPosture.RESTRICTED:
            recommendation.investment_allocation = "prohibited"
            recommendation.tactical_allocation = "prohibited"
            recommendation.income_allocation = "review"
            recommendation.leverage_allocation = "prohibited"
        
        logger.info(f"Capital posture: {posture.value} (confidence: {confidence:.0%})")
        
        return recommendation
    
    def get_posture_description(self, posture: CapitalPosture) -> str:
        """Get human-readable description of posture."""
        
        descriptions = {
            CapitalPosture.DEFENSIVE: "Preserve capital - minimize new deployments",
            CapitalPosture.SELECTIVE: "Deploy only to high-conviction ideas",
            CapitalPosture.NEUTRAL: "Balanced allocation - no strong bias",
            CapitalPosture.OFFENSIVE: "Aggressive deployment - favorable conditions",
            CapitalPosture.RESTRICTED: "No new capital deployment - review only",
        }
        
        return descriptions.get(posture, "Unknown posture")


_capital_deployment_coordinator: Optional[CapitalDeploymentCoordinator] = None


def get_capital_deployment_coordinator() -> CapitalDeploymentCoordinator:
    """Get the capital deployment coordinator."""
    global _capital_deployment_coordinator
    
    if _capital_deployment_coordinator is None:
        _capital_deployment_coordinator = CapitalDeploymentCoordinator()
    
    return _capital_deployment_coordinator
