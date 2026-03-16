"""Sector Ranker - BB-FIN-015"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

from app.finance.sector_intelligence.sector_models import (
    SectorProfile,
    SectorLeadershipRanking,
    MomentumProfile,
    SectorBreadthProfile,
    CapitalFlowSignal,
)

logger = logging.getLogger(__name__)


class SectorRanker:
    """Produces canonical sector rankings."""

    # Weighting for composite score
    WEIGHTS = {
        "rs_vs_spy": 0.25,
        "momentum": 0.25,
        "breadth": 0.20,
        "flow": 0.15,
        "volatility": 0.15,
    }

    def __init__(self):
        self._prior_rankings: Dict[str, int] = {}

    def rank_sectors_by_rs(
        self,
        sector_profiles: List[SectorProfile],
    ) -> List[SectorProfile]:
        """Rank sectors by relative strength."""
        
        # Sort by rs_vs_spy descending
        ranked = sorted(
            sector_profiles,
            key=lambda s: s.rs_vs_spy or 0.0,
            reverse=True
        )
        
        # Assign ranks
        for i, sector in enumerate(ranked):
            sector.rs_rank = i + 1
        
        return ranked

    def rank_sectors_by_momentum(
        self,
        sector_profiles: List[SectorProfile],
    ) -> List[SectorProfile]:
        """Rank sectors by momentum."""
        
        ranked = sorted(
            sector_profiles,
            key=lambda s: s.momentum_score or 0.0,
            reverse=True
        )
        
        return ranked

    def rank_sectors_by_breadth(
        self,
        sector_profiles: List[SectorProfile],
        breadth_profiles: List[SectorBreadthProfile],
    ) -> List[SectorProfile]:
        """Rank sectors by breadth participation."""
        
        # Create lookup
        breadth_lookup = {b.symbol: b for b in breadth_profiles}
        
        ranked = []
        for sector in sector_profiles:
            breadth = breadth_lookup.get(sector.symbol)
            if breadth:
                sector._breadth_score = breadth.participation_pct / 100.0
            else:
                sector._breadth_score = 0.5
            ranked.append(sector)
        
        ranked = sorted(ranked, key=lambda s: s._breadth_score or 0.5, reverse=True)
        
        return ranked

    def rank_sectors_by_flows(
        self,
        sector_profiles: List[SectorProfile],
        flow_signals: List[CapitalFlowSignal],
    ) -> List[SectorProfile]:
        """Rank sectors by capital flow."""
        
        flow_lookup = {f.symbol: f for f in flow_signals}
        
        ranked = []
        for sector in sector_profiles:
            flow = flow_lookup.get(sector.symbol)
            if flow:
                # Convert direction to score
                if flow.direction.value == "inflow":
                    sector._flow_score = flow.strength
                elif flow.direction.value == "outflow":
                    sector._flow_score = -flow.strength
                else:
                    sector._flow_score = 0.0
            else:
                sector._flow_score = 0.0
            ranked.append(sector)
        
        ranked = sorted(ranked, key=lambda s: s._flow_score or 0.0, reverse=True)
        
        return ranked

    def calculate_composite_ranking(
        self,
        sector_profiles: List[SectorProfile],
        momentum_profiles: Dict[str, MomentumProfile],
        breadth_profiles: List[SectorBreadthProfile],
        flow_signals: List[CapitalFlowSignal],
    ) -> List[SectorProfile]:
        """Calculate composite ranking across all factors."""
        
        # Create lookup dictionaries
        momentum_lookup = {m.symbol: m for m in momentum_profiles.values()}
        breadth_lookup = {b.symbol: b for b in breadth_profiles}
        flow_lookup = {f.symbol: f for f in flow_signals}
        
        # Calculate composite scores
        for sector in sector_profiles:
            # RS score
            rs_score = (sector.rs_vs_spy or 0.0) / 10.0  # Normalize
            
            # Momentum score
            momentum = momentum_lookup.get(sector.symbol)
            momentum_score = momentum.trend_slope / 10.0 if momentum else 0.0
            
            # Breadth score
            breadth = breadth_lookup.get(sector.symbol)
            breadth_score = breadth.participation_pct / 100.0 if breadth else 0.5
            
            # Flow score
            flow = flow_lookup.get(sector.symbol)
            if flow:
                if flow.direction.value == "inflow":
                    flow_score = flow.strength
                elif flow.direction.value == "outflow":
                    flow_score = -flow.strength
                else:
                    flow_score = 0.0
            else:
                flow_score = 0.0
            
            # Volatility (inverse - lower vol = higher score)
            vol_score = 0.5
            if sector.volatility:
                vol_score = max(0, 1 - sector.volatility / 30)  # Assume 30 is high vol
            
            # Composite
            composite = (
                rs_score * self.WEIGHTS["rs_vs_spy"] +
                momentum_score * self.WEIGHTS["momentum"] +
                breadth_score * self.WEIGHTS["breadth"] +
                flow_score * self.WEIGHTS["flow"] +
                vol_score * self.WEIGHTS["volatility"]
            )
            
            sector._composite_score = composite
        
        # Sort by composite
        ranked = sorted(
            sector_profiles,
            key=lambda s: s._composite_score or 0.0,
            reverse=True
        )
        
        # Assign final ranks
        for i, sector in enumerate(ranked):
            sector.rs_rank = i + 1
        
        # Store prior rankings
        self._prior_rankings = {s.symbol: s.rs_rank for s in ranked}
        
        return ranked

    def create_leadership_ranking(
        self,
        sector_profiles: List[SectorProfile],
        momentum_profiles: Dict[str, MomentumProfile],
        breadth_profiles: List[SectorBreadthProfile],
        flow_signals: List[CapitalFlowSignal],
    ) -> SectorLeadershipRanking:
        """Create complete leadership ranking."""
        
        # Short term (momentum-based)
        short_term = self.rank_sectors_by_momentum(sector_profiles.copy())
        
        # Medium term (RS-based)
        medium_term = self.rank_sectors_by_rs(sector_profiles.copy())
        
        # Long term (composite)
        long_term = self.calculate_composite_ranking(
            sector_profiles.copy(),
            momentum_profiles,
            breadth_profiles,
            flow_signals,
        )
        
        # Composite is same as long_term
        composite = long_term
        
        return SectorLeadershipRanking(
            timestamp=datetime.utcnow(),
            short_term=short_term,
            medium_term=medium_term,
            long_term=long_term,
            composite=composite,
            total_sectors=len(composite),
            benchmark_symbol="SPY",
        )


# Singleton
_sector_ranker: Optional[SectorRanker] = None


def get_sector_ranker() -> SectorRanker:
    """Get the singleton SectorRanker instance."""
    global _sector_ranker
    if _sector_ranker is None:
        _sector_ranker = SectorRanker()
    return _sector_ranker
