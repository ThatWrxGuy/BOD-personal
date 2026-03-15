"""Signal validator for checking signal integrity."""
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from app.signal_ingestion.signal_models import (
    LiveSignal,
    NormalizedSignal,
    SignalIntegrityReport,
    SignalType,
    MIN_CONFIDENCE_THRESHOLD,
)

logger = logging.getLogger(__name__)


class SignalValidator:
    """Validates signal integrity and freshness."""

    def __init__(self):
        self._validation_rules: dict = {}
        self._stale_signals: List[str] = []

    def validate_signal(
        self,
        signal: NormalizedSignal,
        custom_rules: Optional[dict] = None
    ) -> SignalIntegrityReport:
        """Validate a normalized signal."""
        errors = []
        warnings = []

        # Check timestamp validity
        timestamp_errors = self._validate_timestamp(signal.timestamp)
        errors.extend(timestamp_errors)

        # Check freshness
        if signal.freshness_score <= 0:
            errors.append("Signal is stale (freshness_score = 0)")
            self._stale_signals.append(signal.signal_id)
        elif signal.freshness_score < 0.3:
            warnings.append("Signal is approaching staleness")

        # Check confidence
        if signal.confidence_score < MIN_CONFIDENCE_THRESHOLD:
            warnings.append(
                f"Signal confidence below threshold: {signal.confidence_score:.2f}"
            )

        # Check payload completeness
        completeness = self._check_completeness(signal.normalized_payload)
        if completeness < 0.5:
            errors.append(
                f"Signal payload incomplete: {completeness:.0%} complete"
            )

        # Check for anomalies
        anomaly_warnings = self._check_anomalies(signal.normalized_payload)
        warnings.extend(anomaly_warnings)

        # Apply custom rules if provided
        if custom_rules:
            custom_errors = self._apply_custom_rules(
                signal, custom_rules
            )
            errors.extend(custom_errors)

        is_valid = len(errors) == 0

        if not is_valid:
            logger.warning(
                f"Signal validation failed for {signal.signal_id}: {errors}"
            )

        return SignalIntegrityReport(
            signal_id=signal.signal_id,
            is_valid=is_valid,
            validation_errors=errors,
            warnings=warnings,
            timestamp=datetime.utcnow(),
            freshness_score=signal.freshness_score,
            completeness_score=completeness,
        )

    def _validate_timestamp(self, timestamp: datetime) -> List[str]:
        """Validate timestamp is within acceptable range."""
        errors = []
        now = datetime.utcnow()

        # Check if timestamp is in the future
        if timestamp > now + timedelta(minutes=5):
            errors.append(f"Timestamp is in the future: {timestamp}")

        # Check if timestamp is too old
        if timestamp < now - timedelta(days=7):
            errors.append(f"Timestamp is too old: {timestamp}")

        # Check for invalid timestamp
        if timestamp.year < 2020:
            errors.append(f"Invalid timestamp year: {timestamp.year}")

        return errors

    def _check_completeness(self, payload: dict) -> float:
        """Check payload completeness."""
        expected_fields = [
            "performance_score",
            "risk_score",
            "opportunity_score",
            "momentum_score",
            "resource_allocation"
        ]

        if not payload:
            return 0.0

        present = sum(1 for f in expected_fields if f in payload and payload[f] is not None)
        return present / len(expected_fields)

    def _check_anomalies(self, payload: dict) -> List[str]:
        """Check for anomalous values."""
        warnings = []

        # Check for suspicious values
        for field in ["performance_score", "risk_score", "opportunity_score"]:
            if field in payload:
                value = payload[field]
                if not isinstance(value, (int, float)):
                    continue
                if value < 0 or value > 10:
                    warnings.append(f"{field} out of normal range: {value}")

        # Check for sudden changes
        if "momentum_score" in payload:
            momentum = payload["momentum_score"]
            if isinstance(momentum, (int, float)) and abs(momentum) > 8:
                warnings.append(f"Unusually high momentum: {momentum}")

        return warnings

    def _apply_custom_rules(
        self,
        signal: NormalizedSignal,
        rules: dict
    ) -> List[str]:
        """Apply custom validation rules."""
        errors = []

        # Check required fields
        if "required_fields" in rules:
            for field in rules["required_fields"]:
                if field not in signal.normalized_payload:
                    errors.append(f"Required field missing: {field}")

        # Check value ranges
        if "value_ranges" in rules:
            for field, (min_val, max_val) in rules["value_ranges"].items():
                if field in signal.normalized_payload:
                    value = signal.normalized_payload[field]
                    if not isinstance(value, (int, float)):
                        continue
                    if value < min_val or value > max_val:
                        errors.append(
                            f"{field} value {value} outside range [{min_val}, {max_val}]"
                        )

        return errors

    def get_stale_signals(self) -> List[str]:
        """Get list of stale signal IDs."""
        return self._stale_signals.copy()

    def clear_stale_signals(self):
        """Clear the stale signals list."""
        self._stale_signals.clear()


# Global validator instance
_validator: Optional[SignalValidator] = None


def get_signal_validator() -> SignalValidator:
    """Get the global signal validator instance."""
    global _validator
    if _validator is None:
        _validator = SignalValidator()
    return _validator
