"""Calibration Controller.

Central orchestration for signal calibration pipeline.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.signal_calibration.calibration_models import (
    CalibratedSignal,
    CalibrationSummary,
    SignalWeightProfile,
)
from app.signal_calibration.freshness_evaluator import get_freshness_evaluator
from app.signal_calibration.persistence_tracker import get_persistence_tracker
from app.signal_calibration.severity_scorer import get_severity_scorer
from app.signal_calibration.source_reliability_adjuster import get_source_reliability_adjuster
from app.signal_calibration.temporal_context_analyzer import get_temporal_context_analyzer
from app.signal_calibration.cross_signal_balancer import get_cross_signal_balancer
from app.signal_calibration.signal_weight_engine import get_signal_weight_engine


class CalibrationController:
    """Orchestrates signal calibration pipeline."""
    
    def __init__(self):
        self.freshness_evaluator = get_freshness_evaluator()
        self.persistence_tracker = get_persistence_tracker()
        self.severity_scorer = get_severity_scorer()
        self.source_adjuster = get_source_reliability_adjuster()
        self.temporal_analyzer = get_temporal_context_analyzer()
        self.cross_balancer = get_cross_signal_balancer()
        self.weight_engine = get_signal_weight_engine()
    
    def calibrate_signal(
        self,
        signal: Dict[str, Any],
    ) -> CalibratedSignal:
        """Calibrate a single signal through the full pipeline."""
        
        signal_id = signal.get("signal_id", "")
        signal_type = signal.get("signal_type", "")
        domain = signal.get("domain", "default")
        source_id = signal.get("source_id", "")
        value = signal.get("value", 0.0)
        
        # 1. Freshness evaluation
        freshness = self.freshness_evaluator.evaluate_freshness(
            signal_id=signal_id,
            signal_type=signal_type,
            last_update=signal.get("last_update"),
            expected_interval_seconds=signal.get("expected_interval_seconds"),
        )
        
        # 2. Persistence tracking
        self.persistence_tracker.record_signal(
            signal_id=signal_id,
            signal_type=signal_type,
            timestamp=signal.get("timestamp"),
        )
        persistence = self.persistence_tracker.evaluate_persistence(
            signal_id=signal_id,
            signal_type=signal_type,
            current_value=value,
        )
        
        # 3. Severity scoring
        severity = self.severity_scorer.score_severity(
            signal_id=signal_id,
            signal_type=signal_type,
            domain=domain,
            value=value,
        )
        
        # 4. Source reliability
        reliability = self.source_adjuster.get_reliability_for_connector(source_id)
        
        # 5. Temporal context
        self.temporal_analyzer.record_value(
            signal_id=signal_id,
            value=value,
            timestamp=signal.get("timestamp"),
        )
        temporal = self.temporal_analyzer.analyze_context(
            signal_id=signal_id,
            current_value=value,
        )
        
        # 6. Cross-signal balancing (needs all signals context)
        # This is done in batch for efficiency
        
        # 7. Compute final weight
        weight_profile = self.weight_engine.compute_weight(
            signal_id=signal_id,
            signal_type=signal_type,
            domain=domain,
            source_id=source_id,
            base_value=value,
            freshness_score=freshness.freshness_score,
            freshness_level=freshness.freshness_level,
            persistence_score=persistence.persistence_score,
            persistence_level=persistence.persistence_level,
            severity_score=severity.severity_score,
            severity_level=severity.severity_level,
            reliability_score=reliability.reliability_score,
            temporal_context_score=temporal.context_score,
            temporal_context=temporal.temporal_context,
            domain_balance=1.0,  # Will be adjusted in batch
        )
        
        # Determine usability
        is_usable = (
            freshness.freshness_level.value != "expired" and
            weight_profile.final_weight > 0.1
        )
        
        # Determine priority
        if severity.severity_level.value == "critical":
            priority = "high"
        elif severity.severity_level.value == "high":
            priority = "medium"
        elif persistence.persistence_level.value in ["persistent", "chronic"]:
            priority = "high"
        else:
            priority = "medium"
        
        # Calculate calibrated value
        calibrated_value = value * weight_profile.final_weight
        
        return CalibratedSignal(
            original_signal_id=signal_id,
            signal_id=signal_id,
            signal_type=signal_type,
            domain=domain,
            category=signal.get("category", "default"),
            source_id=source_id,
            base_value=value,
            calibrated_value=calibrated_value,
            weight_profile=weight_profile,
            temporal_context=temporal,
            is_usable=is_usable,
            is_trend_signal=temporal.temporal_context.value in ["sustained", "structural"],
            is_anomaly=temporal.temporal_context.value == "anomaly",
            priority=priority,
        )
    
    def calibrate_batch(
        self,
        signals: List[Dict[str, Any]],
    ) -> List[CalibratedSignal]:
        """Calibrate multiple signals with cross-signal balancing."""
        
        # First pass: calibrate each signal individually
        calibrated_signals = []
        
        for signal in signals:
            calibrated = self.calibrate_signal(signal)
            calibrated_signals.append(calibrated)
        
        # Second pass: apply cross-signal balancing
        signal_dicts = [
            {
                "signal_id": cs.signal_id,
                "domain": cs.domain,
                "weight": cs.weight_profile.final_weight,
            }
            for cs in calibrated_signals
        ]
        
        balance_results = self.cross_balancer.balance_batch(signal_dicts)
        
        # Update weights with balance adjustment
        for calibrated in calibrated_signals:
            balance = balance_results.get(calibrated.signal_id)
            if balance:
                calibrated.weight_profile.cross_domain_balance = balance.balance_score
                # Recalculate final weight with balance
                calibrated.weight_profile.final_weight = (
                    calibrated.weight_profile.final_weight * 0.95 +
                    balance.balance_score * calibrated.weight_profile.severity_score * 0.05
                )
                calibrated.calibrated_value = calibrated.base_value * calibrated.weight_profile.final_weight
        
        return calibrated_signals
    
    def get_calibration_summary(
        self,
        calibrated_signals: List[CalibratedSignal],
    ) -> CalibrationSummary:
        """Generate calibration summary."""
        
        summary = CalibrationSummary(total_signals=len(calibrated_signals))
        
        # Count by category
        for cs in calibrated_signals:
            # Freshness
            if cs.weight_profile.freshness_level.value == "fresh":
                summary.fresh_signals += 1
            elif cs.weight_profile.freshness_level.value in ["stale", "expired"]:
                summary.stale_signals += 1
            
            # Persistence
            if cs.weight_profile.persistence_level.value in ["persistent", "chronic"]:
                summary.persistent_signals += 1
            else:
                summary.transient_signals += 1
            
            # Severity
            if cs.weight_profile.severity_level.value == "critical":
                summary.critical_signals += 1
            elif cs.weight_profile.severity_level.value == "mild":
                summary.mild_signals += 1
        
        # Calculate average weight
        if calibrated_signals:
            total_weight = sum(cs.weight_profile.final_weight for cs in calibrated_signals)
            summary.avg_weight = total_weight / len(calibrated_signals)
        
        # Weight distribution
        weight_dist = self.weight_engine.get_weight_distribution(
            [cs.weight_profile for cs in calibrated_signals]
        )
        summary.weight_distribution = weight_dist
        
        return summary
    
    def get_high_priority_signals(
        self,
        calibrated_signals: List[CalibratedSignal],
    ) -> List[CalibratedSignal]:
        """Get signals that should receive priority attention."""
        
        priority_signals = [
            cs for cs in calibrated_signals
            if cs.is_usable and cs.weight_profile.final_weight > 0.5
        ]
        
        # Sort by weight
        priority_signals.sort(
            key=lambda x: x.weight_profile.final_weight,
            reverse=True,
        )
        
        return priority_signals


# Global controller instance
_calibration_controller: Optional[CalibrationController] = None


def get_calibration_controller() -> CalibrationController:
    """Get the global calibration controller instance."""
    global _calibration_controller
    if _calibration_controller is None:
        _calibration_controller = CalibrationController()
    return _calibration_controller
