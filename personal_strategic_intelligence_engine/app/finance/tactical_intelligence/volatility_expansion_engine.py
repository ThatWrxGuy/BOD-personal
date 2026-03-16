"""Volatility Expansion Engine - BB-FIN-018"""

from typing import Optional, List, Dict
import logging

from app.finance.tactical_intelligence.tactical_models import (
    VolatilityState,
    VolatilityExpansionSignal,
)

logger = logging.getLogger(__name__)


class VolatilityExpansionEngine:
    """Detects volatility compression and expansion patterns."""

    def __init__(self):
        self._range_history: Dict[str, List[float]] = {}

    def analyze_volatility(
        self,
        symbol: str,
        timeframe: str = "5m",
        candles: Optional[List[Dict]] = None,
    ) -> VolatilityExpansionSignal:
        """Analyze volatility state and expansion potential."""
        # Use demo data if not provided
        if candles is None:
            candles = self._generate_demo_candles(symbol, timeframe)
        
        if not candles:
            return VolatilityExpansionSignal(
                symbol=symbol,
                timeframe=timeframe,
                current_state=VolatilityState.STABLE,
                expansion_probability=0.5,
            )
        
        # Calculate ranges
        ranges = []
        for c in candles:
            high = c.get("high", 0)
            low = c.get("low", 0)
            if high > 0:
                ranges.append((high - low) / high * 100)  # As percentage
        
        # Current range
        current_range = ranges[-1] if ranges else 0
        
        # Historical analysis
        if len(ranges) >= 10:
            avg_range = sum(ranges[-10:]) / 10
            min_range = min(ranges[-10:])
            max_range = max(ranges[-10:])
        else:
            avg_range = sum(ranges) / len(ranges) if ranges else 0
            min_range = min(ranges) if ranges else 0
            max_range = max(ranges) if ranges else 0
        
        # Compression ratio (current vs average)
        compression_ratio = current_range / avg_range if avg_range > 0 else 1.0
        
        # Range contraction
        range_contraction = None
        if len(ranges) >= 5:
            recent_avg = sum(ranges[-5:]) / 5
            older_avg = sum(ranges[-10:-5]) / 5 if len(ranges) >= 10 else recent_avg
            range_contraction = (older_avg - recent_avg) / older_avg if older_avg > 0 else 0
        
        # Determine state
        state = self._determine_state(compression_ratio, range_contraction)
        
        # Calculate expansion probability
        expansion_prob = self._calculate_expansion_probability(
            compression_ratio, range_contraction, state
        )
        
        # Expected move
        expected_move = None
        if state == VolatilityState.COMPRESSED and avg_range > 0:
            # Expected expansion to average range
            expected_move = avg_range
        
        # Determine direction bias
        direction = self._determine_direction(candles)
        
        # Generate signal
        signal = self._generate_signal(state, expansion_prob, direction)
        
        return VolatilityExpansionSignal(
            symbol=symbol,
            timeframe=timeframe,
            current_state=state,
            compression_ratio=compression_ratio,
            range_contraction_pct=range_contraction,
            expansion_probability=expansion_prob,
            expected_move_pct=expected_move,
            expansion_direction=direction,
            signal=signal,
        )

    def _determine_state(
        self,
        compression_ratio: float,
        contraction: Optional[float],
    ) -> VolatilityState:
        """Determine current volatility state."""
        if compression_ratio < 0.6:
            return VolatilityState.COMPRESSED
        elif compression_ratio > 1.4:
            return VolatilityState.EXPANDING
        
        if contraction is not None and contraction > 0.2:
            return VolatilityState.CONTRACTING
        elif contraction is not None and contraction < -0.2:
            return VolatilityState.EXPANDING
        
        return VolatilityState.STABLE

    def _calculate_expansion_probability(
        self,
        compression_ratio: float,
        contraction: Optional[float],
        state: VolatilityState,
    ) -> float:
        """Calculate probability of volatility expansion."""
        prob = 0.5  # Base probability
        
        # Compression increases expansion probability
        if state == VolatilityState.COMPRESSED:
            prob = 0.7 + (1 - compression_ratio) * 0.2
        
        # Recent contraction also increases probability
        if contraction and contraction > 0.15:
            prob += 0.15
        
        # Expansion decreases (already happening)
        if state == VolatilityState.EXPANDING:
            prob = 0.3
        
        return min(1.0, max(0.0, prob))

    def _determine_direction(self, candles: List[Dict]) -> Optional[str]:
        """Determine likely direction of expansion."""
        if len(candles) < 5:
            return None
        
        # Compare recent momentum
        recent = candles[-3:]
        older = candles[-6:-3] if len(candles) >= 6 else candles[:-3]
        
        if not recent or not older:
            return None
        
        recent_change = (recent[-1].get("close", 0) - recent[0].get("close", 0)) / recent[0].get("close", 1)
        older_change = (older[-1].get("close", 0) - older[0].get("close", 0)) / older[0].get("close", 1)
        
        if recent_change > older_change * 1.5:
            return "bullish"
        elif recent_change < older_change * 1.5:
            return "bearish"
        
        return None

    def _generate_signal(
        self,
        state: VolatilityState,
        prob: float,
        direction: Optional[str],
    ) -> str:
        """Generate trading signal."""
        signals = {
            VolatilityState.COMPRESSED: "Volatility compressed - expect expansion soon",
            VolatilityState.EXPANDING: "Volatility expanding - momentum trade",
            VolatilityState.CONTRACTING: "Volatility contracting - wait for setup",
            VolatilityState.STABLE: "Volatility stable - normal conditions",
        }
        
        base = signals.get(state, "Unknown")
        
        if direction and prob > 0.6:
            base += f" Direction: {direction} ({prob:.0%} confidence)"
        
        return base

    def _generate_demo_candles(self, symbol: str, timeframe: str) -> List[Dict]:
        """Generate demo candle data with varying volatility."""
        import random
        from datetime import datetime, timedelta
        
        base_prices = {"SPY": 500.0, "QQQ": 440.0, "AAPL": 185.0}
        base = base_prices.get(symbol, 100.0)
        
        # Create compression pattern: start with normal vol, compress, then expand
        candles = []
        now = datetime.utcnow()
        price = base
        
        phases = [15, 10, 5]  # normal, compress, expand
        
        for phase_idx, phase_len in enumerate(phases):
            for i in range(phase_len):
                # Volatility varies by phase
                if phase_idx == 0:
                    vol_factor = random.uniform(0.3, 0.5)  # Normal
                elif phase_idx == 1:
                    vol_factor = random.uniform(0.1, 0.2)  # Compressed
                else:
                    vol_factor = random.uniform(0.5, 0.8)  # Expanding
                
                change = random.uniform(-vol_factor, vol_factor)
                price *= (1 + change / 100)
                
                candles.append({
                    "timestamp": (now - timedelta(minutes=30-phase_idx*phase_len-i)).isoformat(),
                    "open": round(price * (1 + random.uniform(-0.001, 0.001)), 2),
                    "high": round(price * (1 + vol_factor * 0.5), 2),
                    "low": round(price * (1 - vol_factor * 0.5), 2),
                    "close": round(price, 2),
                    "volume": random.randint(100000, 1000000),
                })
        
        return candles


# Singleton
_volatility_engine: Optional[VolatilityExpansionEngine] = None


def get_volatility_expansion_engine() -> VolatilityExpansionEngine:
    """Get the singleton VolatilityExpansionEngine instance."""
    global _volatility_engine
    if _volatility_engine is None:
        _volatility_engine = VolatilityExpansionEngine()
    return _volatility_engine
