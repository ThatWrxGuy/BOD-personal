"""Signal normalizer for converting provider payloads to canonical models."""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from app.signal_ingestion.signal_models import (
    LiveSignal,
    NormalizedSignal,
    SignalType,
    DEFAULT_FRESHNESS_WINDOW_SECONDS,
)

logger = logging.getLogger(__name__)


class SignalNormalizer:
    """Converts provider-specific payloads into canonical signal models."""

    def __init__(self):
        self._schema_mappings: Dict[str, Dict[str, str]] = {
            # Financial data mapping
            "financial": {
                "performance": "performance_score",
                "risk_level": "risk_score",
                "opportunity": "opportunity_score",
                "value": "momentum_score",
                "allocation": "resource_allocation",
            },
            # Productivity signals mapping
            "productivity": {
                "task_completion": "performance_score",
                "focus_score": "performance_score",
                "interruptions": "risk_score",
                "available_opportunities": "opportunity_score",
            },
            # System telemetry mapping
            "telemetry": {
                "uptime": "performance_score",
                "error_rate": "risk_score",
                "capacity": "opportunity_score",
                "load": "momentum_score",
            },
        }

    def normalize_signal(
        self,
        live_signal: LiveSignal,
        source_config: Optional[Dict[str, Any]] = None
    ) -> NormalizedSignal:
        """Normalize a live signal into canonical format."""
        start_time = datetime.utcnow()

        # Get the source's schema mapping
        mapping = self._get_mapping_for_source(live_signal.source_id)

        # Normalize the payload
        normalized_payload = self._normalize_payload(
            live_signal.raw_payload,
            mapping,
            source_config or {}
        )

        # Calculate freshness score
        freshness_score = self._calculate_freshness(
            live_signal.timestamp,
            DEFAULT_FRESHNESS_WINDOW_SECONDS
        )

        # Calculate confidence based on data completeness
        confidence_score = self._calculate_confidence(
            normalized_payload,
            live_signal.raw_payload
        )

        # Calculate processing latency
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        return NormalizedSignal(
            source_id=live_signal.source_id,
            signal_type=live_signal.signal_type,
            raw_payload=live_signal.raw_payload,
            normalized_payload=normalized_payload,
            timestamp=live_signal.timestamp,
            ingestion_timestamp=datetime.utcnow(),
            freshness_score=freshness_score,
            confidence_score=confidence_score,
        )

    def _get_mapping_for_source(self, source_id: str) -> Dict[str, str]:
        """Get the schema mapping for a source."""
        if "financial" in source_id:
            return self._schema_mappings.get("financial", {})
        elif "productivity" in source_id:
            return self._schema_mappings.get("productivity", {})
        elif "telemetry" in source_id:
            return self._schema_mappings.get("telemetry", {})
        return {}

    def _normalize_payload(
        self,
        raw_payload: Dict[str, Any],
        mapping: Dict[str, str],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalize raw payload using schema mapping."""
        normalized = {}

        # Apply schema mapping
        for raw_key, canonical_key in mapping.items():
            if raw_key in raw_payload:
                normalized[canonical_key] = self._sanitize_value(
                    raw_payload[raw_key]
                )

        # Copy unmapped fields that might be useful
        for key, value in raw_payload.items():
            if key not in mapping and isinstance(value, (str, int, float, bool)):
                normalized[key] = self._sanitize_value(value)

        # Add domain type if present
        if "domain" in raw_payload:
            normalized["domain"] = raw_payload["domain"]

        return normalized

    def _sanitize_value(self, value: Any) -> Any:
        """Sanitize values to ensure type consistency."""
        if isinstance(value, float):
            # Clamp to valid range
            return max(0.0, min(10.0, value))
        elif isinstance(value, int):
            return max(0, min(10, value))
        elif isinstance(value, str):
            # Try to convert numeric strings
            try:
                return float(value)
            except (ValueError, TypeError):
                return value
        return value

    def _calculate_freshness(
        self,
        signal_timestamp: datetime,
        window_seconds: int
    ) -> float:
        """Calculate freshness score (0-1) based on signal age."""
        age_seconds = (datetime.utcnow() - signal_timestamp).total_seconds()

        if age_seconds <= 0:
            return 1.0  # Future or now

        if age_seconds >= window_seconds:
            return 0.0  # Stale

        # Linear decay
        return 1.0 - (age_seconds / window_seconds)

    def _calculate_confidence(
        self,
        normalized: Dict[str, Any],
        raw: Dict[str, Any]
    ) -> float:
        """Calculate confidence based on data completeness."""
        # Check what percentage of expected fields are present
        expected_fields = [
            "performance_score",
            "risk_score",
            "opportunity_score",
            "momentum_score",
            "resource_allocation"
        ]

        present_fields = sum(1 for f in expected_fields if f in normalized)
        completeness = present_fields / len(expected_fields)

        # Bonus for additional fields
        bonus = min(0.2, len(normalized) / 20)

        return min(1.0, completeness + bonus)

    def register_custom_mapping(
        self,
        source_pattern: str,
        mapping: Dict[str, str]
    ):
        """Register a custom schema mapping for a source pattern."""
        self._schema_mappings[source_pattern] = mapping
        logger.info(f"Registered custom mapping for: {source_pattern}")


# Global normalizer instance
_normalizer: Optional[SignalNormalizer] = None


def get_signal_normalizer() -> SignalNormalizer:
    """Get the global signal normalizer instance."""
    global _normalizer
    if _normalizer is None:
        _normalizer = SignalNormalizer()
    return _normalizer
