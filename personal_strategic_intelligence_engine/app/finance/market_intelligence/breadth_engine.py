"""Breadth Engine - BB-FIN-014"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

from app.finance.market_intelligence.market_intelligence_models import (
    AssetSignal,
    CrossAssetSnapshot,
    BreadthProfile,
    BreadthState,
    SignalScore,
    ConfidenceLevel,
)

logger = logging.getLogger(__name__)


class BreadthEngine:
    """Analyzes market breadth and participation."""

    # Breadth thresholds
    STRONG_BREADTH_RATIO = 0.65  # 65%+ advancing = strong
    MODERATE_BREADTH_RATIO = 0.55  # 55%+ = moderate
    NARROW_LEAD_RATIO = 0.50  # <50% but market up = narrow

    def __init__(self):
        self._prior_breadth: Optional[float] = None

    def calculate_breadth_ratio(
        self,
        advancing: int,
        declining: int,
        total: int,
    ) -> float:
        """Calculate advance/decline ratio."""
        if total == 0:
            return 0.5
        return advancing / total

    def determine_breadth_state(
        self,
        breadth_ratio: float,
        market_direction: str,  # "up", "down", "neutral"
    ) -> BreadthState:
        """Determine breadth state based on ratio and market direction."""
        if market_direction == "up":
            if breadth_ratio >= self.STRONG_BREADTH_RATIO:
                return BreadthState.STRONG_BREADTH
            elif breadth_ratio >= self.MODERATE_BREADTH_RATIO:
                return BreadthState.MODERATE_BREADTH
            elif breadth_ratio >= self.NARROW_LEAD_RATIO:
                return BreadthState.NARROW_LEAD
            else:
                return BreadthState.WEAK_BREADTH
        elif market_direction == "down":
            if breadth_ratio <= (1 - self.STRONG_BREADTH_RATIO):
                return BreadthState.STRONG_BREADTH  # Strong breadth in down = many declining
            elif breadth_ratio <= (1 - self.MODERATE_BREADTH_RATIO):
                return BreadthState.MODERATE_BREADTH
            else:
                return BreadthState.WEAK_BREADTH
        else:
            return BreadthState.MODERATE_BREADTH

    def calculate_leadership_concentration(
        self,
        sector_changes: Dict[str, float],
    ) -> float:
        """Calculate how concentrated leadership is (0-1 scale)."""
        if not sector_changes:
            return 0.0

        changes = list(sector_changes.values())
        if not changes:
            return 0.0

        # Simple concentration: std deviation of returns
        mean = sum(changes) / len(changes)
        variance = sum((c - mean) ** 2 for c in changes) / len(changes)
        std = variance ** 0.5

        # Higher std = more concentration
        # Normalize: std of 5% = max concentration
        concentration = min(1.0, std / 5.0)
        return concentration

    def analyze_sector_participation(
        self,
        sectors: List[AssetSignal],
    ) -> Dict[str, float]:
        """Analyze sector participation."""
        participation = {}
        changes = {}

        for sector in sectors:
            if sector.change_pct is not None:
                changes[sector.symbol] = sector.change_pct
                # Positive change = participating
                participation[sector.symbol] = 1.0 if sector.change_pct > 0 else 0.0

        return participation

    def analyze_breadth_from_sectors(
        self,
        snapshot: CrossAssetSnapshot,
    ) -> BreadthProfile:
        """Analyze breadth using sector data as proxy."""
        if not snapshot.sectors:
            return BreadthProfile(
                state=BreadthState.MODERATE_BREADTH,
                sector_participation={},
                leadership_concentration=0.0,
            )

        # Calculate participation
        sector_participation = self.analyze_sector_participation(snapshot.sectors)
        
        # Calculate changes
        sector_changes = {}
        for sector in snapshot.sectors:
            if sector.change_pct is not None:
                sector_changes[sector.symbol] = sector.change_pct

        # Determine market direction
        if not sector_changes:
            return BreadthProfile(
                state=BreadthState.MODERATE_BREADTH,
                sector_participation={},
                leadership_concentration=0.0,
            )
        avg_change = sum(sector_changes.values()) / len(sector_changes)
        market_direction = "up" if avg_change > 0.5 else ("down" if avg_change < -0.5 else "neutral")

        # Calculate breadth ratio (as proxy)
        advancing = sum(1 for c in sector_changes.values() if c > 0)
        total = len(sector_changes)
        breadth_ratio = self.calculate_breadth_ratio(advancing, total - advancing, total)

        # Determine state
        state = self.determine_breadth_state(breadth_ratio, market_direction)

        # Calculate concentration
        concentration = self.calculate_leadership_concentration(sector_changes)

        # Determine advancing/declining counts (as proxy)
        advancing_stocks = advancing
        declining_stocks = total - advancing

        return BreadthProfile(
            state=state,
            advance_decline_ratio=breadth_ratio,
            sector_participation=sector_participation,
            leadership_concentration=concentration,
            advancing_stocks=advancing_stocks,
            declining_stocks=declining_stocks,
            total_stocks=total,
        )

    def generate_breadth_score(
        self,
        snapshot: CrossAssetSnapshot,
    ) -> SignalScore:
        """Generate breadth signal score."""
        profile = self.analyze_breadth_from_sectors(snapshot)

        # Convert state to score
        state_scores = {
            BreadthState.STRONG_BREADTH: 1.0,
            BreadthState.MODERATE_BREADTH: 0.5,
            BreadthState.NARROW_LEAD: 0.2,
            BreadthState.WEAK_BREADTH: -0.5,
        }

        score = state_scores.get(profile.state, 0.0)

        # Adjust for concentration
        if profile.leadership_concentration > 0.7:
            score *= 0.8  # Reduce score if too concentrated

        # Determine confidence
        if len(snapshot.sectors) >= 8:
            confidence = ConfidenceLevel.HIGH
        elif len(snapshot.sectors) >= 4:
            confidence = ConfidenceLevel.MODERATE
        else:
            confidence = ConfidenceLevel.LOW

        contributing_factors = [
            f"Breadth state: {profile.state.value}",
            f"Participation: {sum(profile.sector_participation.values())}/{len(profile.sector_participation)} sectors",
            f"Concentration: {profile.leadership_concentration:.2f}",
        ]

        return SignalScore(
            family="breadth",
            score=score,
            direction="positive" if score > 0.2 else ("negative" if score < -0.2 else "neutral"),
            confidence=confidence,
            contributing_factors=contributing_factors,
            timestamp=datetime.utcnow(),
        )


# Singleton
_breadth_engine: Optional[BreadthEngine] = None


def get_breadth_engine() -> BreadthEngine:
    """Get the singleton BreadthEngine instance."""
    global _breadth_engine
    if _breadth_engine is None:
        _breadth_engine = BreadthEngine()
    return _breadth_engine
