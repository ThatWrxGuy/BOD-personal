"""End-to-End Operational Audit System.

This module provides comprehensive audit capabilities for verifying the Personal
Strategic Operating System behaves as intended.

Key Components:
- audit_models: Data models for audit records and reports
- end_to_end_audit_runner: Executes realistic scenarios and multi-cycle simulations
- audit_report_builder: Generates human-readable and JSON reports

Safety:
All audits run with LIVE_EXECUTION_ENABLED = False.
No real-world actions may occur during audit.

Usage:
    from app.audit import create_audit_runner, create_audit_report_builder
    
    # Run audit
    runner = create_audit_runner(seed=42)
    await runner.run_realistic_scenario_audit(ScenarioTypeAudit.PERSONAL_LIFE_OPTIMIZATION)
    
    # Generate report
    builder = create_audit_report_builder()
    report = builder.build_master_report(runner.cycle_records, [...], [...])
"""
from app.audit.audit_models import (
    ApprovalStatus,
    AuditCycleRecord,
    AuditFindings,
    AuditMode,
    AuditStatus,
    DecisionInventory,
    GateOutcome,
    GovernanceOutcomeReport,
    LearningReport,
    MasterAuditReport,
    ScenarioTypeAudit,
    VisionAlignment,
    # Constants
    LIVE_EXECUTION_ENABLED,
    AUTO_EXECUTION_ENABLED,
    EXECUTION_MODE,
    APPROVAL_REQUIRED,
    REPLAY_MODE,
    SHADOW_MODE,
)
from app.audit.end_to_end_audit_runner import (
    EndToEndAuditRunner,
    create_audit_runner,
)
from app.audit.audit_report_builder import (
    AuditReportBuilder,
    create_audit_report_builder,
)

__all__ = [
    # Models
    "ApprovalStatus",
    "AuditCycleRecord",
    "AuditFindings",
    "AuditMode",
    "AuditStatus",
    "DecisionInventory",
    "GateOutcome",
    "GovernanceOutcomeReport",
    "LearningReport",
    "MasterAuditReport",
    "ScenarioTypeAudit",
    "VisionAlignment",
    # Constants
    "LIVE_EXECUTION_ENABLED",
    "AUTO_EXECUTION_ENABLED",
    "EXECUTION_MODE",
    "APPROVAL_REQUIRED",
    "REPLAY_MODE",
    "SHADOW_MODE",
    # Runner
    "EndToEndAuditRunner",
    "create_audit_runner",
    # Builder
    "AuditReportBuilder",
    "create_audit_report_builder",
]
