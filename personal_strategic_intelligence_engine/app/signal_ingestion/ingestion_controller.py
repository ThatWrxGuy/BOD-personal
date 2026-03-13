"""Ingestion controller orchestrating the signal ingestion pipeline."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.signal_ingestion.signal_models import (
    LiveSignal,
    NormalizedSignal,
    SignalIngestionEvent,
    SignalIntegrityReport,
    SignalSource,
    SignalType,
    LIVE_EXECUTION_ENABLED,
)
from app.signal_ingestion.signal_registry import get_signal_registry
from app.signal_ingestion.signal_normalizer import get_signal_normalizer
from app.signal_ingestion.signal_validator import get_signal_validator
from app.signal_ingestion.signal_router import get_signal_router
from app.signal_ingestion.signal_monitor import get_signal_monitor

logger = logging.getLogger(__name__)


class IngestionController:
    """Orchestrates the signal ingestion pipeline."""

    def __init__(self):
        self.registry = get_signal_registry()
        self.normalizer = get_signal_normalizer()
        self.validator = get_signal_validator()
        self.router = get_signal_router()
        self.monitor = get_signal_monitor()

    def ingest_signal(
        self,
        live_signal: LiveSignal
    ) -> Dict[str, Any]:
        """Process a live signal through the full ingestion pipeline."""
        start_time = datetime.utcnow()

        # Verify execution is disabled
        if LIVE_EXECUTION_ENABLED:
            logger.error("LIVE_EXECUTION_ENABLED is True - rejecting ingestion")
            return {
                "success": False,
                "error": "Live execution is not permitted",
            }

        # Create ingestion event for logging
        event = SignalIngestionEvent(
            source_id=live_signal.source_id,
            signal_type=live_signal.signal_type,
            timestamp=live_signal.timestamp,
            validation_status="pending",
            freshness_score=0.0,
            routing_destinations=[],
        )

        try:
            # Step 1: Check source is registered and enabled
            source = self.registry.get_source(live_signal.source_id)
            if not source:
                logger.warning(f"Unknown source: {live_signal.source_id}")
                event.validation_status = "rejected"
                event.error_message = f"Unknown source: {live_signal.source_id}"
                self.monitor.record_ingestion(event)
                return {
                    "success": False,
                    "error": f"Unknown source: {live_signal.source_id}",
                }

            if not source.enabled:
                logger.warning(f"Source disabled: {live_signal.source_id}")
                event.validation_status = "disabled"
                event.error_message = "Source is disabled"
                self.monitor.record_ingestion(event)
                return {
                    "success": False,
                    "error": "Source is disabled",
                }

            # Step 2: Normalize signal
            normalized = self.normalizer.normalize_signal(
                live_signal,
                source.config
            )

            # Step 3: Validate signal
            integrity = self.validator.validate_signal(normalized)

            # Update event with validation results
            event.validation_status = "valid" if integrity.is_valid else "invalid"
            event.freshness_score = normalized.freshness_score

            # Step 4: Route signal (only if valid)
            if integrity.is_valid:
                destinations = self.router.route_signal(normalized)
                event.routing_destinations = destinations
            else:
                logger.warning(
                    f"Signal validation failed: {integrity.validation_errors}"
                )
                event.error_message = "; ".join(integrity.validation_errors)

            # Calculate latency
            latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            event.processing_latency_ms = latency_ms

            # Record event
            self.monitor.record_ingestion(event)

            return {
                "success": True,
                "signal_id": normalized.signal_id,
                "validation": {
                    "is_valid": integrity.is_valid,
                    "errors": integrity.validation_errors,
                    "warnings": integrity.warnings,
                },
                "routing": event.routing_destinations,
                "metrics": {
                    "freshness_score": normalized.freshness_score,
                    "confidence_score": normalized.confidence_score,
                    "processing_latency_ms": latency_ms,
                },
            }

        except Exception as e:
            logger.error(f"Ingestion error: {e}", exc_info=True)
            event.validation_status = "error"
            event.error_message = str(e)
            self.monitor.record_ingestion(event)

            return {
                "success": False,
                "error": str(e),
            }

    def fetch_and_ingest(
        self,
        source_id: str,
        raw_payload: dict,
        signal_type: SignalType,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Fetch and ingest a signal from a provider."""
        live_signal = LiveSignal(
            source_id=source_id,
            signal_type=signal_type,
            raw_payload=raw_payload,
            timestamp=timestamp or datetime.utcnow(),
        )

        return self.ingest_signal(live_signal)

    def get_status(self) -> Dict[str, Any]:
        """Get overall ingestion system status."""
        sources = self.registry.get_all_sources()
        health = self.monitor.get_all_health_status()

        return {
            "live_execution_enabled": LIVE_EXECUTION_ENABLED,
            "total_sources": len(sources),
            "enabled_sources": len([s for s in sources if s.enabled]),
            "providers": [
                {
                    "source_id": h.source_id,
                    "status": h.status,
                    "uptime": f"{h.uptime_percentage:.1f}%",
                    "avg_latency_ms": f"{h.avg_latency_ms:.1f}",
                }
                for h in health
            ],
        }

    def get_sources(self) -> List[Dict[str, Any]]:
        """Get all registered sources."""
        sources = self.registry.get_all_sources()
        return [
            {
                "source_id": s.source_id,
                "name": s.name,
                "category": s.category.value,
                "enabled": s.enabled,
                "health_status": s.health_status,
            }
            for s in sources
        ]

    def register_source(
        self,
        source_id: str,
        name: str,
        category: str,
        description: str = "",
        config: Optional[dict] = None
    ) -> Dict[str, Any]:
        """Register a new signal source."""
        from app.signal_ingestion.signal_models import SignalSourceCategory

        try:
            cat = SignalSourceCategory(category)
        except ValueError:
            cat = SignalSourceCategory.CUSTOM

        source = SignalSource(
            source_id=source_id,
            name=name,
            category=cat,
            description=description,
            config=config or {},
        )

        self.registry.register_source(source)

        return {
            "success": True,
            "source_id": source_id,
        }

    def get_recent_signals(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent signal ingestion events."""
        events = self.monitor.get_recent_events(limit=limit)
        return [
            {
                "event_id": e.event_id,
                "source_id": e.source_id,
                "signal_type": e.signal_type.value,
                "timestamp": e.timestamp.isoformat(),
                "validation_status": e.validation_status,
                "freshness_score": e.freshness_score,
                "routing_destinations": e.routing_destinations,
            }
            for e in events
        ]

    def get_integrity_report(self) -> Dict[str, Any]:
        """Get signal integrity report."""
        recent = self.monitor.get_recent_events(limit=100)

        valid_count = sum(1 for e in recent if e.validation_status == "valid")
        invalid_count = sum(1 for e in recent if e.validation_status == "invalid")

        return {
            "total_signals": len(recent),
            "valid_signals": valid_count,
            "invalid_signals": invalid_count,
            "validity_rate": valid_count / len(recent) if recent else 0,
            "stale_signals": len(self.validator.get_stale_signals()),
            "degraded_providers": [
                h.source_id for h in self.monitor.get_all_health_status()
                if h.status == "degraded"
            ],
        }


# Global controller instance
_controller: Optional[IngestionController] = None


def get_ingestion_controller() -> IngestionController:
    """Get the global ingestion controller instance."""
    global _controller
    if _controller is None:
        _controller = IngestionController()
    return _controller
