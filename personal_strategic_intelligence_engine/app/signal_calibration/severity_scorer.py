"""Severity Scorer.

Measures how strategically significant a signal is.
"""
from typing import Any, Dict, Optional

from app.signal_calibration.calibration_models import (
    SeverityLevel,
    SignalSeverityScore,
)


class SeverityScorer:
    """Scores signal severity based on domain-specific thresholds."""
    
    # Default severity thresholds (by domain)
    DEFAULT_THRESHOLDS = {
        "calendar": {
            "mild": 0.2,
            "moderate": 0.4,
            "high": 0.7,
            "critical": 0.9,
        },
        "finance": {
            "mild": 0.15,
            "moderate": 0.35,
            "high": 0.6,
            "critical": 0.85,
        },
        "tasks": {
            "mild": 0.25,
            "moderate": 0.45,
            "high": 0.7,
            "critical": 0.9,
        },
        "health": {
            "mild": 0.2,
            "moderate": 0.4,
            "high": 0.65,
            "critical": 0.85,
        },
    }
    
    # Severity score weights by level
    SEVERITY_WEIGHTS = {
        SeverityLevel.MILD: 0.25,
        SeverityLevel.MODERATE: 0.5,
        SeverityLevel.HIGH: 0.75,
        SeverityLevel.CRITICAL: 1.0,
    }
    
    def __init__(self, custom_thresholds: Optional[Dict[str, Dict[str, float]]] = None):
        self.thresholds = {**self.DEFAULT_THRESHOLDS}
        if custom_thresholds:
            self.thresholds.update(custom_thresholds)
    
    def score_severity(
        self,
        signal_id: str,
        signal_type: str,
        domain: str,
        value: float,
    ) -> SignalSeverityScore:
        """Calculate severity score for a signal."""
        
        # Get domain-specific thresholds
        domain_thresholds = self.thresholds.get(
            domain, 
            self.thresholds.get("default", self.DEFAULT_THRESHOLDS["calendar"])
        )
        
        # Determine severity level based on absolute value magnitude
        # (For severity, we care about how significant the deviation is)
        abs_value = abs(value)
        
        if abs_value >= domain_thresholds["critical"]:
            severity_level = SeverityLevel.CRITICAL
            severity_score = self.SEVERITY_WEIGHTS[SeverityLevel.CRITICAL]
            reason = f"Critical severity: value {value:.2f} exceeds critical threshold"
            
        elif abs_value >= domain_thresholds["high"]:
            severity_level = SeverityLevel.HIGH
            severity_score = self.SEVERITY_WEIGHTS[SeverityLevel.HIGH]
            reason = f"High severity: value {value:.2f} exceeds high threshold"
            
        elif abs_value >= domain_thresholds["moderate"]:
            severity_level = SeverityLevel.MODERATE
            severity_score = self.SEVERITY_WEIGHTS[SeverityLevel.MODERATE]
            reason = f"Moderate severity: value {value:.2f} exceeds moderate threshold"
            
        elif abs_value >= domain_thresholds["mild"]:
            severity_level = SeverityLevel.MILD
            severity_score = self.SEVERITY_WEIGHTS[SeverityLevel.MILD]
            reason = f"Mild severity: value {value:.2f} exceeds mild threshold"
            
        else:
            severity_level = SeverityLevel.MILD
            severity_score = self.SEVERITY_WEIGHTS[SeverityLevel.MILD] * (abs_value / domain_thresholds["mild"])
            reason = f"Minimal severity: value {value:.2f} below most thresholds"
        
        return SignalSeverityScore(
            signal_id=signal_id,
            signal_type=signal_type,
            domain=domain,
            base_value=value,
            severity_score=severity_score,
            severity_level=severity_level,
            mild_threshold=domain_thresholds["mild"],
            moderate_threshold=domain_thresholds["moderate"],
            high_threshold=domain_thresholds["high"],
            critical_threshold=domain_thresholds["critical"],
            domain_thresholds=self.thresholds,
            reason=reason,
        )
    
    def score_batch(
        self,
        signals: list,
    ) -> Dict[str, SignalSeverityScore]:
        """Score severity for multiple signals."""
        results = {}
        
        for signal in signals:
            score = self.score_severity(
                signal_id=signal.get("signal_id", ""),
                signal_type=signal.get("signal_type", ""),
                domain=signal.get("domain", "default"),
                value=signal.get("value", 0.0),
            )
            results[score.signal_id] = score
        
        return results
    
    def get_severity_distribution(
        self,
        scores: Dict[str, SignalSeverityScore],
    ) -> Dict[str, int]:
        """Get distribution of severity levels."""
        distribution = {
            "mild": 0,
            "moderate": 0,
            "high": 0,
            "critical": 0,
        }
        
        for score in scores.values():
            distribution[score.severity_level.value] += 1
        
        return distribution


# Global scorer instance
_severity_scorer: Optional[SeverityScorer] = None


def get_severity_scorer() -> SeverityScorer:
    """Get the global severity scorer instance."""
    global _severity_scorer
    if _severity_scorer is None:
        _severity_scorer = SeverityScorer()
    return _severity_scorer
