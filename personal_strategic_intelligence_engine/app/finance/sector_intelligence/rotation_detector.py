"""Rotation Detector - BB-FIN-015"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

from app.finance.sector_intelligence.sector_models import (
    SectorProfile,
    RotationEvent,
    RotationPhase,
)

logger = logging.getLogger(__name__)


class RotationDetector:
    """Detects sector rotation events."""

    # Detection thresholds
    LEADING_WEAKENING_THRESHOLD = -0.15  # 15% relative weakening
    LAGGARD_STRENGTHENING_THRESHOLD = 0.15  # 15% relative strengthening
    CROSSOVER_THRESHOLD = 0.10  # 10% crossover for rotation

    def __init__(self):
        self._prior_leaders: List[str] = []
        self._rotation_history: List[RotationEvent] = []

    def detect_rotation(
        self,
        current_rankings: List[SectorProfile],
        prior_rankings: List[SectorProfile],
    ) -> Optional[RotationEvent]:
        """Detect rotation between current and prior rankings."""
        
        if not current_rankings or not prior_rankings:
            return None

        # Create lookup for prior rankings
        prior_lookup = {p.symbol: p for p in prior_rankings}
        
        # Get current top 3 and bottom 3
        current_top = current_rankings[:3]
        current_bottom = current_rankings[-3:]
        
        prior_top = prior_rankings[:3]
        prior_bottom = prior_rankings[-3:]
        
        # Check for leader changes
        leader_changes = []
        for sector in current_top:
            if sector.symbol not in [p.symbol for p in prior_top]:
                leader_changes.append((sector.symbol, "entering"))
        
        for sector in prior_top:
            if sector.symbol not in [p.symbol for p in current_top]:
                leader_changes.append((sector.symbol, "exiting"))
        
        # Check for laggard improvements
        laggard_improvements = []
        for sector in current_bottom:
            prior = prior_lookup.get(sector.symbol)
            if prior and prior.rs_rank and sector.rs_rank:
                rank_change = prior.rs_rank - sector.rs_rank  # Positive = improved
                if rank_change >= 2:
                    laggard_improvements.append((sector.symbol, rank_change))
        
        # Determine rotation phase
        phase = RotationPhase.NONE
        strength = 0.0
        description = ""
        
        if len(leader_changes) >= 2:
            phase = RotationPhase.COMPLETED
            strength = 0.8
            description = f"Sector rotation completed. {len(leader_changes)} leaders changed."
        elif len(leader_changes) >= 1 or len(laggard_improvements) >= 2:
            phase = RotationPhase.ACTIVE
            strength = 0.6
            description = f"Active rotation detected. {len(leader_changes)} leader changes, {len(laggard_improvements)} laggard improvements."
        elif leader_changes or laggard_improvements:
            phase = RotationPhase.EARLY
            strength = 0.3
            description = f"Early rotation signals. {len(leader_changes) + len(laggard_improvements)} changes detected."
        
        # Build event if rotation detected
        if phase != RotationPhase.NONE:
            from_symbol = leader_changes[0][0] if leader_changes else None
            to_symbol = None
            if laggard_improvements:
                to_symbol = laggard_improvements[0][0]
            
            # Determine alert level
            alert_level = "low"
            if strength >= 0.7:
                alert_level = "high"
            elif strength >= 0.4:
                alert_level = "moderate"
            
            event = RotationEvent(
                timestamp=datetime.utcnow(),
                phase=phase,
                from_sector=from_symbol,
                to_sector=to_symbol,
                strength=strength,
                description=description,
                alert_level=alert_level,
            )
            
            # Store in history
            self._rotation_history.append(event)
            
            # Keep only recent history
            if len(self._rotation_history) > 20:
                self._rotation_history = self._rotation_history[-20:]
            
            return event
        
        return None

    def detect_momentum_crossover(
        self,
        sector1: SectorProfile,
        sector2: SectorProfile,
    ) -> Optional[RotationEvent]:
        """Detect momentum crossover between two sectors."""
        
        if not sector1.momentum_score or not sector2.momentum_score:
            return None
        
        m1 = sector1.momentum_score
        m2 = sector2.momentum_score
        
        # Check for crossover
        if m1 > 0 and m2 < 0:
            return RotationEvent(
                timestamp=datetime.utcnow(),
                phase=RotationPhase.ACTIVE,
                from_sector=sector2.symbol,
                to_sector=sector1.symbol,
                strength=min(1.0, abs(m1 - m2)),
                description=f"Momentum crossover: {sector1.symbol} over {sector2.symbol}",
                alert_level="moderate",
            )
        
        return None

    def get_rotation_history(
        self,
        limit: int = 10,
    ) -> List[RotationEvent]:
        """Get recent rotation history."""
        return self._rotation_history[-limit:]


# Singleton
_rotation_detector: Optional[RotationDetector] = None


def get_rotation_detector() -> RotationDetector:
    """Get the singleton RotationDetector instance."""
    global _rotation_detector
    if _rotation_detector is None:
        _rotation_detector = RotationDetector()
    return _rotation_detector
