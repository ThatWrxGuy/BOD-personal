"""System Audit API routes.

API endpoints for system validation, metrics, and reports.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, status

from app.system_audit.audit_models import (
    AuditRequest,
    AuditResult,
    AuditSummary,
    EODIntelligenceReport,
    FinancialIntelligenceReport,
    SystemAuditReport,
)
from app.system_audit.audit_engine import get_audit_engine
from app.system_audit.metrics_collector import get_metrics_collector
from app.system_audit.report_generator import get_report_generator
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/audit", tags=["system-audit"])


# ============ Audit Endpoints ============

@router.post("/run", response_model=AuditResult)
async def run_system_audit(request: AuditRequest):
    """
    Run a full system audit.
    
    Tests all PSIE subsystems and generates validation report.
    """
    engine = get_audit_engine()
    result = await engine.run_full_audit(
        test_signals=request.test_signals,
        test_agents=request.test_agents,
        test_pipeline=request.test_pipeline,
        test_execution=request.test_execution,
        test_learning=request.test_learning,
        test_graph=request.test_graph,
    )
    return result


@router.get("/status")
async def get_audit_status():
    """Get current audit status."""
    engine = get_audit_engine()
    current = engine.get_current_audit()
    latest = engine.get_latest_audit()
    
    if latest:
        return AuditSummary(
            last_audit_id=latest.audit_id,
            last_audit_status=latest.status,
            last_audit_time=latest.start_time,
        )
    
    return AuditSummary()


# ============ Report Endpoints ============

@router.get("/eod", response_model=EODIntelligenceReport)
async def get_eod_report():
    """
    Get End-of-Day Intelligence Report.
    
    Returns daily summary of system activity.
    """
    generator = get_report_generator()
    return generator.generate_eod_report()


@router.get("/financial", response_model=FinancialIntelligenceReport)
async def get_financial_report():
    """
    Get Financial Intelligence Report.
    
    Returns portfolio and financial metrics.
    """
    generator = get_report_generator()
    return generator.generate_financial_report()


@router.get("/system", response_model=SystemAuditReport)
async def get_system_audit_report():
    """
    Get Full System Audit Report.
    
    Returns comprehensive system status and metrics.
    """
    generator = get_report_generator()
    engine = get_audit_engine()
    latest = engine.get_latest_audit()
    
    subsystem_status = None
    if latest:
        subsystem_status = latest.subsystems
    
    return generator.generate_system_audit_report(subsystem_status)


# ============ Metrics Endpoints ============

@router.get("/metrics")
async def get_system_metrics():
    """
    Get system performance metrics.
    
    Returns current metrics from all subsystems.
    """
    collector = get_metrics_collector()
    return collector.collect_summary_metrics()


@router.get("/metrics/health")
async def get_system_health():
    """
    Get system health status.
    
    Returns overall health score and status.
    """
    collector = get_metrics_collector()
    return collector.get_system_health()


@router.get("/metrics/history")
async def get_metrics_history(limit: int = 100):
    """
    Get metrics history.
    
    Returns historical metrics data.
    """
    collector = get_metrics_collector()
    history = collector.get_metrics_history(limit)
    
    return {
        "metrics": [m.dict() for m in history],
        "count": len(history),
    }


# ============ Report History ============

@router.get("/reports/history")
async def get_report_history(
    report_type: Optional[str] = None,
    limit: int = 10,
):
    """
    Get report history.
    
    Returns historical reports.
    """
    generator = get_report_generator()
    return generator.get_report_history(report_type, limit)


# ============ Utility Endpoints ============

@router.get("/history")
async def get_audit_history(limit: int = 10):
    """Get audit execution history."""
    engine = get_audit_engine()
    history = engine.get_audit_history(limit)
    
    return {
        "audits": [a.dict() for a in history],
        "count": len(history),
    }


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "system-audit"}


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    return {"status": "ready", "service": "system-audit"}
