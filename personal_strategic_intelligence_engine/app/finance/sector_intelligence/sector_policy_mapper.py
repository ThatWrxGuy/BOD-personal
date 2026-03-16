"""Sector Policy Mapper - BB-FIN-015"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.finance.sector_intelligence.sector_models import (
    SectorProfile,
    SectorLeadershipRanking,
    SectorPolicyRecommendation,
    RotationEvent,
    CapitalFlowDirection,
)

logger = logging.getLogger(__name__)

# Market regime to expected leadership mapping
REGIME_LEADERSHIP = {
    "RISK_ON_TREND": {
        "overweight": ["XLK", "XLY"],  # Tech, Consumer Discretionary
        "neutral": ["XLI", "XLF", "XLE"],
        "underweight": ["XLU", "XLP"],
    },
    "RISK_ON_MOMENTUM": {
        "overweight": ["XLK", "XLF"],
        "neutral": ["XLE", "XLI", "XLV"],
        "underweight": ["XLU", "XLRE"],
    },
    "NEUTRAL_MIXED": {
        "overweight": ["XLI", "XLV"],
        "neutral": ["XLK", "XLF", "XLE"],
        "underweight": ["XLC", "XLRE"],
    },
    "ROTATION_TRANSITION": {
        "overweight": ["XLI", "XLF"],
        "neutral": ["XLE", "XLV", "XLP"],
        "underweight": ["XLK", "XLY"],
    },
    "RISK_OFF_DEFENSIVE": {
        "overweight": ["XLU", "XLP", "XLV"],
        "neutral": ["XLB", "XLC"],
        "underweight": ["XLK", "XLF", "XLE", "XLY"],
    },
    "VOLATILITY_STRESS": {
        "overweight": ["XLU", "XLP"],
        "neutral": [],
        "underweight": ["XLK", "XLY", "XLF", "XLE"],
    },
    "LIQUIDITY_DISLOCATION": {
        "overweight": ["XLU"],
        "neutral": ["XLP"],
        "underweight": ["XLK", "XLF", "XLRE", "XLE"],
    },
    "RANGE_COMPRESSION": {
        "overweight": ["XLI", "XLB"],
        "neutral": ["XLF", "XLV"],
        "underweight": ["XLK", "XLE"],
    },
    "MEAN_REVERSION": {
        "overweight": ["XLV", "XLP"],
        "neutral": ["XLK", "XLF"],
        "underweight": ["XLE", "XLY"],
    },
    "MACRO_EVENT_UNCERTAINTY": {
        "overweight": ["XLU", "XLP", "XLV"],
        "neutral": ["XLC", "XLB"],
        "underweight": ["XLK", "XLF", "XLE", "XLY"],
    },
}

# Sector names
SECTOR_NAMES = {
    "XLK": "Technology",
    "XLF": "Financials",
    "XLE": "Energy",
    "XLV": "Healthcare",
    "XLI": "Industrials",
    "XLP": "Consumer Staples",
    "XLY": "Consumer Discretionary",
    "XLU": "Utilities",
    "XLB": "Materials",
    "XLRE": "Real Estate",
    "XLC": "Communication Services",
}


class SectorPolicyMapper:
    """Translates leadership intelligence into portfolio guidance."""

    def __init__(self):
        pass

    def generate_recommendations(
        self,
        leadership: SectorLeadershipRanking,
        rotation: Optional[RotationEvent] = None,
        market_regime: Optional[str] = None,
    ) -> List[SectorPolicyRecommendation]:
        """Generate portfolio recommendations from sector intelligence."""
        
        recommendations = []
        
        # Get regime guidance if available
        regime_guidance = REGIME_LEADERSHIP.get(market_regime, {})
        overweight_sectors = set(regime_guidance.get("overweight", []))
        underweight_sectors = set(regime_guidance.get("underweight", []))
        
        # Get top and bottom sectors
        composite = leadership.composite
        
        # Generate recommendations for each sector
        for i, sector in enumerate(composite):
            symbol = sector.symbol
            name = SECTOR_NAMES.get(symbol, sector.name)
            
            # Determine base weight from ranking
            total = len(composite)
            base_weight = 1.0 / total if total > 0 else 0.0
            
            # Adjust based on ranking position
            if i == 0:  # Top sector
                weight = base_weight * 1.5
                adjustment = "increase"
                priority = 1
            elif i < 3:  # Top 3
                weight = base_weight * 1.2
                adjustment = "increase"
                priority = 2
            elif i >= total - 2:  # Bottom 2
                weight = base_weight * 0.5
                adjustment = "decrease"
                priority = total
            elif i >= total - 3:  # Bottom 3
                weight = base_weight * 0.7
                adjustment = "decrease"
                priority = total - 1
            else:
                weight = base_weight
                adjustment = "maintain"
                priority = i + 1
            
            # Override based on regime
            if symbol in overweight_sectors:
                weight *= 1.2
                adjustment = "increase"
                rationale = [f"Overweight per regime {market_regime}"]
            elif symbol in underweight_sectors:
                weight *= 0.5
                adjustment = "decrease"
                rationale = [f"Underweight per regime {market_regime}"]
            else:
                rationale = [f"Ranked #{i+1} of {total}"]
            
            # Add rotation rationale if applicable
            if rotation:
                if symbol == rotation.to_sector:
                    rationale.append("Rotation target sector")
                elif symbol == rotation.from_sector:
                    rationale.append("Rotation source sector - reducing")
            
            # Add momentum rationale
            if sector.momentum_score and sector.momentum_score > 0.3:
                rationale.append(f"Strong momentum ({sector.momentum_score:.1f})")
            elif sector.momentum_score and sector.momentum_score < -0.2:
                rationale.append(f"Weak momentum ({sector.momentum_score:.1f})")
            
            # Determine risk level
            risk_level = "moderate"
            if sector.symbol in ["XLK", "XLE", "XLRE"]:  # Higher beta sectors
                risk_level = "high"
            elif sector.symbol in ["XLU", "XLP", "XLV"]:  # Defensive
                risk_level = "low"
            
            rec = SectorPolicyRecommendation(
                symbol=symbol,
                name=name,
                weight=min(1.0, weight),
                adjustment=adjustment,
                rationale=rationale,
                risk_level=risk_level,
                priority=priority,
            )
            recommendations.append(rec)
        
        # Sort by priority
        recommendations = sorted(recommendations, key=lambda r: r.priority)
        
        return recommendations

    def get_regime_leaders(self, regime: str) -> List[str]:
        """Get expected leadership for a regime."""
        return REGIME_LEADERSHIP.get(regime, {}).get("overweight", [])

    def get_regime_laggards(self, regime: str) -> List[str]:
        """Get expected laggards for a regime."""
        return REGIME_LEADERSHIP.get(regime, {}).get("underweight", [])


# Singleton
_policy_mapper: Optional[SectorPolicyMapper] = None


def get_sector_policy_mapper() -> SectorPolicyMapper:
    """Get the singleton SectorPolicyMapper instance."""
    global _policy_mapper
    if _policy_mapper is None:
        _policy_mapper = SectorPolicyMapper()
    return _policy_mapper
