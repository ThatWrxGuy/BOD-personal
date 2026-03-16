"""0DTE Opportunity Engine - BB-FIN-019"""

from typing import Optional, Dict, List
import logging
import uuid
import random

from app.finance.spy_0dte_agent.spy_0dte_models import (
    SPY0DTEOpportunity,
    TradeDirection,
    OpportunityConfidence,
    RiskLevel,
    DeltaVelocitySignal,
    GammaLevelMap,
    StrikeRecommendation,
)

logger = logging.getLogger(__name__)


class OpportunityEngine:
    """Combines all signals to detect 0DTE opportunities."""

    def __init__(self):
        pass

    def detect_opportunity(
        self,
        delta_signal: Optional[DeltaVelocitySignal],
        gamma_levels: GammaLevelMap,
        strike_recommendation: StrikeRecommendation,
        intraday_state,
        market_regime: Optional[str] = None,
        options_environment: Optional[str] = None,
    ) -> SPY0DTEOpportunity:
        """Detect and evaluate 0DTE opportunity."""
        
        # Start with direction from delta signal
        if delta_signal:
            direction = delta_signal.direction
            confidence = delta_signal.confidence
        else:
            # Use gamma/structure for direction
            direction = self._infer_direction_from_gamma(gamma_levels)
            confidence = OpportunityConfidence.MEDIUM
        
        # Skip if avoid
        if direction == TradeDirection.AVOID:
            return self._create_avoid_opportunity(
                "No clear directional signal", intraday_state
            )
        
        # Check if environment is suitable
        suitability = self._check_environment_suitability(
            market_regime, options_environment, intraday_state
        )
        
        if not suitability["suitable"]:
            return self._create_avoid_opportunity(
                suitability["reason"], intraday_state
            )
        
        # Assess risk
        risk_level, risk_reason = self._assess_risk(
            delta_signal, gamma_levels, intraday_state
        )
        
        # Determine entry window
        entry_window = self._determine_entry_window(
            delta_signal, gamma_levels, intraday_state
        )
        
        # Calculate metrics
        max_loss_pct = 100.0  # 0DTE can lose everything
        reward_risk = self._calculate_reward_risk(
            strike_recommendation, direction, intraday_state
        )
        
        # Build reasoning
        reasoning = self._build_reasoning(
            delta_signal, gamma_levels, intraday_state,
            market_regime, options_environment
        )
        
        # Warning
        warning = self._generate_warning(risk_level, intraday_state)
        
        return SPY0DTEOpportunity(
            opportunity_id=str(uuid.uuid4())[:8],
            direction=direction,
            confidence=confidence,
            recommended_strike=strike_recommendation.strike,
            strike_distance_pct=strike_recommendation.distance_from_spot_pct,
            entry_window=entry_window,
            risk_level=risk_level,
            max_loss_pct=max_loss_pct,
            reward_risk_ratio=reward_risk,
            target_profit_pct=reward_risk * max_loss_pct if reward_risk else None,
            delta_signal=delta_signal,
            gamma_levels=gamma_levels,
            strike_recommendation=strike_recommendation,
            reasoning=reasoning,
            warning=warning,
        )

    def _infer_direction_from_gamma(self, gamma_levels: GammaLevelMap) -> TradeDirection:
        """Infer direction from gamma levels."""
        # If net gamma is positive and price near support, expect up
        if gamma_levels.net_gamma > 0 and gamma_levels.gamma_zone == "acceleration":
            # Check price position
            if gamma_levels.pin_level:
                # Would need current price - simplified here
                return TradeDirection.CALL
        
        return TradeDirection.AVOID

    def _check_environment_suitability(
        self,
        market_regime: Optional[str],
        options_environment: Optional[str],
        intraday_state,
    ) -> Dict:
        """Check if environment is suitable for 0DTE."""
        reasons = []
        
        # Check market regime
        if market_regime:
            if "VOLATILITY_STRESS" in market_regime:
                return {"suitable": False, "reason": "Volatility stress regime"}
            if "RISK_OFF" in market_regime:
                reasons.append("Risk-off regime - reduced suitability")
        
        # Check options environment
        if options_environment:
            if "high" in options_environment.lower():
                reasons.append("High IV environment")
        
        # Check intraday phase
        if intraday_state.phase.value == "closing":
            return {"suitable": False, "reason": "Near market close - time decay too high"}
        
        # Check expansion probability
        if intraday_state.expansion_probability < 0.3:
            reasons.append("Low volatility expansion probability")
        
        # Final verdict
        if len(reasons) >= 2:
            return {"suitable": False, "reason": "; ".join(reasons)}
        
        return {"suitable": True, "reason": reasons[0] if reasons else "Environment suitable"}

    def _assess_risk(
        self,
        delta_signal: Optional[DeltaVelocitySignal],
        gamma_levels: GammaLevelMap,
        intraday_state,
    ) -> tuple:
        """Assess risk level."""
        risk_score = 0
        
        # 0DTE is inherently high risk
        risk_score += 2
        
        # Low confidence
        if delta_signal and delta_signal.confidence == OpportunityConfidence.LOW:
            risk_score += 2
        
        # Weak signal
        if delta_signal and not delta_signal.confirmed:
            risk_score += 1
        
        # Poor follow-through probability
        if delta_signal and delta_signal.follow_through_probability < 0.5:
            risk_score += 2
        
        # High IV percentile
        if intraday_state.iv_percentile > 0.8:
            risk_score += 1
        
        # Low expansion probability
        if intraday_state.expansion_probability < 0.4:
            risk_score += 1
        
        # Gamma zone
        if gamma_levels.gamma_zone == "deceleration":
            risk_score += 1
        
        # Determine level
        if risk_score >= 7:
            return RiskLevel.EXTREME, "Multiple high-risk factors"
        elif risk_score >= 5:
            return RiskLevel.HIGH, "Elevated risk factors"
        elif risk_score >= 3:
            return RiskLevel.MODERATE, "Moderate risk"
        else:
            return RiskLevel.LOW, "Relatively low risk for 0DTE"

    def _determine_entry_window(
        self,
        delta_signal: Optional[DeltaVelocitySignal],
        gamma_levels: GammaLevelMap,
        intraday_state,
    ) -> str:
        """Determine optimal entry window."""
        # Strong momentum burst = enter now
        if delta_signal and delta_signal.signal_type.value == "momentum_burst":
            if delta_signal.confirmed and delta_signal.follow_through_probability > 0.7:
                return "now"
        
        # Breakout displacement = wait for confirmation
        if delta_signal and delta_signal.signal_type.value == "breakout_displacement":
            if not delta_signal.confirmed:
                return "wait_for_breakout"
        
        # High compression = wait for expansion
        if intraday_state.compression_ratio and intraday_state.compression_ratio < 0.6:
            return "wait_for_pullback"
        
        # Default
        return "now"

    def _calculate_reward_risk(
        self,
        strike: StrikeRecommendation,
        direction: TradeDirection,
        intraday_state,
    ) -> Optional[float]:
        """Calculate reward-to-risk ratio."""
        # Estimate based on gamma levels and volatility
        base_ratio = 2.0
        
        # Adjust for gamma zone
        # In acceleration zone, higher reward potential
        base_ratio *= 1.2
        
        # Adjust for expansion probability
        base_ratio *= (0.5 + intraday_state.expansion_probability)
        
        return round(base_ratio, 2)

    def _build_reasoning(
        self,
        delta_signal: Optional[DeltaVelocitySignal],
        gamma_levels: GammaLevelMap,
        intraday_state,
        market_regime: Optional[str],
        options_environment: Optional[str],
    ) -> List[str]:
        """Build reasoning list."""
        reasoning = []
        
        # Delta signal
        if delta_signal:
            reasoning.append(f"Delta signal: {delta_signal.signal_type.value}")
            reasoning.append(f"Velocity: {delta_signal.velocity_score:.2f}")
        
        # Gamma
        reasoning.append(f"Gamma zone: {gamma_levels.gamma_zone}")
        if gamma_levels.pin_level:
            reasoning.append(f"Pin level: {gamma_levels.pin_level:.2f}")
        
        # Intraday
        reasoning.append(f"Phase: {intraday_state.phase.value}")
        reasoning.append(f"Expansion prob: {intraday_state.expansion_probability:.0%}")
        
        # Context
        if market_regime:
            reasoning.append(f"Regime: {market_regime}")
        if options_environment:
            reasoning.append(f"Options env: {options_environment}")
        
        return reasoning

    def _generate_warning(
        self,
        risk_level: RiskLevel,
        intraday_state,
    ) -> Optional[str]:
        """Generate risk warning."""
        warnings = []
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.EXTREME]:
            warnings.append(f"Risk level: {risk_level.value.upper()}")
        
        if intraday_state.phase.value == "closing":
            warnings.append("Near close - theta decay extreme")
        
        if intraday_state.iv_percentile > 0.8:
            warnings.append("High IV - expensive premiums")
        
        if intraday_state.compression_ratio and intraday_state.compression_ratio < 0.5:
            warnings.append("High compression - volatile expansion likely")
        
        if warnings:
            return " | ".join(warnings)
        
        return None

    def _create_avoid_opportunity(
        self,
        reason: str,
        intraday_state,
    ) -> SPY0DTEOpportunity:
        """Create an avoid opportunity."""
        return SPY0DTEOpportunity(
            opportunity_id=str(uuid.uuid4())[:8],
            direction=TradeDirection.AVOID,
            confidence=OpportunityConfidence.LOW,
            recommended_strike=0,
            strike_distance_pct=0,
            entry_window="none",
            risk_level=RiskLevel.EXTREME,
            max_loss_pct=100,
            reasoning=[reason],
            warning="No suitable 0DTE opportunity",
        )


# Singleton
_opportunity_engine: Optional[OpportunityEngine] = None


def get_opportunity_engine() -> OpportunityEngine:
    """Get the singleton OpportunityEngine instance."""
    global _opportunity_engine
    if _opportunity_engine is None:
        _opportunity_engine = OpportunityEngine()
    return _opportunity_engine
