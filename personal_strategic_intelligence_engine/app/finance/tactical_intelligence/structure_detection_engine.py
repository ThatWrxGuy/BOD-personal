"""Structure Detection Engine - BB-FIN-018"""

from typing import Optional, List, Dict
import logging

from app.finance.tactical_intelligence.tactical_models import (
    MarketStructure,
    MarketStructureState,
)

logger = logging.getLogger(__name__)


class StructureDetectionEngine:
    """Analyzes price structure and trend patterns."""

    def __init__(self):
        self._price_history: Dict[str, List[Dict]] = {}

    def add_candle(
        self,
        symbol: str,
        timestamp: str,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: float,
    ) -> None:
        """Add candle data to history."""
        if symbol not in self._price_history:
            self._price_history[symbol] = []
        
        self._price_history[symbol].append({
            "timestamp": timestamp,
            "open": open,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        })
        
        # Keep last 100 candles per symbol
        if len(self._price_history[symbol]) > 100:
            self._price_history[symbol] = self._price_history[symbol][-100:]

    def analyze_structure(
        self,
        symbol: str,
        timeframe: str = "5m",
        candles: Optional[List[Dict]] = None,
    ) -> MarketStructureState:
        """Analyze market structure."""
        # Use demo data if not provided
        if candles is None:
            candles = self._generate_demo_candles(symbol, timeframe)
        
        if not candles:
            return MarketStructureState(
                symbol=symbol,
                timeframe=timeframe,
                structure=MarketStructure.UNKNOWN,
                trend_strength=0.0,
            )
        
        # Store in history
        for c in candles:
            self.add_candle(
                symbol, c.get("timestamp", ""),
                c.get("open", 0), c.get("high", 0),
                c.get("low", 0), c.get("close", 0),
                c.get("volume", 0)
            )
        
        # Get current values
        current = candles[-1]
        close = current.get("close", 0)
        high = current.get("high", 0)
        low = current.get("low", 0)
        
        # Analyze structure
        structure = self._detect_structure(candles)
        trend_strength = self._calculate_trend_strength(candles)
        higher_highs, lower_lows = self._count_swings(candles)
        
        # Calculate range metrics
        range_width = None
        compression_ratio = None
        if len(candles) >= 10:
            recent = candles[-10:]
            highs = [c.get("high", 0) for c in recent]
            lows = [c.get("low", 0) for c in recent]
            range_width = max(highs) - min(lows)
            if close > 0:
                compression_ratio = range_width / close
        
        return MarketStructureState(
            symbol=symbol,
            timeframe=timeframe,
            structure=structure,
            high=high,
            low=low,
            close=close,
            trend_strength=trend_strength,
            consecutive_higher_highs=higher_highs,
            consecutive_lower_lows=lower_lows,
            range_width=range_width,
            compression_ratio=compression_ratio,
        )

    def _detect_structure(self, candles: List[Dict]) -> MarketStructure:
        """Detect current market structure."""
        if len(candles) < 5:
            return MarketStructure.UNKNOWN
        
        # Get recent candles
        recent = candles[-5:]
        closes = [c.get("close", 0) for c in recent]
        highs = [c.get("high", 0) for c in recent]
        lows = [c.get("low", 0) for c in recent]
        
        # Check for consolidation (tight range)
        range_pct = (max(highs) - min(lows)) / closes[-1] if closes[-1] > 0 else 0
        if range_pct < 0.005:  # Less than 0.5% range
            return MarketStructure.CONSOLIDATION
        
        # Check for breakout
        if len(candles) >= 10:
            prev_range_high = max([c.get("high", 0) for c in candles[-10:-5]])
            prev_range_low = min([c.get("low", 0) for c in candles[-10:-5]])
            
            if closes[-1] > prev_range_high:
                return MarketStructure.BREAKOUT_UP
            elif closes[-1] < prev_range_low:
                return MarketStructure.BREAKOUT_DOWN
        
        # Check for trend
        first_close = closes[0]
        last_close = closes[-1]
        pct_change = (last_close - first_close) / first_close if first_close > 0 else 0
        
        if pct_change > 0.02:  # More than 2% up
            return MarketStructure.TREND_UP
        elif pct_change < -0.02:
            return MarketStructure.TREND_DOWN
        
        # Check for reversal
        if len(candles) >= 3:
            if closes[-1] > closes[-2] < closes[-3]:  # Hammer/bottom
                return MarketStructure.REVERSAL
        
        return MarketStructure.CONSOLIDATION

    def _calculate_trend_strength(self, candles: List[Dict]) -> float:
        """Calculate trend strength (0-1)."""
        if len(candles) < 5:
            return 0.0
        
        closes = [c.get("close", 0) for c in candles]
        
        # Simple linear regression slope
        n = len(closes)
        if n < 2:
            return 0.0
        
        # Calculate average change
        changes = [closes[i] - closes[i-1] for i in range(1, n)]
        avg_change = sum(changes) / len(changes) if changes else 0
        
        # Normalize by average price
        avg_price = sum(closes) / n
        if avg_price == 0:
            return 0.0
        
        normalized_change = abs(avg_change) / avg_price * 100
        
        # Convert to 0-1 scale
        strength = min(1.0, normalized_change / 2.0)
        
        # Adjust for consistency
        if changes:
            consistency = 1 - (len([c for c in changes if c * avg_change < 0]) / len(changes))
            strength = strength * 0.7 + consistency * 0.3
        
        return strength

    def _count_swings(self, candles: List[Dict]) -> tuple:
        """Count consecutive higher highs and lower lows."""
        if len(candles) < 3:
            return 0, 0
        
        higher_highs = 0
        lower_lows = 0
        
        for i in range(2, len(candles)):
            if (candles[i].get("high", 0) > candles[i-1].get("high", 0) > candles[i-2].get("high", 0)):
                higher_highs += 1
            if (candles[i].get("low", 0) < candles[i-1].get("low", 0) < candles[i-2].get("low", 0)):
                lower_lows += 1
        
        return higher_highs, lower_lows

    def _generate_demo_candles(self, symbol: str, timeframe: str) -> List[Dict]:
        """Generate demo candle data."""
        import random
        from datetime import datetime, timedelta
        
        # Base price varies by symbol
        base_prices = {
            "SPY": 500.0,
            "QQQ": 440.0,
            "AAPL": 185.0,
            "TSLA": 250.0,
            "NVDA": 480.0,
        }
        base = base_prices.get(symbol, 100.0)
        
        # Generate 20 candles
        candles = []
        now = datetime.utcnow()
        price = base
        
        for i in range(20):
            # Random walk with drift
            change = random.uniform(-0.5, 0.5)  # -0.5% to +0.5% per candle
            price *= (1 + change / 100)
            
            # Create OHLC
            open_price = price * (1 + random.uniform(-0.001, 0.001))
            close_price = price
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.002))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.002))
            
            candles.append({
                "timestamp": (now - timedelta(minutes=20-i)).isoformat(),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": random.randint(100000, 1000000),
            })
        
        return candles

    def get_structure_description(self, state: MarketStructureState) -> str:
        """Get human-readable structure description."""
        descriptions = {
            MarketStructure.TREND_UP: f"Bullish trend (strength: {state.trend_strength:.0%})",
            MarketStructure.TREND_DOWN: f"Bearish trend (strength: {state.trend_strength:.0%})",
            MarketStructure.CONSOLIDATION: "Consolidation phase - waiting for breakout",
            MarketStructure.BREAKOUT_UP: "Bullish breakout from range",
            MarketStructure.BREAKOUT_DOWN: "Bearish breakout from range",
            MarketStructure.REVERSAL: "Potential reversal signal",
            MarketStructure.UNKNOWN: "Insufficient data",
        }
        
        base = descriptions.get(state.structure, "Unknown")
        
        if state.compression_ratio and state.compression_ratio < 0.01:
            base += " - HIGH COMPRESSION"
        
        return base


# Singleton
_structure_engine: Optional[StructureDetectionEngine] = None


def get_structure_detection_engine() -> StructureDetectionEngine:
    """Get the singleton StructureDetectionEngine instance."""
    global _structure_engine
    if _structure_engine is None:
        _structure_engine = StructureDetectionEngine()
    return _structure_engine
