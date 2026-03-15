"""Confidence calibrator for adjusting confidence based on outcomes."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.learning.outcome_models import (
    ConfidenceCalibrationResult,
    RecommendationEffectivenessScore,
    OutcomeQuality,
)

logger = logging.getLogger(__name__)


class ConfidenceCalibrator:
    """Adjusts future confidence based on outcome data."""

    # Maximum adjustment per domain per evaluation
    MAX_ADJUSTMENT = 0.15
    MIN_CONFIDENCE = 0.1
    MAX_CONFIDENCE = 0.95

    def __init__(self):
        self._calibration_history: Dict[str, List[ConfidenceCalibrationResult]] = {}
        self._current_confidence: Dict[str, float] = {}  # domain -> confidence

    def calibrate_confidence(
        self,
        domain: str,
        effectiveness_score: "RecommendationEffectivenessScore",
    ) -> "ConfidenceCalibrationResult":
        """Calibrate confidence for a domain based on effectiveness."""
        
        # Get baseline confidence (default 0.7)
        baseline = self._current_confidence.get(domain, 0.7)

        # Calculate adjustment based on effectiveness
        adjustment = self._calculate_adjustment(
            effectiveness_score.average_effectiveness,
            effectiveness_score.confidence_impact,
            effectiveness_score.total_evaluations,
        )

        # Apply adjustment
        adjusted = baseline + adjustment
        
        # Bound confidence
        adjusted = max(self.MIN_CONFIDENCE, min(self.MAX_CONFIDENCE, adjusted))

        # Create result
        result = ConfidenceCalibrationResult(
            domain=domain,
            baseline_confidence=baseline,
            adjusted_confidence=adjusted,
            calibration_factor=adjustment,
            evidence_count=effectiveness_score.total_evaluations,
            rationale=self._generate_rationale(
                domain, adjustment, effectiveness_score
            ),
        )

        # Update current confidence
        self._current_confidence[domain] = adjusted

        # Store in history
        if domain not in self._calibration_history:
            self._calibration_history[domain] = []
        self._calibration_history[domain].append(result)

        logger.info(
            f"Calibrated {domain}: {baseline:.2f} -> {adjusted:.2f} "
            f"(adjustment: {adjustment:+.2f})"
        )

        return result

    def _calculate_adjustment(
        self,
        effectiveness: float,
        confidence_impact: float,
        evidence_count: int,
    ) -> float:
        """Calculate confidence adjustment based on effectiveness."""
        
        # Base adjustment from effectiveness
        # effectiveness: 0-1 scale where 1 is best
        if effectiveness >= 0.7:
            base_adjustment = 0.05  # Increase confidence
        elif effectiveness >= 0.4:
            base_adjustment = 0.0  # No change
        else:
            base_adjustment = -0.05  # Decrease confidence

        # Factor in the pre-calculated confidence impact
        impact_factor = confidence_impact

        # Factor in evidence count (more evidence = less adjustment)
        evidence_factor = min(1.0, evidence_count / 5)

        # Calculate final adjustment
        adjustment = (base_adjustment + impact_factor) * evidence_factor

        # Bound adjustment
        return max(-self.MAX_ADJUSTMENT, min(self.MAX_ADJUSTMENT, adjustment))

    def _generate_rationale(
        self,
        domain: str,
        adjustment: float,
        score: RecommendationEffectivenessScore,
    ) -> str:
        """Generate human-readable rationale for calibration."""
        
        parts = []

        # Effectiveness summary
        if score.average_effectiveness >= 0.7:
            parts.append("high effectiveness")
        elif score.average_effectiveness >= 0.4:
            parts.append("moderate effectiveness")
        else:
            parts.append("low effectiveness")

        # Evidence count
        parts.append(f"{score.total_evaluations} evaluations")

        # Pattern flags
        if score.pattern_flags:
            parts.append(f"patterns: {', '.join(score.pattern_flags[:2])}")

        # Adjustment direction
        if adjustment > 0:
            parts.append("confidence increased")
        elif adjustment < 0:
            parts.append("confidence decreased")
        else:
            parts.append("confidence unchanged")

        return "; ".join(parts)

    def get_confidence_for_domain(self, domain: str) -> float:
        """Get current confidence for a domain."""
        return self._current_confidence.get(domain, 0.7)

    def get_all_confidences(self) -> Dict[str, float]:
        """Get all domain confidences."""
        return self._current_confidence.copy()

    def get_calibration_history(
        self,
        domain: str,
        limit: int = 10
    ) -> List[ConfidenceCalibrationResult]:
        """Get calibration history for a domain."""
        history = self._calibration_history.get(domain, [])
        return history[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get calibrator statistics."""
        
        if not self._current_confidence:
            return {
                "domains_calibrated": 0,
                "total_adjustments": 0,
                "avg_confidence": 0.0,
            }

        total_adjustments = sum(len(h) for h in self._calibration_history.values())
        
        return {
            "domains_calibrated": len(self._current_confidence),
            "total_adjustments": total_adjustments,
            "avg_confidence": sum(self._current_confidence.values()) / len(self._current_confidence),
            "confidences": self._current_confidence,
        }

    def reset_calibration(self, domain: Optional[str] = None):
        """Reset calibration for a domain or all domains."""
        if domain:
            if domain in self._current_confidence:
                del self._current_confidence[domain]
            if domain in self._calibration_history:
                del self._calibration_history[domain]
        else:
            self._current_confidence.clear()
            self._calibration_history.clear()


# Global calibrator instance
_calibrator: Optional[ConfidenceCalibrator] = None


def get_confidence_calibrator() -> ConfidenceCalibrator:
    """Get the global confidence calibrator instance."""
    global _calibrator
    if _calibrator is None:
        _calibrator = ConfidenceCalibrator()
    return _calibrator
