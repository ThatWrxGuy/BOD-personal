"""Breakout Confirmation Engine - BB-FIN-018"""

from typing import Optional, List, Dict
import logging

from app.finance.tactical_intelligence.tactical_models import (
    BreakoutQuality,
    BreakoutSignal,
)

logger = logging.getLogger(__name__)


class BreakoutConfirmationEngine:
    """Confirms breakout validity and quality."""

    def __init__(self):
        self._breakout_history: Dict[str, List[Dict]] = {}

    def analyze_breakout(
        self,
        symbol: str,
        timeframe: str = "5m",
        candles: Optional[List[Dict]] = None,
    ) -> Optional[BreakoutSignal]:
        """Analyze if a breakout is occurring and confirm its validity."""
        # Use demo data if not provided
        if candles is None:
            candles = self._generate_demo_candles(symbol, timeframe)
        
        if len(candles) < 10:
            return None
        
        # Check for breakout
        breakout = self._detect_breakout(candles)
        
        if not breakout:
            return None
        
        # Analyze quality
        quality = self._assess_quality(candles, breakout["direction"])
        
        # Calculate metrics
        strength = self._calculate_strength(candles, breakout)
        
        volume_conf = self._confirm_with_volume(candles)
        momentum_conf = self._confirm_with_momentum(candles)
        
        # Follow-through and false breakout risk
        follow_through = self._calculate_follow_through_probability(
            strength, volume_conf, momentum_conf
        )
        false_risk = self._calculate_false_breakout_risk(
            candles, breakout, quality, strength
        )
        
        return BreakoutSignal(
            symbol=symbol,
            timeframe=timeframe,
            direction=breakout["direction"],
            breakout_level=breakout["level"],
            previous_range_high=breakout.get("range_high", 0),
            previous_range_low=breakout.get("range_low", 0),
            quality=quality,
            strength=strength,
            volume_confirmation=volume_conf,
            momentum_confirmation=momentum_conf,
            follow_through_probability=follow_through,
            false_breakout_risk=false_risk,
            breakout_valid=false_risk < 0.5,
        )

    def _detect_breakout(self, candles: List[Dict]) -> Optional[Dict]:
        """Detect if a breakout is occurring."""
        if len(candles) < 10:
            return None
        
        # Previous range (last 5 candles before current)
        prev_candles = candles[-10:-5]
        current = candles[-1]
        
        range_high = max([c.get("high", 0) for c in prev_candles])
        range_low = min([c.get("low", 0) for c in prev_candles])
        
        close = current.get("close", 0)
        
        # Check for breakout
        if close > range_high:
            return {
                "direction": "bullish",
                "level": close,
                "range_high": range_high,
                "range_low": range_low,
            }
        elif close < range_low:
            return {
                "direction": "bearish",
                "level": close,
                "range_high": range_high,
                "range_low": range_low,
            }
        
        return None

    def _assess_quality(self, candles: List[Dict], direction: str) -> BreakoutQuality:
        """Assess breakout quality."""
        current = candles[-1]
        close = current.get("close", 0)
        open_price = current.get("open", 0)
        
        # Calculate body size
        body = abs(close - open_price) / open_price if open_price > 0 else 0
        
        # Calculate wick size
        high = current.get("high", 0)
        low = current.get("low", 0)
        wick = (high - low) / close if close > 0 else 0
        
        # Quality based on candle composition
        if direction == "bullish":
            # Good bullish breakout: large green candle, small wick
            if body > 0.003 and wick < body:  # >0.3% body, wick < body
                return BreakoutQuality.STRONG
            elif body > 0.001:
                return BreakoutQuality.MODERATE
            else:
                return BreakoutQuality.WEAK
        else:
            # Good bearish breakout: large red candle, small wick
            if body > 0.003 and wick < body:
                return BreakoutQuality.STRONG
            elif body > 0.001:
                return BreakoutQuality.MODERATE
            else:
                return BreakoutQuality.WEAK

    def _calculate_strength(self, candles: List[Dict], breakout: Dict) -> float:
        """Calculate breakout strength (0-1)."""
        direction = breakout["direction"]
        
        # Calculate displacement
        if direction == "bullish":
            displacement = (breakout["level"] - breakout["range_low"]) / breakout["range_low"]
        else:
            displacement = (breakout["range_high"] - breakout["level"]) / breakout["range_high"]
        
        # Normalize (5% displacement = max strength)
        strength = min(1.0, displacement / 0.05)
        
        return strength

    def _confirm_with_volume(self, candles: List[Dict]) -> bool:
        """Check volume confirmation."""
        if len(candles) < 5:
            return False
        
        # Compare recent volume to average
        recent = candles[-3:]
        older = candles[:-3]
        
        recent_vol = sum([c.get("volume", 0) for c in recent]) / len(recent)
        older_vol = sum([c.get("volume", 0) for c in older]) / len(older) if older else recent_vol
        
        # Volume should be 1.5x average for confirmation
        return recent_vol > older_vol * 1.5

    def _confirm_with_momentum(self, candles: List[Dict]) -> bool:
        """Check momentum confirmation."""
        if len(candles) < 5:
            return False
        
        # Check if momentum is aligned with direction
        closes = [c.get("close", 0) for c in candles]
        
        # Compare first half to second half
        first_half = closes[:len(closes)//2]
        second_half = closes[len(closes)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        # Positive momentum = higher closes in second half
        return second_avg > first_avg

    def _calculate_follow_through_probability(
        self,
        strength: float,
        volume_conf: bool,
        momentum_conf: bool,
    ) -> float:
        """Calculate probability of follow-through."""
        prob = 0.5  # Base
        
        # Stronger breakout = more follow-through
        prob += strength * 0.2
        
        # Volume confirmation
        if volume_conf:
            prob += 0.15
        
        # Momentum confirmation
        if momentum_conf:
            prob += 0.15
        
        return min(1.0, prob)

    def _calculate_false_breakout_risk(
        self,
        candles: List[Dict],
        breakout: Dict,
        quality: BreakoutQuality,
        strength: float,
    ) -> float:
        """Calculate risk of false breakout."""
        risk = 0.3  # Base risk
        
        # Poor quality = higher risk
        if quality == BreakoutQuality.WEAK:
            risk += 0.3
        elif quality == BreakoutQuality.MODERATE:
            risk += 0.1
        
        # Weak strength = higher risk
        if strength < 0.3:
            risk += 0.2
        
        # Check for wick penetration (potential false breakout)
        current = candles[-1]
        high = current.get("high", 0)
        low = current.get("low", 0)
        
        if breakout["direction"] == "bullish":
            # Check if close is below high (wick only broke out)
            if current.get("close", 0) < high * 0.999:
                risk += 0.2
        else:
            if current.get("close", 0) > low * 1.001:
                risk += 0.2
        
        return min(1.0, risk)

    def _generate_demo_candles(self, symbol: str, timeframe: str) -> List[Dict]:
        """Generate demo candle data with breakout pattern."""
        import random
        from datetime import datetime, timedelta
        
        base_prices = {"SPY": 500.0, "QQQ": 440.0, "AAPL": 185.0}
        base = base_prices.get(symbol, 100.0)
        
        candles = []
        now = datetime.utcnow()
        price = base
        
        # Create consolidation then breakout
        for i in range(15):
            if i < 10:
                # Consolidation
                price *= (1 + random.uniform(-0.001, 0.001))
            else:
                # Breakout
                price *= (1 + random.uniform(0.002, 0.005))
            
            candles.append({
                "timestamp": (now - timedelta(minutes=15-i)).isoformat(),
                "open": round(price * (1 + random.uniform(-0.001, 0.001)), 2),
                "high": round(price * (1 + random.uniform(0, 0.002)), 2),
                "low": round(price * (1 - random.uniform(0, 0.002)), 2),
                "close": round(price, 2),
                "volume": random.randint(100000, 500000) * (1.5 if i > 10 else 1),
            })
        
        return candles


# Singleton
_breakout_engine: Optional[BreakoutConfirmationEngine] = None


def get_breakout_confirmation_engine() -> BreakoutConfirmationEngine:
    """Get the singleton BreakoutConfirmationEngine instance."""
    global _breakout_engine
    if _breakout_engine is None:
        _breakout_engine = BreakoutConfirmationEngine()
    return _breakout_engine
