"""Shadow monitoring data models for long-horizon observation.

Defines structures for tracking system behavior over extended periods.
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MonitoringStatus(str, Enum):
    """Status of shadow monitoring."""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


class MonitoringWindow(str, Enum):
    """Time windows for monitoring."""
    ONE_DAY = "1d"
    SEVEN_DAYS = "7d"
    THIRTY_DAYS = "30d"


class AnomalyType(str, Enum):
    """Types of anomalies detected."""
    RECOMMENDATION_SPIKE = "recommendation_spike"
    CONFIDENCE_CRASH = "confidence_crash"
    DOCTRINE_CONFLICT_SURGE = "doctrine_conflict_surge"
    SIGNAL_DEGRADATION = "signal_degradation"
    GOVERNANCE_LOAD_SPIKE = "governance_load_spike"
    TIER_DISTRIBUTION_SHIFT = "tier_distribution_shift"
    EXECUTION_INTENT_SPIKE = "execution_intent_spike"
    APPROVAL_BURDEN_SPIKE = "approval_burden_spike"


class SeverityLevel(str, Enum):
    """Severity of anomalies."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ShadowCycleRecord(BaseModel):
    """Record of a single shadow monitoring cycle."""
    cycle_id: str = Field(default_factory=lambda: f"shadow_cycle_{datetime.utcnow().timestamp()}")
    cycle_number: int
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cycle_duration_ms: float = 0.0
    
    # Signal metrics
    signals_processed: int = 0
    signals_by_domain: Dict[str, int] = Field(default_factory=dict)
    stale_signals: int = 0
    malformed_signals: int = 0
    
    # Recommendation metrics
    recommendations_generated: int = 0
    recommendations_by_domain: Dict[str, int] = Field(default_factory=dict)
    recommendations_by_urgency: Dict[str, int] = Field(default_factory=dict)
    repeated_recommendations: int = 0
    
    # Execution intent metrics
    execution_intents_generated: int = 0
    approval_required_count: int = 0
    doctrine_blocked_count: int = 0
    risk_rejected_count: int = 0
    
    # Doctrine metrics
    doctrine_flags: List[str] = Field(default_factory=list)
    doctrine_conflicts: int = 0
    alignment_score: float = 0.0
    alignment_level: str = "neutral"
    
    # Risk metrics
    risk_flags: List[str] = Field(default_factory=list)
    risk_level: str = "low"
    
    # Confidence metrics
    confidence_score: float = 0.5
    confidence_delta: float = 0.0
    
    # Tier distribution
    tier_distribution: Dict[str, int] = Field(default_factory=dict)
    current_tier: str = "tier_0_manual_only"
    
    # Learning metrics
    learning_updates: int = 0
    calibration_adjustments: float = 0.0
    
    # Governance load
    governance_load_score: float = 0.0
    pending_approvals: int = 0
    
    # Raw data
    state_snapshot: Dict[str, Any] = Field(default_factory=dict)


class RecommendationActivitySummary(BaseModel):
    """Summary of recommendation activity over a period."""
    total_recommendations: int = 0
    recommendations_by_domain: Dict[str, int] = Field(default_factory=dict)
    recommendations_by_urgency: Dict[str, int] = Field(default_factory=dict)
    avg_recommendations_per_cycle: float = 0.0
    repeated_recommendation_rate: float = 0.0
    low_value_recommendation_rate: float = 0.0
    
    # Trends
    trend_direction: str = "stable"  # increasing, decreasing, stable
    trend_magnitude: float = 0.0


class ConfidenceDriftEvent(BaseModel):
    """Event detected as confidence drift."""
    event_id: str = Field(default_factory=lambda: f"conf_drift_{datetime.utcnow().timestamp()}")
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Drift details
    drift_type: str  # sudden_collapse, sudden_inflation, gradual_drift, oscillation
    severity: SeverityLevel
    
    # Measurements
    previous_confidence: float
    current_confidence: float
    confidence_delta: float
    duration_cycles: int
    
    # Context
    cycle_range: tuple[int, int] = (0, 0)
    probable_cause: Optional[str] = None
    
    # Recommendations
    requires_attention: bool = False
    recommendation: Optional[str] = None


