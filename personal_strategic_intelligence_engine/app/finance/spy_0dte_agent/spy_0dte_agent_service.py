"""SPY 0DTE Agent Service - BB-FIN-019"""

from typing import Optional, List, Dict
import logging

from app.finance.spy_0dte_agent.spy_0dte_models import (
    SPY0DTEReport,
    SPY0DTEOpportunity,
    TradeDirection,
    StrikeRecommendation,
    GammaLevelMap,
)
from app.finance.spy_0dte_agent.delta_velocity_engine import get_delta_velocity_engine
from app.finance.spy_0dte_agent.gamma_level_engine import get_gamma_level_engine
from app.finance.spy_0dte_agent.strike_selection_engine import get_strike_selection_engine
from app.finance.spy_0dte_agent.intraday_flow_engine import get_intraday_flow_engine
from app.finance.spy_0dte_agent.opportunity_engine import get_opportunity_engine

logger = logging.getLogger(__name__)


class SPY0DTEAgentService:
    """Orchestrates the complete SPY 0DTE intelligence pipeline."""

    def __init__(self):
        self._delta_engine = get_delta_velocity_engine()
        self._gamma_engine = get_gamma_level_engine()
        self._strike_engine = get_strike_selection_engine()
        self._flow_engine = get_intraday_flow_engine()
        self._opportunity_engine = get_opportunity_engine()

    def analyze(
        self,
        market_regime: Optional[str] = None,
        options_environment: Optional[str] = None,
    ) -> SPY0DTEReport:
        """Run complete SPY 0DTE analysis."""
        
        # Get intraday state
        intraday = self._flow_engine.analyze()
        current_price = intraday.session_high  # Use high as proxy for current
        
        # Get gamma levels
        gamma_levels = self._gamma_engine.get_gamma_levels(current_price)
        gamma_dict = {
            "gamma_support": gamma_levels.gamma_support,
            "gamma_resistance": gamma_levels.gamma_resistance,
            "gamma_flip": gamma_levels.gamma_flip,
            "net_gamma": gamma_levels.net_gamma,
        }
        
        # Get delta velocity signal
        delta_signal = self._delta_engine.analyze(gamma_levels=gamma_dict)
        
        # Determine direction
        if delta_signal:
            direction = delta_signal.direction
        else:
            direction = self._infer_direction(intraday, gamma_levels)
        
        # Get strike recommendation
        strike = self._strike_engine.select_strike(
            current_price, direction, gamma_dict
        )
        
        # Get additional strikes for comparison
        all_strikes = self._get_alternative_strikes(current_price, direction, gamma_dict)
        
        # Detect opportunity
        opportunity = self._opportunity_engine.detect_opportunity(
            delta_signal=delta_signal,
            gamma_levels=gamma_levels,
            strike_recommendation=strike,
            intraday_state=intraday,
            market_regime=market_regime,
            options_environment=options_environment,
        )
        
        # Determine suitability
        suitable = self._assess_suitability(opportunity, intraday, market_regime)
        
        return SPY0DTEReport(
            current_price=current_price,
            market_regime=market_regime,
            options_environment=options_environment,
            intraday=intraday,
            gamma_levels=gamma_levels,
            delta_signal=delta_signal,
            opportunity=opportunity,
            recommended_strikes=all_strikes,
            suitable_for_0dte=suitable["suitable"],
            primary_risk=suitable["risk"],
        )

    def _infer_direction(self, intraday, gamma_levels: GammaLevelMap) -> TradeDirection:
        """Infer direction from intraday and gamma."""
        # Use phase and gamma to determine direction
        if intraday.phase.value == "trending":
            # Would need actual price direction
            return TradeDirection.CALL
        
        if gamma_levels.net_gamma > 0:
            return TradeDirection.CALL
        
        return TradeDirection.PUT

    def _get_alternative_strikes(
        self,
        current_price: float,
        direction: TradeDirection,
        gamma_levels: Dict,
    ) -> List[StrikeRecommendation]:
        """Get alternative strike recommendations."""
        strikes = []
        
        # Get 3 strikes
        for _ in range(3):
            strike = self._strike_engine.select_strike(current_price, direction, gamma_levels)
            strikes.append(strike)
        
        return strikes[:3]

    def _assess_suitability(
        self,
        opportunity: SPY0DTEOpportunity,
        intraday,
        market_regime: Optional[str],
    ) -> Dict:
        """Assess overall suitability for 0DTE."""
        reasons = []
        
        # Direction check
        if opportunity.direction == TradeDirection.AVOID:
            return {"suitable": False, "risk": "No clear opportunity"}
        
        # Risk check
        if opportunity.risk_level.value == "extreme":
            reasons.append("Extreme risk level")
        
        # Phase check
        if intraday.phase.value == "closing":
            reasons.append("Near market close")
        
        # Regime check
        if market_regime and "RISK_OFF" in market_regime:
            reasons.append("Risk-off regime")
        
        # IV check
        if intraday.iv_percentile > 0.9:
            reasons.append("Very high IV")
        
        suitable = len(reasons) == 0
        
        return {
            "suitable": suitable,
            "risk": reasons[0] if reasons else None,
        }

    def get_opportunities(self) -> Dict:
        """Get current opportunities summary."""
        report = self.analyze()
        
        return {
            "opportunity": report.opportunity.model_dump(),
            "suitable": report.suitable_for_0dte,
            "risk": report.primary_risk,
        }

    def get_gamma_levels(self) -> GammaLevelMap:
        """Get current gamma levels."""
        return self._gamma_engine.get_gamma_levels()

    def get_strike_recommendations(
        self,
        direction: str = "call",
    ) -> List[StrikeRecommendation]:
        """Get strike recommendations."""
        # Use a default price
        current_price = 500.0
        
        dir_enum = TradeDirection.CALL if direction.lower() == "call" else TradeDirection.PUT
        
        gamma = self._gamma_engine.get_gamma_levels(current_price)
        gamma_dict = {
            "gamma_support": gamma.gamma_support,
            "gamma_resistance": gamma.gamma_resistance,
            "gamma_flip": gamma.gamma_flip,
            "net_gamma": gamma.net_gamma,
        }
        
        return self._get_alternative_strikes(current_price, dir_enum, gamma_dict)

    def get_intraday_structure(self) -> Dict:
        """Get intraday market structure analysis."""
        # Get intraday state
        intraday = self._flow_engine.analyze()
        
        # Get flow signals
        flow_signals = self._flow_engine.detect_flow_signals(
            self._flow_engine._generate_demo_candles()
        )
        
        # Get delta signal
        gamma = self._gamma_engine.get_gamma_levels()
        gamma_dict = {
            "gamma_support": gamma.gamma_support,
            "gamma_resistance": gamma.gamma_resistance,
            "gamma_flip": gamma.gamma_flip,
            "net_gamma": gamma.net_gamma,
        }
        delta_signal = self._delta_engine.analyze(gamma_levels=gamma_dict)
        
        return {
            "symbol": "SPY",
            "phase": intraday.phase.value,
            "current_iv": intraday.current_iv,
            "iv_percentile": intraday.iv_percentile,
            "session_high": intraday.session_high,
            "session_low": intraday.session_low,
            "range_pct": intraday.range_pct,
            "compression_ratio": intraday.compression_ratio,
            "expansion_probability": intraday.expansion_probability,
            "vwap": intraday.vwap,
            "vwap_distance_pct": intraday.vwap_distance_pct,
            "flow_signals": flow_signals,
            "delta_signal": {
                "type": delta_signal.signal_type.value if delta_signal else None,
                "direction": delta_signal.direction.value if delta_signal else None,
                "confirmed": delta_signal.confirmed if delta_signal else None,
            } if delta_signal else None,
        }


# Singleton
_spy_0dte_service: Optional[SPY0DTEAgentService] = None


def get_spy_0dte_agent_service() -> SPY0DTEAgentService:
    """Get the singleton SPY0DTEAgentService instance."""
    global _spy_0dte_service
    if _spy_0dte_service is None:
        _spy_0dte_service = SPY0DTEAgentService()
    return _spy_0dte_service
