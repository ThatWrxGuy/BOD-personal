"""Liquidity Stress Engine - BB-FIN-014"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.finance.market_intelligence.market_intelligence_models import (
    CrossAssetSnapshot,
    LiquidityProfile,
    LiquidityState,
    SignalScore,
    ConfidenceLevel,
)

logger = logging.getLogger(__name__)


class LiquidityStressEngine:
    """Analyzes liquidity conditions and stress."""

    # Stress thresholds
    STRESS_VIX_THRESHOLD = 30
    RAPID_DECLINE_THRESHOLD = -5  # %

    def __init__(self):
        self._prior_liquidity_state: Optional[LiquidityState] = None

    def analyze_liquidity(
        self,
        snapshot: CrossAssetSnapshot,
    ) -> LiquidityProfile:
        """Analyze liquidity from market snapshot."""
        signals = []
        stress_score = 0.0

        # VIX-based stress
        if snapshot.vix:
            if snapshot.vix > self.STRESS_VIX_THRESHOLD:
                stress_score += 0.6
                signals.append(f"High VIX ({snapshot.vix:.1f}) indicates stress")

        # Check for rapid decline (liquidity event)
        for eq in snapshot.equities:
            if eq.change_pct and eq.change_pct < self.RAPID_DECLINE_THRESHOLD:
                stress_score += 0.3
                signals.append(f"{eq.symbol} down {eq.change_pct:.1f}%")
                break

        # Credit spread widening (if available)
        if snapshot.credit_spreads:
            # Simplified: just note presence
            signals.append(f"Credit spreads: {snapshot.credit_spreads}")

        # Crypto as liquidity proxy
        if snapshot.crypto:
            crypto_changes = [c.change_pct for c in snapshot.crypto if c.change_pct is not None]
            if crypto_changes:
                avg_crypto = sum(crypto_changes) / len(crypto_changes)
                if avg_crypto < -10:
                    stress_score += 0.4
                    signals.append("Crypto significant decline - liquidity concern")

        # Bond market as liquidity indicator
        bond_declines = [b.change_pct for b in snapshot.bonds if b.change_pct and b.change_pct < -2]
        if bond_declines:
            stress_score += 0.3
            signals.append(f"Bond pressure: {len(bond_declines)} bonds down >2%")

        # Determine state
        if stress_score >= 0.7:
            state = LiquidityState.STRESSED
        elif stress_score >= 0.4:
            state = LiquidityState.TIGHT
        elif stress_score >= 0.1:
            state = LiquidityState.NORMAL
        else:
            state = LiquidityState.ABUNDANT

        # Invert for score (positive = good liquidity)
        liquidity_score = 1.0 - stress_score

        return LiquidityProfile(
            state=state,
            liquidity_score=liquidity_score,
            liquidity_signals=signals[:10],
        )

    def generate_liquidity_score(
        self,
        snapshot: CrossAssetSnapshot,
    ) -> SignalScore:
        """Generate liquidity signal score."""
        profile = self.analyze_liquidity(snapshot)

        # Score directly from liquidity state
        state_scores = {
            LiquidityState.ABUNDANT: 1.0,
            LiquidityState.NORMAL: 0.5,
            LiquidityState.TIGHT: -0.3,
            LiquidityState.STRESSED: -0.8,
        }

        score = state_scores.get(profile.state, 0.0)

        # Adjust for signals
        if len(profile.liquidity_signals) > 3:
            score -= 0.1

        # Clamp
        score = max(-1.0, min(1.0, score))

        # Determine confidence
        confidence = ConfidenceLevel.MODERATE if profile.liquidity_signals else ConfidenceLevel.LOW

        direction = "positive" if score > 0.2 else ("negative" if score < -0.2 else "neutral")

        return SignalScore(
            family="liquidity",
            score=score,
            direction=direction,
            confidence=confidence,
            contributing_factors=profile.liquidity_signals[:5],
            timestamp=datetime.utcnow(),
        )


# Singleton
_liquidity_engine: Optional[LiquidityStressEngine] = None


def get_liquidity_stress_engine() -> LiquidityStressEngine:
    """Get the singleton LiquidityStressEngine instance."""
    global _liquidity_engine
    if _liquidity_engine is None:
        _liquidity_engine = LiquidityStressEngine()
    return _liquidity_engine
