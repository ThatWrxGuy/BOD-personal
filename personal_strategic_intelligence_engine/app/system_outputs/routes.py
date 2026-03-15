"""System Outputs API routes.

API endpoints for PSIE operational outputs and intelligence reports.

Per V47-007, this module provides:
- Executive Brief
- Strategy Proposals
- Governance Queue
- Execution Status
- Financial Intelligence
- Options Intelligence
- Learning Report
- EOD Report
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, status

from app.system_outputs.output_models import (
    OutputsOverview,
    StrategyReport,
    ExecutionReport,
    FinancialReport,
    LearningReport,
    SystemMetricsReport,
    EODReport,
)
from app.system_outputs.output_generator import get_output_generator
from app.system_outputs.output_collector import get_output_collector
from app.system_outputs.report_generator import get_report_generator
from app.core.response_wrapper import (
    success_response,
    error_response,
    wrap_list_response,
)
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/outputs", tags=["system-outputs"])


# ============ Overview Endpoint ============

@router.get("/overview")
async def get_outputs_overview():
    """Get complete intelligence outputs overview."""
    generator = get_output_generator()
    return success_response(generator.generate_overview().dict())


# ============ Category Endpoints ============

@router.get("/strategies")
async def get_strategy_outputs():
    """Get strategy activity report."""
    generator = get_output_generator()
    return success_response(generator.generate_strategy_report().dict())


@router.get("/executions")
async def get_execution_outputs():
    """Get execution activity report."""
    generator = get_output_generator()
    return success_response(generator.generate_execution_report().dict())


@router.get("/financial")
async def get_financial_outputs():
    """Get financial intelligence report."""
    generator = get_output_generator()
    return success_response(generator.generate_financial_report().dict())


@router.get("/learning")
async def get_learning_outputs():
    """Get learning insights report."""
    generator = get_output_generator()
    return success_response(generator.generate_learning_report().dict())


@router.get("/system")
async def get_system_metrics():
    """Get system metrics report."""
    generator = get_output_generator()
    return success_response(generator.generate_system_metrics_report().dict())


# ============ EOD Report ============

@router.get("/eod")
async def get_eod_report():
    """Get End-of-Day Intelligence Report."""
    generator = get_output_generator()
    return success_response(generator.generate_eod_report().dict())


# ============ Reports List ============

@router.get("/reports")
async def get_all_reports():
    """Get all generated reports."""
    generator = get_output_generator()
    return success_response({
        "strategy": generator.generate_strategy_report().dict(),
        "execution": generator.generate_execution_report().dict(),
        "financial": generator.generate_financial_report().dict(),
        "learning": generator.generate_learning_report().dict(),
        "system": generator.generate_system_metrics_report().dict(),
        "eod": generator.generate_eod_report().dict(),
    })


# ============ Raw Outputs ============

@router.get("/raw/strategies")
async def get_raw_strategy_outputs(limit: int = 50):
    """Get raw strategy outputs."""
    collector = get_output_collector()
    outputs = collector.get_strategy_outputs(limit)
    return wrap_list_response([o.dict() for o in outputs], total=len(outputs))


@router.get("/raw/executions")
async def get_raw_execution_outputs(limit: int = 50):
    """Get raw execution outputs."""
    collector = get_output_collector()
    outputs = collector.get_execution_outputs(limit)
    return wrap_list_response([o.dict() for o in outputs], total=len(outputs))


@router.get("/raw/learning")
async def get_raw_learning_outputs(limit: int = 50):
    """Get raw learning outputs."""
    collector = get_output_collector()
    outputs = collector.get_learning_outputs(limit)
    return wrap_list_response([o.dict() for o in outputs], total=len(outputs))


# ============ Statistics ============

@router.get("/statistics")
async def get_output_statistics():
    """Get output statistics."""
    collector = get_output_collector()
    counts = collector.get_output_counts()
    return success_response({
        "total_outputs": sum(counts.values()),
        "by_category": counts,
    })


# ============ Utility Endpoints ============

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return success_response({"status": "healthy", "service": "system-outputs"})


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    return success_response({"status": "ready", "service": "system-outputs"})


# ============ V47-007 CEO Intelligence Reports ============

@router.get("/executive-brief")
async def get_executive_brief():
    """Get Daily Executive Intelligence Brief (V47-007)."""
    generator = get_report_generator()
    return success_response(generator.generate_executive_brief())


@router.get("/strategy-proposals")
async def get_strategy_proposals():
    """Get Strategy Proposal Report (V47-007)."""
    generator = get_report_generator()
    return success_response(generator.generate_strategy_proposals())


@router.get("/governance-queue")
async def get_governance_queue():
    """Get Governance Approval Queue (V47-007)."""
    generator = get_report_generator()
    return success_response(generator.generate_governance_queue())


@router.get("/execution-status")
async def get_execution_status():
    """Get Execution Status Report (V47-007)."""
    generator = get_report_generator()
    return success_response(generator.generate_execution_status())


@router.get("/financial-intelligence")
async def get_financial_intelligence():
    """Get Financial Risk & Opportunity Report (V47-007)."""
    generator = get_report_generator()
    return success_response(generator.generate_financial_intelligence())


@router.get("/options-intelligence")
async def get_options_intelligence():
    """Get SPY 0DTE Options Intelligence Brief (V47-007)."""
    generator = get_report_generator()
    return success_response(generator.generate_options_intelligence())


@router.get("/learning-report")
async def get_learning_report():
    """Get Learning & System Evolution Report (V47-007)."""
    generator = get_report_generator()
    return success_response(generator.generate_learning_report())


@router.get("/eod-report")
async def get_eod_report_v47():
    """Get End-of-Day System Report (V47-007)."""
    generator = get_report_generator()
    return success_response(generator.generate_eod_report())


@router.get("/reports/list")
async def list_all_reports():
    """List all available reports (V47-007)."""
    reports = [
        {"id": "executive-brief", "name": "Daily Executive Brief", "classification": "advisory"},
        {"id": "strategy-proposals", "name": "Strategy Proposals", "classification": "decision_required"},
        {"id": "governance-queue", "name": "Governance Queue", "classification": "decision_required"},
        {"id": "execution-status", "name": "Execution Status", "classification": "advisory"},
        {"id": "financial-intelligence", "name": "Financial Intelligence", "classification": "review_required"},
        {"id": "options-intelligence", "name": "Options Intelligence", "classification": "review_required"},
        {"id": "learning-report", "name": "Learning Report", "classification": "advisory"},
        {"id": "eod-report", "name": "EOD Report", "classification": "advisory"},
    ]
    return success_response({"reports": reports, "total": len(reports)})
