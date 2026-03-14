"""Strategic Audit - DEPRECATED

This module is deprecated. All functionality has been moved to app/audit/.
Please update imports to use app.audit instead.

Migration:
  - from app.strategic_audit.audit_models -> from app.audit.strategic.audit_models
  - from app.strategic_audit.audit_cycle_runner -> from app.audit.strategic.audit_cycle_runner
  - from app.strategic_audit.intelligence_metrics_calculator -> from app.audit.strategic.intelligence_metrics_calculator
"""
# Backward compatibility re-exports
from app.audit.strategic.audit_models import (
    AuditSummary,
    CycleAuditRecord,
    DecisionRecord,
    GovernanceOutcome,
    LearningUpdate,
    MemoryRelationship,
    PatternInsight,
    SignalObservation,
    StrategicBehaviorScore,
    StrategicIntelligenceMetrics,
    TimeHorizon,
)

from app.audit.strategic.audit_cycle_runner import AuditCycleRunner

from app.audit.strategic.intelligence_metrics_calculator import IntelligenceMetricsCalculator

__all__ = [
    # Models
    "AuditSummary",
    "CycleAuditRecord", 
    "DecisionRecord",
    "GovernanceOutcome",
    "LearningUpdate",
    "MemoryRelationship",
    "PatternInsight",
    "SignalObservation",
    "StrategicBehaviorScore",
    "StrategicIntelligenceMetrics",
    "TimeHorizon",
    # Runners
    "AuditCycleRunner",
    # Calculators
    "IntelligenceMetricsCalculator",
]
