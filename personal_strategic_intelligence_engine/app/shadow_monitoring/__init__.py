"""Shadow Monitoring & Long-Horizon Observation Layer.

This module provides comprehensive monitoring capabilities for shadow operation,
allowing the Personal Strategic Operating System to run continuously in safe,
non-autonomous observation mode over extended periods.

Key Components:
- monitoring_models: Data models for monitoring records and reports
- shadow_controller: Central orchestration for shadow operation
- cycle_monitor: Tracks cycle-level activity over time
- recommendation_monitor: Tracks recommendation patterns
- confidence_drift_detector: Measures confidence movement over time
- governance_load_monitor: Measures governance burden over time
- signal_reliability_monitor: Measures signal source quality
- approval_burden_analyzer: Estimates operational cost of manual review
- anomaly_detector: Detects operational anomalies
- monitoring_reporter: Produces structured monitoring reports
- monitoring_store: Persists monitoring records

Safety:
All monitoring runs in SHADOW_MODE with LIVE_EXECUTION_ENABLED = False.
No real-world actions can be triggered during shadow operation.

Usage:
    from app.shadow_monitoring import create_shadow_controller
    
    # Create and start shadow monitoring
    controller = create_shadow_controller()
    await controller.start()
    
    # Run cycles
    await controller.run_cycle()
    
    # Get reports
    report = controller.generate_report()
"""
from app.shadow_monitoring.monitoring_models import (
    AnomalyType,
    ApprovalBurdenSnapshot,
    ConfidenceDriftEvent,
    GovernanceLoadSnapshot,
    LongHorizonReadinessAssessment,
    MonitoringAnomaly,
    MonitoringStatus,
    MonitoringWindow,
    RecommendationActivitySummary,
    SeverityLevel,
    ShadowCycleRecord,
    ShadowOperationReport,
    SignalReliabilitySnapshot,
    # Constants
    SHADOW_MODE,
    LIVE_EXECUTION_ENABLED,
    AUTO_EXECUTION_ENABLED,
    EXECUTION_MODE,
    APPROVAL_REQUIRED,
)
from app.shadow_monitoring.cycle_monitor import CycleMonitor, create_cycle_monitor
from app.shadow_monitoring.recommendation_monitor import (
    RecommendationMonitor,
    create_recommendation_monitor,
)
from app.shadow_monitoring.confidence_drift_detector import (
    ConfidenceDriftDetector,
    create_confidence_drift_detector,
)
from app.shadow_monitoring.governance_load_monitor import (
    GovernanceLoadMonitor,
    create_governance_load_monitor,
)
from app.shadow_monitoring.signal_reliability_monitor import (
    SignalReliabilityMonitor,
    create_signal_reliability_monitor,
)
from app.shadow_monitoring.approval_burden_analyzer import (
    ApprovalBurdenAnalyzer,
    create_approval_burden_analyzer,
)
from app.shadow_monitoring.anomaly_detector import (
    AnomalyDetector,
    create_anomaly_detector,
)
from app.shadow_monitoring.monitoring_reporter import (
    MonitoringReporter,
    create_monitoring_reporter,
)
from app.shadow_monitoring.monitoring_store import (
    MonitoringStore,
    create_monitoring_store,
)
from app.shadow_monitoring.shadow_controller import (
    ShadowController,
    create_shadow_controller,
)

__all__ = [
    # Models
    "AnomalyType",
    "ApprovalBurdenSnapshot",
    "ConfidenceDriftEvent",
    "GovernanceLoadSnapshot",
    "LongHorizonReadinessAssessment",
    "MonitoringAnomaly",
    "MonitoringStatus",
    "MonitoringWindow",
    "RecommendationActivitySummary",
    "SeverityLevel",
    "ShadowCycleRecord",
    "ShadowOperationReport",
    "SignalReliabilitySnapshot",
    # Constants
    "SHADOW_MODE",
    "LIVE_EXECUTION_ENABLED",
    "AUTO_EXECUTION_ENABLED",
    "EXECUTION_MODE",
    "APPROVAL_REQUIRED",
    # Monitors
    "CycleMonitor",
    "create_cycle_monitor",
    "RecommendationMonitor",
    "create_recommendation_monitor",
    "ConfidenceDriftDetector",
    "create_confidence_drift_detector",
    "GovernanceLoadMonitor",
    "create_governance_load_monitor",
    "SignalReliabilityMonitor",
    "create_signal_reliability_monitor",
    "ApprovalBurdenAnalyzer",
    "create_approval_burden_analyzer",
    "AnomalyDetector",
    "create_anomaly_detector",
    # Reporter
    "MonitoringReporter",
    "create_monitoring_reporter",
    # Store
    "MonitoringStore",
    "create_monitoring_store",
    # Controller
    "ShadowController",
    "create_shadow_controller",
]
