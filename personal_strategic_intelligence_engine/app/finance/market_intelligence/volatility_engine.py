"""Volatility Engine - BB-FIN-014"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.finance.market_intelligence.market_intelligence_models import (
    CrossAssetSnapshot,
    VolatilityProfile,
    VolatilityState,
    SignalScore,
    ConfidenceLevel,
)

logger = logging.getLogger(__name__)


class VolatilityEngine:
    """Analyzes volatility conditions and VIX."""

    # VIX thresholds (approximate)
    VIX_COMPRESSED = 12  # Very low volatility
    VIX_NORMAL_LOW = 16  # Normal low
    VIX_NORMAL_HIGH = 22  # Normal high
    VIX_EXPANDING = 28  # Elevated
    VIX_STRESSED = 35  # High stress

    def __init__(self):
        self._prior_vix: Optional[float] = None

    def determine_volatility_state(self, vix: float, prior_vix: Optional[float] = None) -> VolatilityState:
        """Determine volatility state from VIX level and change."""
        state = VolatilityState.NORMAL

        if vix <= self.VIX_COMPRESSED:
            state = VolatilityState.COMPRESSED
        elif vix <= self.VIX_NORMAL_HIGH:
            state = VolatilityState.NORMAL
        elif vix <= self.VIX_EXPANDING:
            state = VolatilityState.EXPANDING
        else:
            state = VolatilityState.STRESSED

        # Check for rapid expansion
        if prior_vix and vix > prior_vix * 1.3:
            state = VolatilityState.EXPANDING
        if prior_vix and vix > prior_vix * 1.5:
            state = VolatilityState.STRESSED

        return state

    def calculate_vix_percentile(self, vix: float) -> float:
        """Calculate approximate VIX percentile (simplified)."""
        # Simple approximation based on historical ranges
        if vix <= 12:
            return 0.05
        elif vix <= 15:
            return 0.15
        elif vix <= 20:
            return 0.35
        elif vix <= 25:
            return 0.55
        elif vix <= 30:
            return 0.75
        elif vix <= 40:
            return 0.90
        else:
            return 0.98

    def analyze_volatility(
        self,
        snapshot: CrossAssetSnapshot,
    ) -> VolatilityProfile:
        """Analyze volatility from market snapshot."""
        vix = snapshot.vix
        prior_vix = self._prior_vix

        if vix is None:
            return VolatilityProfile(
                state=VolatilityState.NORMAL,
                vol_signals=["No VIX data available"],
            )

        state = self.determine_volatility_state(vix, prior_vix)
        percentile = self.calculate_vix_percentile(vix)

        # Track for next iteration
        self._prior_vix = vix

        # Determine term structure (would need VIX futures in production)
        term_structure = "normal"

        # Build signals
        signals = []
        if state == VolatilityState.COMPRESSED:
            signals.append(f"VIX compressed at {vix:.1f}")
        elif state == VolatilityState.EXPANDING:
            signals.append(f"VIX elevated at {vix:.1f}")
        elif state == VolatilityState.STRESSED:
            signals.append(f"VIX stressed at {vix:.1f}")
        else:
            signals.append(f"VIX normal at {vix:.1f}")

        if prior_vix:
            change = ((vix - prior_vix) / prior_vix) * 100
            signals.append(f"VIX change: {change:+.1f}%")

        signals.append(f"VIX percentile: {percentile:.0%}")

        return VolatilityProfile(
            state=state,
            vix_level=vix,
            vix_percentile=percentile,
            term_structure=term_structure,
            vol_signals=signals,
        )

    def generate_volatility_score(
        self,
        snapshot: CrossAssetSnapshot,
    ) -> SignalScore:
        """Generate volatility signal score."""
        profile = self.analyze_volatility(snapshot)

        # Convert state to score
        # Lower VIX = higher score (good for risk-on)
        state_scores = {
            VolatilityState.COMPRESSED: 0.8,  # Low vol = opportunity
            VolatilityState.NORMAL: 0.3,
            VolatilityState.EXPANDING: -0.4,
            VolatilityState.STRESSED: -0.9,
        }

        score = state_scores.get(profile.state, 0.0)

        # Adjust based on VIX level
        if profile.vix_level:
            if profile.vix_level <= 12:
                score = max(score, 0.9)
            elif profile.vix_level >= 35:
                score = min(score, -0.95)

        # Determine confidence
        confidence = ConfidenceLevel.HIGH if profile.vix_level else ConfidenceLevel.LOW

        direction = "positive" if score > 0.2 else ("negative" if score < -0.2 else "neutral")

        return SignalScore(
            family="volatility",
            score=score,
            direction=direction,
            confidence=confidence,
            contributing_factors=profile.vol_signals[:5],
            timestamp=datetime.utcnow(),
        )


# Singleton
_volatility_engine: Optional[VolatilityEngine] = None


def get_volatility_engine() -> VolatilityEngine:
    """Get the singleton VolatilityEngine instance."""
    global _volatility_engine
    if _volatility_engine is None:
        _volatility_engine = VolatilityEngine()
    return _volatility_engine
