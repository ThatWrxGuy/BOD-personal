"""
BB-AUD-001: System Integrity & Strategic Intelligence Audit Framework

This module provides comprehensive system auditing capabilities for Busy Bee.

Components:
- SystemAuditEngine: Main orchestrator for all audits
- ArchitectureValidator: Validates system architecture
- AgentIntegrityScanner: Validates agent registry and integrity  
- SignalHealthMonitor: Validates signal system health
- GovernanceComplianceChecker: Validates governance hierarchy
- DecisionTraceAnalyzer: Validates decision traceability
- DataConsistencyValidator: Validates data consistency
- DashboardIntegrityMonitor: Validates dashboard accuracy
- AuditReportGenerator: Generates executive audit reports

Usage:
    from infrastructure.system_audit import SystemAuditEngine, AuditType
    
    engine = SystemAuditEngine("/path/to/BOD-personal")
    result = engine.run_audit(AuditType.FULL_DEEP_AUDIT)
    
    print(f"System Health: {result.overall_health_score}%")
"""

from .system_audit_engine import (
    SystemAuditEngine,
    SystemAuditResult,
    AuditType,
    AuditSchedule,
    create_system_audit_engine,
)

from .architecture_validator import (
    ArchitectureValidator,
    ArchitectureValidationResult,
    ArchitectureIssue,
    LayerLevel,
    run_architecture_audit,
)

from .agent_integrity_scanner import (
    AgentIntegrityScanner,
    AgentIntegrityResult,
    AgentIntegrityIssue,
    AgentStatus,
    AgentRole,
    AgentInfo,
    run_agent_integrity_audit,
)

from .signal_health_monitor import (
    SignalHealthMonitor,
    SignalHealthResult,
    SignalHealthIssue,
    SignalMetrics,
    SignalType,
    SignalHealthStatus,
    run_signal_health_audit,
)

from .governance_checker import (
    GovernanceComplianceChecker,
    GovernanceComplianceResult,
    GovernanceIssue,
    GovernanceCheck,
    AuthorityLevel,
    GovernanceIssueType,
    run_governance_audit,
)

from .decision_trace_analyzer import (
    DecisionTraceAnalyzer,
    DecisionTraceResult,
    DecisionTraceIssue,
    DecisionTrace,
    DecisionNode,
    DecisionStatus,
    run_decision_trace_audit,
)

from .data_consistency_validator import (
    DataConsistencyValidator,
    DataConsistencyResult,
    DataConsistencyIssue,
    DataIssueType,
    run_data_consistency_audit,
)

from .dashboard_integrity_monitor import (
    DashboardIntegrityMonitor,
    DashboardIntegrityResult,
    DashboardIssue,
    DashboardMetric,
    DashboardIssueType,
    run_dashboard_integrity_audit,
)

from .audit_report_generator import (
    AuditReportGenerator,
    AuditReport,
    generate_audit_report,
)


__all__ = [
    # Main engine
    "SystemAuditEngine",
    "SystemAuditResult", 
    "AuditType",
    "AuditSchedule",
    "create_system_audit_engine",
    
    # Architecture
    "ArchitectureValidator",
    "ArchitectureValidationResult",
    "ArchitectureIssue",
    "LayerLevel",
    "run_architecture_audit",
    
    # Agent integrity
    "AgentIntegrityScanner",
    "AgentIntegrityResult",
    "AgentIntegrityIssue",
    "AgentStatus",
    "AgentRole",
    "AgentInfo",
    "run_agent_integrity_audit",
    
    # Signal health
    "SignalHealthMonitor",
    "SignalHealthResult",
    "SignalHealthIssue",
    "SignalMetrics",
    "SignalType",
    "SignalHealthStatus",
    "run_signal_health_audit",
    
    # Governance
    "GovernanceComplianceChecker",
    "GovernanceComplianceResult",
    "GovernanceIssue",
    "GovernanceCheck",
    "AuthorityLevel",
    "GovernanceIssueType",
    "run_governance_audit",
    
    # Decision trace
    "DecisionTraceAnalyzer",
    "DecisionTraceResult",
    "DecisionTraceIssue",
    "DecisionTrace",
    "DecisionNode",
    "DecisionStatus",
    "run_decision_trace_audit",
    
    # Data consistency
    "DataConsistencyValidator",
    "DataConsistencyResult",
    "DataConsistencyIssue",
    "DataIssueType",
    "run_data_consistency_audit",
    
    # Dashboard
    "DashboardIntegrityMonitor",
    "DashboardIntegrityResult",
    "DashboardIssue",
    "DashboardMetric",
    "DashboardIssueType",
    "run_dashboard_integrity_audit",
    
    # Reporting
    "AuditReportGenerator",
    "AuditReport",
    "generate_audit_report",
]
