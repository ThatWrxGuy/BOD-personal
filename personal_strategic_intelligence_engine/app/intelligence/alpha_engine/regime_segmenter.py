"""Regime Segmenter.

Segments results by environmental conditions.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass

from app.intelligence.alpha_engine.alpha_models import RegimeAnalysis, MARKET_REGIMES


@dataclass
class MarketRegime:
    """Market regime classification."""
    name: str
    characteristics: Dict[str, float]
    description: str


class RegimeSegmenter:
    """Segments analysis by market regime."""
    
    def __init__(self):
        self.regime_definitions = self._initialize_regimes()
    
    def _initialize_regimes(self) -> Dict[str, MarketRegime]:
        """Initialize regime definitions."""
        
        return {
            "high_iv": MarketRegime(
                name="high_iv",
                characteristics={"iv_percentile": 0.7, "iv_rank": 0.7},
                description="Elevated implied volatility",
            ),
            "low_iv": MarketRegime(
                name="low_iv",
                characteristics={"iv_percentile": 0.3, "iv_rank": 0.3},
                description="Low implied volatility",
            ),
            "trend_day": MarketRegime(
                name="trend_day",
                characteristics={"trend_strength": 0.7},
                description="Strong directional movement",
            ),
            "range_day": MarketRegime(
                name="range_day",
                characteristics={"range_width": 0.5, "trend_strength": 0.2},
                description="Price bounded in range",
            ),
            "event_day": MarketRegime(
                name="event_day",
                characteristics={"event_pending": True},
                description="Major news/event expected",
            ),
            "opening_drive": MarketRegime(
                name="opening_drive",
                characteristics={"time": "open", "volatility": "high"},
                description="Strong opening move",
            ),
            "midday_compression": MarketRegime(
                name="midday_compression",
                characteristics={"time": "midday", "volatility": "low"},
                description="Low volatility midday",
            ),
            "power_hour": MarketRegime(
                name="power_hour",
                characteristics={"time": "close", "volume": "high"},
                description="High volume closing hour",
            ),
        }
    
    def classify_regime(
        self,
        market_data: Dict,
    ) -> str:
        """Classify current market regime."""
        
        # Use heuristics to determine regime
        iv_percentile = market_data.get("iv_percentile", 0.5)
        iv_rank = market_data.get("iv_rank", 0.5)
        time = market_data.get("time_of_day", "midday")
        volume = market_data.get("volume", "normal")
        
        # IV-based regimes
        if iv_percentile > 0.7:
            return "high_iv"
        if iv_percentile < 0.3:
            return "low_iv"
        
        # Time-based regimes
        if time == "open":
            return "opening_drive"
        if time == "close":
            return "power_hour"
        if time == "midday":
            return "midday_compression"
        
        return "range_day"
    
    def segment_performance(
        self,
        performance_data: List[Dict],
    ) -> List[RegimeAnalysis]:
        """Segment performance by regime."""
        
        # Group by regime
        regime_data = {}
        for record in performance_data:
            regime = record.get("regime", "unknown")
            if regime not in regime_data:
                regime_data[regime] = []
            regime_data[regime].append(record)
        
        # Calculate metrics per regime
        analyses = []
        for regime, records in regime_data.items():
            if not records:
                continue
            
            # Calculate average metrics
            metrics = {
                "expectancy": sum(r.get("expectancy", 0) for r in records) / len(records),
                "win_rate": sum(r.get("win_rate", 0) for r in records) / len(records),
                "sharpe": sum(r.get("sharpe", 0) for r in records) / len(records),
            }
            
            analyses.append(RegimeAnalysis(
                regime=regime,
                performance_metrics=metrics,
                sample_size=len(records),
                confidence=min(0.9, len(records) / 50),
            ))
        
        return analyses
    
    def get_regime_requirements(self, regime: str) -> Optional[Dict]:
        """Get requirements for a specific regime."""
        
        regime_def = self.regime_definitions.get(regime)
        if regime_def:
            return regime_def.characteristics
        return None


def create_segmenter() -> RegimeSegmenter:
    """Create regime segmenter."""
    return RegimeSegmenter()
