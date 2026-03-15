"""Model Calibration Engine.

Calibrates signal scoring models and confidence estimates.
"""

from datetime import datetime
from typing import List, Dict, Optional

from app.intelligence.evolution.evolution_models import (
    CalibrationReport,
)


class ModelCalibrationEngine:
    """Calibrates tactical scoring models."""
    
    def __init__(self):
        self.calibration_history: List[CalibrationReport] = []
    
    def calibrate_signal_scoring(
        self,
        signal_records: List[Dict],
    ) -> CalibrationReport:
        """Calibrate signal scoring model."""
        
        if not signal_records:
            return self._empty_report("signal_scoring")
        
        # Analyze score vs outcome correlation
        high_score_signals = [s for s in signal_records if s.get("signal_score", 0) >= 70]
        mid_score_signals = [s for s in signal_records if 50 <= s.get("signal_score", 0) < 70]
        low_score_signals = [s for s in signal_records if s.get("signal_score", 0) < 50]
        
        # Calculate actual win rates by score bucket
        high_win_rate = self._calculate_win_rate(high_score_signals)
        mid_win_rate = self._calculate_win_rate(mid_score_signals)
        low_win_rate = self._calculate_win_rate(low_score_signals)
        
        # Calculate calibration error
        high_error = abs(70 - high_win_rate)
        mid_error = abs(60 - mid_win_rate)
        low_error = abs(40 - low_win_rate)
        
        calibration_error = (high_error + mid_error + low_error) / 3
        
        # Confidence accuracy
        confidence_accuracy = 100 - calibration_error
        
        # Score reliability
        score_reliability = (high_win_rate - low_win_rate) / 100 if high_win_rate > low_win_rate else 0
        
        # Recommended adjustments
        adjustments = {}
        if high_error > 15:
            adjustments["high_score_threshold"] = -10
        if mid_error > 15:
            adjustments["mid_score_baseline"] = 5
        if low_error > 15:
            adjustments["low_score_baseline"] = -5
        
        report = CalibrationReport(
            timestamp=datetime.now(),
            calibrated_model="signal_scoring",
            calibration_error=calibration_error,
            confidence_accuracy=confidence_accuracy,
            score_reliability=score_reliability,
            recommended_adjustments=adjustments,
        )
        
        self.calibration_history.append(report)
        return report
    
    def calibrate_confidence(
        self,
        signal_records: List[Dict],
    ) -> CalibrationReport:
        """Calibrate confidence estimates."""
        
        if not signal_records:
            return self._empty_report("confidence_estimates")
        
        # Analyze confidence vs actual outcomes
        high_conf = [s for s in signal_records if s.get("confidence_score", 0) >= 70]
        mid_conf = [s for s in signal_records if 50 <= s.get("confidence_score", 0) < 70]
        low_conf = [s for s in signal_records if s.get("confidence_score", 0) < 50]
        
        high_actual = self._calculate_win_rate(high_conf)
        mid_actual = self._calculate_win_rate(mid_conf)
        low_actual = self._calculate_win_rate(low_conf)
        
        # Calculate calibration
        high_error = abs(70 - high_actual)
        mid_error = abs(55 - mid_actual)
        low_error = abs(35 - low_actual)
        
        calibration_error = (high_error + mid_error + low_error) / 3
        confidence_accuracy = 100 - calibration_error
        
        # Score reliability
        score_reliability = (high_actual - low_actual) / 100 if high_actual > low_actual else 0
        
        adjustments = {}
        if high_error > 20:
            adjustments["high_confidence_scaling"] = -15
        if low_error > 20:
            adjustments["low_confidence_scaling"] = 10
        
        report = CalibrationReport(
            timestamp=datetime.now(),
            calibrated_model="confidence_estimates",
            calibration_error=calibration_error,
            confidence_accuracy=confidence_accuracy,
            score_reliability=score_reliability,
            recommended_adjustments=adjustments,
        )
        
        self.calibration_history.append(report)
        return report
    
    def calibrate_timing_reliability(
        self,
        signal_records: List[Dict],
    ) -> CalibrationReport:
        """Calibrate timing decision reliability."""
        
        if not signal_records:
            return self._empty_report("timing_reliability")
        
        # Analyze timing decisions
        timing_analyses = {}
        
        for signal in signal_records:
            timing = signal.get("timing_decision", "unknown")
            if timing not in timing_analyses:
                timing_analyses[timing] = []
            timing_analyses[timing].append(signal)
        
        # Calculate reliability per timing decision
        avg_error = 0
        count = 0
        
        for timing, signals in timing_analyses.items():
            actual = self._calculate_win_rate(signals)
            # Expected based on historical
            expected = {"enter_now": 55, "wait_for_pullback": 60, "wait_for_confirmation": 65, "avoid_entry": 40}.get(timing, 50)
            avg_error += abs(expected - actual)
            count += 1
        
        calibration_error = avg_error / count if count > 0 else 0
        confidence_accuracy = 100 - calibration_error
        score_reliability = (100 - calibration_error) / 100
        
        report = CalibrationReport(
            timestamp=datetime.now(),
            calibrated_model="timing_reliability",
            calibration_error=calibration_error,
            confidence_accuracy=confidence_accuracy,
            score_reliability=score_reliability,
            recommended_adjustments={},
        )
        
        self.calibration_history.append(report)
        return report
    
    def calibrate_suppression_thresholds(
        self,
        signal_records: List[Dict],
    ) -> CalibrationReport:
        """Calibrate suppression thresholds."""
        
        if not signal_records:
            return self._empty_report("suppression_thresholds")
        
        # Analyze suppressed signals
        suppressed = [s for s in signal_records if s.get("suppressed")]
        non_suppressed = [s for s in signal_records if not s.get("suppressed")]
        
        suppressed_win_rate = self._calculate_win_rate(suppressed)
        non_suppressed_win_rate = self._calculate_win_rate(non_suppressed)
        
        # A good suppression should block more losses than wins
        calibration_error = abs(suppressed_win_rate - non_suppressed_win_rate) / 2
        confidence_accuracy = max(0, 100 - calibration_error * 2)
        
        # If suppressed signals win more than non-suppressed, thresholds too tight
        adjustments = {}
        if suppressed_win_rate > non_suppressed_win_rate + 10:
            adjustments["suppression_relaxation"] = 0.8
        elif suppressed_win_rate < non_suppressed_win_rate - 10:
            adjustments["suppression_tighten"] = 1.2
        
        report = CalibrationReport(
            timestamp=datetime.now(),
            calibrated_model="suppression_thresholds",
            calibration_error=calibration_error,
            confidence_accuracy=confidence_accuracy,
            score_reliability=confidence_accuracy / 100,
            recommended_adjustments=adjustments,
        )
        
        self.calibration_history.append(report)
        return report
    
    def _calculate_win_rate(self, signals: List[Dict]) -> float:
        """Calculate win rate from signals."""
        if not signals:
            return 0
        
        wins = [s for s in signals if s.get("outcome") == "win"]
        return len(wins) / len(signals) * 100
    
    def _empty_report(self, model_name: str) -> CalibrationReport:
        """Return empty calibration report."""
        return CalibrationReport(
            timestamp=datetime.now(),
            calibrated_model=model_name,
            calibration_error=0,
            confidence_accuracy=0,
            score_reliability=0,
            recommended_adjustments={},
        )


def create_engine() -> ModelCalibrationEngine:
    """Create a new model calibration engine."""
    return ModelCalibrationEngine()
