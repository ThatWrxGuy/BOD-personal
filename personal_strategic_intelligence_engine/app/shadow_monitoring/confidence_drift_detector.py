"""Confidence drift detector for measuring confidence movement over time.

Detects unstable confidence drift, sudden collapse, or inflation.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.shadow_monitoring.monitoring_models import (
    ConfidenceDriftEvent,
    MonitoringWindow,
    SeverityLevel,
    ShadowCycleRecord,
)


class ConfidenceDriftDetector:
    """Detector for confidence drift over time."""
    
    def __init__(
        self,
        collapse_threshold: float = 0.3,
        inflation_threshold: float = 0.3,
        drift_threshold: float = 0.1,
    ):
        """Initialize confidence drift detector.
        
        Args:
            collapse_threshold: Threshold for sudden confidence collapse
            inflation_threshold: Threshold for sudden confidence inflation
            drift_threshold: Threshold for gradual drift detection
        """
        self.collapse_threshold = collapse_threshold
        self.inflation_threshold = inflation_threshold
        self.drift_threshold = drift_threshold
        
        self.previous_confidence: Optional[float] = None
        self.confidence_history: List[float] = []
        self.drift_events: List[ConfidenceDriftEvent] = []
    
    def record_confidence(self, confidence: float, cycle_number: int) -> None:
        """Record confidence from a cycle."""
        self.confidence_history.append(confidence)
        
        # Check for sudden changes
        if self.previous_confidence is not None:
            delta = confidence - self.previous_confidence
            
            # Detect sudden collapse
            if delta < -self.collapse_threshold:
                event = self._create_drift_event(
                    drift_type="sudden_collapse",
                    severity=SeverityLevel.HIGH if delta < -0.5 else SeverityLevel.MEDIUM,
                    previous=self.previous_confidence,
                    current=confidence,
                    delta=delta,
                    cycle_number=cycle_number,
                )
                self.drift_events.append(event)
            
            # Detect sudden inflation
            elif delta > self.inflation_threshold:
                event = self._create_drift_event(
                    drift_type="sudden_inflation",
                    severity=SeverityLevel.MEDIUM,
                    previous=self.previous_confidence,
                    current=confidence,
                    delta=delta,
                    cycle_number=cycle_number,
                )
                self.drift_events.append(event)
        
        # Keep history bounded
        if len(self.confidence_history) > 1000:
            self.confidence_history = self.confidence_history[-500:]
        
        self.previous_confidence = confidence
    
    def detect_gradual_drift(self, window: int = 50) -> Optional[ConfidenceDriftEvent]:
        """Detect gradual confidence drift over a window."""
        if len(self.confidence_history) < window:
            return None
        
        recent = self.confidence_history[-window:]
        
        first_avg = sum(recent[:window//2]) / (window // 2)
        second_avg = sum(recent[window//2:]) / (window - window // 2)
        
        delta = second_avg - first_avg
        
        if abs(delta) > self.drift_threshold * window:
            severity = SeverityLevel.HIGH if abs(delta) > 0.3 else SeverityLevel.MEDIUM
            
            event = self._create_drift_event(
                drift_type="gradual_drift",
                severity=severity,
                previous=first_avg,
                current=second_avg,
                delta=delta,
                cycle_number=0,
            )
            self.drift_events.append(event)
            return event
        
        return None
    
    def detect_oscillation(self, window: int = 20) -> Optional[ConfidenceDriftEvent]:
        """Detect oscillating confidence."""
        if len(self.confidence_history) < window:
            return None
        
        recent = self.confidence_history[-window:]
        
        # Count direction changes
        changes = 0
        for i in range(1, len(recent)):
            if (recent[i] > recent[i-1]) != (recent[i-1] > recent[i-2] if i > 1 else False):
                changes += 1
        
        if changes >= window // 2:  # At least half the window changed direction
            severity = SeverityLevel.MEDIUM if changes >= window // 3 else SeverityLevel.LOW
            
            event = self._create_drift_event(
                drift_type="oscillation",
                severity=severity,
                previous=recent[0],
                current=recent[-1],
                delta=recent[-1] - recent[0],
                cycle_number=0,
            )
            self.drift_events.append(event)
            return event
        
        return None
    
    def get_drift_events(self) -> List[ConfidenceDriftEvent]:
        """Get all detected drift events."""
        return self.drift_events
    
    def get_confidence_statistics(self, window: MonitoringWindow) -> Dict[str, float]:
        """Get confidence statistics for a window."""
        window_sizes = {
            MonitoringWindow.ONE_DAY: 24,
            MonitoringWindow.SEVEN_DAYS: 24 * 7,
            MonitoringWindow.THIRTY_DAYS: 24 * 30,
        }
        
        size = window_sizes.get(window, 24)
        history = self.confidence_history[-size:]
        
        if not history:
            return {"avg": 0.0, "min": 0.0, "max": 0.0, "std": 0.0}
        
        avg = sum(history) / len(history)
        min_val = min(history)
        max_val = max(history)
        
        variance = sum((h - avg) ** 2 for h in history) / len(history)
        std = variance ** 0.5
        
        return {
            "avg": avg,
            "min": min_val,
            "max": max_val,
            "std": std,
            "range": max_val - min_val,
        }
    
    def compare_with_simulation(
        self,
        simulation_stability: float,
    ) -> Dict[str, Any]:
        """Compare real-world drift with simulation expectations."""
        real_stability = 1.0 - self._calculate_variance()
        
        deviation = abs(real_stability - simulation_stability)
        
        return {
            "real_stability": real_stability,
            "simulation_stability": simulation_stability,
            "deviation": deviation,
            "matches_expectations": deviation < 0.2,
        }
    
    def _calculate_variance(self) -> float:
        """Calculate variance of confidence history."""
        if len(self.confidence_history) < 2:
            return 0.0
        
        avg = sum(self.confidence_history) / len(self.confidence_history)
        variance = sum((c - avg) ** 2 for c in self.confidence_history) / len(self.confidence_history)
        
        return variance
    
    def _create_drift_event(
        self,
        drift_type: str,
        severity: SeverityLevel,
        previous: float,
        current: float,
        delta: float,
        cycle_number: int,
    ) -> ConfidenceDriftEvent:
        """Create a confidence drift event."""
        return ConfidenceDriftEvent(
            drift_type=drift_type,
            severity=severity,
            previous_confidence=previous,
            current_confidence=current,
            confidence_delta=delta,
            duration_cycles=1,
            cycle_range=(cycle_number, cycle_number),
            requires_attention=severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL],
            recommendation=self._get_recommendation(drift_type, severity),
        )
    
    def _get_recommendation(self, drift_type: str, severity: SeverityLevel) -> str:
        """Get recommendation for drift type."""
        if severity == SeverityLevel.LOW:
            return "Monitor but no action required"
        
        recommendations = {
            "sudden_collapse": "Investigate cause of confidence collapse. Review recent signals and learning updates.",
            "sudden_inflation": "Verify confidence is not inflated. Check for feedback loop issues.",
            "gradual_drift": "Review doctrine consistency. Consider recalibrating confidence thresholds.",
            "oscillation": "Investigate oscillating signals. Check for conflicting domain signals.",
        }
        
        return recommendations.get(drift_type, "Review confidence behavior")
    
    def reset(self) -> None:
        """Reset detector state."""
        self.confidence_history = []
        self.drift_events = []
        self.previous_confidence = None


def create_confidence_drift_detector() -> ConfidenceDriftDetector:
    """Factory function to create a confidence drift detector."""
    return ConfidenceDriftDetector()
