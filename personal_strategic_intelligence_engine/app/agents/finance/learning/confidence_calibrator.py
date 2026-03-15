"""Confidence Calibrator.

Evaluates how well predicted confidence aligns with actual outcomes.
"""

from datetime import datetime
from typing import List, Dict

from app.agents.finance.learning.learning_models import (
    SignalOutcomeRecord,
    SignalOutcome,
    ConfidenceBucket,
    ConfidenceBucketStats,
    ConfidenceCalibrationReport,
)


class ConfidenceCalibrator:
    """Calibrates confidence scores against actual outcomes."""
    
    def __init__(self):
        self.bucket_definitions = [
            (ConfidenceBucket.VERY_LOW, 0, 30),
            (ConfidenceBucket.LOW, 30, 50),
            (ConfidenceBucket.MEDIUM, 50, 70),
            (ConfidenceBucket.HIGH, 70, 85),
            (ConfidenceBucket.VERY_HIGH, 85, 100),
        ]
    
    def calibrate(
        self,
        records: List[SignalOutcomeRecord],
    ) -> ConfidenceCalibrationReport:
        """Perform confidence calibration analysis."""
        
        if not records:
            return self._empty_report()
        
        # Filter resolved records
        resolved = [r for r in records if r.outcome != SignalOutcome.PENDING]
        
        if not resolved:
            return self._empty_report()
        
        # Group by confidence buckets
        bucket_stats = {}
        for bucket, min_conf, max_conf in self.bucket_definitions:
            bucket_records = [
                r for r in resolved
                if min_conf <= r.confidence_score < max_conf
            ]
            
            if not bucket_records:
                bucket_stats[bucket] = ConfidenceBucketStats(
                    bucket=bucket,
                    min_confidence=min_conf,
                    max_confidence=max_conf,
                    signal_count=0,
                    win_count=0,
                    loss_count=0,
                    win_rate=0,
                    avg_profit_loss=0,
                )
                continue
            
            wins = [r for r in bucket_records if r.outcome == SignalOutcome.WIN]
            losses = [r for r in bucket_records if r.outcome == SignalOutcome.LOSS]
            pnls = [r.profit_loss for r in bucket_records if r.profit_loss is not None]
            
            win_rate = len(wins) / len(bucket_records) * 100 if bucket_records else 0
            avg_pnl = sum(pnls) / len(pnls) if pnls else 0
            
            bucket_stats[bucket] = ConfidenceBucketStats(
                bucket=bucket,
                min_confidence=min_conf,
                max_confidence=max_conf,
                signal_count=len(bucket_records),
                win_count=len(wins),
                loss_count=len(losses),
                win_rate=win_rate,
                avg_profit_loss=avg_pnl,
            )
        
        # Calculate overall calibration error
        calibration_error = self._calculate_calibration_error(bucket_stats)
        
        # Determine if over/under confident
        is_overconfident = self._is_overconfident(bucket_stats)
        is_underconfident = self._is_underconfident(bucket_stats)
        
        # Generate recommendations
        adjustments = self._generate_adjustments(bucket_stats)
        
        return ConfidenceCalibrationReport(
            timestamp=datetime.now(),
            buckets=list(bucket_stats.values()),
            overall_calibration_error=calibration_error,
            is_overconfident=is_overconfident,
            is_underconfident=is_underconfident,
            recommended_adjustments=adjustments,
        )
    
    def _empty_report(self) -> ConfidenceCalibrationReport:
        """Return empty calibration report."""
        bucket_stats = []
        for bucket, min_conf, max_conf in self.bucket_definitions:
            bucket_stats.append(ConfidenceBucketStats(
                bucket=bucket,
                min_confidence=min_conf,
                max_confidence=max_conf,
                signal_count=0,
                win_count=0,
                loss_count=0,
                win_rate=0,
                avg_profit_loss=0,
            ))
        
        return ConfidenceCalibrationReport(
            timestamp=datetime.now(),
            buckets=bucket_stats,
            overall_calibration_error=0,
            is_overconfident=False,
            is_underconfident=False,
            recommended_adjustments={},
        )
    
    def _calculate_calibration_error(self, bucket_stats: Dict[ConfidenceBucket, ConfidenceBucketStats]) -> float:
        """Calculate overall calibration error."""
        errors = []
        
        for bucket, stats in bucket_stats.items():
            if stats.signal_count == 0:
                continue
            
            # Expected win rate based on confidence midpoint
            expected = (stats.min_confidence + stats.max_confidence) / 2
            # Actual win rate
            actual = stats.win_rate
            
            # Absolute error
            error = abs(expected - actual)
            errors.append(error)
        
        return sum(errors) / len(errors) if errors else 0
    
    def _is_overconfident(self, bucket_stats: Dict[ConfidenceBucket, ConfidenceBucketStats]) -> bool:
        """Check if system is overconfident (high confidence but lower actual win rate)."""
        high_buckets = [
            stats for bucket, stats in bucket_stats.items()
            if bucket in [ConfidenceBucket.HIGH, ConfidenceBucket.VERY_HIGH]
        ]
        
        if not high_buckets:
            return False
        
        # If actual win rate is significantly lower than predicted
        for stats in high_buckets:
            predicted = (stats.min_confidence + stats.max_confidence) / 2
            if stats.win_rate < predicted - 15:  # 15% threshold
                return True
        
        return False
    
    def _is_underconfident(self, bucket_stats: Dict[ConfidenceBucket, ConfidenceBucketStats]) -> bool:
        """Check if system is underconfident (low confidence but higher actual win rate)."""
        low_buckets = [
            stats for bucket, stats in bucket_stats.items()
            if bucket in [ConfidenceBucket.VERY_LOW, ConfidenceBucket.LOW]
        ]
        
        if not low_buckets:
            return False
        
        for stats in low_buckets:
            predicted = (stats.min_confidence + stats.max_confidence) / 2
            if stats.win_rate > predicted + 15:
                return True
        
        return False
    
    def _generate_adjustments(self, bucket_stats: Dict[ConfidenceBucket, ConfidenceBucketStats]) -> Dict[str, float]:
        """Generate recommended confidence adjustments."""
        adjustments = {}
        
        for bucket, stats in bucket_stats.items():
            if stats.signal_count < 5:
                continue
            
            predicted = (stats.min_confidence + stats.max_confidence) / 2
            actual = stats.win_rate
            
            diff = actual - predicted
            
            if abs(diff) > 10:
                bucket_name = bucket.value
                adjustments[bucket_name] = diff
        
        return adjustments
    
    def get_bucket_summary(self, records: List[SignalOutcomeRecord]) -> Dict:
        """Get quick bucket summary."""
        report = self.calibrate(records)
        
        return {
            bucket.bucket.value: {
                "signal_count": bucket.signal_count,
                "win_rate": bucket.win_rate,
                "predicted_vs_actual": bucket.predicted_vs_actual,
            }
            for bucket in report.buckets
        }


def create_calibrator() -> ConfidenceCalibrator:
    """Create a new confidence calibrator."""
    return ConfidenceCalibrator()
