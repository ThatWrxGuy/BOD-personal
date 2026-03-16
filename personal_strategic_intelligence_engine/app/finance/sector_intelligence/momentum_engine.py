"""Momentum Engine - BB-FIN-015"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.finance.sector_intelligence.sector_models import (
    SectorProfile,
    MomentumProfile,
    MomentumPhase,
)

logger = logging.getLogger(__name__)


class MomentumEngine:
    """Analyzes momentum persistence and phase."""

    # Thresholds
    ACCELERATION_THRESHOLD = 0.15  # 15% acceleration
    EXHAUSTION_THRESHOLD = 0.08   # 8% exhaustion indicator

    def __init__(self):
        self._prior_momentum: Dict[str, float] = {}

    def analyze_momentum(
        self,
        sector: SectorProfile,
        prior_changes: Optional[Dict[str, List[float]]] = None,
    ) -> MomentumProfile:
        """Analyze momentum for a sector."""
        
        symbol = sector.symbol
        
        # Use available change data
        changes = []
        if sector.change_1d:
            changes.append(sector.change_1d)
        if sector.change_1w:
            changes.append(sector.change_1w)
        if sector.change_1m:
            changes.append(sector.change_1m)
        
        if not changes:
            return MomentumProfile(
                symbol=symbol,
                phase=MomentumPhase.PERSISTENT,
                acceleration_score=0.0,
                persistence_score=0.5,
                exhaustion_score=0.0,
            )

        # Current momentum (average change)
        current_momentum = sum(changes) / len(changes) if changes else 0.0
        
        # Prior momentum for comparison
        prior_momentum = self._prior_momentum.get(symbol, current_momentum)
        
        # Calculate acceleration
        if prior_momentum != 0:
            acceleration = (current_momentum - prior_momentum) / abs(prior_momentum)
        else:
            acceleration = 0.0
        
        # Determine phase
        if acceleration > self.ACCELERATION_THRESHOLD:
            phase = MomentumPhase.ACCELERATING
        elif acceleration < -self.ACCELERATION_THRESHOLD:
            phase = MomentumPhase.DECELERATING
        elif current_momentum > 5:
            phase = MomentumPhase.PERSISTENT
        elif current_momentum < -3:
            phase = MomentumPhase.REVERSING
        else:
            phase = MomentumPhase.PERSISTENT
        
        # Calculate scores
        acceleration_score = max(-1.0, min(1.0, acceleration * 2))
        
        # Persistence: how long momentum has been positive/negative
        persistence = 0.5
        if prior_momentum > 0 and current_momentum > 0:
            persistence = 0.8
        elif prior_momentum < 0 and current_momentum < 0:
            persistence = 0.8
        persistence_score = persistence
        
        # Exhaustion: check for extreme moves
        exhaustion_score = 0.0
        if abs(current_momentum) > 10:
            exhaustion_score = 0.8
        elif abs(current_momentum) > 7:
            exhaustion_score = 0.5
        
        # Divergence detection (would need price vs momentum in production)
        has_positive_div = False
        has_negative_div = False
        
        # Trend slope
        trend_slope = current_momentum
        
        # Momentum continuation
        continuation = 0.7 if current_momentum > 0 else 0.3
        
        # Store for next iteration
        self._prior_momentum[symbol] = current_momentum
        
        return MomentumProfile(
            symbol=symbol,
            phase=phase,
            acceleration_score=acceleration_score,
            persistence_score=persistence_score,
            exhaustion_score=exhaustion_score,
            has_positive_divergence=has_positive_div,
            has_negative_divergence=has_negative_div,
            trend_slope=trend_slope,
            momentum_continuation_pct=continuation,
        )

    def detect_momentum_shifts(
        self,
        current_profiles: List[SectorProfile],
        prior_profiles: List[SectorProfile],
    ) -> List[str]:
        """Detect significant momentum shifts between periods."""
        
        shifts = []
        
        # Create lookup for prior profiles
        prior_lookup = {p.symbol: p for p in prior_profiles}
        
        for current in current_profiles:
            prior = prior_lookup.get(current.symbol)
            if not prior:
                continue
            
            # Check for acceleration
            curr_mom = current.momentum_score or 0
            prior_mom = prior.momentum_score or 0
            
            if curr_mom > 0.3 and prior_mom < 0.1:
                shifts.append(f"{current.symbol}: momentum accelerating")
            elif curr_mom < -0.3 and prior_mom > 0.1:
                shifts.append(f"{current.symbol}: momentum reversing")
        
        return shifts

    def calculate_momentum_for_sectors(
        self,
        sector_profiles: List[SectorProfile],
    ) -> List[SectorProfile]:
        """Calculate momentum for all sectors."""
        
        for sector in sector_profiles:
            momentum = self.analyze_momentum(sector)
            sector.momentum_phase = momentum.phase
            sector.momentum_score = momentum.trend_slope
        
        return sector_profiles


# Singleton
_momentum_engine: Optional[MomentumEngine] = None


def get_momentum_engine() -> MomentumEngine:
    """Get the singleton MomentumEngine instance."""
    global _momentum_engine
    if _momentum_engine is None:
        _momentum_engine = MomentumEngine()
    return _momentum_engine
