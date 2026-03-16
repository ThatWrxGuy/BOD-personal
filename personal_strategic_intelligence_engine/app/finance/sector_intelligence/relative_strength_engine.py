"""Relative Strength Engine - BB-FIN-015"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

from app.finance.sector_intelligence.sector_models import (
    SectorProfile,
    RelativeStrengthScore,
    MomentumPhase,
)

logger = logging.getLogger(__name__)


# Sector universe
SECTOR_UNIVERSE = {
    "XLK": {"name": "Technology", "weight": 0.28},
    "XLF": {"name": "Financials", "weight": 0.13},
    "XLE": {"name": "Energy", "weight": 0.04},
    "XLV": {"name": "Healthcare", "weight": 0.13},
    "XLI": {"name": "Industrials", "weight": 0.08},
    "XLP": {"name": "Consumer Staples", "weight": 0.07},
    "XLY": {"name": "Consumer Discretionary", "weight": 0.11},
    "XLU": {"name": "Utilities", "weight": 0.03},
    "XLB": {"name": "Materials", "weight": 0.03},
    "XLRE": {"name": "Real Estate", "weight": 0.03},
    "XLC": {"name": "Communication Services", "weight": 0.08},
}

# Benchmark
SPY = "SPY"


class RelativeStrengthEngine:
    """Calculates relative strength between sectors and benchmarks."""

    def __init__(self):
        self.benchmark = SPY
        self._prior_rankings: Dict[str, int] = {}

    def calculate_rs_vs_benchmark(
        self,
        sector_price: float,
        benchmark_price: float,
        sector_prior: float,
        benchmark_prior: float,
    ) -> RelativeStrengthScore:
        """Calculate relative strength vs benchmark."""
        
        # Current ratio
        current_ratio = sector_price / benchmark_price if benchmark_price else 1.0
        
        # Ratio changes
        prior_ratio = sector_prior / benchmark_prior if benchmark_prior else 1.0
        ratio_change_1m = ((current_ratio - prior_ratio) / prior_ratio * 100) if prior_ratio else 0.0
        
        # Strength score (-1 to 1)
        if ratio_change_1m > 5:
            strength_score = min(1.0, ratio_change_1m / 10)
        elif ratio_change_1m < -5:
            strength_score = max(-1.0, ratio_change_1m / 10)
        else:
            strength_score = ratio_change_1m / 10
        
        # Momentum score (use current price change as proxy)
        sector_change = ((sector_price - sector_prior) / sector_prior * 100) if sector_prior else 0.0
        if sector_change > 3:
            momentum_score = min(1.0, sector_change / 6)
        elif sector_change < -3:
            momentum_score = max(-1.0, sector_change / 6)
        else:
            momentum_score = sector_change / 6
        
        # Overall score
        overall_score = (strength_score * 0.6 + momentum_score * 0.4)
        
        return RelativeStrengthScore(
            base_symbol=SPY,
            target_symbol="SECTOR",
            current_ratio=current_ratio,
            ratio_change_1m=ratio_change_1m,
            strength_score=strength_score,
            momentum_score=momentum_score,
            overall_score=overall_score,
            confidence="moderate",
        )

    def calculate_sector_vs_sector(
        self,
        sector1_price: float,
        sector2_price: float,
        sector1_prior: float,
        sector2_prior: float,
    ) -> RelativeStrengthScore:
        """Calculate relative strength between two sectors."""
        
        # Current ratio
        current_ratio = sector1_price / sector2_price if sector2_price else 1.0
        
        # Ratio changes
        prior_ratio = sector1_prior / sector2_prior if sector2_prior else 1.0
        ratio_change = ((current_ratio - prior_ratio) / prior_ratio * 100) if prior_ratio else 0.0
        
        # Scores
        strength_score = max(-1.0, min(1.0, ratio_change / 10))
        
        # Individual changes
        s1_change = ((sector1_price - sector1_prior) / sector1_prior * 100) if sector1_prior else 0.0
        s2_change = ((sector2_price - sector2_prior) / sector2_prior * 100) if sector2_prior else 0.0
        momentum_score = max(-1.0, min(1.0, (s1_change - s2_change) / 6))
        
        overall = strength_score * 0.5 + momentum_score * 0.5
        
        return RelativeStrengthScore(
            base_symbol="SECTOR2",
            target_symbol="SECTOR1",
            current_ratio=current_ratio,
            ratio_change_1m=ratio_change,
            strength_score=strength_score,
            momentum_score=momentum_score,
            overall_score=overall,
        )

    def rank_sectors(
        self,
        sector_profiles: List[SectorProfile],
    ) -> List[SectorProfile]:
        """Rank sectors by relative strength."""
        
        # Sort by rs_rank if available, otherwise by rs_vs_spy
        ranked = sorted(
            sector_profiles,
            key=lambda s: (s.rs_rank if s.rs_rank else 999, s.rs_vs_spy if s.rs_vs_spy else 0),
            reverse=True
        )
        
        # Update rankings
        for i, sector in enumerate(ranked):
            sector.rs_rank = i + 1
        
        return ranked

    def get_sector_universe(self) -> Dict[str, Dict[str, str]]:
        """Get the sector universe."""
        return SECTOR_UNIVERSE

    def analyze_all_sectors(
        self,
        prices: Dict[str, float],
        changes_1m: Optional[Dict[str, float]] = None,
    ) -> List[SectorProfile]:
        """Analyze all sectors in the universe."""
        
        profiles = []
        changes_1m = changes_1m or {}
        
        for symbol, info in SECTOR_UNIVERSE.items():
            price = prices.get(symbol, 100.0)  # Default price if not provided
            change_1m = changes_1m.get(symbol, 0.0)
            
            # Calculate RS vs SPY (use SPY price as proxy)
            spy_price = prices.get("SPY", 450.0)
            rs_vs_spy = (price / spy_price - 1) * 100 if spy_price else 0.0
            
            profile = SectorProfile(
                symbol=symbol,
                name=info["name"],
                price=price,
                change_1m=change_1m,
                rs_vs_spy=rs_vs_spy,
            )
            profiles.append(profile)
        
        # Rank sectors
        profiles = self.rank_sectors(profiles)
        
        return profiles


# Singleton
_rs_engine: Optional[RelativeStrengthEngine] = None


def get_relative_strength_engine() -> RelativeStrengthEngine:
    """Get the singleton RelativeStrengthEngine instance."""
    global _rs_engine
    if _rs_engine is None:
        _rs_engine = RelativeStrengthEngine()
    return _rs_engine
