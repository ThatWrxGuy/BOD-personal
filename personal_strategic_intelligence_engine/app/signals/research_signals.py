"""Research signal collector for external information feeds."""
import random
from datetime import datetime, timedelta

from app.models.strategic_signal import SignalCategory
from app.signals.signal_base import BaseSignalCollector, SignalData


class ResearchSignalCollector(BaseSignalCollector):
    """Collects signals from research and information feeds."""

    def __init__(self, config: dict = None):
        super().__init__()
        self.config = config or {}

    @property
    def category(self) -> str:
        return SignalCategory.RESEARCH

    async def collect(self) -> list[SignalData]:
        """Collect research signals."""
        signals = []

        # In production, this would connect to:
        # - News APIs
        # - RSS feeds
        # - Research databases
        # - Newsletters
        # - Competitor monitoring

        # Example: Industry news signal
        if random.random() > 0.6:
            topics = ["AI", "blockchain", "climate", "healthcare", "finance", "retail"]
            topic = random.choice(topics)
            relevance = random.uniform(0.5, 0.95)
            signals.append(SignalData(
                source="news_feed",
                title=f"Industry News: {topic}",
                description=f"Recent developments in {topic} that may impact your strategy.",
                raw_data={
                    "topic": topic,
                    "relevance": relevance,
                    "urgency": random.randint(3, 7),
                    "confidence": 0.6,
                    "type": "industry_news",
                },
                category=self.category,
            ))

        # Example: Competitor update
        if random.random() > 0.8:
            signals.append(SignalData(
                source="competitor_monitor",
                title="Competitor Activity Detected",
                description="A competitor has made a significant announcement.",
                raw_data={
                    "competitor": "competitor_xyz",
                    "signal_strength": random.uniform(4, 8),
                    "urgency": random.randint(4, 7),
                    "confidence": 0.55,
                    "type": "competitor_update",
                },
                category=self.category,
            ))

        # Example: Technology trend
        if random.random() > 0.75:
            techs = ["LLMs", "edge computing", "quantum", "5G", "AR/VR"]
            tech = random.choice(techs)
            signals.append(SignalData(
                source="tech_trends",
                title=f"Technology Trend: {tech}",
                description=f"New developments in {tech} worth evaluating.",
                raw_data={
                    "technology": tech,
                    "signal_strength": random.uniform(3, 7),
                    "urgency": 4,
                    "confidence": 0.5,
                    "type": "tech_trend",
                },
                category=self.category,
            ))

        # Example: Regulatory change
        if random.random() > 0.9:
            regions = ["US", "EU", "UK", "global"]
            region = random.choice(regions)
            signals.append(SignalData(
                source="regulatory_monitor",
                title=f"Regulatory Change in {region}",
                description=f"New regulations announced in {region} that may affect your industry.",
                raw_data={
                    "region": region,
                    "signal_strength": random.uniform(5, 9),
                    "urgency": 7,
                    "confidence": 0.7,
                    "type": "regulatory_change",
                },
                category=self.category,
            ))

        return signals

    def get_interval_seconds(self) -> int:
        """Collect every 6 hours."""
        return 6 * 60 * 60
