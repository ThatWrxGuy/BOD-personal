"""Sector Breadth Engine - BB-FIN-015"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.finance.sector_intelligence.sector_models import (
    SectorProfile,
    SectorBreadthProfile,
)

logger = logging.getLogger(__name__)


class SectorBreadthEngine:
    """Evaluates participation within sectors."""

    # Thresholds
    CONCENTRATION_THRESHOLD = 0.7  # 70% in top stocks = concentrated

    def __init__(self):
        self._prior_breadth: Dict[str, float] = {}

    def analyze_sector_breadth(
        self,
        sector: SectorProfile,
    ) -> SectorBreadthProfile:
        """Analyze breadth for a single sector."""
        
        # Use sector data to create breadth profile
        # In production, would use actual advancing/declining data
        
        # Use available data or defaults
        advancing = sector.advancing_stocks or 3
        declining = sector.declining_stocks or 2
        total = advancing + declining
        
        # Calculate ratios
        ad_ratio = advancing / total if total > 0 else 0.5
        participation = advancing / total * 100 if total > 0 else 50.0
        
        # Determine concentration risk
        concentration_risk = "low"
        if sector.symbol in ["XLK", "XLF"]:  # Tech/Finance often concentrated
            concentration_risk = "medium"
        
        is_concentrated = concentration_risk in ["medium", "high"]
        
        return SectorBreadthProfile(
            symbol=sector.symbol,
            advancing_stocks=advancing,
            declining_stocks=declining,
            total_stocks=total,
            advance_decline_ratio=ad_ratio,
            participation_pct=participation,
            is_concentrated=is_concentrated,
            concentration_risk=concentration_risk,
        )

    def analyze_all_breadths(
        self,
        sector_profiles: List[SectorProfile],
    ) -> List[SectorBreadthProfile]:
        """Analyze breadth for all sectors."""
        
        profiles = []
        
        for sector in sector_profiles:
            breadth = self.analyze_sector_breadth(sector)
            profiles.append(breadth)
        
        return profiles

    def get_leadership_quality(
        self,
        breadth_profiles: List[SectorBreadthProfile],
    ) -> Dict[str, float]:
        """Assess quality of sector leadership."""
        
        quality_scores = {}
        
        for profile in breadth_profiles:
            # Base score from participation
            score = profile.participation_pct / 100.0
            
            # Penalize concentration
            if profile.is_concentrated:
                score *= 0.7
            
            quality_scores[profile.symbol] = score
        
        return quality_scores


# Singleton
_breadth_engine: Optional[SectorBreadthEngine] = None


def get_sector_breadth_engine() -> SectorBreadthEngine:
    """Get the singleton SectorBreadthEngine instance."""
    global _breadth_engine
    if _breadth_engine is None:
        _breadth_engine = SectorBreadthEngine()
    return _breadth_engine
