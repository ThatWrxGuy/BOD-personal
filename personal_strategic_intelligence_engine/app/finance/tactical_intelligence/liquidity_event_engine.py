"""Liquidity Event Engine - BB-FIN-018"""

from typing import Optional, List, Dict
import logging

from app.finance.tactical_intelligence.tactical_models import (
    LiquidityEventType,
    LiquiditySweepEvent,
)

logger = logging.getLogger(__name__)


class LiquidityEventEngine:
    """Detects liquidity events and order flow patterns."""

    def __init__(self):
        self._recent_events: Dict[str, List[Dict]] = {}

    def detect_events(
        self,
        symbol: str,
        candles: Optional[List[Dict]] = None,
    ) -> List[LiquiditySweepEvent]:
        """Detect liquidity events from candle data."""
        if candles is None:
            candles = self._generate_demo_candles(symbol)
        
        events = []
        
        # Analyze each candle for liquidity events
        for i in range(1, len(candles)):
            event = self._analyze_candle(candles[i], candles[i-1], candles[i-2] if i >= 2 else None)
            if event:
                events.append(event)
        
        # Limit to last 5 events
        return events[-5:]

    def _analyze_candle(
        self,
        candle: Dict,
        prev_candle: Optional[Dict],
        prev_prev_candle: Optional[Dict],
    ) -> Optional[LiquiditySweepEvent]:
        """Analyze a single candle for liquidity events."""
        if not candle or not prev_candle:
            return None
        
        high = candle.get("high", 0)
        low = candle.get("low", 0)
        close = candle.get("close", 0)
        open_price = candle.get("open", 0)
        volume = candle.get("volume", 0)
        
        prev_high = prev_candle.get("high", 0)
        prev_low = prev_candle.get("low", 0)
        prev_close = prev_candle.get("close", 0)
        
        # Check for stop hunt (wick through previous low/high)
        if prev_low > 0 and low < prev_low * 0.998:  # 0.2% below previous low
            return LiquiditySweepEvent(
                symbol=candle.get("symbol", ""),
                event_type=LiquidityEventType.STOP_HUNT,
                sweep_level=prev_low,
                stop_level=low,
                direction="bullish",  # Stop hunt typically from longs
                wick_penetration=True,
                interpretation="Stop hunt below recent low - liquidity collected",
            )
        
        if prev_high > 0 and high > prev_high * 1.002:  # 0.2% above previous high
            return LiquiditySweepEvent(
                symbol=candle.get("symbol", ""),
                event_type=LiquidityEventType.STOP_HUNT,
                sweep_level=prev_high,
                stop_level=high,
                direction="bearish",
                wick_penetration=True,
                interpretation="Stop hunt above recent high - liquidity collected",
            )
        
        # Check for liquidity sweep (volume surge with wick)
        if volume > 500000:  # High volume threshold
            if low < prev_low and open_price > close:  # Bearish candle breaking low
                return LiquiditySweepEvent(
                    symbol=candle.get("symbol", ""),
                    event_type=LiquidityEventType.LIQUIDITY_SWEEP,
                    sweep_level=prev_low,
                    direction="bearish",
                    volume_surge=True,
                    interpretation="Liquidity sweep of stops below - potential reversal",
                )
            
            if high > prev_high and open_price < close:  # Bullish candle breaking high
                return LiquiditySweepEvent(
                    symbol=candle.get("symbol", ""),
                    event_type=LiquidityEventType.LIQUIDITY_SWEEP,
                    sweep_level=prev_high,
                    direction="bullish",
                    volume_surge=True,
                    interpretation="Liquidity sweep of stops above - momentum continuing",
                )
        
        # Check for false breakout
        if prev_prev_candle:
            prev_prev_high = prev_prev_candle.get("high", 0)
            prev_prev_low = prev_prev_candle.get("low", 0)
            
            if high > prev_prev_high and close < prev_prev_high:  # Failed breakout up
                return LiquiditySweepEvent(
                    symbol=candle.get("symbol", ""),
                    event_type=LiquidityEventType.FALSE_BREAKOUT,
                    sweep_level=prev_prev_high,
                    direction="bearish",
                    interpretation="False breakout - failed to hold above resistance",
                )
            
            if low < prev_prev_low and close > prev_prev_low:  # Failed breakout down
                return LiquiditySweepEvent(
                    symbol=candle.get("symbol", ""),
                    event_type=LiquidityEventType.FALSE_BREAKOUT,
                    sweep_level=prev_prev_low,
                    direction="bullish",
                    interpretation="False breakdown - failed to hold below support",
                )
        
        return None

    def _generate_demo_candles(self, symbol: str) -> List[Dict]:
        """Generate demo candle data with some liquidity events."""
        import random
        from datetime import datetime, timedelta
        
        base_prices = {"SPY": 500.0, "QQQ": 440.0, "AAPL": 185.0}
        base = base_prices.get(symbol, 100.0)
        
        candles = []
        now = datetime.utcnow()
        price = base
        
        for i in range(15):
            # Occasionally create a liquidity event
            is_event = random.random() < 0.15  # 15% chance
            
            if is_event:
                # Create a wick event
                if random.random() < 0.5:
                    # Stop hunt down
                    price *= 0.998
                    high = price * 1.001
                    low = price * 0.997
                else:
                    # Stop hunt up
                    price *= 1.002
                    high = price * 1.003
                    low = price * 0.999
            else:
                price *= (1 + random.uniform(-0.002, 0.002))
                high = price * (1 + random.uniform(0, 0.001))
                low = price * (1 - random.uniform(0, 0.001))
            
            candles.append({
                "symbol": symbol,
                "timestamp": (now - timedelta(minutes=15-i)).isoformat(),
                "open": round(price * 0.999, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(price, 2),
                "volume": random.randint(100000, 800000),
            })
        
        return candles


# Singleton
_liquidity_engine: Optional[LiquidityEventEngine] = None


def get_liquidity_event_engine() -> LiquidityEventEngine:
    """Get the singleton LiquidityEventEngine instance."""
    global _liquidity_engine
    if _liquidity_engine is None:
        _liquidity_engine = LiquidityEventEngine()
    return _liquidity_engine
