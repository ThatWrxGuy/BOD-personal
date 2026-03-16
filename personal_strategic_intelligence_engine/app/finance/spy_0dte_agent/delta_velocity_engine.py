"""Delta Velocity Engine - BB-FIN-019"""

from typing import Optional, Dict, List
import logging
import random

from app.finance.spy_0dte_agent.spy_0dte_models import (
    DeltaVelocitySignal,
    SignalType,
    TradeDirection,
)

logger = logging.getLogger(__name__)


class DeltaVelocityEngine:
    """Detects rapid delta expansion moments for 0DTE opportunities."""

    def __init__(self):
        self._recent_velocities: List[float] = []

    def analyze(
        self,
        candles: Optional[List[Dict]] = None,
        gamma_levels: Optional[Dict] = None,
    ) -> Optional[DeltaVelocitySignal]:
        """Analyze for delta velocity signals."""
        # Use demo data if not provided
        if candles is None:
            candles = self._generate_demo_candles()
        
        if len(candles) < 5:
            return None
        
        # Calculate velocity metrics
        velocity = self._calculate_velocity(candles)
        acceleration = self._calculate_acceleration(candles)
        
        # Detect signals
        signal = self._detect_signal(candles, velocity, acceleration, gamma_levels)
        
        return signal

    def _calculate_velocity(self, candles: List[Dict]) -> float:
        """Calculate current delta velocity (0-1)."""
        if len(candles) < 3:
            return 0.0
        
        # Price movement per candle
        closes = [c.get("close", 0) for c in candles]
        
        # Recent momentum (last 3 candles)
        recent = closes[-3:]
        if len(recent) < 2:
            return 0.0
        
        recent_change = (recent[-1] - recent[0]) / recent[0] if recent[0] > 0 else 0
        
        # Compare to earlier candles
        older = closes[:-3] if len(closes) > 3 else closes[:-1]
        if older and len(older) >= 2:
            older_change = (older[-1] - older[0]) / older[0] if older[0] > 0 else 0
        else:
            older_change = 0
        
        # Velocity is the ratio of recent to older momentum
        if abs(older_change) > 0.0001:
            velocity = recent_change / older_change
        else:
            velocity = 2.0 if recent_change > 0 else -2.0
        
        # Normalize to 0-1
        velocity = min(1.0, max(-1.0, velocity))
        
        return abs(velocity)

    def _calculate_acceleration(self, candles: List[Dict]) -> float:
        """Calculate acceleration of delta changes."""
        if len(candles) < 5:
            return 0.0
        
        closes = [c.get("close", 0) for c in candles]
        
        # Calculate momentum for each candle
        momenta = []
        for i in range(1, len(closes)):
            if closes[i-1] > 0:
                momenta.append((closes[i] - closes[i-1]) / closes[i-1])
        
        if len(momenta) < 2:
            return 0.0
        
        # Acceleration = change in momentum
        recent = momenta[-2:]
        older = momenta[:-2]
        
        if not recent or not older:
            return 0.0
        
        avg_recent = sum(recent) / len(recent)
        avg_older = sum(older) / len(older) if older else 0
        
        return avg_recent - avg_older

    def _detect_signal(
        self,
        candles: List[Dict],
        velocity: float,
        acceleration: float,
        gamma_levels: Optional[Dict],
    ) -> Optional[DeltaVelocitySignal]:
        """Detect specific delta velocity signal type."""
        if len(candles) < 5:
            return None
        
        closes = [c.get("close", 0) for c in candles]
        volumes = [c.get("volume", 0) for c in candles]
        
        current_price = closes[-1]
        
        # Detect momentum burst
        if self._is_momentum_burst(velocity, acceleration, candles):
            direction = TradeDirection.CALL if acceleration > 0 else TradeDirection.PUT
            
            return DeltaVelocitySignal(
                signal_type=SignalType.MOMENTUM_BURST,
                direction=direction,
                velocity_score=velocity,
                acceleration=acceleration,
                confirmed=True,
                follow_through_probability=0.8,
                structure_context="Momentum burst detected",
                volume_surge=self._is_volume_surge(volumes),
                reasoning=[
                    f"Velocity: {velocity:.2f}",
                    f"Acceleration: {acceleration:.4f}",
                    f"Price action: {'bullish' if acceleration > 0 else 'bearish'}",
                ],
            )
        
        # Detect breakout displacement
        if self._is_breakout_displacement(candles):
            direction = TradeDirection.CALL if closes[-1] > closes[-5] else TradeDirection.PUT
            
            return DeltaVelocitySignal(
                signal_type=SignalType.BREAKOUT_DISPLACEMENT,
                direction=direction,
                velocity_score=velocity,
                acceleration=acceleration,
                confirmed=True,
                follow_through_probability=0.75,
                structure_context="Breakout displacement",
                volume_surge=self._is_volume_surge(volumes),
                reasoning=[
                    "Breakout from consolidation",
                    f"Displacement: {abs(closes[-1] - closes[-5]) / closes[-5] * 100:.2f}%",
                ],
            )
        
        # Detect gamma wall breach
        if gamma_levels:
            if self._is_gamma_wall_breach(current_price, gamma_levels):
                direction = TradeDirection.CALL if current_price > gamma_levels.get("gamma_resistance", 0) else TradeDirection.PUT
                
                return DeltaVelocitySignal(
                    signal_type=SignalType.GAMMA_WALL_BREACH,
                    direction=direction,
                    velocity_score=velocity,
                    acceleration=acceleration,
                    confirmed=True,
                    follow_through_probability=0.85,
                    structure_context="Gamma wall breach",
                    volume_surge=self._is_volume_surge(volumes),
                    reasoning=[
                        f"Breached {'resistance' if direction == TradeDirection.CALL else 'support'} gamma level",
                        f"Gamma flip at: {gamma_levels.get('gamma_flip', 0)}",
                    ],
                )
        
        # Detect reversal sweep
        if self._is_reversal_sweep(candles, acceleration):
            direction = TradeDirection.PUT if acceleration > 0 else TradeDirection.CALL
            
            return DeltaVelocitySignal(
                signal_type=SignalType.REVERSAL_SWEEP,
                direction=direction,
                velocity_score=velocity,
                acceleration=acceleration,
                confirmed=False,
                follow_through_probability=0.5,
                structure_context="Reversal sweep",
                volume_surge=self._is_volume_surge(volumes),
                reasoning=["Reversal detected", "Wait for confirmation"],
            )
        
        # No clear signal
        return None

    def _is_momentum_burst(
        self,
        velocity: float,
        acceleration: float,
        candles: List[Dict],
    ) -> bool:
        """Detect momentum burst condition."""
        # Strong velocity
        if velocity < 0.7:
            return False
        
        # Strong acceleration
        if abs(acceleration) < 0.001:
            return False
        
        # Check for strong candle
        if len(candles) >= 3:
            recent = candles[-1]
            change = abs(recent.get("close", 0) - recent.get("open", 0)) / recent.get("open", 1) if recent.get("open", 0) > 0 else 0
            if change > 0.002:  # >0.2% candle
                return True
        
        return False

    def _is_breakout_displacement(self, candles: List[Dict]) -> bool:
        """Detect breakout displacement."""
        if len(candles) < 10:
            return False
        
        # Previous consolidation range
        prev_candles = candles[-10:-3]
        range_high = max([c.get("high", 0) for c in prev_candles])
        range_low = min([c.get("low", 0) for c in prev_candles])
        
        current = candles[-1].get("close", 0)
        
        # Breakout above or below
        if current > range_high * 1.002 or current < range_low * 0.998:
            return True
        
        return False

    def _is_gamma_wall_breach(
        self,
        current_price: float,
        gamma_levels: Dict,
    ) -> bool:
        """Detect gamma wall breach."""
        gamma_resistance = gamma_levels.get("gamma_resistance", 0)
        gamma_support = gamma_levels.get("gamma_support", 0)
        
        if gamma_resistance > 0 and current_price > gamma_resistance * 1.002:
            return True
        
        if gamma_support > 0 and current_price < gamma_support * 0.998:
            return True
        
        return False

    def _is_reversal_sweep(
        self,
        candles: List[Dict],
        acceleration: float,
    ) -> bool:
        """Detect reversal sweep pattern."""
        if len(candles) < 5:
            return False
        
        # Check for hammer/shooting star patterns
        recent = candles[-3:]
        
        for c in recent:
            high = c.get("high", 0)
            low = c.get("low", 0)
            close = c.get("close", 0)
            open_price = c.get("open", 0)
            
            body = abs(close - open_price)
            upper_wick = high - max(close, open_price)
            lower_wick = min(close, open_price) - low
            
            # Hammer (bullish reversal)
            if lower_wick > body * 2 and upper_wick < body * 0.5:
                return True
            
            # Shooting star (bearish reversal)
            if upper_wick > body * 2 and lower_wick < body * 0.5:
                return True
        
        return False

    def _is_volume_surge(self, volumes: List[int]) -> bool:
        """Check if there's a volume surge."""
        if len(volumes) < 5:
            return False
        
        recent = sum(volumes[-3:]) / 3
        older = sum(volumes[:-3]) / len(volumes[:-3]) if len(volumes) > 3 else recent
        
        return recent > older * 1.5

    def _generate_demo_candles(self) -> List[Dict]:
        """Generate demo candle data."""
        from datetime import datetime, timedelta
        
        candles = []
        now = datetime.utcnow()
        price = 500.0  # SPY base
        
        for i in range(15):
            # Create patterns
            if i < 10:
                # Consolidation
                price *= (1 + random.uniform(-0.001, 0.001))
            elif i < 13:
                # Momentum building
                price *= (1 + random.uniform(0.001, 0.003))
            else:
                # Burst
                price *= (1 + random.uniform(0.003, 0.006))
            
            candles.append({
                "timestamp": (now - timedelta(minutes=15-i)).isoformat(),
                "open": round(price * 0.999, 2),
                "high": round(price * 1.002, 2),
                "low": round(price * 0.998, 2),
                "close": round(price, 2),
                "volume": random.randint(500000, 2000000),
            })
        
        return candles


# Singleton
_delta_velocity_engine: Optional[DeltaVelocityEngine] = None


def get_delta_velocity_engine() -> DeltaVelocityEngine:
    """Get the singleton DeltaVelocityEngine instance."""
    global _delta_velocity_engine
    if _delta_velocity_engine is None:
        _delta_velocity_engine = DeltaVelocityEngine()
    return _delta_velocity_engine
