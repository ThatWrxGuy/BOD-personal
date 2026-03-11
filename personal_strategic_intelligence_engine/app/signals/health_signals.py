"""Health signal collector for health metrics."""
import random

from app.models.strategic_signal import SignalCategory
from app.signals.signal_base import BaseSignalCollector, SignalData


class HealthSignalCollector(BaseSignalCollector):
    """Collects signals from health metrics and wearables."""

    def __init__(self, config: dict = None):
        super().__init__()
        self.config = config or {}

    @property
    def category(self) -> str:
        return SignalCategory.HEALTH

    async def collect(self) -> list[SignalData]:
        """Collect health signals."""
        signals = []

        # In production, this would connect to:
        # - Wearable devices (Apple Watch, Fitbit, Oura)
        # - Health apps
        # - Sleep trackers
        # - Exercise logs

        # Example: Sleep quality alert
        if random.random() > 0.7:
            sleep_hours = random.uniform(4, 9)
            quality_score = random.uniform(50, 100)
            
            if sleep_hours < 6 or quality_score < 60:
                signals.append(SignalData(
                    source="health_tracker",
                    title="Sleep Quality Alert",
                    description=f"Sleep was {sleep_hours:.1f} hours with {quality_score:.0f}% quality. Below target.",
                    raw_data={
                        "metric": "sleep",
                        "metric_value": quality_score,
                        "threshold": 70,
                        "sleep_hours": sleep_hours,
                        "signal_strength": (70 - quality_score) / 10 if quality_score < 70 else 0,
                        "urgency": 8 if sleep_hours < 5 else 6,
                        "confidence": 0.85,
                        "type": "sleep_alert",
                    },
                    category=self.category,
                ))

        # Example: Activity level warning
        if random.random() > 0.8:
            steps_today = random.randint(2000, 15000)
            daily_goal = 10000
            
            if steps_today < daily_goal * 0.3:
                signals.append(SignalData(
                    source="activity_tracker",
                    title="Low Activity Day",
                    description=f"Only {steps_today} steps today, well below the {daily_goal} goal.",
                    raw_data={
                        "metric": "steps",
                        "metric_value": steps_today,
                        "threshold": daily_goal * 0.5,
                        "signal_strength": 7.0,
                        "urgency": 4,
                        "confidence": 0.9,
                        "type": "activity_alert",
                    },
                    category=self.category,
                ))

        # Example: Heart rate anomaly
        if random.random() > 0.9:
            resting_hr = random.randint(50, 100)
            signals.append(SignalData(
                source="heart_rate_monitor",
                title="Heart Rate Variation",
                description=f"Resting heart rate at {resting_hr} bpm. Slightly elevated.",
                raw_data={
                    "metric": "resting_hr",
                    "metric_value": resting_hr,
                    "threshold": 80,
                    "signal_strength": 4.0,
                    "urgency": 3,
                    "confidence": 0.8,
                    "type": "hr_anomaly",
                },
                category=self.category,
            ))

        # Example: Recovery score
        if random.random() > 0.85:
            recovery = random.uniform(20, 100)
            signals.append(SignalData(
                source="recovery_tracker",
                title="Recovery Status Update",
                description=f"Today's recovery score: {recovery:.0f}%. "
                           f"{'Consider rest day' if recovery < 40 else 'Good to go'}.",
                raw_data={
                    "metric": "recovery",
                    "metric_value": recovery,
                    "threshold": 50,
                    "signal_strength": (50 - recovery) / 5 if recovery < 50 else 0,
                    "urgency": 7 if recovery < 30 else 4,
                    "confidence": 0.85,
                    "type": "recovery_alert",
                },
                category=self.category,
            ))

        return signals

    def get_interval_seconds(self) -> int:
        """Collect daily."""
        return 24 * 60 * 60
