"""Correlation Engine - BB-FIN-014"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.finance.market_intelligence.market_intelligence_models import (
    CrossAssetSnapshot,
    CorrelationProfile,
    SignalScore,
    ConfidenceLevel,
)

logger = logging.getLogger(__name__)


class CorrelationEngine:
    """Analyzes cross-asset correlations and risk concentration."""

    HIGH_CORRELATION_THRESHOLD = 0.7

    def __init__(self):
        self._prior_correlation: Optional[float] = None

    def estimate_equity_bond_correlation(
        self,
        snapshot: CrossAssetSnapshot,
    ) -> float:
        """Estimate equity-bond correlation from price movements."""
        # In production, would use historical data
        # Here, use proxy based on current conditions

        # Get equity and bond changes
        equity_changes = []
        for eq in snapshot.equities:
            if eq.change_pct is not None:
                equity_changes.append(eq.change_pct)

        bond_changes = []
        for bond in snapshot.bonds:
            if bond.change_pct is not None:
                bond_changes.append(bond.change_pct)

        if not equity_changes or not bond_changes:
            return 0.0

        # Simple correlation proxy:
        # If both positive on average = positive correlation
        # If opposite = negative correlation
        avg_equity = sum(equity_changes) / len(equity_changes)
        avg_bond = sum(bond_changes) / len(bond_changes)

        # This is a very rough proxy
        return (avg_equity * avg_bond) / 100  # Normalized

    def estimate_sector_correlation(
        self,
        snapshot: CrossAssetSnapshot,
    ) -> float:
        """Estimate average sector correlation."""
        if not snapshot.sectors:
            return 0.0

        changes = [s.change_pct for s in snapshot.sectors if s.change_pct is not None]
        if len(changes) < 2:
            return 0.0

        # Calculate standard deviation as proxy for correlation
        mean = sum(changes) / len(changes)
        variance = sum((c - mean) ** 2 for c in changes) / len(changes)
        std = variance ** 0.5

        # Higher std = lower correlation (more dispersion)
        # Lower std = higher correlation (moving together)
        # Convert to 0-1 scale where 1 = high correlation
        correlation = max(0, 1 - (std / 5))  # 5% std = max correlation
        return correlation

    def analyze_correlations(
        self,
        snapshot: CrossAssetSnapshot,
    ) -> CorrelationProfile:
        """Analyze correlation profile from snapshot."""
        # Equity-bond correlation
        equity_bond_corr = self.estimate_equity_bond_correlation(snapshot)

        # Sector correlation
        sector_corr = self.estimate_sector_correlation(snapshot)

        # Determine if high correlation environment
        is_high_corr = (
            equity_bond_corr > self.HIGH_CORRELATION_THRESHOLD
            or sector_corr > self.HIGH_CORRELATION_THRESHOLD
        )

        # Determine trend
        correlation_trend = "stable"
        if self._prior_correlation is not None:
            current_avg = (abs(equity_bond_corr) + sector_corr) / 2
            prior = self._prior_correlation
            if current_avg > prior * 1.1:
                correlation_trend = "increasing"
            elif current_avg < prior * 0.9:
                correlation_trend = "decreasing"

        # Store for next iteration
        self._prior_correlation = (abs(equity_bond_corr) + sector_corr) / 2

        # Build signals
        signals = []
        signals.append(f"Equity-bond correlation: {equity_bond_corr:.2f}")
        signals.append(f"Sector correlation: {sector_corr:.2f}")
        if is_high_corr:
            signals.append("High correlation environment detected")
        signals.append(f"Correlation trend: {correlation_trend}")

        return CorrelationProfile(
            equity_bond_correlation=equity_bond_corr,
            sector_correlation_avg=sector_corr,
            is_high_correlation_env=is_high_corr,
            correlation_trend=correlation_trend,
            correlation_signals=signals,
        )

    def generate_correlation_score(
        self,
        snapshot: CrossAssetSnapshot,
    ) -> SignalScore:
        """Generate correlation signal score."""
        profile = self.analyze_correlations(snapshot)

        # High correlations = negative for diversification
        # Low correlations = positive for diversification
        
        # Base score from equity-bond correlation
        if profile.equity_bond_correlation is not None:
            # Negative correlation (typical risk-off) = positive for portfolio
            # But during stress, correlations spike positive
            if profile.equity_bond_correlation < -0.3:
                score = 0.5  # Good diversification
            elif profile.equity_bond_correlation > 0.3:
                score = -0.4  # Poor diversification
            else:
                score = 0.0
        else:
            score = 0.0

        # Adjust for high correlation environment
        if profile.is_high_correlation_env:
            score -= 0.3

        # Adjust for trend
        if profile.correlation_trend == "increasing":
            score -= 0.2  # Correlations rising = bad
        elif profile.correlation_trend == "decreasing":
            score += 0.2  # Correlations falling = good

        # Clamp score
        score = max(-1.0, min(1.0, score))

        # Determine confidence
        if profile.equity_bond_correlation is not None and profile.sector_correlation_avg is not None:
            confidence = ConfidenceLevel.MODERATE
        else:
            confidence = ConfidenceLevel.LOW

        direction = "positive" if score > 0.2 else ("negative" if score < -0.2 else "neutral")

        return SignalScore(
            family="correlation",
            score=score,
            direction=direction,
            confidence=confidence,
            contributing_factors=profile.correlation_signals[:5],
            timestamp=datetime.utcnow(),
        )


# Singleton
_correlation_engine: Optional[CorrelationEngine] = None


def get_correlation_engine() -> CorrelationEngine:
    """Get the singleton CorrelationEngine instance."""
    global _correlation_engine
    if _correlation_engine is None:
        _correlation_engine = CorrelationEngine()
    return _correlation_engine
