"""Executive Command Center API routes."""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.executive.command_center import get_command_center
from app.executive.dashboard_service import get_dashboard_service
from app.executive.override_manager import get_override_manager
from app.executive.executive_reports import get_executive_reports
from app.executive.command_types import ExecutiveCommand, CommandCategory

router = APIRouter(prefix="/executive", tags=["executive"])


@router.get("/overview")
async def get_system_overview(
    session: AsyncSession = Depends(get_db),
):
    """Get system-wide overview."""
    
    command_center = await get_command_center(session)
    return await command_center.get_system_overview()


@router.get("/strategic-state")
async def get_strategic_state(
    session: AsyncSession = Depends(get_db),
):
    """Get detailed strategic state."""
    
    command_center = await get_command_center(session)
    return await command_center.get_strategic_state()


@router.get("/dashboard")
async def get_dashboard(
    session: AsyncSession = Depends(get_db),
):
    """Get complete dashboard data."""
    
    dashboard = await get_dashboard_service(session)
    return await dashboard.get_dashboard()


# === REPORTS ===

@router.get("/reports/daily")
async def get_daily_report(
    session: AsyncSession = Depends(get_db),
):
    """Get daily strategic report."""
    
    reports = await get_executive_reports(session)
    return await reports.generate_daily_report()


@router.get("/reports/weekly")
async def get_weekly_report(
    session: AsyncSession = Depends(get_db),
):
    """Get weekly strategic review."""
    
    reports = await get_executive_reports(session)
    return await reports.generate_weekly_report()


@router.get("/reports/monthly")
async def get_monthly_report(
    session: AsyncSession = Depends(get_db),
):
    """Get monthly system performance report."""
    
    reports = await get_executive_reports(session)
    return await reports.generate_monthly_report()


# === COMMANDS ===

@router.post("/command")
async def execute_command(
    command_type: str = Query(...),
    category: str = Query(...),
    target: Optional[str] = Query(None),
    parameters: dict = Query({}),
    issued_by: str = Query("operator"),
    session: AsyncSession = Depends(get_db),
):
    """Execute an executive command."""
    
    command = ExecutiveCommand(
        command_type=command_type,
        category=CommandCategory(category),
        target=target,
        parameters=parameters,
        issued_by=issued_by,
    )
    
    command_center = await get_command_center(session)
    return await command_center.execute_command(command)


# === OVERRIDES ===

@router.post("/override/pause-autonomy")
async def pause_autonomy(
    issued_by: str = Query("operator"),
    session: AsyncSession = Depends(get_db),
):
    """Pause autonomous strategy loop."""
    
    override_mgr = await get_override_manager(session)
    return await override_mgr.pause_autonomy(issued_by)


@router.post("/override/resume-autonomy")
async def resume_autonomy(
    issued_by: str = Query("operator"),
    session: AsyncSession = Depends(get_db),
):
    """Resume autonomous strategy loop."""
    
    override_mgr = await get_override_manager(session)
    return await override_mgr.resume_autonomy(issued_by)


@router.post("/override/run-strategy-cycle")
async def run_strategy_cycle(
    issued_by: str = Query("operator"),
    session: AsyncSession = Depends(get_db),
):
    """Force immediate strategy cycle."""
    
    override_mgr = await get_override_manager(session)
    return await override_mgr.force_strategy_cycle(issued_by)


@router.get("/override/history")
async def get_override_history(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """Get override history."""
    
    override_mgr = await get_override_manager(session)
    return await override_mgr.get_override_history(limit)


# === GOALS ===

@router.get("/goals")
async def get_goal_status(
    session: AsyncSession = Depends(get_db),
):
    """Get goal status dashboard."""
    
    command_center = await get_command_center(session)
    return await command_center.get_goal_status()


# === RISKS ===

@router.get("/risks")
async def get_risk_dashboard(
    session: AsyncSession = Depends(get_db),
):
    """Get risk dashboard."""
    
    command_center = await get_command_center(session)
    return await command_center.get_risk_dashboard()


# === FINANCIAL ===

@router.get("/financial")
async def get_financial_snapshot(
    session: AsyncSession = Depends(get_db),
):
    """Get financial state snapshot."""
    
    command_center = await get_command_center(session)
    return await command_center.get_financial_snapshot()


# === AUTONOMY ===

@router.get("/autonomy")
async def get_autonomy_status(
    session: AsyncSession = Depends(get_db),
):
    """Get autonomy status."""
    
    command_center = await get_command_center(session)
    overview = await command_center.get_system_overview()
    
    override_mgr = await get_override_manager(session)
    is_paused = await override_mgr.is_autonomy_paused()
    
    return {
        "status": overview.get("autonomy_status", "unknown"),
        "is_paused": is_paused,
    }


@router.get("/autonomy/cycles")
async def get_recent_cycles(
    session: AsyncSession = Depends(get_db),
):
    """Get recent strategy cycles."""
    
    command_center = await get_command_center(session)
    return await command_center.get_recent_strategy_cycles()
