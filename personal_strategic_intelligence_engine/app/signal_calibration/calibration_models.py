"""Calibration Models.

Defines structures for signal calibration.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FreshnessLevel(str, Enum):
    """Signal freshness classification."""
    FRESH = "fresh"          # Recently updated
    AGING = "aging"         # Somewhat stale
    STALE = "stale"         # Significantly outdated
    EXPIRED = "expired"     # Too old to use


class PersistenceLevel(str, Enum):
    """Signal persistence classification."""
    TRANSIENT = "transient"     # One-off event
    EMERGING = "emerging"       # Started recently
    PERSISTENT = "persistent"   # Sustained condition
    CHRONIC = "chronic"         # Long-standing issue


class SeverityLevel(str, Enum):
    """Signal severity classification."""
    MILD = "mild"           # Minor deviation
    MODERATE = "moderate"   # Noticeable issue
    HIGH = "high"           # Significant concern
    CRITICAL = "critical"   # Urgent attention needed


class TemporalContext(str, Enum):
    """Temporal context classification."""
    ANOMALY = "anomaly"             # One-off unusual event
    SHORT_TERM_SHIFT = "short_term" # Recent change
    SUSTAINED_TREND = "sustained"    # Ongoing direction
    STRUCTURAL = "structural"         # Fundamental condition


class CalibrationSummary(BaseModel):
    """Summary of signal calibration."""
    total_signals: int = 0
    fresh_signals: int = 0
    stale_signals: int = 0
    transient_signals: int = 0
    persistent_signals: int = 0
    mild_signals: int = 0
    critical_signals: int = 0
    
    avg_weight: float = 0.0
    weight_distribution: Dict[str, int] = Field(default_factory=dict)
    
    calibrated_at: datetime = Field(default_factory=datetime.utcnow)


class SignalFreshnessScore(BaseModel):
    """Freshness evaluation for a signal."""
    signal_id: str
    signal_type: str
    
    # Timing
    last_update: Optional[datetime] = None
    age_seconds: float = 0.0
    
    # Scores
    freshness_score: float = 1.0  # 0.0 to 1.0
    freshness_level: FreshnessLevel = FreshnessLevel.FRESH
    
    # Thresholds
    expected_update_interval_seconds: float = 300
    
    # Metadata
    reason: str = ""


class SignalPersistenceProfile(BaseModel):
    """Persistence profile for a signal."""
    signal_id: str
    signal_type: str
    
    # Pattern
    occurrences: int = 0
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    
    # Classification
    persistence_level: PersistenceLevel = PersistenceLevel.TRANSIENT
    persistence_score: float = 0.0  # 0.0 to 1.0
    
    # Trend
    trend_direction: str = "stable"  # increasing, decreasing, stable
    trend_magnitude: float = 0.0
    
    # Metadata
    reason: str = ""


class SignalSeverityScore(BaseModel):
    """Severity evaluation for a signal."""
    signal_id: str
    signal_type: str
    domain: str
    
    # Base severity
    base_value: float = 0.0
    severity_score: float = 0.0  # 0.0 to 1.0
    severity_level: SeverityLevel = SeverityLevel.MILD
    
    # Thresholds
    mild_threshold: float = 0.3
    moderate_threshold: float = 0.5
    high_threshold: float = 0.7
    critical_threshold: float = 0.9
    
    # Domain-specific context
    domain_thresholds: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    
    # Metadata
    reason: str = ""


class SourceReliabilityScore(BaseModel):
    """Source reliability adjustment."""
    source_id: str
    source_type: str
    
    # Metrics
    uptime_percentage: float = 100.0
    success_rate: float = 1.0
    avg_latency_ms: float = 0.0
    error_count: int = 0
    
    # Adjustment
    reliability_score: float = 1.0  # 0.0 to 1.0
    
    # Metadata
    last_evaluation: datetime = Field(default_factory=datetime.utcnow)
    reason: str = ""


class TemporalSignalContext(BaseModel):
    """Temporal context for a signal."""
    signal_id: str
    
    # Context classification
    temporal_context: TemporalContext = TemporalContext.ANOMALY
    context_score: float = 0.0  # 0.0 to 1.0
    
    # Analysis
    is_trend: bool = False
    trend_duration_hours: float = 0.0
    
    # Comparison
    vs_historical_avg: float = 0.0
    vs_short_term_avg: float = 0.0
    
    # Metadata
    reason: str = ""


class CrossSignalBalanceResult(BaseModel):
    """Result of cross-signal balancing."""
    signal_id: str
    domain: str
    
    # Balancing
    domain_weight: float = 1.0
    balance_score: float = 0.0  # 0.0 to 1.0
    
    # Proportionality
    vs_highest_impact: float = 1.0
    proportional_to_severity: bool = True
    
    # Metadata
    reason: str = ""


class SignalWeightProfile(BaseModel):
    """Complete weight profile for a signal."""
    signal_id: str
    signal_type: str
    domain: str
    source_id: str
    
    # Base value
    base_value: float = 0.0
    
    # Component scores
    freshness_score: float = 1.0
    persistence_score: float = 0.5
    severity_score: float = 0.5
    reliability_score: float = 1.0
    temporal_context_score: float = 0.5
    cross_domain_balance: float = 1.0
    
    # Final weight
    final_weight: float = 1.0
    
    # Classification
    freshness_level: FreshnessLevel = FreshnessLevel.FRESH
    persistence_level: PersistenceLevel = PersistenceLevel.TRANSIENT
    severity_level: SeverityLevel = SeverityLevel.MILD
    temporal_context: TemporalContext = TemporalContext.ANOMALY
    
    # Calibration metadata
    calibration_rationale: str = ""
    calibrated_at: datetime = Field(default_factory=datetime.utcnow)


class CalibratedSignal(BaseModel):
    """Complete calibrated signal with all metadata."""
    # Original signal reference
    original_signal_id: str
    
    # Identity
    signal_id: str
    signal_type: str
    domain: str
    category: str
    source_id: str
    
    # Value
    base_value: float = 0.0
    calibrated_value: float = 0.0
    
    # Weight profile
    weight_profile: SignalWeightProfile
    
    # Context
    temporal_context: TemporalSignalContext
    
    # Classification
    is_usable: bool = True
    is_trend_signal: bool = False
    is_anomaly: bool = False
    priority: str = "medium"
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    calibrated_at: datetime = Field(default_factory=datetime.utcnow)


# Safety constants
LIVE_EXECUTION_ENABLED = False
CALIBRATION_MODE = "advisory"
