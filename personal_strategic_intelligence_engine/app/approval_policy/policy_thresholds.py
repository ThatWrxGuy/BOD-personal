"""Policy thresholds - configurable thresholds for approval decisions."""
import logging
from typing import Dict, Optional

from app.approval_policy.approval_policy_models import ApprovalTierLevel

logger = logging.getLogger(__name__)


class PolicyThresholds:
    """Configurable policy thresholds for approval decisions."""

    # Default thresholds
    DEFAULT_THRESHOLDS = {
        # Tier 2 (Conditional Auto) eligibility thresholds
        "min_execution_samples": 10,
        "min_success_rate": 0.90,  # 90%
        "min_confidence": 0.85,    # 85%
        "max_risk_score": 0.30,    # 30%
        
        # Tier 1 (Manual Fast-Path) eligibility
        "fast_path_min_samples": 3,
        "fast_path_min_success_rate": 0.70,
        
        # Tier downgrade thresholds
        "downgrade_success_rate": 0.60,
        "downgrade_min_samples": 5,
        
        # Safety margins
        "confidence_buffer": 0.05,
        "risk_buffer": 0.05,
    }

    def __init__(self, custom_thresholds: Optional[Dict[str, float]] = None):
        """
        Initialize with custom thresholds.
        
        Args:
            custom_thresholds: Optional custom threshold values
        """
        self._thresholds = self.DEFAULT_THRESHOLDS.copy()
        
        if custom_thresholds:
            self._thresholds.update(custom_thresholds)
        
        logger.info(f"Initialized PolicyThresholds with {len(self._thresholds)} thresholds")

    def get(self, key: str, default: float = 0.0) -> float:
        """Get a threshold value."""
        return self._thresholds.get(key, default)

    def set(self, key: str, value: float):
        """Set a threshold value."""
        if key in self.DEFAULT_THRESHOLDS:
            self._thresholds[key] = value
            logger.info(f"Set threshold {key} = {value}")
        else:
            logger.warning(f"Unknown threshold key: {key}")

    def reset(self):
        """Reset to default thresholds."""
        self._thresholds = self.DEFAULT_THRESHOLDS.copy()
        logger.info("Reset thresholds to defaults")

    def get_all(self) -> Dict[str, float]:
        """Get all thresholds."""
        return self._thresholds.copy()

    # Convenience methods
    @property
    def min_execution_samples(self) -> int:
        """Minimum execution samples for auto-eligibility."""
        return int(self._thresholds["min_execution_samples"])

    @property
    def min_success_rate(self) -> float:
        """Minimum success rate for auto-eligibility."""
        return self._thresholds["min_success_rate"]

    @property
    def min_confidence(self) -> float:
        """Minimum confidence for auto-eligibility."""
        return self._thresholds["min_confidence"]

    @property
    def max_risk_score(self) -> float:
        """Maximum risk score for auto-eligibility."""
        return self._thresholds["max_risk_score"]

    @property
    def fast_path_min_samples(self) -> int:
        """Minimum samples for fast-path approval."""
        return int(self._thresholds["fast_path_min_samples"])

    @property
    def fast_path_min_success_rate(self) -> float:
        """Minimum success rate for fast-path."""
        return self._thresholds["fast_path_min_success_rate"]

    @property
    def downgrade_success_rate(self) -> float:
        """Success rate threshold for downgrade."""
        return self._thresholds["downgrade_success_rate"]

    def meets_auto_eligibility(
        self,
        execution_count: int,
        success_rate: float,
        confidence: float,
        risk_score: float,
    ) -> tuple:
        """
        Check if requirements are met for auto-eligibility.
        
        Returns:
            (meets_requirements, blockers_list)
        """
        blockers = []
        
        if execution_count < self.min_execution_samples:
            blockers.append(
                f"Execution count {execution_count} < {self.min_execution_samples}"
            )
        
        if success_rate < self.min_success_rate:
            blockers.append(
                f"Success rate {success_rate:.1%} < {self.min_success_rate:.1%}"
            )
        
        if confidence < self.min_confidence:
            blockers.append(
                f"Confidence {confidence:.1%} < {self.min_confidence:.1%}"
            )
        
        if risk_score > self.max_risk_score:
            blockers.append(
                f"Risk score {risk_score:.1%} > {self.max_risk_score:.1%}"
            )
        
        return len(blockers) == 0, blockers


# Global thresholds instance
_thresholds: Optional["PolicyThresholds"] = None


def get_policy_thresholds() -> PolicyThresholds:
    """Get the global policy thresholds instance."""
    global _thresholds
    if _thresholds is None:
        _thresholds = PolicyThresholds()
    return _thresholds
