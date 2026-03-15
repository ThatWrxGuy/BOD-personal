"""Signal Weight Engine.

Computes final signal influence weights by combining all calibration factors.
"""
from typing import Any, Dict, List, Optional

from app.signal_calibration.calibration_models import (
    SignalWeightProfile,
    FreshnessLevel,
    PersistenceLevel,
    SeverityLevel,
    TemporalContext,
)


class SignalWeightEngine:
    """Computes final signal weights."""
    
    # Weight combination formula weights
    FRESHNESS_WEIGHT = 0.20      # 20% - recency matters
    PERSISTENCE_WEIGHT = 0.25    # 25% - sustained conditions matter most
    SEVERITY_WEIGHT = 0.30       # 30% - severity is key driver
    RELIABILITY_WEIGHT = 0.10    # 10% - source quality
    TEMPORAL_WEIGHT = 0.10       # 10% - context matters
    DOMAIN_WEIGHT = 0.05         # 5% - cross-domain balance
    
    def __init__(self):
        self.weights = {
            "freshness": self.FRESHNESS_WEIGHT,
            "persistence": self.PERSISTENCE_WEIGHT,
            "severity": self.SEVERITY_WEIGHT,
            "reliability": self.RELIABILITY_WEIGHT,
            "temporal": self.TEMPORAL_WEIGHT,
            "domain": self.DOMAIN_WEIGHT,
        }
    
    def compute_weight(
        self,
        signal_id: str,
        signal_type: str,
        domain: str,
        source_id: str,
        base_value: float,
        
        # Calibration inputs
        freshness_score: float = 1.0,
        freshness_level: FreshnessLevel = FreshnessLevel.FRESH,
        
        persistence_score: float = 0.5,
        persistence_level: PersistenceLevel = PersistenceLevel.TRANSIENT,
        
        severity_score: float = 0.5,
        severity_level: SeverityLevel = SeverityLevel.MILD,
        
        reliability_score: float = 1.0,
        
        temporal_context_score: float = 0.5,
        temporal_context: TemporalContext = TemporalContext.ANOMALY,
        
        domain_balance: float = 1.0,
    ) -> SignalWeightProfile:
        """Compute final signal weight from all calibration factors."""
        
        # Combine weights using weighted formula
        final_weight = (
            freshness_score * self.weights["freshness"] +
            persistence_score * self.weights["persistence"] +
            severity_score * self.weights["severity"] +
            reliability_score * self.weights["reliability"] +
            temporal_context_score * self.weights["temporal"] +
            domain_balance * self.weights["domain"]
        )
        
        # Adjust for unusable signals
        if freshness_level == FreshnessLevel.EXPIRED:
            final_weight = 0.0
            rationale = "Signal expired - no weight"
        elif domain_balance <= 0.1:
            final_weight *= 0.5
            rationale = "Domain weight reduced"
        else:
            rationale = self._generate_rationale(
                freshness_level=freshness_level,
                persistence_level=persistence_level,
                severity_level=severity_level,
                reliability_score=reliability_score,
                temporal_context=temporal_context,
            )
        
        return SignalWeightProfile(
            signal_id=signal_id,
            signal_type=signal_type,
            domain=domain,
            source_id=source_id,
            base_value=base_value,
            freshness_score=freshness_score,
            persistence_score=persistence_score,
            severity_score=severity_score,
            reliability_score=reliability_score,
            temporal_context_score=temporal_context_score,
            cross_domain_balance=domain_balance,
            final_weight=final_weight,
            freshness_level=freshness_level,
            persistence_level=persistence_level,
            severity_level=severity_level,
            temporal_context=temporal_context,
            calibration_rationale=rationale,
        )
    
    def compute_weight_from_dict(
        self,
        signal: Dict[str, Any],
        calibration: Dict[str, Any],
    ) -> SignalWeightProfile:
        """Compute weight from signal and calibration dictionaries."""
        
        return self.compute_weight(
            signal_id=signal.get("signal_id", ""),
            signal_type=signal.get("signal_type", ""),
            domain=signal.get("domain", "default"),
            source_id=signal.get("source_id", ""),
            base_value=signal.get("value", 0.0),
            
            freshness_score=calibration.get("freshness_score", 1.0),
            freshness_level=calibration.get("freshness_level", FreshnessLevel.FRESH),
            
            persistence_score=calibration.get("persistence_score", 0.5),
            persistence_level=calibration.get("persistence_level", PersistenceLevel.TRANSIENT),
            
            severity_score=calibration.get("severity_score", 0.5),
            severity_level=calibration.get("severity_level", SeverityLevel.MILD),
            
            reliability_score=calibration.get("reliability_score", 1.0),
            
            temporal_context_score=calibration.get("temporal_context_score", 0.5),
            temporal_context=calibration.get("temporal_context", TemporalContext.ANOMALY),
            
            domain_balance=calibration.get("domain_balance", 1.0),
        )
    
    def _generate_rationale(
        self,
        freshness_level: FreshnessLevel,
        persistence_level: PersistenceLevel,
        severity_level: SeverityLevel,
        reliability_score: float,
        temporal_context: TemporalContext,
    ) -> str:
        """Generate human-readable rationale for weight calculation."""
        
        rationale_parts = []
        
        # Freshness
        if freshness_level == FreshnessLevel.FRESH:
            rationale_parts.append("fresh")
        elif freshness_level == FreshnessLevel.AGING:
            rationale_parts.append("aging")
        elif freshness_level == FreshnessLevel.STALE:
            rationale_parts.append("stale")
        
        # Persistence
        if persistence_level in [PersistenceLevel.PERSISTENT, PersistenceLevel.CHRONIC]:
            rationale_parts.append("persistent")
        
        # Severity
        if severity_level in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
            rationale_parts.append("high-impact")
        
        # Reliability
        if reliability_score < 0.7:
            rationale_parts.append("lower-reliability")
        
        # Temporal
        if temporal_context == TemporalContext.SUSTAINED_TREND:
            rationale_parts.append("sustained-trend")
        elif temporal_context == TemporalContext.STRUCTURAL:
            rationale_parts.append("structural")
        
        if rationale_parts:
            return f"Weighted: {', '.join(rationale_parts)}"
        else:
            return "Balanced calibration"
    
    def get_weight_distribution(
        self,
        profiles: List[SignalWeightProfile],
    ) -> Dict[str, int]:
        """Get distribution of weight categories."""
        distribution = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "minimal": 0,
        }
        
        for profile in profiles:
            if profile.final_weight >= 0.8:
                distribution["critical"] += 1
            elif profile.final_weight >= 0.6:
                distribution["high"] += 1
            elif profile.final_weight >= 0.4:
                distribution["medium"] += 1
            elif profile.final_weight >= 0.2:
                distribution["low"] += 1
            else:
                distribution["minimal"] += 1
        
        return distribution


# Global engine instance
_signal_weight_engine: Optional[SignalWeightEngine] = None


def get_signal_weight_engine() -> SignalWeightEngine:
    """Get the global signal weight engine instance."""
    global _signal_weight_engine
    if _signal_weight_engine is None:
        _signal_weight_engine = SignalWeightEngine()
    return _signal_weight_engine