class GovernanceLoadSnapshot(BaseModel):
    """Snapshot of governance load."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    window: MonitoringWindow
    
    # Load metrics
    avg_governance_load: float = 0.0
    max_governance_load: float = 0.0
    governance_load_trend: str = "stable"
    
    # Flag metrics
    total_doctrine_flags: int = 0
    total_risk_flags: int = 0
    flag_trend: str = "stable"
    
    # Queue metrics
    avg_pending_approvals: float = 0.0
    max_pending_approvals: int = 0
    approval_queue_trend: str = "stable"
    
    # Operator burden
    estimated_hours_per_day: float = 0.0
    burden_level: str = "minimal"  # minimal, low, moderate, high, critical


class ApprovalBurdenSnapshot(BaseModel):
    """Snapshot of approval burden."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    window: MonitoringWindow
    
    # Counts
    total_approval_required: int = 0
    fast_path_approvals: int = 0
    manual_only_approvals: int = 0
    
    # Distribution
    approval_distribution: Dict[str, float] = Field(default_factory=dict)
    domain_burden: Dict[str, int] = Field(default_factory=dict)
    
    # Efficiency
    auto_approval_rate: float = 0.0
    manual_review_rate: float = 0.0
    
    # Burden estimation
    estimated_daily_reviews: int = 0
    burden_level: str = "minimal"


class SignalReliabilitySnapshot(BaseModel):
    """Snapshot of signal source reliability."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    window: MonitoringWindow
    
    # Reliability metrics
    overall_reliability: float = 1.0  # 0-1
    reliability_trend: str = "stable"
    
    # Source-specific
    source_reliability: Dict[str, float] = Field(default_factory=dict)
    source_uptime: Dict[str, float] = Field(default_factory=dict)
    
    # Data quality
    stale_signal_rate: float = 0.0
    malformed_signal_rate: float = 0.0
    missing_data_rate: float = 0.0
    
    # Trends
    quality_trend: str = "stable"


class MonitoringAnomaly(BaseModel):
    """Anomaly detected in shadow operation."""
    anomaly_id: str = Field(default_factory=lambda: f"anomaly_{datetime.utcnow().timestamp()}")
    anomaly_type: AnomalyType
    severity: SeverityLevel
    
    # Detection
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    cycle_number: int
    
    # Details
    description: str
    affected_areas: List[str] = Field(default_factory=list)
    
    # Measurements
    current_value: float = 0.0
    expected_range: tuple[float, float] = (0.0, 1.0)
    deviation: float = 0.0
    
    # Context
    probable_cause: Optional[str] = None
    related_cycles: List[int] = Field(default_factory=list)
    
    # Resolution
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None


class ShadowOperationReport(BaseModel):
    """Comprehensive report of shadow operation."""
    report_id: str = Field(default_factory=lambda: f"shadow_report_{datetime.utcnow().timestamp()}")
    
    # Time window
    window: MonitoringWindow
    start_time: datetime
    end_time: datetime
    
    # Cycle summary
    total_cycles: int = 0
    cycles_completed: int = 0
    cycles_failed: int = 0
    avg_cycle_duration_ms: float = 0.0
    
    # Activity summary
    signals_processed: int = 0
    recommendations_generated: int = 0
    execution_intents_generated: int = 0
    
    # Metrics summaries
    recommendation_summary: RecommendationActivitySummary = Field(
        default_factory=RecommendationActivitySummary
    )
    confidence_drift_events: List[ConfidenceDriftEvent] = Field(default_factory=list)
    governance_load: Optional[GovernanceLoadSnapshot] = None
    approval_burden: Optional[ApprovalBurdenSnapshot] = None
    signal_reliability: Optional[SignalReliabilitySnapshot] = None
    
    # Anomalies
    anomalies_detected: List[MonitoringAnomaly] = Field(default_factory=list)
    critical_anomalies: int = 0
    high_severity_anomalies: int = 0
    
    # Readiness
    overall_health_score: float = 1.0
    readiness_level: str = "not_ready"  # not_ready, developing, ready
    
    # Generated at
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class LongHorizonReadinessAssessment(BaseModel):
    """Assessment of system readiness based on shadow operation."""
    assessment_id: str = Field(default_factory=lambda: f"readiness_{datetime.utcnow().timestamp()}")
    
    # Assessment window
    window: MonitoringWindow
    assessed_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Readiness criteria
    stability_score: float = 0.0
    recommendation_quality_score: float = 0.0
    governance_efficiency_score: float = 0.0
    operator_burden_score: float = 0.0
    signal_quality_score: float = 0.0
    
    # Overall readiness
    overall_readiness_score: float = 0.0
    readiness_level: str = "not_ready"
    
    # Findings
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    # Comparison with simulation
    matches_simulation_expectations: bool = True
    simulation_deviations: List[str] = Field(default_factory=list)


# Safety constants
SHADOW_MODE = True  # Always True for shadow monitoring
LIVE_EXECUTION_ENABLED = False  # Never enabled in shadow mode
AUTO_EXECUTION_ENABLED = False  # Never enabled in shadow mode
EXECUTION_MODE = "disabled"  # Disabled execution mode
APPROVAL_REQUIRED = True  # Always require approval
