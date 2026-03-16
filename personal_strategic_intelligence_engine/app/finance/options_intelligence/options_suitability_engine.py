"""Options Suitability Engine - BB-FIN-017"""

from typing import Optional, List
import logging

from app.finance.options_intelligence.options_models import (
    IVRegime,
    OptionsSuitability,
    OptionsSuitabilityScore,
    LiquidityRating,
)
from app.finance.options_intelligence.iv_regime_engine import get_iv_regime_engine
from app.finance.options_intelligence.options_liquidity_engine import get_options_liquidity_engine
from app.finance.options_intelligence.term_structure_engine import get_term_structure_engine
from app.finance.options_intelligence.gamma_exposure_engine import get_gamma_exposure_engine

logger = logging.getLogger(__name__)


class OptionsSuitabilityEngine:
    """Determine options suitability for securities."""

    def __init__(self):
        self._iv_engine = get_iv_regime_engine()
        self._liquidity_engine = get_options_liquidity_engine()
        self._term_engine = get_term_structure_engine()
        self._gamma_engine = get_gamma_exposure_engine()

    def evaluate_suitability(
        self,
        symbol: str,
        sector: Optional[str] = None,
        market_regime: Optional[str] = None,
        security_opportunity: Optional[str] = None,
        current_price: float = 100.0,
    ) -> OptionsSuitabilityScore:
        """Evaluate options suitability for a security."""
        
        # Get IV analysis
        iv_profile = self._iv_engine.analyze_iv_environment(symbol)
        
        # Get liquidity analysis
        liquidity_profile = self._liquidity_engine.analyze_liquidity(symbol)
        
        # Get term structure
        term_profile = self._term_engine.analyze_term_structure(symbol)
        
        # Get dealer positioning
        dealer_profile = self._gamma_engine.estimate_dealer_positioning(symbol, current_price)
        
        # Calculate component scores
        iv_score = self._score_iv_component(iv_profile.iv_regime)
        liquidity_score = self._score_liquidity_component(liquidity_profile)
        structure_score = self._score_structure_component(term_profile, dealer_profile)
        dealer_score = self._score_dealer_component(dealer_profile)
        
        # Calculate overall score with market regime weighting
        overall_score = self._calculate_overall_score(
            iv_score,
            liquidity_score,
            structure_score,
            dealer_score,
            market_regime,
        )
        
        # Determine suitability
        suitability = self._determine_suitability(overall_score, iv_profile.iv_regime, market_regime)
        
        # Generate recommendation
        recommendation, rationale = self._generate_recommendation(
            symbol,
            iv_profile.iv_regime,
            liquidity_profile.liquidity_rating,
            market_regime,
            security_opportunity,
        )
        
        return OptionsSuitabilityScore(
            symbol=symbol,
            sector=sector,
            iv_score=iv_score,
            iv_regime=iv_profile.iv_regime,
            liquidity_score=liquidity_score,
            liquidity_rating=liquidity_profile.liquidity_rating,
            structure_score=structure_score,
            dealer_score=dealer_score,
            overall_score=overall_score,
            suitability=suitability,
            recommendation=recommendation,
            rationale=rationale,
        )

    def _score_iv_component(self, regime: IVRegime) -> float:
        """Score IV regime component (0-1, higher = better for options)."""
        scores = {
            IVRegime.COMPRESSED: 0.9,  # Low IV = cheap premium = good for buying
            IVRegime.NORMAL: 0.6,
            IVRegime.ELEVATED: 0.4,    # High IV = expensive
            IVRegime.EXTREME: 0.2,     # Very high IV = avoid
        }
        return scores.get(regime, 0.5)

    def _score_liquidity_component(self, liquidity) -> float:
        """Score liquidity component (0-1)."""
        ratings = {
            LiquidityRating.HIGH: 1.0,
            LiquidityRating.MEDIUM: 0.7,
            LiquidityRating.LOW: 0.4,
            LiquidityRating.VERY_LOW: 0.1,
        }
        return ratings.get(liquidity.liquidity_rating, 0.5)

    def _score_structure_component(self, term_profile, dealer_profile) -> float:
        """Score term structure and dealer positioning component."""
        score = 0.5
        
        # Positive: flat or slight contango
        from app.finance.options_intelligence.options_models import TermStructureShape
        if term_profile.shape in [TermStructureShape.FLAT, TermStructureShape.CONTANGO]:
            score += 0.2
        
        # Negative: inversion
        if term_profile.shape == TermStructureShape.INVERSION:
            score -= 0.2
        
        # Dealer: neutral is best
        if dealer_profile.hedging_pressure == "neutral":
            score += 0.1
        elif dealer_profile.hedging_pressure in ["long", "short"]:
            score -= 0.1
        
        # Squeeze risk
        score -= dealer_profile.gamma_squeeze_risk * 0.2
        
        return max(0.0, min(1.0, score))

    def _score_dealer_component(self, dealer_profile) -> float:
        """Score dealer positioning component."""
        score = 0.5
        
        # Low pinning risk is good
        score += (1 - dealer_profile.pinning_risk) * 0.2
        
        # Low squeeze potential is good
        score += (1 - dealer_profile.gamma_squeeze_risk) * 0.2
        
        # Neutral hedging is best
        if dealer_profile.hedging_pressure == "neutral":
            score += 0.1
        
        return max(0.0, min(1.0, score))

    def _calculate_overall_score(
        self,
        iv_score: float,
        liquidity_score: float,
        structure_score: float,
        dealer_score: float,
        market_regime: Optional[str],
    ) -> float:
        """Calculate overall suitability score."""
        # Base weights
        weights = {
            "iv": 0.30,
            "liquidity": 0.25,
            "structure": 0.25,
            "dealer": 0.20,
        }
        
        # Apply market regime modifiers
        regime_multiplier = 1.0
        if market_regime:
            if market_regime.startswith("RISK_ON"):
                regime_multiplier = 1.1  # Slightly favor options in risk-on
            elif market_regime.startswith("RISK_OFF"):
                regime_multiplier = 0.7  # Reduce options in risk-off
            elif market_regime == "VOLATILITY_STRESS":
                regime_multiplier = 0.5  # Reduce options in high vol
        
        overall = (
            iv_score * weights["iv"] +
            liquidity_score * weights["liquidity"] +
            structure_score * weights["structure"] +
            dealer_score * weights["dealer"]
        ) * regime_multiplier
        
        return max(0.0, min(1.0, overall))

    def _determine_suitability(
        self,
        score: float,
        regime: IVRegime,
        market_regime: Optional[str],
    ) -> OptionsSuitability:
        """Determine suitability classification."""
        # Hard overrides
        if regime == IVRegime.EXTREME:
            return OptionsSuitability.DISCOURAGED
        
        if market_regime == "VOLATILITY_STRESS":
            return OptionsSuitability.DISCOURAGED
        
        # Score-based
        if score > 0.7:
            return OptionsSuitability.FAVORABLE
        elif score > 0.4:
            return OptionsSuitability.NEUTRAL
        else:
            return OptionsSuitability.DISCOURAGED

    def _generate_recommendation(
        self,
        symbol: str,
        regime: IVRegime,
        liquidity: LiquidityRating,
        market_regime: Optional[str],
        security_opportunity: Optional[str],
    ) -> tuple:
        """Generate recommendation and rationale."""
        rationale = []
        
        # IV rationale
        if regime == IVRegime.COMPRESSED:
            rationale.append("IV compressed - cheap premium")
        elif regime == IVRegime.EXTREME:
            rationale.append("IV elevated - expensive premium")
        
        # Liquidity rationale
        if liquidity == LiquidityRating.HIGH:
            rationale.append("High options liquidity")
        elif liquidity == LiquidityRating.VERY_LOW:
            rationale.append("Low options liquidity - caution")
        
        # Market regime rationale
        if market_regime:
            if market_regime.startswith("RISK_ON"):
                rationale.append("Risk-on environment favors options")
            elif market_regime.startswith("RISK_OFF"):
                rationale.append("Risk-off - reduce options exposure")
        
        # Security opportunity
        if security_opportunity:
            rationale.append(f"Security opportunity: {security_opportunity}")
        
        # Generate recommendation text
        if regime == IVRegime.COMPRESSED and liquidity in [LiquidityRating.HIGH, LiquidityRating.MEDIUM]:
            recommendation = f"Favorable for {symbol} - IV compressed, good liquidity. Consider long volatility."
        elif regime == IVRegime.EXTREME:
            recommendation = f"Discouraged for {symbol} - IV extreme. Wait for normalization."
        elif liquidity == LiquidityRating.VERY_LOW:
            recommendation = f"Discouraged for {symbol} - insufficient options liquidity."
        elif regime == IVRegime.ELEVATED:
            recommendation = f"Neutral for {symbol} - elevated IV. Credit strategies favorable."
        else:
            recommendation = f"Neutral suitability for {symbol}."
        
        return recommendation, rationale


# Singleton
_suitability_engine: Optional[OptionsSuitabilityEngine] = None


def get_options_suitability_engine() -> OptionsSuitabilityEngine:
    """Get the singleton OptionsSuitabilityEngine instance."""
    global _suitability_engine
    if _suitability_engine is None:
        _suitability_engine = OptionsSuitabilityEngine()
    return _suitability_engine
