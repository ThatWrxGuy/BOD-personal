"""Anomaly detector for detecting operational anomalies in shadow mode.

Detects unusual patterns like recommendation spikes, confidence crashes, etc.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.shadow_monitoring.monitoring_models import (
    AnomalyType,
    MonitoringAnomaly,
    MonitoringWindow,
    SeverityLevel,
    ShadowCycleRecord,
)


class AnomalyDetector:
    """Detector for operational anomalies."""
    
    def __init__(
        self,
        recommendation_spike_threshold: float = 3.0,
        confidence_crash_threshold: float = 0.3,
        load_spike_threshold: float = 0.8,
    ):
        """Initialize anomaly detector.
        
        Args:
            recommendation_spike_threshold: Std devs for recommendation spike
            confidence_crash_threshold: Delta for confidence crash
            load_spike_threshold: Load value for spike
        """
        self.recommendation_spike_threshold = recommendation_spike_threshold
        self.confidence_crash_threshold = confidence_crash_threshold
        self.load_spike_threshold = load_spike_threshold
        
        self.anomalies: List[MonitoringAnomaly] = []
        
        # Baseline metrics
        self.baseline_recommendations: float = 0.0
        self.baseline_confidence: float = 0.5
        self.baseline_load: float = 0.0
    
    def update_baseline(self, cycles: List[ShadowCycleRecord]) -> None:
        """Update baseline metrics from recent cycles."""
        if len(cycles) < 10:
            return
        
        # Calculate baselines from first 10 cycles
        baseline_cycles = cycles[:10]
        
        self.baseline_recommendations = sum(
            c.recommendations_generated for c in baseline_cycles
        ) / len(baseline_cycles)
        
        self.baseline_confidence = sum(
            c.confidence_score for c in baseline_cycles
        ) / len(baseline_cycles)
        
        self.baseline_load = sum(
            c.governance_load_score for c in baseline_cycles
        ) / len(baseline_cycles)
    
    def detect_anomalies(
        self,
        cycles: List[ShadowCycleRecord],
    ) -> List[MonitoringAnomaly]:
        """Detect anomalies in cycle data."""
        if not cycles:
            return []
        
        self.anomalies = []
        
        # Update baseline
        self.update_baseline(cycles)
        
        # Check each cycle for anomalies
        for cycle in cycles[-20:]:  # Check recent cycles
            self._check_recommendation_spike(cycle)
            self._check_confidence_crash(cycle)
            self._check_load_spike(cycle)
            self._check_doctrine_conflict_surge(cycle)
            self._check_tier_distribution_shift(cycle)
        
        return self.anomalies
    
    def _check_recommendation_spike(self, cycle: ShadowCycleRecord) -> None:
        """Check for recommendation spike."""
        if self.baseline_recommendations == 0:
            return
        
        ratio = cycle.recommendations_generated / self.baseline_recommendations
        
        if ratio > self.recommendation_spike_threshold:
            anomaly = MonitoringAnomaly(
                anomaly_type=AnomalyType.RECOMMENDATION_SPIKE,
                severity=SeverityLevel.HIGH if ratio > 5 else SeverityLevel.MEDIUM,
                cycle_number=cycle.cycle_number,
                description=f"Recommendation spike detected: {cycle.recommendations_generated} recommendations (baseline: {self.baseline_recommendations:.1f})",
                current_value=float(cycle.recommendations_generated),
                expected_range=(0, self.baseline_recommendations * self.recommendation_spike_threshold),
                deviation=ratio,
            )
            self.anomalies.append(anomaly)
    
    def _check_confidence_crash(self, cycle: ShadowCycleRecord) -> None:
        """Check for confidence crash."""
        delta = cycle.confidence_score - self.baseline_confidence
        
        if delta < -self.confidence_crash_threshold:
            severity = SeverityLevel.CRITICAL if delta < -0.5 else SeverityLevel.HIGH
            
            anomaly = MonitoringAnomaly(
                anomaly_type=AnomalyType.CONFIDENCE_CRASH,
                severity=severity,
                cycle_number=cycle.cycle_number,
                description=f"Confidence crash detected: {cycle.confidence_score:.2f} (baseline: {self.baseline_confidence:.2f})",
                current_value=cycle.confidence_score,
                expected_range=(self.baseline_confidence - 0.1, self.baseline_confidence + 0.1),
                deviation=abs(delta),
            )
            self.anomalies.append(anomaly)
    
    def _check_load_spike(self, cycle: ShadowCycleRecord) -> None:
        """Check for governance load spike."""
        if cycle.governance_load_score > self.load_spike_threshold:
            severity = SeverityLevel.HIGH if cycle.governance_load_score > 0.9 else SeverityLevel.MEDIUM
            
            anomaly = MonitoringAnomaly(
                anomaly_type=AnomalyType.GOVERNANCE_LOAD_SPIKE,
                severity=severity,
                cycle_number=cycle.cycle_number,
                description=f"Governance load spike: {cycle.governance_load_score:.2f}",
                current_value=cycle.governance_load_score,
                expected_range=(0, self.load_spike_threshold),
                deviation=cycle.governance_load_score,
            )
            self.anomalies.append(anomaly)
    
    def _check_doctrine_conflict_surge(self, cycle: ShadowCycleRecord) -> None:
        """Check for doctrine conflict surge."""
        if cycle.doctrine_conflicts > 3:
            severity = SeverityLevel.HIGH if cycle.doctrine_conflicts > 5 else SeverityLevel.MEDIUM
            
            anomaly = MonitoringAnomaly(
                anomaly_type=AnomalyType.DOCTRINE_CONFLICT_SURGE,
                severity=severity,
                cycle_number=cycle.cycle_number,
                description=f"Doctrine conflict surge: {cycle.doctrine_conflicts} conflicts",
                current_value=float(cycle.doctrine_conflicts),
                expected_range=(0, 3),
                deviation=float(cycle.doctrine_conflicts),
            )
            self.anomalies.append(anomaly)
    
    def _check_tier_distribution_shift(self, cycle: ShadowCycleRecord) -> None:
        """Check for tier distribution shift."""
        # This would need historical tier distribution comparison
        # For now, skip this check
        pass
    
    def get_anomalies(
        self,
        severity: Optional[SeverityLevel] = None,
    ) -> List[MonitoringAnomaly]:
        """Get detected anomalies, optionally filtered by severity."""
        if severity:
            return [a for a in self.anomalies if a.severity == severity]
        return self.anomalies
    
    def get_critical_anomalies(self) -> List[MonitoringAnomaly]:
        """Get critical severity anomalies."""
        return self.get_anomalies(SeverityLevel.CRITICAL)
    
    def get_high_severity_anomalies(self) -> List[MonitoringAnomaly]:
        """Get high severity anomalies."""
        return self.get_anomalies(SeverityLevel.HIGH)
    
    def clear_anomalies(self) -> None:
        """Clear detected anomalies."""
        self.anomalies = []
    
    def reset(self) -> None:
        """Reset detector state."""
        self.anomalies = []
        self.baseline_recommendations = 0.0
        self.baseline_confidence = 0.5
        self.baseline_load = 0.0


def create_anomaly_detector() -> AnomalyDetector:
    """Factory function to create an anomaly detector."""
    return AnomalyDetector()
