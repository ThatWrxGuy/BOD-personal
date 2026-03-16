"""Trend Engine - BB-FIN-014"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

from app.finance.market_intelligence.market_intelligence_models import (
    AssetSignal,
    CrossAssetSnapshot,
    TrendDirection,
    SignalScore,
    ConfidenceLevel,
)

logger = logging.getLogger(__name__)


class TrendEngine:
    """Analyzes trend direction and persistence across asset classes."""

    # Thresholds for trend classification
    STRONG_UP_THRESHOLD = 0.05  # >5% indicates strong uptrend
    MODERATE_UP_THRESHOLD = 0.02  # >2% indicates moderate uptrend
    MODERATE_DOWN_THRESHOLD = -0.02  # <-2% indicates moderate downtrend
    STRONG_DOWN_THRESHOLD = -0.05  # <-5% indicates strong downtrend

    def __init__(self):
        self._prior_trends: Dict[str, TrendDirection] = {}

    def analyze_trend(self, signal: AssetSignal) -> TrendDirection:
        """Analyze trend direction for a single asset."""
        if signal.change_pct is None:
            return TrendDirection.SIDEWAYS

        change = signal.change_pct / 100  # Convert to decimal

        if change >= self.STRONG_UP_THRESHOLD:
            return TrendDirection.STRONG_UP
        elif change >= self.MODERATE_UP_THRESHOLD:
            return TrendDirection.MODERATE_UP
        elif change <= self.STRONG_DOWN_THRESHOLD:
            return TrendDirection.STRONG_DOWN
        elif change <= self.MODERATE_DOWN_THRESHOLD:
            return TrendDirection.MODERATE_DOWN
        else:
            return TrendDirection.SIDEWAYS

    def calculate_trend_strength(
        self,
        current_signal: AssetSignal,
        prior_signals: List[AssetSignal],
    ) -> float:
        """Calculate trend strength from multiple timeframes."""
        if not prior_signals:
            return 0.0

        # Use change_pct as proxy for trend
        changes = [s.change_pct for s in prior_signals if s.change_pct is not None]
        if not changes:
            return 0.0

        # Average change
        avg_change = sum(changes) / len(changes)

        # Consistency (what % of periods are positive)
        positive_count = sum(1 for c in changes if c > 0)
        consistency = positive_count / len(changes)

        # Combine into strength score (-1 to 1)
        strength = (avg_change / 10) * 0.7 + (consistency - 0.5) * 0.3

        return max(-1.0, min(1.0, strength))

    def detect_trend_exhaustion(
        self,
        current_signal: AssetSignal,
        prior_changes: List[float],
    ) -> Tuple[bool, str]:
        """Detect potential trend exhaustion signals."""
        if len(prior_changes) < 5:
            return False, ""

        recent = prior_changes[-3:]
        prior = prior_changes[:-3]

        # Check for weakening momentum
        if all(c > 0 for c in prior) and all(c < prior[-1] for c in recent):
            return True, "Uptrend losing momentum - gains diminishing"

        if all(c < 0 for c in prior) and all(c > prior[-1] for c in recent):
            return True, "Downtrend losing momentum - losses diminishing"

        # Check for extreme move (potential reversal)
        if current_signal.change_pct and abs(current_signal.change_pct) > 8:
            return True, f"Extreme move: {current_signal.change_pct:.1f}% - potential reversal"

        return False, ""

    def analyze_cross_asset_trends(
        self,
        snapshot: CrossAssetSnapshot,
    ) -> SignalScore:
        """Analyze trends across all asset classes."""
        all_trends = []
        contributing_factors = []

        # Analyze equities
        equity_trends = []
        for eq in snapshot.equities:
            trend = self.analyze_trend(eq)
            equity_trends.append(trend)
            eq.trend = trend
            if trend in [TrendDirection.STRONG_UP, TrendDirection.MODERATE_UP]:
                contributing_factors.append(f"{eq.symbol}: {trend.value}")

        # Analyze bonds
        bond_trends = []
        for bond in snapshot.bonds:
            trend = self.analyze_trend(bond)
            bond_trends.append(trend)
            bond.trend = trend

        # Analyze commodities
        commodity_trends = []
        for cmd in snapshot.commodities:
            trend = self.analyze_trend(cmd)
            commodity_trends.append(trend)
            cmd.trend = trend

        # Aggregate trend direction
        all_trends.extend(equity_trends)
        all_trends.extend(bond_trends)
        all_trends.extend(commodity_trends)

        # Calculate overall trend score
        positive = sum(
            1 for t in all_trends
            if t in [TrendDirection.STRONG_UP, TrendDirection.MODERATE_UP]
        )
        negative = sum(
            1 for t in all_trends
            if t in [TrendDirection.STRONG_DOWN, TrendDirection.MODERATE_DOWN]
        )

        if len(all_trends) == 0:
            score = 0.0
            direction = "neutral"
        elif positive > negative:
            score = min(1.0, (positive - negative) / len(all_trends) * 2)
            direction = "bullish"
        elif negative > positive:
            score = max(-1.0, -(negative - positive) / len(all_trends) * 2)
            direction = "bearish"
        else:
            score = 0.0
            direction = "neutral"

        # Determine confidence
        total = len(all_trends)
        if total >= 10:
            confidence = ConfidenceLevel.HIGH
        elif total >= 5:
            confidence = ConfidenceLevel.MODERATE
        else:
            confidence = ConfidenceLevel.LOW

        # Add key factors
        if equity_trends:
            major_trends = [t for t in equity_trends if t != TrendDirection.SIDEWAYS]
            if major_trends:
                contributing_factors.insert(
                    0, f"Major equity trend: {major_trends[0].value}"
                )

        return SignalScore(
            family="trend",
            score=score,
            direction=direction,
            confidence=confidence,
            contributing_factors=contributing_factors[:10],
            timestamp=datetime.utcnow(),
        )

    def get_leadership(self, snapshot: CrossAssetSnapshot) -> Dict[str, str]:
        """Determine which asset class is leading."""
        leaders = {}

        # Calculate average change by asset class
        def avg_change(signals):
            changes = [s.change_pct for s in signals if s.change_pct is not None]
            return sum(changes) / len(changes) if changes else 0.0

        if snapshot.equities:
            leaders["equities"] = avg_change(snapshot.equities)
        if snapshot.bonds:
            leaders["bonds"] = avg_change(snapshot.bonds)
        if snapshot.commodities:
            leaders["commodities"] = avg_change(snapshot.commodities)
        if snapshot.crypto:
            leaders["crypto"] = avg_change(snapshot.crypto)

        # Convert to leadership string
        result = {}
        for asset, change in leaders.items():
            if change > 2:
                result[asset] = "strong_leader"
            elif change > 0:
                result[asset] = "leader"
            elif change < -2:
                result[asset] = "laggard"
            else:
                result[asset] = "neutral"

        return result


# Singleton
_trend_engine: Optional[TrendEngine] = None


def get_trend_engine() -> TrendEngine:
    """Get the singleton TrendEngine instance."""
    global _trend_engine
    if _trend_engine is None:
        _trend_engine = TrendEngine()
    return _trend_engine
