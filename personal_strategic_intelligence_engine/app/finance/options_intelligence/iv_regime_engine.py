"""IV Regime Engine - BB-FIN-017"""

from typing import Optional, Dict, List
import logging

from app.finance.options_intelligence.options_models import (
    IVRegime,
    OptionsEnvironmentProfile,
)

logger = logging.getLogger(__name__)


# IV regime thresholds (percentile-based)
IV_REGIME_THRESHOLDS = {
    "compressed": 0.15,    # Bottom 15%
    "normal": 0.40,         # 15-40%
    "elevated": 0.70,       # 40-70%
    "extreme": 1.0,         # Top 30%
}

# IV rank thresholds
IV_RANK_THRESHOLDS = {
    "compressed": 0.20,
    "normal": 0.45,
    "elevated": 0.75,
    "extreme": 0.90,
}


class IVRegimeEngine:
    """Compute IV regime classification and related metrics."""

    def __init__(self):
        self._historical_iv: Dict[str, List[float]] = {}

    def add_iv_observation(self, symbol: str, iv: float) -> None:
        """Add IV observation for tracking."""
        if symbol not in self._historical_iv:
            self._historical_iv[symbol] = []
        self._historical_iv[symbol].append(iv)
        
        # Keep only last 252 observations (1 year)
        if len(self._historical_iv[symbol]) > 252:
            self._historical_iv[symbol] = self._historical_iv[symbol][-252:]

    def calculate_iv_percentile(self, symbol: str, current_iv: float) -> float:
        """Calculate IV percentile (0-1)."""
        if symbol not in self._historical_iv or len(self._historical_iv[symbol]) < 20:
            # Default to middle if insufficient history
            return 0.5
        
        history = self._historical_iv[symbol]
        below_count = sum(1 for iv in history if iv < current_iv)
        return below_count / len(history)

    def calculate_iv_rank(self, symbol: str, current_iv: float) -> float:
        """Calculate IV rank (0-1) based on 52-week range."""
        if symbol not in self._historical_iv or len(self._historical_iv[symbol]) < 20:
            return 0.5
        
        history = self._historical_iv[symbol]
        iv_min = min(history)
        iv_max = max(history)
        
        if iv_max == iv_min:
            return 0.5
        
        rank = (current_iv - iv_min) / (iv_max - iv_min)
        return max(0.0, min(1.0, rank))

    def classify_regime(self, iv_percentile: float, iv_rank: float) -> IVRegime:
        """Classify IV regime based on percentile and rank."""
        # Use average of percentile and rank
        avg = (iv_percentile + iv_rank) / 2
        
        if avg < IV_REGIME_THRESHOLDS["compressed"]:
            return IVRegime.COMPRESSED
        elif avg < IV_REGIME_THRESHOLDS["normal"]:
            return IVRegime.NORMAL
        elif avg < IV_REGIME_THRESHOLDS["elevated"]:
            return IVRegime.ELEVATED
        else:
            return IVRegime.EXTREME

    def calculate_iv_hv_spread(
        self,
        current_iv: float,
        realized_vol: float
    ) -> Optional[float]:
        """Calculate IV vs realized volatility spread."""
        if realized_vol is None or realized_vol == 0:
            return None
        return current_iv - realized_vol

    def analyze_iv_environment(
        self,
        symbol: str,
        current_iv: Optional[float] = None,
        realized_vol: Optional[float] = None,
    ) -> OptionsEnvironmentProfile:
        """Complete IV environment analysis."""
        # Use demo data if not provided
        if current_iv is None:
            current_iv = self._generate_demo_iv(symbol)
        if realized_vol is None:
            realized_vol = current_iv * 0.85  # Typical relationship
        
        # Add observation
        self.add_iv_observation(symbol, current_iv)
        
        # Calculate metrics
        iv_percentile = self.calculate_iv_percentile(symbol, current_iv)
        iv_rank = self.calculate_iv_rank(symbol, current_iv)
        iv_regime = self.classify_regime(iv_percentile, iv_rank)
        iv_hv_spread = self.calculate_iv_hv_spread(current_iv, realized_vol)
        
        return OptionsEnvironmentProfile(
            symbol=symbol,
            current_iv=current_iv,
            iv_percentile=iv_percentile,
            iv_rank=iv_rank,
            iv_regime=iv_regime,
            realized_vol=realized_vol,
            iv_hv_spread=iv_hv_spread,
            suitability=OptionsSuitability.NEUTRAL,  # Will be set by suitability engine
            suitability_score=0.5,
        )

    def _generate_demo_iv(self, symbol: str) -> float:
        """Generate demo IV based on symbol characteristics."""
        import random
        
        # Different IV characteristics per symbol
        base_iv = {
            "SPY": 14.0,
            "QQQ": 18.0,
            "IWM": 20.0,
            "AAPL": 25.0,
            "TSLA": 55.0,
            "NVDA": 40.0,
            "AMD": 45.0,
            "META": 30.0,
        }.get(symbol, 25.0)
        
        # Add some variance
        return base_iv + random.uniform(-5, 10)

    def get_regime_description(self, regime: IVRegime) -> str:
        """Get plain language description of regime."""
        descriptions = {
            IVRegime.COMPRESSED: "IV is historically low. Expect volatility expansion.",
            IVRegime.NORMAL: "IV is at typical levels. Standard options pricing.",
            IVRegime.ELEVATED: "IV is elevated. Higher option premiums.",
            IVRegime.EXTREME: "IV is at extreme highs. Caution advised.",
        }
        return descriptions.get(regime, "")

    def get_regime_recommendation(self, regime: IVRegime) -> str:
        """Get strategy recommendation for regime."""
        recommendations = {
            IVRegime.COMPRESSED: "Long volatility strategies favorable. Consider straddles.",
            IVRegime.NORMAL: "Standard strategies. Focus on direction.",
            IVRegime.ELEVATED: "Sell volatility. Credit spreads attractive.",
            IVRegime.EXTREME: "Avoid long volatility. Protective puts if holding.",
        }
        return recommendations.get(regime, "")


# Singleton
_iv_engine: Optional[IVRegimeEngine] = None


def get_iv_regime_engine() -> IVRegimeEngine:
    """Get the singleton IVRegimeEngine instance."""
    global _iv_engine
    if _iv_engine is None:
        _iv_engine = IVRegimeEngine()
    return _iv_engine


# Import at end to avoid circular import
from app.finance.options_intelligence.options_models import OptionsSuitability
