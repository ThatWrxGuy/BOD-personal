"""Regime Classifier for SPY 0DTE Options.

Classifies market regimes for intraday trading to improve signal quality.
"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import math


class MarketRegime(str, Enum):
    """Market regime classification."""
    TREND_UP = "trend_up"
    TREND_DOWN = "trend_down"
    RANGE_CHOP = "range_chop"
    REVERSAL = "reversal"
    VOLATILITY_EXPANSION = "volatility_expansion"
    LOW_PARTICIPATION = "low_participation"


class VolatilityRegime(str, Enum):
    """Volatility regime classification."""
    LOW = "low"
    NORMAL = "normal"
    ELEVATED = "elevated"
    EXTREME = "extreme"


@dataclass
class RegimeContext:
    """Context information for regime classification."""
    regime: MarketRegime
    volatility_regime: VolatilityRegime
    confidence: float
    trend_strength: float
    volatility_percent: float
    volume_ratio: float
    timestamp: datetime
    
    def to_dict(self) -> dict:
        return {
            "regime": self.regime.value,
            "volatility_regime": self.volatility_regime.value,
            "confidence": self.confidence,
            "trend_strength": self.trend_strength,
            "volatility_percent": self.volatility_percent,
            "volume_ratio": self.volume_ratio,
            "timestamp": self.timestamp.isoformat(),
        }


class RegimeClassifier:
    """
    Lightweight market regime classifier.
    
    Analyzes price action, volume, and volatility to classify
    current market conditions for improved signal generation.
    """
    
    def __init__(
        self,
        trend_threshold: float = 0.3,
        reversal_threshold: float = -0.5,
        volume_lookback: int = 20,
    ):
        """
        Initialize regime classifier.
        
        Args:
            trend_threshold: Minimum change % to classify as trend
            reversal_threshold: Change % to classify as reversal
            volume_lookback: Bars to look back for volume analysis
        """
        self.trend_threshold = trend_threshold
        self.reversal_threshold = reversal_threshold
        self.volume_lookback = volume_lookback
        
        # Historical data for analysis
        self.price_history: list[float] = []
        self.volume_history: list[int] = []
        self.timestamp_history: list[datetime] = []
    
    def add_bar(self, price: float, volume: int, timestamp: datetime) -> None:
        """Add a price bar to history."""
        self.price_history.append(price)
        self.volume_history.append(volume)
        self.timestamp_history.append(timestamp)
        
        # Keep only recent history
        max_history = max(100, self.volume_lookback * 3)
        if len(self.price_history) > max_history:
            self.price_history = self.price_history[-max_history:]
            self.volume_history = self.volume_history[-max_history:]
            self.timestamp_history = self.timestamp_history[-max_history:]
    
    def classify_regime(
        self,
        current_price: float,
        lookback_bars: int = 30,
    ) -> RegimeContext:
        """
        Classify current market regime.
        
        Args:
            current_price: Current price
            lookback_bars: Number of bars to analyze
        
        Returns:
            RegimeContext with classification
        """
        if len(self.price_history) < 10:
            # Not enough data - return neutral regime
            return RegimeContext(
                regime=MarketRegime.RANGE_CHOP,
                volatility_regime=VolatilityRegime.NORMAL,
                confidence=0.3,
                trend_strength=0.0,
                volatility_percent=1.0,
                volume_ratio=1.0,
                timestamp=datetime.now(),
            )
        
        # Use recent bars
        prices = self.price_history[-lookback_bars:]
        volumes = self.volume_history[-lookback_bars:] if len(self.volume_history) >= lookback_bars else self.volume_history
        
        # Calculate metrics
        change_pct = self._calculate_change_percent(prices)
        volatility = self._calculate_volatility(prices)
        trend_strength = self._calculate_trend_strength(prices)
        volume_ratio = self._calculate_volume_ratio(volumes)
        
        # Classify regime
        regime = self._classify_market_regime(
            change_pct, trend_strength, volatility, volume_ratio
        )
        
        # Classify volatility
        vol_regime = self._classify_volatility(volatility)
        
        # Calculate confidence based on signal clarity
        confidence = min(1.0, abs(trend_strength) * 0.7 + (1 - volatility) * 0.3)
        
        return RegimeContext(
            regime=regime,
            volatility_regime=vol_regime,
            confidence=confidence,
            trend_strength=trend_strength,
            volatility_percent=volatility,
            volume_ratio=volume_ratio,
            timestamp=datetime.now(),
        )
    
    def _calculate_change_percent(self, prices: list[float]) -> float:
        """Calculate percentage change over period."""
        if len(prices) < 2:
            return 0.0
        return ((prices[-1] - prices[0]) / prices[0]) * 100
    
    def _calculate_volatility(self, prices: list[float]) -> float:
        """Calculate price volatility (standard deviation of returns)."""
        if len(prices) < 2:
            return 0.0
        
        returns = []
        for i in range(1, len(prices)):
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        
        if not returns:
            return 0.0
        
        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / len(returns)
        std_dev = math.sqrt(variance)
        
        # Annualize (assuming 1-min bars, 390 min/day)
        annualized_vol = std_dev * math.sqrt(390) * 100
        return annualized_vol
    
    def _calculate_trend_strength(self, prices: list[float]) -> float:
        """Calculate trend strength using linear regression."""
        if len(prices) < 3:
            return 0.0
        
        n = len(prices)
        x = list(range(n))
        y = prices
        
        # Linear regression
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        
        # Normalize by price level
        normalized_slope = (slope / y_mean) * 100
        
        # Scale to -1 to 1 range
        return max(-1.0, min(1.0, normalized_slope * 10))
    
    def _calculate_volume_ratio(self, volumes: list[int]) -> float:
        """Calculate volume ratio vs average."""
        if len(volumes) < 2:
            return 1.0
        
        avg_volume = sum(volumes[:-1]) / (len(volumes) - 1)
        if avg_volume == 0:
            return 1.0
        
        current_volume = volumes[-1]
        return current_volume / avg_volume
    
    def _classify_market_regime(
        self,
        change_pct: float,
        trend_strength: float,
        volatility: float,
        volume_ratio: float,
    ) -> MarketRegime:
        """Classify market regime based on metrics."""
        
        # Check for reversal
        if abs(change_pct) > 1.0 and trend_strength * change_pct < 0:
            return MarketRegime.REVERSAL
        
        # Check for volatility expansion
        if volatility > 3.0 or volume_ratio > 2.0:
            return MarketRegime.VOLATILITY_EXPANSION
        
        # Check for low participation
        if volume_ratio < 0.5:
            return MarketRegime.LOW_PARTICIPATION
        
        # Check for trend
        if trend_strength > self.trend_threshold and change_pct > 0.5:
            return MarketRegime.TREND_UP
        elif trend_strength < -self.trend_threshold and change_pct < -0.5:
            return MarketRegime.TREND_DOWN
        
        # Default to range/chop
        return MarketRegime.RANGE_CHOP
    
    def _classify_volatility(self, volatility: float) -> VolatilityRegime:
        """Classify volatility regime."""
        if volatility < 0.5:
            return VolatilityRegime.LOW
        elif volatility < 1.5:
            return VolatilityRegime.NORMAL
        elif volatility < 3.0:
            return VolatilityRegime.ELEVATED
        else:
            return VolatilityRegime.EXTREME
    
    def get_suppression_reason(
        self,
        regime: RegimeContext,
    ) -> Optional[str]:
        """
        Get suppression reason based on regime conditions.
        
        Returns reason string if signal should be suppressed, None otherwise.
        """
        # Suppress in extreme volatility
        if regime.volatility_regime == VolatilityRegime.EXTREME:
            return f"Extreme volatility regime ({regime.volatility_percent:.1f}%)"
        
        # Suppress in low participation
        if regime.regime == MarketRegime.LOW_PARTICIPATION:
            return f"Low participation environment (volume ratio: {regime.volume_ratio:.2f})"
        
        # Suppress in very low confidence
        if regime.confidence < 0.3:
            return f"Low regime confidence ({regime.confidence:.2f})"
        
        return None


def classify_session_regime(
    bars: list,
) -> RegimeContext:
    """
    Classify regime for a complete session.
    
    Args:
        bars: List of price bars with close, volume, timestamp
    
    Returns:
        RegimeContext for session
    """
    classifier = RegimeClassifier()
    
    for bar in bars:
        classifier.add_bar(
            price=bar.close,
            volume=bar.volume,
            timestamp=bar.timestamp,
        )
    
    if bars:
        return classifier.classify_regime(bars[-1].close)
    
    return RegimeContext(
        regime=MarketRegime.RANGE_CHOP,
        volatility_regime=VolatilityRegime.NORMAL,
        confidence=0.5,
        trend_strength=0.0,
        volatility_percent=1.0,
        volume_ratio=1.0,
        timestamp=datetime.now(),
    )
