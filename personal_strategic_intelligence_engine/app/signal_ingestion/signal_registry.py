"""Signal registry for managing external signal providers."""
import logging
from datetime import datetime
from typing import Dict, List, Optional

from app.signal_ingestion.signal_models import (
    SignalSource,
    SignalSourceCategory,
    SignalHealthStatus,
)

logger = logging.getLogger(__name__)


class SignalRegistry:
    """Maintains the registry of signal providers."""

    def __init__(self):
        self._sources: Dict[str, SignalSource] = {}
        self._health_status: Dict[str, SignalHealthStatus] = {}
        self._initialize_default_sources()

    def _initialize_default_sources(self):
        """Initialize with default signal sources for testing."""
        default_sources = [
            SignalSource(
                source_id="demo_financial",
                name="Demo Financial Data",
                category=SignalSourceCategory.FINANCIAL_DATA,
                description="Demo financial signal provider for testing",
                enabled=True,
                reliability_score=0.8,
            ),
            SignalSource(
                source_id="demo_productivity",
                name="Demo Productivity Signals",
                category=SignalSourceCategory.PRODUCTIVITY_SIGNALS,
                description="Demo productivity signal provider for testing",
                enabled=True,
                reliability_score=0.75,
            ),
            SignalSource(
                source_id="demo_telemetry",
                name="Demo System Telemetry",
                category=SignalSourceCategory.SYSTEM_TELEMETRY,
                description="Demo system telemetry provider for testing",
                enabled=True,
                reliability_score=0.9,
            ),
        ]
        for source in default_sources:
            self._sources[source.source_id] = source
            self._health_status[source.source_id] = SignalHealthStatus(
                source_id=source.source_id,
                status="healthy",
                uptime_percentage=100.0,
            )

    def register_source(self, source: SignalSource) -> bool:
        """Register a new signal source."""
        if source.source_id in self._sources:
            logger.warning(f"Source {source.source_id} already registered, updating")
            self._sources[source.source_id] = source
            return False
        
        self._sources[source.source_id] = source
        self._health_status[source.source_id] = SignalHealthStatus(
            source_id=source.source_id,
            status="unknown",
        )
        logger.info(f"Registered signal source: {source.source_id}")
        return True

    def enable_source(self, source_id: str) -> bool:
        """Enable a signal source."""
        if source_id not in self._sources:
            return False
        self._sources[source_id].enabled = True
        logger.info(f"Enabled source: {source_id}")
        return True

    def disable_source(self, source_id: str) -> bool:
        """Disable a signal source."""
        if source_id not in self._sources:
            return False
        self._sources[source_id].enabled = False
        logger.info(f"Disabled source: {source_id}")
        return True

    def get_source(self, source_id: str) -> Optional[SignalSource]:
        """Get a signal source by ID."""
        return self._sources.get(source_id)

    def get_all_sources(self) -> List[SignalSource]:
        """Get all registered sources."""
        return list(self._sources.values())

    def get_enabled_sources(self) -> List[SignalSource]:
        """Get all enabled sources."""
        return [s for s in self._sources.values() if s.enabled]

    def get_sources_by_category(self, category: SignalSourceCategory) -> List[SignalSource]:
        """Get sources by category."""
        return [s for s in self._sources.values() if s.category == category]

    def update_health_status(self, status: SignalHealthStatus):
        """Update health status for a source."""
        self._health_status[status.source_id] = status
        source = self._sources.get(status.source_id)
        if source:
            source.health_status = status.status
            source.last_ingestion = datetime.utcnow()

    def get_health_status(self, source_id: str) -> Optional[SignalHealthStatus]:
        """Get health status for a source."""
        return self._health_status.get(source_id)

    def get_all_health_status(self) -> List[SignalHealthStatus]:
        """Get health status for all sources."""
        return list(self._health_status.values())

    def unregister_source(self, source_id: str) -> bool:
        """Unregister a signal source."""
        if source_id in self._sources:
            del self._sources[source_id]
            if source_id in self._health_status:
                del self._health_status[source_id]
            logger.info(f"Unregistered source: {source_id}")
            return True
        return False


# Global registry instance
_registry: Optional[SignalRegistry] = None


def get_signal_registry() -> SignalRegistry:
    """Get the global signal registry instance."""
    global _registry
    if _registry is None:
        _registry = SignalRegistry()
    return _registry
