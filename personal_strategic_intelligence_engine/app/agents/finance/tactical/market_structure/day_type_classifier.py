"""Day Type Classifier for Market Structure Analysis.

Classifies the current session and evolving intraday state.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List
import random

from app.agents.finance.tactical.market_structure.structure_models import (
    DayType,
    DayTypeClassification,
)


class DayTypeClassifier:
    """
    Classifies day type based on intraday price action.
    """
    
    def __init__(self):
        self.session_open_price: float = 0.0
        self.current_price: float = 0.0
        self.session_high: float = 0.0
        self.session_low: float = float('inf')
        self.trend_strength: float = 0.0
        self.open_direction: str = "neutral"
        self.open_range_size: float = 0.0
        self.is_provisional: bool = True
        self.last_classification: Optional[DayType] = None
        self.classification_history: List[DayTypeClassification] = []
    
    def set_session_open(self, price: float) -> None:
        """Set session open price."""
        self.session_open_price = price
    
    def update(
        self,
        current_price: float,
        high: float,
        low: float,
        timestamp: datetime,
    ) -> DayTypeClassification:
        """
        Update classification based on current price action.
        
        Args:
            current_price: Current SPY price
            high: Session high
            low: Session low
            timestamp: Current timestamp
        
        Returns:
            DayTypeClassification
        """
        self.current_price = current_price
        self.session_high = max(self.session_high, high) if self.session_high > 0 else high
        self.session_low = min(self.session_low, low) if self.session_low < float('inf') else low
        
        # Determine if early session (first 30 minutes)
        minutes_from_open = (timestamp - timestamp.replace(hour=9, minute=30, second=0)).seconds / 60
        self.is_provisional = minutes_from_open < 30
        
        # Calculate metrics
        self._calculate_metrics()
        
        # Classify day type
        day_type = self._classify_day_type()
        
        # Calculate confidence
        confidence = self._calculate_confidence(day_type)
        
        classification = DayTypeClassification(
            day_type=day_type,
            confidence=confidence,
            is_provisional=self.is_provisional,
            trend_strength=self.trend_strength,
            open_direction=self.open_direction,
            open_range_size=self.open_range_size,
            timestamp=timestamp,
        )
        
        self.last_classification = day_type
        self.classification_history.append(classification)
        
        return classification
    
    def _calculate_metrics(self) -> None:
        """Calculate classification metrics."""
        
        # Open direction
        change_from_open = ((self.current_price - self.session_open_price) / 
                          self.session_open_price * 100) if self.session_open_price > 0 else 0
        
        if change_from_open > 0.3:
            self.open_direction = "up"
        elif change_from_open < -0.3:
            self.open_direction = "down"
        else:
            self.open_direction = "neutral"
        
        # Open range size
        if self.session_high > 0 and self.session_low < float('inf'):
            self.open_range_size = self.session_high - self.session_low
        
        # Trend strength
        if self.session_open_price > 0:
            pct_change = abs(self.current_price - self.session_open_price) / self.session_open_price
            self.trend_strength = min(pct_change * 100, 1.0)
    
    def _classify_day_type(self) -> DayType:
        """Classify the day type."""
        
        if not self.session_open_price:
            return DayType.RANGE_DAY
        
        change_pct = (self.current_price - self.session_open_price) / self.session_open_price * 100
        range_size = (self.session_high - self.session_low) if self.session_high > 0 and self.session_low < float('inf') else 0
        
        # Check for trend day
        if abs(change_pct) > 1.0:
            if change_pct > 0:
                return DayType.TREND_DAY_UP
            else:
                return DayType.TREND_DAY_DOWN
        
        # Check for open drive
        if self.is_provisional:
            if change_pct > 0.5:
                return DayType.OPEN_DRIVE_UP
            elif change_pct < -0.5:
                return DayType.OPEN_DRIVE_DOWN
        
        # Check for volatility expansion
        if range_size > 3.0:  # More than 3 points range
            return DayType.VOLATILITY_EXPANSION_DAY
        
        # Check for low participation
        if range_size < 0.5:  # Very tight range
            return DayType.LOW_PARTICIPATION_DAY
        
        # Check for reversal
        if len(self.classification_history) > 10:
            prev_classification = self.classification_history[-5]
            if prev_classification.day_type in [DayType.TREND_DAY_UP, DayType.OPEN_DRIVE_UP]:
                if change_pct < -0.3:
                    return DayType.REVERSAL_DAY
            elif prev_classification.day_type in [DayType.TREND_DAY_DOWN, DayType.OPEN_DRIVE_DOWN]:
                if change_pct > 0.3:
                    return DayType.REVERSAL_DAY
        
        # Check for double distribution
        if range_size > 1.5 and abs(change_pct) < 0.5:
            return DayType.DOUBLE_DISTRIBUTION_DAY
        
        # Check for chop
        if range_size < 1.0:
            return DayType.CHOP_DAY
        
        # Default to range day
        return DayType.RANGE_DAY
    
    def _calculate_confidence(self, day_type: DayType) -> float:
        """Calculate confidence in classification."""
        
        # Provisional = lower confidence
        if self.is_provisional:
            return 0.5
        
        # High trend strength = higher confidence
        if day_type in [DayType.TREND_DAY_UP, DayType.TREND_DAY_DOWN]:
            return 0.7 + self.trend_strength * 0.3
        
        # Strong moves = higher confidence
        change_pct = abs((self.current_price - self.session_open_price) / 
                        self.session_open_price * 100) if self.session_open_price > 0 else 0
        
        if change_pct > 1.0:
            return 0.8
        elif change_pct > 0.5:
            return 0.7
        else:
            return 0.6
    
    def get_current_classification(self) -> DayTypeClassification:
        """Get the most recent classification."""
        if self.classification_history:
            return self.classification_history[-1]
        
        return DayTypeClassification(
            day_type=DayType.RANGE_DAY,
            confidence=0.5,
            is_provisional=True,
            trend_strength=0.0,
            open_direction="neutral",
            open_range_size=0.0,
            timestamp=datetime.now(),
        )


def create_day_type_classifier() -> DayTypeClassifier:
    """Factory function to create day type classifier."""
    return DayTypeClassifier()
