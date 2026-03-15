"""Intraday Price Level Mapping for Market Structure Analysis.

Identifies and scores key intraday structure levels.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from collections import defaultdict

from app.agents.finance.tactical.market_structure.structure_models import (
    IntradayLevel,
    IntradayLevelMap,
    LevelType,
    LevelStatus,
)


class PriceLevelEngine:
    """
    Identifies and tracks key intraday price levels.
    """
    
    def __init__(self):
        self.session_open: float = 0.0
        self.session_high: float = 0.0
        self.session_low: float = float('inf')
        self.prior_close: float = 0.0
        
        # Opening range
        self.or_high: float = 0.0
        self.or_low: float = float('inf')
        self.or_established: bool = False
        self.or_end_time: Optional[datetime] = None
        
        # Level tracking
        self.levels: List[IntradayLevel] = []
        self.level_touches: Dict[float, int] = defaultdict(int)
        self.last_touches: Dict[float, datetime] = {}
        
        # Premarkets
        self.premarket_high: float = 0.0
        self.premarket_low: float = float('inf')
        
        # Pivots
        self.pivot: float = 0.0
        self.r1: float = 0.0
        self.r2: float = 0.0
        self.s1: float = 0.0
        self.s2: float = 0.0
    
    def set_prior_close(self, price: float) -> None:
        """Set prior close price."""
        self.prior_close = price
    
    def set_premarket(self, high: float, low: float) -> None:
        """Set premarket levels."""
        self.premarket_high = high
        self.premarket_low = low
    
    def set_session_open(self, price: float) -> None:
        """Set session open price."""
        self.session_open = price
        self.or_high = price
        self.or_low = price
    
    def update_session(
        self,
        high: float,
        low: float,
        close: float,
    ) -> None:
        """Update session high/low."""
        if self.session_high == 0.0:
            self.session_high = high
        else:
            self.session_high = max(self.session_high, high)
        
        if self.session_low == float('inf'):
            self.session_low = low
        else:
            self.session_low = min(self.session_low, low)
    
    def update_opening_range(
        self,
        high: float,
        low: float,
        timestamp: datetime,
        minutes: int = 30,
    ) -> None:
        """Update opening range."""
        if not self.or_established:
            self.or_high = max(self.or_high, high)
            self.or_low = min(self.or_low, low)
            
            # Check if OR is established (after 30 minutes)
            if minutes >= 30 and not self.or_established:
                self.or_established = True
                self.or_end_time = timestamp
    
    def calculate_pivots(self) -> None:
        """Calculate pivot levels."""
        if self.session_high == 0.0 or self.session_low == float('inf'):
            return
        
        # Classic pivot calculation
        self.pivot = (self.session_high + self.session_low + self.session_open) / 3
        self.r1 = 2 * self.pivot - self.session_low
        self.r2 = self.pivot + (self.session_high - self.session_low)
        self.s1 = 2 * self.pivot - self.session_high
        self.s2 = self.pivot - (self.session_high - self.session_low)
    
    def record_level_touch(
        self,
        price: float,
        timestamp: datetime,
    ) -> None:
        """Record a touch at a price level."""
        self.level_touches[price] += 1
        self.last_touches[price] = timestamp
    
    def get_level_map(
        self,
        current_price: float,
    ) -> IntradayLevelMap:
        """
        Get current intraday level map.
        
        Args:
            current_price: Current SPY price
        
        Returns:
            IntradayLevelMap with all relevant levels
        """
        levels = []
        
        # Session high
        if self.session_high > 0:
            levels.append(self._create_level(
                self.session_high,
                LevelType.SESSION_HIGH,
                current_price,
            ))
        
        # Session low
        if self.session_low < float('inf'):
            levels.append(self._create_level(
                self.session_low,
                LevelType.SESSION_LOW,
                current_price,
            ))
        
        # Opening range high
        if self.or_high > 0 and self.or_established:
            levels.append(self._create_level(
                self.or_high,
                LevelType.OR_HIGH,
                current_price,
            ))
        
        # Opening range low
        if self.or_low < float('inf') and self.or_established:
            levels.append(self._create_level(
                self.or_low,
                LevelType.OR_LOW,
                current_price,
            ))
        
        # Prior close
        if self.prior_close > 0:
            levels.append(self._create_level(
                self.prior_close,
                LevelType.PRIOR_CLOSE,
                current_price,
            ))
        
        # Pivot levels
        if self.pivot > 0:
            levels.append(self._create_level(
                self.pivot,
                LevelType.PIVOT,
                current_price,
                relevance=0.7,
            ))
        
        if self.r1 > 0:
            levels.append(self._create_level(
                self.r1,
                LevelType.RESISTANCE,
                current_price,
                relevance=0.6,
            ))
        
        if self.s1 > 0:
            levels.append(self._create_level(
                self.s1,
                LevelType.SUPPORT,
                current_price,
                relevance=0.6,
            ))
        
        # Sort by relevance
        levels.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Find nearest support and resistance
        supports = [l for l in levels if l.level_type == LevelType.SUPPORT]
        resistances = [l for l in levels if l.level_type == LevelType.RESISTANCE]
        
        nearest_support = None
        nearest_resistance = None
        
        if supports:
            below = [l for l in supports if l.price < current_price]
            if below:
                nearest_support = max(below, key=lambda x: x.price)
        
        if resistances:
            above = [l for l in resistances if l.price > current_price]
            if above:
                nearest_resistance = min(above, key=lambda x: x.price)
        
        return IntradayLevelMap(
            levels=levels,
            session_high=next((l for l in levels if l.level_type == LevelType.SESSION_HIGH), None),
            session_low=next((l for l in levels if l.level_type == LevelType.SESSION_LOW), None),
            nearest_support=nearest_support,
            nearest_resistance=nearest_resistance,
        )
    
    def _create_level(
        self,
        price: float,
        level_type: LevelType,
        current_price: float,
        relevance: float = 1.0,
    ) -> IntradayLevel:
        """Create an IntradayLevel."""
        distance = abs(current_price - price)
        
        # Adjust relevance based on touches
        touches = self.level_touches.get(price, 1)
        relevance = min(relevance * (1 + touches * 0.1), 1.0)
        
        # Determine status
        status = LevelStatus.INTACT
        if level_type == LevelType.SESSION_HIGH and current_price > price:
            status = LevelStatus.BROKEN
        elif level_type == LevelType.SESSION_LOW and current_price < price:
            status = LevelStatus.BROKEN
        
        return IntradayLevel(
            price=price,
            level_type=level_type,
            relevance_score=relevance,
            last_touch=self.last_touches.get(price, datetime.now()),
            touch_count=touches,
            status=status,
            distance_from_price=distance,
        )
    
    def get_nearby_levels(
        self,
        current_price: float,
        threshold: float = 1.0,
    ) -> List[IntradayLevel]:
        """Get levels near current price."""
        level_map = self.get_level_map(current_price)
        
        return [
            l for l in level_map.levels
            if abs(l.price - current_price) <= threshold
        ]
    
    def analyze_level_interaction(
        self,
        current_price: float,
    ) -> dict:
        """Analyze current level interactions."""
        level_map = self.get_level_map(current_price)
        
        analysis = {
            "approaching_level": False,
            "breaking_level": False,
            "rejecting_level": False,
            "between_levels": False,
            "nearest_level_type": None,
            "nearest_level_distance": 0.0,
        }
        
        # Check if between levels
        if level_map.nearest_support and level_map.nearest_resistance:
            if (level_map.nearest_support.price < current_price <
                level_map.nearest_resistance.price):
                analysis["between_levels"] = True
                analysis["nearest_level_type"] = "range"
                analysis["nearest_level_distance"] = min(
                    current_price - level_map.nearest_support.price,
                    level_map.nearest_resistance.price - current_price,
                )
        
        # Check session levels
        if self.session_high > 0:
            if current_price < self.session_high < current_price + 1:
                analysis["approaching_level"] = True
                analysis["nearest_level_type"] = "resistance"
                analysis["nearest_level_distance"] = self.session_high - current_price
        
        if self.session_low < float('inf'):
            if current_price - 1 < self.session_low < current_price:
                analysis["approaching_level"] = True
                analysis["nearest_level_type"] = "support"
                analysis["nearest_level_distance"] = current_price - self.session_low
        
        return analysis


def create_price_level_engine() -> PriceLevelEngine:
    """Factory function to create price level engine."""
    return PriceLevelEngine()
