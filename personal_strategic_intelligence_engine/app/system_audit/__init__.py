"""System Audit - PSIE validation and operational reporting.

This module provides system validation and operational reporting:
- audit_engine.py - Orchestrates end-to-end validation
- validation_runner.py - Executes validation scenarios
- metrics_collector.py - Collects system metrics
- report_generator.py - Generates operational reports

Reports generated:
- EOD Intelligence Report
- Financial Intelligence Report
- System Audit Report
"""
from app.system_audit.audit_models import (
    AuditStatus,
    SubsystemStatus,
    ValidationStep,
    AuditResult,
    SystemMetrics,
    EODIntelligenceReport,
    FinancialIntelligenceReport,
    SystemAuditReport,
    AuditRequest,
    AuditSummary,
)

from app.system_audit.audit_engine import (
    AuditEngine,
    get_audit_engine,
    reset_audit_engine,
)

from app.system_audit.validation_runner import (
    ValidationRunner,
    get_validation_runner,
)

from app.system_audit.metrics_collector import (
    MetricsCollector,
    get_metrics_collector,
    reset_metrics_collector,
)

from app.system_audit.report_generator import (
    ReportGenerator,
    get_report_generator,
    reset_report_generator,
)

from app.system_audit.routes import router

__all__ = [
    # Models
    "AuditStatus",
    "SubsystemStatus",
    "ValidationStep",
    "AuditResult",
    "SystemMetrics",
    "EODIntelligenceReport",
    "FinancialIntelligenceReport",
    "SystemAuditReport",
    "AuditRequest",
    "AuditSummary",
    # Components
    "AuditEngine",
    "get_audit_engine",
    "reset_audit_engine",
    "ValidationRunner",
    "get_validation_runner",
    "MetricsCollector",
    "get_metrics_collector",
    "reset_metrics_collector",
    "ReportGenerator",
    "get_report_generator",
    "reset_report_generator",
    # Routes
    "router",
]
