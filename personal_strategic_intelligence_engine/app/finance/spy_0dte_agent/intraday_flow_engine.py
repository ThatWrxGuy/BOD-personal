"""Intraday Flow Engine - BB-FIN-019"""

from typing import Optional, Dict, List
import logging
import random

from app.finance.spy_0dte_agent.spy_0dte_models import IntradayVolatilityState, IntradayPhase

logger = logging.getLogger(__name__)


class IntradayFlowEngine:
    """Analyzes intraday flow patterns for 0DTE opportunities."""

    def __init__(self):
        self._vwap_history: List[float] = []

    def analyze(
        self,
        candles: Optional[List[Dict]] = None,
    ) -> IntradayVolatilityState:
        """Analyze intraday volatility state."""
        # Use demo data if not provided
        if candles is None:
            candles = self._generate_demo_candles()
        
        if not candles:
            return self._default_state()
        
        # Calculate metrics
        current_price = candles[-1].get("close", 500)
        
        # Session range
        session_high = max([c.get("high", 0) for c in candles])
        session_low = min([c.get("low", 0) for c in candles])
        
        range_pct = ((session_high - session_low) / session_low * 100) if session_low > 0 else 0
        
        # Determine phase
        phase = self._determine_phase(candles, session_high, session_low, current_price)
        
        # VWAP (simplified)
        vwap = self._calculate_vwap(candles)
        vwap_distance = None
        if vwap and current_price > 0:
            vwap_distance = ((current_price - vwap) / vwap) * 100
        
        # Compression analysis
        compression = self._analyze_compression(candles, session_high, session_low)
        
        # IV (simplified - using range as proxy)
        current_iv = self._estimate_iv(candles)
        
        # IV percentile
        iv_percentile = self._estimate_iv_percentile(current_iv)
        
        return IntradayVolatilityState(
            symbol="SPY",
            phase=phase,
            current_iv=current_iv,
            iv_percentile=iv_percentile,
            session_high=session_high,
            session_low=session_low,
            range_pct=range_pct,
            compression_ratio=compression.get("ratio"),
            expansion_probability=compression.get("expansion_prob", 0.5),
            vwap=vwap,
            vwap_distance_pct=vwap_distance,
        )

    def _determine_phase(
        self,
        candles: List[Dict],
        session_high: float,
        session_low: float,
        current_price: float,
    ) -> IntradayPhase:
        """Determine current intraday phase."""
        if len(candles) < 10:
            return IntradayPhase.CONSOLIDATION
        
        # Opening range: first 15-30 minutes
        if len(candles) <= 5:
            return IntradayPhase.OPENING_RANGE
        
        # Check for trend
        closes = [c.get("close", 0) for c in candles]
        
        # Recent momentum
        recent = closes[-5:]
        older = closes[:-5]
        
        if not recent or not older:
            return IntradayPhase.CONSOLIDATION
        
        avg_recent = sum(recent) / len(recent)
        avg_older = sum(older) / len(older)
        
        pct_change = (avg_recent - avg_older) / avg_older if avg_older > 0 else 0
        
        if abs(pct_change) > 0.01:  # >1% move
            return IntradayPhase.TRENDING
        
        # Check for reversal
        if len(candles) >= 3:
            if closes[-1] > closes[-2] < closes[-3]:
                return IntradayPhase.REVERSAL
            if closes[-1] < closes[-2] > closes[-3]:
                return IntradayPhase.REVERSAL
        
        # Check range position
        range_position = (current_price - session_low) / (session_high - session_low) if session_high > session_low else 0.5
        
        # Near session end
        if len(candles) > 30:
            return IntradayPhase.CLOSING
        
        return IntradayPhase.CONSOLIDATION

    def _calculate_vwap(self, candles: List[Dict]) -> Optional[float]:
        """Calculate Volume Weighted Average Price."""
        if not candles:
            return None
        
        total_pv = 0
        total_vol = 0
        
        for c in candles:
            typical_price = (c.get("high", 0) + c.get("low", 0) + c.get("close", 0)) / 3
            volume = c.get("volume", 0)
            
            total_pv += typical_price * volume
            total_vol += volume
        
        if total_vol > 0:
            return total_pv / total_vol
        return None

    def _analyze_compression(
        self,
        candles: List[Dict],
        session_high: float,
        session_low: float,
    ) -> Dict:
        """Analyze volatility compression."""
        if len(candles) < 10:
            return {"ratio": 1.0, "expansion_prob": 0.5}
        
        # Calculate recent range vs older range
        recent = candles[-10:]
        older = candles[:-10]
        
        recent_range = max([c.get("high", 0) for c in recent]) - min([c.get("low", 0) for c in recent])
        older_range = max([c.get("high", 0) for c in older]) - min([c.get("low", 0) for c in older]) if older else recent_range
        
        if older_range == 0:
            return {"ratio": 1.0, "expansion_prob": 0.5}
        
        ratio = recent_range / older_range
        
        # High compression = high expansion probability
        if ratio < 0.5:
            expansion_prob = 0.8
        elif ratio < 0.7:
            expansion_prob = 0.6
        elif ratio < 1.0:
            expansion_prob = 0.4
        else:
            expansion_prob = 0.3
        
        return {"ratio": ratio, "expansion_prob": expansion_prob}

    def _estimate_iv(self, candles: List[Dict]) -> float:
        """Estimate implied volatility from price action."""
        if len(candles) < 5:
            return 15.0
        
        # Calculate returns
        closes = [c.get("close", 0) for c in candles]
        returns = []
        for i in range(1, len(closes)):
            if closes[i-1] > 0:
                returns.append((closes[i] - closes[i-1]) / closes[i-1])
        
        if not returns:
            return 15.0
        
        # Simple volatility estimate (annualized)
        import math
        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        std_dev = math.sqrt(variance)
        
        # Annualize (assuming 5-minute candles = 78 per day)
        iv = std_dev * math.sqrt(78) * 100
        
        return min(50, max(10, iv))  # Clamp between 10-50

    def _estimate_iv_percentile(self, iv: float) -> float:
        """Estimate IV percentile (simplified)."""
        # Assume historical IV range of 10-40
        percentile = (iv - 10) / 30
        return max(0, min(1, percentile))

    def _default_state(self) -> IntradayVolatilityState:
        """Return default intraday state."""
        return IntradayVolatilityState(
            symbol="SPY",
            phase=IntradayPhase.CONSOLIDATION,
            current_iv=15.0,
            iv_percentile=0.25,
            session_high=505,
            session_low=495,
            range_pct=2.0,
            compression_ratio=1.0,
            expansion_probability=0.5,
            vwap=500,
            vwap_distance_pct=0.0,
        )

    def detect_flow_signals(self, candles: List[Dict]) -> Dict:
        """Detect specific intraday flow signals."""
        if len(candles) < 5:
            return {"signals": [], "summary": "Insufficient data"}
        
        signals = []
        
        # Opening range break
        if self._is_opening_range_breakout(candles):
            signals.append({
                "type": "opening_range_breakout",
                "direction": "bullish" if candles[-1].get("close", 0) > candles[4].get("high", 0) else "bearish",
                "strength": 0.7,
            })
        
        # VWAP reclaim
        if self._is_vwap_reclaim(candles):
            signals.append({
                "type": "vwap_reclaim",
                "direction": "bullish",
                "strength": 0.6,
            })
        
        # Liquidity sweep
        if self._is_liquidity_sweep(candles):
            signals.append({
                "type": "liquidity_sweep",
                "direction": "bullish",
                "strength": 0.5,
            })
        
        # Trend continuation
        if self._is_trend_continuation(candles):
            signals.append({
                "type": "trend_continuation",
                "direction": "bullish" if candles[-1].get("close", 0) > candles[0].get("close", 0) else "bearish",
                "strength": 0.6,
            })
        
        return {
            "signals": signals,
            "summary": f"Detected {len(signals)} flow signals" if signals else "No clear flow signals",
        }

    def _is_opening_range_breakout(self, candles: List[Dict]) -> bool:
        """Detect opening range breakout."""
        if len(candles) < 5:
            return False
        
        opening_range_high = max([c.get("high", 0) for c in candles[:5]])
        opening_range_low = min([c.get("low", 0) for c in candles[:5]])
        
        current_close = candles[-1].get("close", 0)
        
        return current_close > opening_range_high or current_close < opening_range_low

    def _is_vwap_reclaim(self, candles: List[Dict]) -> bool:
        """Detect VWAP reclaim."""
        vwap = self._calculate_vwap(candles[:-3])  # Earlier candles
        current_close = candles[-1].get("close", 0)
        
        if not vwap:
            return False
        
        # Reclaim = price crosses above/below VWAP
        return (current_close > vwap and candles[-3].get("close", 0) < vwap) or \
               (current_close < vwap and candles[-3].get("close", 0) > vwap)

    def _is_liquidity_sweep(self, candles: List[Dict]) -> bool:
        """Detect liquidity sweep pattern."""
        if len(candles) < 3:
            return False
        
        # High volume with price movement
        recent = candles[-1]
        volume = recent.get("volume", 0)
        avg_volume = sum([c.get("volume", 0) for c in candles[:-1]]) / len(candles[:-1])
        
        if volume > avg_volume * 1.5:
            # Check for wick penetration
            if recent.get("low", 0) < candles[-2].get("low", 0) * 0.999:
                return True
            if recent.get("high", 0) > candles[-2].get("high", 0) * 1.001:
                return True
        
        return False

    def _is_trend_continuation(self, candles: List[Dict]) -> bool:
        """Detect trend continuation pattern."""
        if len(candles) < 10:
            return False
        
        # Higher highs and higher lows = uptrend
        highs = [c.get("high", 0) for c in candles]
        lows = [c.get("low", 0) for c in candles]
        
        recent_higher = sum(1 for i in range(5, len(highs)) if highs[i] > highs[i-1])
        recent_lower = sum(1 for i in range(5, len(lows)) if lows[i] > lows[i-1])
        
        return recent_higher >= 3 or recent_lower >= 3

    def _generate_demo_candles(self) -> List[Dict]:
        """Generate demo candle data."""
        from datetime import datetime, timedelta
        
        candles = []
        now = datetime.utcnow()
        price = 500.0
        
        for i in range(30):
            # Build momentum
            if i < 20:
                price *= (1 + random.uniform(-0.001, 0.001))
            else:
                price *= (1 + random.uniform(0.001, 0.003))
            
            candles.append({
                "timestamp": (now - timedelta(minutes=30-i)).isoformat(),
                "open": round(price * 0.999, 2),
                "high": round(price * 1.002, 2),
                "low": round(price * 0.998, 2),
                "close": round(price, 2),
                "volume": random.randint(300000, 1500000),
            })
        
        return candles


# Singleton
_intraday_flow_engine: Optional[IntradayFlowEngine] = None


def get_intraday_flow_engine() -> IntradayFlowEngine:
    """Get the singleton IntradayFlowEngine instance."""
    global _intraday_flow_engine
    if _intraday_flow_engine is None:
        _intraday_flow_engine = IntradayFlowEngine()
    return _intraday_flow_engine
