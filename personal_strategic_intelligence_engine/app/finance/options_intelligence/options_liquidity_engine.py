"""Options Liquidity Engine - BB-FIN-017"""

from typing import Optional, Dict, List
import logging

from app.finance.options_intelligence.options_models import (
    LiquidityRating,
    OptionsLiquidityProfile,
)

logger = logging.getLogger(__name__)


class OptionsLiquidityEngine:
    """Evaluate options market liquidity."""

    def __init__(self):
        self._historical_volume: Dict[str, List[float]] = {}

    def analyze_liquidity(
        self,
        symbol: str,
        avg_volume: Optional[float] = None,
        total_oi: Optional[float] = None,
        avg_spread: Optional[float] = None,
        volume_history: Optional[List[float]] = None,
    ) -> OptionsLiquidityProfile:
        """Analyze options liquidity."""
        # Use demo data if not provided
        if avg_volume is None:
            avg_volume, total_oi, avg_spread = self._generate_demo_liquidity(symbol)
        
        # Calculate metrics
        oi_stability = self._calculate_oi_stability(volume_history)
        spread_quality = self._rate_spread_quality(avg_spread)
        
        # Calculate tradability score
        tradability = self._calculate_tradability_score(avg_volume, total_oi, avg_spread)
        
        # Overall rating
        liquidity_rating = self._determine_liquidity_rating(tradability, spread_quality)
        
        # Volume trend
        volume_trend = self._analyze_volume_trend(symbol, volume_history)
        
        return OptionsLiquidityProfile(
            symbol=symbol,
            avg_daily_volume=avg_volume,
            total_oi=total_oi,
            avg_spread=avg_spread,
            oi_stability=oi_stability,
            spread_quality=spread_quality,
            tradability_score=tradability,
            liquidity_rating=liquidity_rating,
            volume_trend=volume_trend,
        )

    def _calculate_oi_stability(self, volume_history: Optional[List[float]]) -> float:
        """Calculate OI stability (0-1)."""
        if not volume_history or len(volume_history) < 5:
            return 0.5
        
        # Calculate coefficient of variation
        import statistics
        mean = statistics.mean(volume_history)
        if mean == 0:
            return 0.5
        
        stdev = statistics.stdev(volume_history)
        cv = stdev / mean
        
        # Lower CV = more stable (higher score)
        # CV of 0 = score 1.0, CV of 1+ = score 0.0
        stability = max(0, 1 - cv)
        return stability

    def _rate_spread_quality(self, avg_spread: Optional[float]) -> LiquidityRating:
        """Rate spread quality."""
        if avg_spread is None:
            return LiquidityRating.MEDIUM
        
        # Spread as percentage of underlying price (approximate)
        # For demo, avg_spread is already in dollars
        if avg_spread < 0.10:
            return LiquidityRating.HIGH
        elif avg_spread < 0.25:
            return LiquidityRating.MEDIUM
        elif avg_spread < 0.50:
            return LiquidityRating.LOW
        else:
            return LiquidityRating.VERY_LOW

    def _calculate_tradability_score(
        self,
        avg_volume: Optional[float],
        total_oi: Optional[float],
        avg_spread: Optional[float],
    ) -> float:
        """Calculate overall tradability score (0-1)."""
        # Volume component (40%)
        volume_score = 0.0
        if avg_volume:
            if avg_volume > 500000:
                volume_score = 1.0
            elif avg_volume > 100000:
                volume_score = 0.8
            elif avg_volume > 50000:
                volume_score = 0.6
            elif avg_volume > 10000:
                volume_score = 0.4
            else:
                volume_score = 0.2
        
        # OI component (30%)
        oi_score = 0.0
        if total_oi:
            if total_oi > 1000000:
                oi_score = 1.0
            elif total_oi > 500000:
                oi_score = 0.8
            elif total_oi > 100000:
                oi_score = 0.6
            elif total_oi > 50000:
                oi_score = 0.4
            else:
                oi_score = 0.2
        
        # Spread component (30%)
        spread_score = 0.0
        if avg_spread:
            if avg_spread < 0.10:
                spread_score = 1.0
            elif avg_spread < 0.25:
                spread_score = 0.8
            elif avg_spread < 0.50:
                spread_score = 0.6
            elif avg_spread < 1.00:
                spread_score = 0.4
            else:
                spread_score = 0.2
        
        return (volume_score * 0.4) + (oi_score * 0.3) + (spread_score * 0.3)

    def _determine_liquidity_rating(
        self,
        tradability: float,
        spread_quality: LiquidityRating,
    ) -> LiquidityRating:
        """Determine overall liquidity rating."""
        if tradability > 0.75 and spread_quality == LiquidityRating.HIGH:
            return LiquidityRating.HIGH
        elif tradability > 0.5 and spread_quality in [LiquidityRating.HIGH, LiquidityRating.MEDIUM]:
            return LiquidityRating.MEDIUM
        elif tradability > 0.25:
            return LiquidityRating.LOW
        else:
            return LiquidityRating.VERY_LOW

    def _analyze_volume_trend(
        self,
        symbol: str,
        volume_history: Optional[List[float]],
    ) -> str:
        """Analyze volume trend."""
        if not volume_history or len(volume_history) < 5:
            return "stable"
        
        # Compare recent average to historical
        recent = sum(volume_history[-3:]) / 3
        older = sum(volume_history[:-3]) / max(1, len(volume_history) - 3)
        
        if older == 0:
            return "stable"
        
        ratio = recent / older
        
        if ratio > 1.3:
            return "increasing"
        elif ratio < 0.7:
            return "decreasing"
        else:
            return "stable"

    def _generate_demo_liquidity(self, symbol: str):
        """Generate demo liquidity data."""
        import random
        
        # Typical options volume by symbol type
        liquid_etfs = {"SPY": 5000000, "QQQ": 3000000, "IWM": 1500000}
        tech_stocks = {"AAPL": 800000, "MSFT": 600000, "NVDA": 1000000, "TSLA": 2000000}
        other_stocks = {"JPM": 300000, "XOM": 400000}
        
        if symbol in liquid_etfs:
            base = liquid_etfs[symbol]
        elif symbol in tech_stocks:
            base = tech_stocks[symbol]
        elif symbol in other_stocks:
            base = other_stocks[symbol]
        else:
            base = 200000
        
        # Add variance
        avg_volume = base * random.uniform(0.7, 1.3)
        total_oi = avg_volume * random.uniform(3, 8)
        
        # Spread inversely related to volume
        if avg_volume > 1000000:
            avg_spread = 0.05
        elif avg_volume > 500000:
            avg_spread = 0.10
        elif avg_volume > 100000:
            avg_spread = 0.20
        else:
            avg_spread = 0.50
        
        return avg_volume, total_oi, avg_spread

    def is_suitable_for_strategy(
        self,
        liquidity: OptionsLiquidityProfile,
        strategy: str,
    ) -> bool:
        """Check if liquidity is suitable for a strategy."""
        if strategy in ["straddle", "strangle"]:
            # Need high liquidity for volatility strategies
            return liquidity.liquidity_rating in [LiquidityRating.HIGH, LiquidityRating.MEDIUM]
        
        elif strategy in ["covered_call", "cash_secured_put"]:
            # Can tolerate lower liquidity
            return liquidity.liquidity_rating != LiquidityRating.VERY_LOW
        
        elif strategy in ["iron_condor", "butterfly"]:
            # Need high liquidity for multi-leg
            return liquidity.liquidity_rating == LiquidityRating.HIGH
        
        return True


# Singleton
_liquidity_engine: Optional[OptionsLiquidityEngine] = None


def get_options_liquidity_engine() -> OptionsLiquidityEngine:
    """Get the singleton OptionsLiquidityEngine instance."""
    global _liquidity_engine
    if _liquidity_engine is None:
        _liquidity_engine = OptionsLiquidityEngine()
    return _liquidity_engine
