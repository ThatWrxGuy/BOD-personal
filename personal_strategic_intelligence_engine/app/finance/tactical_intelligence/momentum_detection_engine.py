"""Momentum Detection Engine - BB-FIN-018"""

from typing import Optional, List, Dict
import logging

from app.finance.tactical_intelligence.tactical_models import (
    MomentumState,
    MomentumBurstSignal,
)

logger = logging.getLogger(__name__)


class MomentumDetectionEngine:
    """Detects momentum bursts and acceleration patterns."""

    def __init__(self):
        self._momentum_history: Dict[str, List[float]] = {}

    def analyze_momentum(
        self,
        symbol: str,
        timeframe: str = "5m",
        candles: Optional[List[Dict]] = None,
    ) -> MomentumBurstSignal:
        """Analyze momentum state and detect bursts."""
        # Use demo data if not provided
        if candles is None:
            candles = self._generate_demo_candles(symbol, timeframe)
        
        if not candles:
            return MomentumBurstSignal(
                symbol=symbol,
                timeframe=timeframe,
                momentum_state=MomentumState.NEUTRAL,
                impulse_strength=0.5,
            )
        
        # Calculate momentum metrics
        closes = [c.get("close", 0) for c in candles]
        
        # Calculate acceleration (2nd derivative)
        momentum = self._calculate_momentum(closes)
        acceleration = self._calculate_acceleration(momentum)
        
        # Calculate impulse strength
        impulse_strength = self._calculate_impulse_strength(candles)
        
        # Determine state
        state = self._determine_state(acceleration, impulse_strength)
        
        # Detect burst
        is_burst = self._detect_burst(momentum, acceleration, impulse_strength)
        
        # Count bursts in recent candles
        burst_count = self._count_recent_bursts(symbol, candles)
        
        # Follow-through probability
        follow_through = self._calculate_follow_through(momentum, acceleration, is_burst)
        
        return MomentumBurstSignal(
            symbol=symbol,
            timeframe=timeframe,
            momentum_state=state,
            acceleration=acceleration,
            impulse_strength=impulse_strength,
            is_burst=is_burst,
            burst_magnitude=abs(acceleration) if is_burst else None,
            bursts_in_last_n_bars=burst_count,
            follow_through_likely=follow_through,
        )

    def _calculate_momentum(self, closes: List[float]) -> List[float]:
        """Calculate momentum (rate of change) for each candle."""
        if len(closes) < 2:
            return []
        
        momentum = []
        for i in range(1, len(closes)):
            if closes[i-1] > 0:
                roc = (closes[i] - closes[i-1]) / closes[i-1] * 100
                momentum.append(roc)
            else:
                momentum.append(0)
        
        return momentum

    def _calculate_acceleration(self, momentum: List[float]) -> float:
        """Calculate acceleration (change in momentum)."""
        if len(momentum) < 2:
            return 0.0
        
        # Compare recent momentum to older momentum
        recent = momentum[-3:] if len(momentum) >= 3 else momentum
        older = momentum[:-3] if len(momentum) > 3 else momentum[:-1]
        
        if not recent or not older:
            return 0.0
        
        avg_recent = sum(recent) / len(recent)
        avg_older = sum(older) / len(older) if older else 0
        
        return avg_recent - avg_older

    def _calculate_impulse_strength(self, candles: List[Dict]) -> float:
        """Calculate impulse strength (0-1)."""
        if len(candles) < 3:
            return 0.5
        
        closes = [c.get("close", 0) for c in candles]
        volumes = [c.get("volume", 0) for c in candles]
        
        # Price momentum
        total_change = abs(closes[-1] - closes[0]) / closes[0] if closes[0] > 0 else 0
        
        # Volume trend
        avg_volume = sum(volumes) / len(volumes)
        recent_volume = sum(volumes[-3:]) / 3
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
        
        # Combine
        strength = min(1.0, total_change * 10) * 0.6 + min(1.0, volume_ratio) * 0.4
        
        return strength

    def _determine_state(self, acceleration: float, impulse: float) -> MomentumState:
        """Determine momentum state."""
        # Strong acceleration
        if acceleration > 0.3 and impulse > 0.6:
            return MomentumState.ACCELERATING
        
        # Strong deceleration
        if acceleration < -0.3 and impulse > 0.6:
            return MomentumState.DECELERATING
        
        # Reversal pattern
        if impulse > 0.5 and abs(acceleration) > 0.2:
            return MomentumState.REVERSING
        
        return MomentumState.NEUTRAL

    def _detect_burst(self, momentum: List[float], acceleration: float, impulse: float) -> bool:
        """Detect if current candle is a momentum burst."""
        # Burst conditions
        if len(momentum) < 3:
            return False
        
        # Sudden acceleration
        if abs(acceleration) > 0.5:
            return True
        
        # Strong impulse
        if impulse > 0.7 and abs(momentum[-1]) > 0.3:
            return True
        
        # Momentum spike
        recent = momentum[-3:]
        if max(recent) > sum(recent) * 1.5:  # One candle dominates
            return True
        
        return False

    def _count_recent_bursts(self, symbol: str, candles: List[Dict]) -> int:
        """Count bursts in recent candles."""
        # This would track history in production
        # For demo, randomly generate
        import random
        return random.randint(0, 2)

    def _calculate_follow_through(
        self,
        momentum: List[float],
        acceleration: float,
        is_burst: bool,
    ) -> bool:
        """Calculate probability of follow-through after burst."""
        if not is_burst:
            return True
        
        # Positive acceleration = more likely follow-through
        if acceleration > 0.2:
            return True
        
        # Strong recent momentum = more likely follow-through
        if momentum and momentum[-1] > 0.3:
            return True
        
        return False

    def _generate_demo_candles(self, symbol: str, timeframe: str) -> List[Dict]:
        """Generate demo candle data with momentum patterns."""
        import random
        from datetime import datetime, timedelta
        
        base_prices = {"SPY": 500.0, "QQQ": 440.0, "AAPL": 185.0}
        base = base_prices.get(symbol, 100.0)
        
        candles = []
        now = datetime.utcnow()
        price = base
        
        # Create momentum pattern
        for i in range(20):
            # Build momentum then burst
            if i < 15:
                # Gradual
                change = random.uniform(-0.1, 0.2)
            else:
                # Burst
                change = random.uniform(0.3, 0.8)
            
            price *= (1 + change / 100)
            
            candles.append({
                "timestamp": (now - timedelta(minutes=20-i)).isoformat(),
                "open": round(price * (1 + random.uniform(-0.001, 0.001)), 2),
                "high": round(price * (1 + random.uniform(0, 0.003)), 2),
                "low": round(price * (1 - random.uniform(0, 0.001)), 2),
                "close": round(price, 2),
                "volume": random.randint(100000, 800000) * (1 + i * 0.1 if i > 15 else 1),
            })
        
        return candles


# Singleton
_momentum_engine: Optional[MomentumDetectionEngine] = None


def get_momentum_detection_engine() -> MomentumDetectionEngine:
    """Get the singleton MomentumDetectionEngine instance."""
    global _momentum_engine
    if _momentum_engine is None:
        _momentum_engine = MomentumDetectionEngine()
    return _momentum_engine
