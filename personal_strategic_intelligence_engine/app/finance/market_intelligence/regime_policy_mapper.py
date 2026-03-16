"""Regime Policy Mapper - BB-FIN-014"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.finance.market_intelligence.market_intelligence_models import (
    RegimeState,
    RegimeType,
    RegimePolicy,
    RiskPosture,
)

logger = logging.getLogger(__name__)


class RegimePolicyMapper:
    """Maps regime classifications to portfolio policy guidance."""

    def __init__(self):
        self._policy_cache: Dict[RegimeType, RegimePolicy] = {}

    def map_regime_to_policy(self, regime: RegimeState) -> RegimePolicy:
        """Map a regime state to policy recommendations."""
        
        # Use cached policy if regime stable
        cache_key = regime.primary_regime
        if cache_key in self._policy_cache:
            cached = self._policy_cache[cache_key]
            # Update timestamp
            cached.timestamp = datetime.utcnow()
            return cached

        # Generate policy based on regime type
        policy = self._generate_policy(regime)
        
        # Cache for future use
        self._policy_cache[cache_key] = policy
        
        return policy

    def _generate_policy(self, regime: RegimeState) -> RegimePolicy:
        """Generate policy for a specific regime."""
        
        regime_type = regime.primary_regime
        
        # Base policy from regime type
        if regime_type == RegimeType.RISK_ON_TREND:
            return self._risk_on_trend_policy(regime)
        elif regime_type == RegimeType.RISK_ON_MOMENTUM:
            return self._risk_on_momentum_policy(regime)
        elif regime_type == RegimeType.NEUTRAL_MIXED:
            return self._neutral_mixed_policy(regime)
        elif regime_type == RegimeType.ROTATION_TRANSITION:
            return self._rotation_policy(regime)
        elif regime_type == RegimeType.RISK_OFF_DEFENSIVE:
            return self._risk_off_policy(regime)
        elif regime_type == RegimeType.VOLATILITY_STRESS:
            return self._volatility_stress_policy(regime)
        elif regime_type == RegimeType.LIQUIDITY_DISLOCATION:
            return self._liquidity_dislocation_policy(regime)
        elif regime_type == RegimeType.RANGE_COMPRESSION:
            return self._range_compression_policy(regime)
        elif regime_type == RegimeType.MEAN_REVERSION:
            return self._mean_reversion_policy(regime)
        elif regime_type == RegimeType.MACRO_EVENT_UNCERTAINTY:
            return self._macro_uncertainty_policy(regime)
        else:
            return self._neutral_mixed_policy(regime)

    def _risk_on_trend_policy(self, regime: RegimeState) -> RegimePolicy:
        """Policy for risk-on trending market."""
        return RegimePolicy(
            timestamp=datetime.utcnow(),
            regime=regime.primary_regime,
            risk_posture=RiskPosture.AGGRESSIVE,
            max_gross_exposure=1.5,
            max_single_position_risk=0.03,
            recommended_net_exposure=0.8,
            cash_preference=0.05,
            hedging_bias="none",
            aggression_level="aggressive",
            position_sizing_multiplier=1.5,
            approved_strategy_classes=[
                "trend_following",
                "momentum",
                "breakout",
                "growth_equity",
            ],
            restricted_strategy_classes=[
                "mean_reversion",
                "volatility_selling",
            ],
            stop_discipline="normal",
            risk_compression_enabled=False,
            governance_notes=[
                "Strong trend confirmed - allow growth exposure",
                "Reduce hedging to maximize trend capture",
            ],
        )

    def _risk_on_momentum_policy(self, regime: RegimeState) -> RegimePolicy:
        """Policy for risk-on momentum market."""
        return RegimePolicy(
            timestamp=datetime.utcnow(),
            regime=regime.primary_regime,
            risk_posture=RiskPosture.GROWTH,
            max_gross_exposure=1.2,
            max_single_position_risk=0.025,
            recommended_net_exposure=0.5,
            cash_preference=0.10,
            hedging_bias="partial",
            aggression_level="moderate",
            position_sizing_multiplier=1.2,
            approved_strategy_classes=[
                "momentum",
                "sector_rotation",
                "growth_equity",
            ],
            restricted_strategy_classes=[
                "volatility_selling",
                "credit_stress",
            ],
            stop_discipline="normal",
            risk_compression_enabled=False,
            governance_notes=[
                "Momentum favorable - maintain growth bias",
                "Partial hedging recommended",
            ],
        )

    def _neutral_mixed_policy(self, regime: RegimeState) -> RegimePolicy:
        """Policy for neutral/mixed market."""
        return RegimePolicy(
            timestamp=datetime.utcnow(),
            regime=regime.primary_regime,
            risk_posture=RiskPosture.NEUTRAL,
            max_gross_exposure=0.8,
            max_single_position_risk=0.02,
            recommended_net_exposure=0.2,
            cash_preference=0.20,
            hedging_bias="partial",
            aggression_level="moderate",
            position_sizing_multiplier=0.8,
            approved_strategy_classes=[
                "mean_reversion",
                "range_trading",
                "quality_factor",
            ],
            restricted_strategy_classes=[
                "momentum",
                "aggressive_growth",
            ],
            stop_discipline="normal",
            risk_compression_enabled=False,
            governance_notes=[
                "Mixed conditions - reduce exposure",
                "Focus on quality and defense",
            ],
        )

    def _rotation_policy(self, regime: RegimeState) -> RegimePolicy:
        """Policy for rotation/transition market."""
        return RegimePolicy(
            timestamp=datetime.utcnow(),
            regime=regime.primary_regime,
            risk_posture=RiskPosture.NEUTRAL,
            max_gross_exposure=0.6,
            max_single_position_risk=0.015,
            recommended_net_exposure=0.0,
            cash_preference=0.30,
            hedging_bias="partial",
            aggression_level="conservative",
            position_sizing_multiplier=0.6,
            approved_strategy_classes=[
                "sector_rotation",
                "defensive_equity",
                "quality_factor",
            ],
            restricted_strategy_classes=[
                "momentum",
                "breakout",
                "aggressive_growth",
            ],
            stop_discipline="tight",
            risk_compression_enabled=True,
            governance_notes=[
                "Market in transition - reduce risk",
                "Watch for new leadership to emerge",
                "Tighten stops",
            ],
        )

    def _risk_off_policy(self, regime: RegimeState) -> RegimePolicy:
        """Policy for risk-off defensive market."""
        return RegimePolicy(
            timestamp=datetime.utcnow(),
            regime=regime.primary_regime,
            risk_posture=RiskPosture.DEFENSIVE,
            max_gross_exposure=0.4,
            max_single_position_risk=0.01,
            recommended_net_exposure=-0.2,
            cash_preference=0.40,
            hedging_bias="full",
            aggression_level="conservative",
            position_sizing_multiplier=0.4,
            approved_strategy_classes=[
                "defensive_equity",
                "short_bonds",
                "put_protection",
            ],
            restricted_strategy_classes=[
                "momentum",
                "growth_equity",
                "breakout",
                "volatility_selling",
            ],
            stop_discipline="tight",
            risk_compression_enabled=True,
            governance_notes=[
                "Risk-off environment - minimize exposure",
                "Full hedging recommended",
                "Prioritize capital preservation",
            ],
        )

    def _volatility_stress_policy(self, regime: RegimeState) -> RegimePolicy:
        """Policy for high volatility stress."""
        return RegimePolicy(
            timestamp=datetime.utcnow(),
            regime=regime.primary_regime,
            risk_posture=RiskPosture.CRISIS,
            max_gross_exposure=0.2,
            max_single_position_risk=0.008,
            recommended_net_exposure=-0.3,
            cash_preference=0.50,
            hedging_bias="full",
            aggression_level="conservative",
            position_sizing_multiplier=0.2,
            approved_strategy_classes=[
                "volatility_hedging",
                "defensive_equity",
                "cash",
            ],
            restricted_strategy_classes=[
                "momentum",
                "growth_equity",
                "breakout",
                "volatility_selling",
                "option_selling",
            ],
            stop_discipline="very_tight",
            risk_compression_enabled=True,
            governance_notes=[
                "Volatility spike - extreme caution",
                "Consider reducing all positions",
                "Volatility hedging only",
            ],
        )

    def _liquidity_dislocation_policy(self, regime: RegimeState) -> RegimePolicy:
        """Policy for liquidity dislocation."""
        return RegimePolicy(
            timestamp=datetime.utcnow(),
            regime=regime.primary_regime,
            risk_posture=RiskPosture.CRISIS,
            max_gross_exposure=0.15,
            max_single_position_risk=0.005,
            recommended_net_exposure=-0.4,
            cash_preference=0.60,
            hedging_bias="full",
            aggression_level="conservative",
            position_sizing_multiplier=0.15,
            approved_strategy_classes=[
                "liquidity_hedging",
                "cash",
                "government_bonds",
            ],
            restricted_strategy_classes=[
                "all_risk_strategies",
                "leverage",
                "illiquid_positions",
            ],
            stop_discipline="very_tight",
            risk_compression_enabled=True,
            governance_notes=[
                "Liquidity crisis - capital preservation priority",
                "No new positions",
                "Government bonds only for safety",
            ],
        )

    def _range_compression_policy(self, regime: RegimeState) -> RegimePolicy:
        """Policy for range compression."""
        return RegimePolicy(
            timestamp=datetime.utcnow(),
            regime=regime.primary_regime,
            risk_posture=RiskPosture.NEUTRAL,
            max_gross_exposure=0.5,
            max_single_position_risk=0.015,
            recommended_net_exposure=0.1,
            cash_preference=0.25,
            hedging_bias="none",
            aggression_level="moderate",
            position_sizing_multiplier=0.5,
            approved_strategy_classes=[
                "range_trading",
                "mean_reversion",
                "option_straddles",
            ],
            restricted_strategy_classes=[
                "breakout",
                "momentum",
            ],
            stop_discipline="normal",
            risk_compression_enabled=False,
            governance_notes=[
                "Low volatility / compression - sell volatility",
                "Range-bound trading favored",
            ],
        )

    def _mean_reversion_policy(self, regime: RegimeState) -> RegimePolicy:
        """Policy for mean reversion environment."""
        return RegimePolicy(
            timestamp=datetime.utcnow(),
            regime=regime.primary_regime,
            risk_posture=RiskPosture.GROWTH,
            max_gross_exposure=0.7,
            max_single_position_risk=0.02,
            recommended_net_exposure=0.3,
            cash_preference=0.15,
            hedging_bias="partial",
            aggression_level="moderate",
            position_sizing_multiplier=0.7,
            approved_strategy_classes=[
                "mean_reversion",
                "contrarian",
                "range_trading",
            ],
            restricted_strategy_classes=[
                "trend_following",
                "momentum",
            ],
            stop_discipline="tight",
            risk_compression_enabled=False,
            governance_notes=[
                "Mean reversion environment detected",
                "Look for oversold opportunities",
            ],
        )

    def _macro_uncertainty_policy(self, regime: RegimeState) -> RegimePolicy:
        """Policy for macro event uncertainty."""
        return RegimePolicy(
            timestamp=datetime.utcnow(),
            regime=regime.primary_regime,
            risk_posture=RiskPosture.DEFENSIVE,
            max_gross_exposure=0.3,
            max_single_position_risk=0.01,
            recommended_net_exposure=-0.1,
            cash_preference=0.45,
            hedging_bias="full",
            aggression_level="conservative",
            position_sizing_multiplier=0.3,
            approved_strategy_classes=[
                "defensive_equity",
                "gold",
                "short_duration_bonds",
            ],
            restricted_strategy_classes=[
                "growth_equity",
                "momentum",
                "emerging_markets",
            ],
            stop_discipline="tight",
            risk_compression_enabled=True,
            governance_notes=[
                "Macro uncertainty elevated",
                "Reduce exposure ahead of events",
                "Hedge for tail risk",
            ],
        )


# Singleton
_policy_mapper: Optional[RegimePolicyMapper] = None


def get_regime_policy_mapper() -> RegimePolicyMapper:
    """Get the singleton RegimePolicyMapper instance."""
    global _policy_mapper
    if _policy_mapper is None:
        _policy_mapper = RegimePolicyMapper()
    return _policy_mapper
