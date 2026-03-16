"""Options Intelligence Service - BB-FIN-017"""

from datetime import datetime
from typing import Optional, List, Dict
import logging

from app.finance.options_intelligence.options_models import (
    IVRegime,
    TermStructureShape,
    SkewType,
    OptionsSuitability,
    OptionsIntelligenceReport,
    OptionsEnvironmentProfile,
)
from app.finance.options_intelligence.iv_regime_engine import get_iv_regime_engine
from app.finance.options_intelligence.term_structure_engine import get_term_structure_engine
from app.finance.options_intelligence.skew_analysis_engine import get_skew_analysis_engine
from app.finance.options_intelligence.gamma_exposure_engine import get_gamma_exposure_engine
from app.finance.options_intelligence.options_liquidity_engine import get_options_liquidity_engine
from app.finance.options_intelligence.options_suitability_engine import get_options_suitability_engine

logger = logging.getLogger(__name__)


class OptionsIntelligenceService:
    """Orchestrates the complete options intelligence pipeline."""

    def __init__(self):
        self._iv_engine = get_iv_regime_engine()
        self._term_engine = get_term_structure_engine()
        self._skew_engine = get_skew_analysis_engine()
        self._gamma_engine = get_gamma_exposure_engine()
        self._liquidity_engine = get_options_liquidity_engine()
        self._suitability_engine = get_options_suitability_engine()
        
        # Context from other modules
        self._market_regime: Optional[str] = None
        self._sector_context: Optional[str] = None

    def set_market_context(
        self,
        regime: Optional[str] = None,
        sector_context: Optional[str] = None,
    ) -> None:
        """Set context from BB-FIN-014 and BB-FIN-015."""
        self._market_regime = regime
        self._sector_context = sector_context

    def analyze(
        self,
        symbol: str,
        current_price: float = 100.0,
        market_regime: Optional[str] = None,
        sector_context: Optional[str] = None,
        security_opportunity: Optional[str] = None,
    ) -> OptionsIntelligenceReport:
        """Run complete options intelligence analysis."""
        
        # Use provided context or stored
        regime = market_regime or self._market_regime
        sector = sector_context or self._sector_context
        
        # Run all analyses
        iv_profile = self._iv_engine.analyze_iv_environment(symbol)
        term_profile = self._term_engine.analyze_term_structure(symbol)
        skew_profile = self._skew_engine.analyze_skew(symbol)
        dealer_profile = self._gamma_engine.estimate_dealer_positioning(symbol, current_price)
        liquidity_profile = self._liquidity_engine.analyze_liquidity(symbol)
        
        # Get suitability
        suitability = self._suitability_engine.evaluate_suitability(
            symbol=symbol,
            sector=sector,
            market_regime=regime,
            security_opportunity=security_opportunity,
            current_price=current_price,
        )
        
        # Generate summary
        summary = self._generate_summary(
            iv_profile.iv_regime,
            term_profile.shape,
            skew_profile.skew_type,
            suitability.suitability,
            regime,
        )
        
        return OptionsIntelligenceReport(
            timestamp=datetime.utcnow(),
            iv_regime=iv_profile.iv_regime,
            iv_percentile=iv_profile.iv_percentile,
            iv_rank=iv_profile.iv_rank,
            term_structure=term_profile.shape,
            skew=skew_profile.skew_type,
            dealer_positioning=dealer_profile,
            liquidity=liquidity_profile,
            suitability=suitability.suitability,
            suitability_score=suitability.overall_score,
            summary=summary,
            market_regime=regime,
            sector_context=sector,
            security_opportunity=security_opportunity,
        )

    def analyze_batch(
        self,
        symbols: List[str],
        prices: Optional[Dict[str, float]] = None,
        market_regime: Optional[str] = None,
        sector_context: Optional[str] = None,
    ) -> List[OptionsIntelligenceReport]:
        """Analyze multiple symbols."""
        reports = []
        
        for symbol in symbols:
            price = prices.get(symbol, 100.0) if prices else 100.0
            report = self.analyze(
                symbol=symbol,
                current_price=price,
                market_regime=market_regime,
                sector_context=sector_context,
            )
            reports.append(report)
        
        return reports

    def get_iv_regime(self, symbol: str) -> Dict:
        """Get IV regime for a symbol."""
        profile = self._iv_engine.analyze_iv_environment(symbol)
        return {
            "symbol": symbol,
            "iv_regime": profile.iv_regime.value,
            "iv_percentile": profile.iv_percentile,
            "iv_rank": profile.iv_rank,
            "current_iv": profile.current_iv,
            "realized_vol": profile.realized_vol,
            "iv_hv_spread": profile.iv_hv_spread,
            "description": self._iv_engine.get_regime_description(profile.iv_regime),
            "recommendation": self._iv_engine.get_regime_recommendation(profile.iv_regime),
        }

    def get_term_structure(self, symbol: str) -> Dict:
        """Get term structure analysis."""
        profile = self._term_engine.analyze_term_structure(symbol)
        return {
            "symbol": symbol,
            "shape": profile.shape.value,
            "front_iv": profile.front_iv,
            "back_iv": profile.back_iv,
            "expiration_ivs": profile.expiration_ivs,
            "signal": profile.signal,
        }

    def get_skew(self, symbol: str) -> Dict:
        """Get skew analysis."""
        profile = self._skew_engine.analyze_skew(symbol)
        return {
            "symbol": symbol,
            "skew_type": profile.skew_type.value,
            "atm_iv": profile.atm_iv,
            "rr_25": profile.rr_25,
            "tail_premium": profile.tail_premium,
            "upside_demand": profile.upside_demand,
            "downside_protection": profile.downside_protection,
            "interpretation": self._skew_engine.get_skew_interpretation(profile),
        }

    def get_gamma(self, symbol: str, current_price: float = 100.0) -> Dict:
        """Get gamma exposure analysis."""
        profile = self._gamma_engine.estimate_dealer_positioning(symbol, current_price)
        gamma_map = self._gamma_engine.create_gamma_map(symbol, current_price)
        
        return {
            "symbol": symbol,
            "net_gamma": profile.net_gamma,
            "gamma_zone": profile.gamma_zone.value,
            "support": profile.gamma_support,
            "resistance": profile.gamma_resistance,
            "pin_level": gamma_map.pin_level,
            "pinning_probability": gamma_map.pinning_probability,
            "squeeze_potential": profile.gamma_squeeze_risk,
            "hedging_pressure": profile.hedging_pressure,
        }

    def get_liquidity(self, symbol: str) -> Dict:
        """Get liquidity analysis."""
        profile = self._liquidity_engine.analyze_liquidity(symbol)
        return {
            "symbol": symbol,
            "avg_volume": profile.avg_daily_volume,
            "total_oi": profile.total_oi,
            "avg_spread": profile.avg_spread,
            "tradability_score": profile.tradability_score,
            "liquidity_rating": profile.liquidity_rating.value,
            "volume_trend": profile.volume_trend,
        }

    def get_suitability(
        self,
        symbol: str,
        sector: Optional[str] = None,
        market_regime: Optional[str] = None,
    ) -> Dict:
        """Get options suitability."""
        score = self._suitability_engine.evaluate_suitability(
            symbol=symbol,
            sector=sector,
            market_regime=market_regime,
        )
        
        return {
            "symbol": symbol,
            "suitability": score.suitability.value,
            "overall_score": score.overall_score,
            "iv_score": score.iv_score,
            "liquidity_score": score.liquidity_score,
            "structure_score": score.structure_score,
            "dealer_score": score.dealer_score,
            "recommendation": score.recommendation,
            "rationale": score.rationale,
        }

    def _generate_summary(
        self,
        iv_regime: IVRegime,
        term_shape: TermStructureShape,
        skew: SkewType,
        suitability: OptionsSuitability,
        market_regime: Optional[str],
    ) -> str:
        """Generate executive summary."""
        parts = []
        
        # IV regime
        parts.append(f"IV: {iv_regime.value}")
        
        # Term structure
        parts.append(f"Term: {term_shape.value}")
        
        # Skew
        parts.append(f"Skew: {skew.value}")
        
        # Overall
        parts.append(f"Suitability: {suitability.value}")
        
        # Market regime context
        if market_regime:
            parts.append(f"Market: {market_regime}")
        
        return " | ".join(parts)

    def get_global_conditions(self) -> Dict:
        """Get global options market conditions (aggregated)."""
        # This would analyze multiple symbols in production
        return {
            "iv_regime": IVRegime.NORMAL.value,
            "term_structure": TermStructureShape.CONTANGO.value,
            "skew": SkewType.PUT_SKEW.value,
            "overall_conditions": "Neutral - standard options environment",
            "recommendation": "Focus on directional strategies in liquid names",
        }


# Singleton
_service: Optional[OptionsIntelligenceService] = None


def get_options_intelligence_service() -> OptionsIntelligenceService:
    """Get the singleton OptionsIntelligenceService instance."""
    global _service
    if _service is None:
        _service = OptionsIntelligenceService()
    return _service
