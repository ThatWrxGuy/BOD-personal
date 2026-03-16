"""Gamma Level Engine - BB-FIN-019"""

from typing import Optional, Dict, List
import logging
import random

from app.finance.spy_0dte_agent.spy_0dte_models import GammaLevelMap

logger = logging.getLogger(__name__)


class GammaLevelEngine:
    """Detects gamma levels, walls, and dealer positioning for SPY."""

    def __init__(self):
        self._gamma_levels_cache: Optional[GammaLevelMap] = None

    def get_gamma_levels(
        self,
        current_price: Optional[float] = None,
        gamma_exposure_data: Optional[Dict] = None,
    ) -> GammaLevelMap:
        """Get current gamma levels for SPY."""
        # Use provided price or generate
        if current_price is None:
            current_price = self._generate_demo_price()
        
        # Generate gamma levels based on current price
        if gamma_exposure_data is None:
            gamma_exposure_data = self._generate_demo_gamma_exposure(current_price)
        
        # Extract levels
        gamma_support = gamma_exposure_data.get("gamma_support", current_price * 0.99)
        gamma_resistance = gamma_exposure_data.get("gamma_resistance", current_price * 1.01)
        gamma_flip = gamma_exposure_data.get("gamma_flip", current_price)
        net_gamma = gamma_exposure_data.get("net_gamma", 0)
        
        # Determine gamma zone
        gamma_zone = self._determine_gamma_zone(net_gamma, current_price, gamma_support, gamma_resistance)
        
        # Calculate pinning probability
        pinning_prob = self._calculate_pinning_probability(
            current_price, gamma_support, gamma_resistance, gamma_flip
        )
        
        # Find pin level (nearest gamma level)
        pin_level = self._find_pin_level(current_price, gamma_support, gamma_resistance, gamma_flip)
        
        # Calculate gamma walls (call/put walls)
        call_wall = self._calculate_call_wall(current_price, gamma_resistance)
        put_wall = self._calculate_put_wall(current_price, gamma_support)
        
        return GammaLevelMap(
            gamma_support=gamma_support,
            gamma_resistance=gamma_resistance,
            gamma_flip=gamma_flip,
            net_gamma=net_gamma,
            gamma_zone=gamma_zone,
            pin_level=pin_level,
            pinning_probability=pinning_prob,
            call_wall=call_wall,
            put_wall=put_wall,
        )

    def _generate_demo_price(self) -> float:
        """Generate a realistic SPY price."""
        return random.uniform(495, 510)

    def _generate_demo_gamma_exposure(self, current_price: float) -> Dict:
        """Generate demo gamma exposure data."""
        # Create realistic gamma levels around current price
        gamma_support = current_price - random.uniform(3, 8)
        gamma_resistance = current_price + random.uniform(3, 8)
        gamma_flip = current_price + random.uniform(-2, 2)
        
        # Net gamma can be positive (market makers long gamma) or negative
        net_gamma = random.uniform(-10000, 10000)
        
        return {
            "gamma_support": gamma_support,
            "gamma_resistance": gamma_resistance,
            "gamma_flip": gamma_flip,
            "net_gamma": net_gamma,
        }

    def _determine_gamma_zone(
        self,
        net_gamma: float,
        current_price: float,
        gamma_support: float,
        gamma_resistance: float,
    ) -> str:
        """Determine the gamma zone."""
        if net_gamma > 5000:
            # Long gamma - acceleration zone
            return "acceleration"
        elif net_gamma < -5000:
            # Short gamma - deceleration zone
            return "deceleration"
        else:
            return "neutral"

    def _calculate_pinning_probability(
        self,
        current_price: float,
        gamma_support: float,
        gamma_resistance: float,
        gamma_flip: float,
    ) -> float:
        """Calculate probability of pinning to a gamma level."""
        # Distance to nearest gamma level
        dist_to_support = abs(current_price - gamma_support)
        dist_to_resistance = abs(current_price - gamma_resistance)
        dist_to_flip = abs(current_price - gamma_flip)
        
        min_dist = min(dist_to_support, dist_to_resistance, dist_to_flip)
        
        # Closer to a level = higher pinning probability
        if min_dist < 1:
            return 0.9
        elif min_dist < 2:
            return 0.7
        elif min_dist < 3:
            return 0.5
        elif min_dist < 5:
            return 0.3
        else:
            return 0.1

    def _find_pin_level(
        self,
        current_price: float,
        gamma_support: float,
        gamma_resistance: float,
        gamma_flip: float,
    ) -> Optional[float]:
        """Find the nearest pinning level."""
        dist_to_support = abs(current_price - gamma_support)
        dist_to_resistance = abs(current_price - gamma_resistance)
        dist_to_flip = abs(current_price - gamma_flip)
        
        min_dist = min(dist_to_support, dist_to_resistance, dist_to_flip)
        
        if min_dist < 3:
            if min_dist == dist_to_support:
                return gamma_support
            elif min_dist == dist_to_resistance:
                return gamma_resistance
            else:
                return gamma_flip
        
        return None

    def _calculate_call_wall(self, current_price: float, gamma_resistance: float) -> float:
        """Calculate call wall (resistance area)."""
        # Call wall is typically above current price
        return gamma_resistance + random.uniform(2, 5)

    def _calculate_put_wall(self, current_price: float, gamma_support: float) -> float:
        """Calculate put wall (support area)."""
        # Put wall is typically below current price
        return gamma_support - random.uniform(2, 5)

    def analyze_gamma_context(
        self,
        current_price: float,
        direction: str,
    ) -> Dict:
        """Analyze gamma context for a given direction."""
        gamma = self.get_gamma_levels(current_price)
        
        if direction == "bullish":
            # For calls, resistance levels matter
            distance_to_resistance = gamma.gamma_resistance - current_price
            distance_to_flip = gamma.gamma_flip - current_price
            
            return {
                "direction": "bullish",
                "target_level": gamma.gamma_resistance,
                "distance": distance_to_resistance,
                "flip_level": gamma.gamma_flip,
                "zone": gamma.gamma_zone,
                "signal": self._generate_gamma_signal(
                    distance_to_resistance, distance_to_flip, "bullish"
                ),
            }
        else:
            # For puts, support levels matter
            distance_to_support = current_price - gamma.gamma_support
            distance_to_flip = current_price - gamma.gamma_flip
            
            return {
                "direction": "bearish",
                "target_level": gamma.gamma_support,
                "distance": distance_to_support,
                "flip_level": gamma.gamma_flip,
                "zone": gamma.gamma_zone,
                "signal": self._generate_gamma_signal(
                    distance_to_support, distance_to_flip, "bearish"
                ),
            }

    def _generate_gamma_signal(
        self,
        distance_to_target: float,
        distance_to_flip: float,
        direction: str,
    ) -> str:
        """Generate a signal based on gamma levels."""
        if distance_to_target < 2:
            return f"Near {'resistance' if direction == 'bullish' else 'support'} - potential gamma squeeze"
        elif distance_to_flip < 2:
            return "Near gamma flip level - high volatility expected"
        elif distance_to_target < 5:
            return f"Moving toward {'resistance' if direction == 'bullish' else 'support'}"
        else:
            return "No immediate gamma barriers - clear move"


# Singleton
_gamma_level_engine: Optional[GammaLevelEngine] = None


def get_gamma_level_engine() -> GammaLevelEngine:
    """Get the singleton GammaLevelEngine instance."""
    global _gamma_level_engine
    if _gamma_level_engine is None:
        _gamma_level_engine = GammaLevelEngine()
    return _gamma_level_engine
