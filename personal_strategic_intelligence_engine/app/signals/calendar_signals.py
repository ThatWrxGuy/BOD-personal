"""Calendar signal collector for scheduling signals."""
import random
from datetime import datetime, timedelta

from app.models.strategic_signal import SignalCategory
from app.signals.signal_base import BaseSignalCollector, SignalData


class CalendarSignalCollector(BaseSignalCollector):
    """Collects signals from calendar and scheduling systems."""

    def __init__(self, config: dict = None):
        super().__init__()
        self.config = config or {}

    @property
    def category(self) -> str:
        return SignalCategory.CALENDAR

    async def collect(self) -> list[SignalData]:
        """Collect calendar signals."""
        signals = []

        # In production, this would connect to:
        # - Google Calendar
        # - Outlook
        # - Calendar APIs

        # Example: Calendar overload detection
        if random.random() > 0.6:
            hours_today = random.uniform(6, 12)
            capacity = 8  # Standard workday hours
            
            if hours_today > capacity:
                signals.append(SignalData(
                    source="calendar",
                    title="Calendar Overload Alert",
                    description=f"You have {hours_today:.1f} hours of meetings today, exceeding capacity.",
                    raw_data={
                        "hours_scheduled": hours_today,
                        "capacity": capacity,
                        "signal_strength": min(10.0, (hours_today / capacity - 1) * 20 + 5),
                        "urgency": 8 if hours_today > capacity * 1.5 else 6,
                        "confidence": 0.95,
                        "type": "overload",
                    },
                    category=self.category,
                ))

        # Example: Back-to-back meeting fatigue
        if random.random() > 0.7:
            consecutive = random.randint(4, 8)
            if consecutive >= 4:
                signals.append(SignalData(
                    source="calendar",
                    title="Back-to-Back Meeting Warning",
                    description=f"You have {consecutive} consecutive meetings scheduled.",
                    raw_data={
                        "consecutive_meetings": consecutive,
                        "signal_strength": min(10.0, consecutive * 1.5),
                        "urgency": 7,
                        "confidence": 0.95,
                        "type": "consecutive",
                    },
                    category=self.category,
                ))

        # Example: Free time opportunity
        if random.random() > 0.8:
            free_hours = random.uniform(1, 4)
            if free_hours >= 2:
                signals.append(SignalData(
                    source="calendar",
                    title="Free Time Block Available",
                    description=f"You have {free_hours:.1f} hours of unscheduled time tomorrow.",
                    raw_data={
                        "free_hours": free_hours,
                        "signal_strength": 5.0,
                        "urgency": 2,
                        "confidence": 0.9,
                        "type": "free_time",
                    },
                    category=self.category,
                ))

        # Example: Deadline approaching
        if random.random() > 0.75:
            days_until = random.randint(1, 7)
            if days_until <= 3:
                signals.append(SignalData(
                    source="calendar",
                    title="Deadline Approaching",
                    description=f"A deadline is coming up in {days_until} days.",
                    raw_data={
                        "days_until": days_until,
                        "signal_strength": min(10.0, (7 - days_until) * 1.5 + 3),
                        "urgency": 8 if days_until == 1 else 6,
                        "confidence": 0.9,
                        "type": "deadline",
                    },
                    category=self.category,
                ))

        # Example: Travel time
        if random.random() > 0.85:
            travel_hours = random.uniform(1, 4)
            signals.append(SignalData(
                source="calendar",
                title="Significant Travel Time",
                description=f"You have {travel_hours:.1f} hours of travel scheduled today.",
                raw_data={
                    "travel_hours": travel_hours,
                    "signal_strength": min(10.0, travel_hours * 2.5),
                    "urgency": 5,
                    "confidence": 0.9,
                    "type": "travel",
                },
                category=self.category,
            ))

        return signals

    def get_interval_seconds(self) -> int:
        """Collect every hour."""
        return 60 * 60
