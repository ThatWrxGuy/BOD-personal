"""Market signal collector for financial market data."""
import random
from typing import Any

from app.models.strategic_signal import SignalCategory
from app.signals.signal_base import BaseSignalCollector, SignalData


class MarketSignalCollector(BaseSignalCollector):
    """Collects signals from financial markets."""

    def __init__(self, api_key: str = None):
        super().__init__()
        self.api_key = api_key

    @property
    def category(self) -> str:
        return SignalCategory.MARKET

    async def collect(self) -> list[SignalData]:
        """Collect market signals."""
        signals = []

        # In production, this would call market APIs
        # For now, generate sample signals based on market conditions
        
        # Example: Check for high volatility
        volatility = random.uniform(0, 30)  # Simulated VIX-like value
        
        if volatility > 25:
            signals.append(SignalData(
                source="market_feed",
                title="High Market Volatility Detected",
                description=f"Market volatility at {volatility:.1f}, indicating elevated uncertainty.",
                raw_data={
                    "volatility": volatility,
                    "signal_strength": min(10.0, volatility / 2.5),
                    "urgency": 8 if volatility > 28 else 6,
                    "confidence": 0.75,
                    "type": "volatility",
                },
                category=self.category,
            ))

        # Example: Major index movement
        if random.random() > 0.8:
            direction = "up" if random.random() > 0.5 else "down"
            change = random.uniform(1, 3)
            signals.append(SignalData(
                source="market_feed",
                title=f"Major Index {direction.capitalize()} Movement",
                description=f"Market moved {direction} by {change:.1f}% today.",
                raw_data={
                    "direction": direction,
                    "change_percent": change,
                    "signal_strength": change * 3,
                    "urgency": 6,
                    "confidence": 0.8,
                    "type": "index_move",
                },
                category=self.category,
            ))

        # Example: Sector rotation signal
        if random.random() > 0.9:
            sectors = ["tech", "energy", "healthcare", "finance", "consumer"]
            from_sector = random.choice(sectors)
            to_sector = random.choice([s for s in sectors if s != from_sector])
            signals.append(SignalData(
                source="market_feed",
                title="Sector Rotation Detected",
                description=f"Rotation from {from_sector} to {to_sector} observed.",
                raw_data={
                    "from_sector": from_sector,
                    "to_sector": to_sector,
                    "signal_strength": 6.0,
                    "urgency": 4,
                    "confidence": 0.6,
                    "type": "sector_rotation",
                },
                category=self.category,
            ))

        return signals

    def get_interval_seconds(self) -> int:
        """Collect every 5 minutes."""
        return 300
