"""Base classes for signal system."""
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from app.models.strategic_signal import SignalCategory


class SignalData:
    """Data transfer object for raw signal data before processing."""

    def __init__(
        self,
        source: str,
        title: str,
        description: str,
        raw_data: dict[str, Any],
        category: str,
    ):
        self.source = source
        self.title = title
        self.description = description
        self.raw_data = raw_data
        self.category = category
        self.timestamp = datetime.utcnow()


class SignalScore:
    """Scores for a processed signal."""

    def __init__(
        self,
        signal_strength: float,
        urgency: int,
        confidence: float,
    ):
        self.signal_strength = signal_strength  # 0-10
        self.urgency = urgency  # 1-10
        self.confidence = confidence  # 0-1


class BaseSignalCollector(ABC):
    """Abstract base class for signal collectors."""

    def __init__(self):
        self.source_name = self.__class__.__name__.replace("Collector", "").lower()

    @property
    @abstractmethod
    def category(self) -> str:
        """Return the signal category this collector handles."""
        pass

    @property
    @abstractmethod
    async def collect(self) -> list[SignalData]:
        """Collect raw signals from external source."""
        pass

    @abstractmethod
    def get_interval_seconds(self) -> int:
        """Return the collection interval in seconds."""
        pass


class BaseSignalProcessor(ABC):
    """Abstract base class for signal processors."""

    @abstractmethod
    def process(self, signal_data: SignalData) -> dict[str, Any]:
        """Process raw signal data into structured format."""
        pass

    @abstractmethod
    def calculate_scores(self, signal_data: SignalData) -> SignalScore:
        """Calculate signal strength, urgency, and confidence."""
        pass


class SignalRegistry:
    """Registry for managing signal collectors."""

    def __init__(self):
        self._collectors: dict[str, BaseSignalCollector] = {}
        self._processors: dict[str, BaseSignalProcessor] = {}

    def register_collector(self, collector: BaseSignalCollector) -> None:
        """Register a signal collector."""
        self._collectors[collector.category] = collector

    def register_processor(self, processor: BaseSignalProcessor, category: str) -> None:
        """Register a signal processor for a category."""
        self._processors[category] = processor

    def get_collector(self, category: str) -> Optional[BaseSignalCollector]:
        """Get a collector by category."""
        return self._collectors.get(category)

    def get_processor(self, category: str) -> Optional[BaseSignalProcessor]:
        """Get a processor by category."""
        return self._processors.get(category)

    def get_all_collectors(self) -> list[BaseSignalCollector]:
        """Get all registered collectors."""
        return list(self._collectors.values())

    def get_collector_intervals(self) -> dict[str, int]:
        """Get all collector intervals in seconds."""
        return {
            category: collector.get_interval_seconds()
            for category, collector in self._collectors.items()
        }


# Global registry instance
_signal_registry: Optional[SignalRegistry] = None


def get_signal_registry() -> SignalRegistry:
    """Get the global signal registry."""
    global _signal_registry
    if _signal_registry is None:
        _signal_registry = SignalRegistry()
    return _signal_registry
