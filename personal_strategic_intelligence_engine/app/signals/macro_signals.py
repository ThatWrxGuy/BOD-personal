"""Macro economic signal collector."""
import random

from app.models.strategic_signal import SignalCategory
from app.signals.signal_base import BaseSignalCollector, SignalData


class MacroSignalCollector(BaseSignalCollector):
    """Collects signals from macroeconomic indicators."""

    def __init__(self, config: dict = None):
        super().__init__()
        self.config = config or {}

    @property
    def category(self) -> str:
        return SignalCategory.MACRO

    async def collect(self) -> list[SignalData]:
        """Collect macroeconomic signals."""
        signals = []

        # In production, this would connect to:
        # - Federal Reserve data
        # - Economic indicators (GDP, unemployment, inflation)
        # - Central bank announcements
        # - Economic news APIs

        # Example: Interest rate change signal
        if random.random() > 0.8:
            direction = "raised" if random.random() > 0.5 else "lowered"
            change = random.uniform(0.25, 0.75)
            signals.append(SignalData(
                source="macro_indicator",
                title=f"Interest Rates {direction.capitalize()}",
                description=f"Central bank has {direction} rates by {change:.2f}%.",
                raw_data={
                    "indicator": "interest_rate",
                    "direction": direction,
                    "change_bps": change * 100,
                    "signal_strength": min(10.0, change * 10),
                    "urgency": 8,
                    "confidence": 0.7,
                    "type": "rate_change",
                },
                category=self.category,
            ))

        # Example: Inflation signal
        if random.random() > 0.75:
            inflation_change = random.uniform(-0.5, 2.0)
            direction = "increased" if inflation_change > 0 else "decreased"
            signals.append(SignalData(
                source="macro_indicator",
                title="Inflation Update",
                description=f"Inflation has {direction} by {abs(inflation_change):.1f}%.",
                raw_data={
                    "indicator": "inflation",
                    "change_percent": inflation_change,
                    "signal_strength": min(10.0, abs(inflation_change) * 5),
                    "urgency": 7 if inflation_change > 1 else 5,
                    "confidence": 0.65,
                    "type": "inflation_alert",
                },
                category=self.category,
            ))

        # Example: Employment signal
        if random.random() > 0.85:
            change = random.uniform(-0.5, 1.0)
            signals.append(SignalData(
                source="macro_indicator",
                title="Employment Data Release",
                description=f"Employment changed by {change:+.1f}% this month.",
                raw_data={
                    "indicator": "employment",
                    "change_percent": change,
                    "signal_strength": min(10.0, abs(change) * 8),
                    "urgency": 5,
                    "confidence": 0.6,
                    "type": "employment_alert",
                },
                category=self.category,
            ))

        # Example: GDP growth signal
        if random.random() > 0.9:
            gdp_growth = random.uniform(-2, 3)
            signals.append(SignalData(
                source="macro_indicator",
                title="GDP Growth Update",
                description=f"GDP growth at {gdp_growth:+.1f}% for the quarter.",
                raw_data={
                    "indicator": "gdp",
                    "growth_percent": gdp_growth,
                    "signal_strength": min(10.0, abs(gdp_growth) * 3),
                    "urgency": 6 if gdp_growth < 0 else 4,
                    "confidence": 0.6,
                    "type": "gdp_alert",
                },
                category=self.category,
            ))

        return signals

    def get_interval_seconds(self) -> int:
        """Collect daily."""
        return 24 * 60 * 60
