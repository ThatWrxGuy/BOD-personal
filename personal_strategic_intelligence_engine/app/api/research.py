"""Research API routes."""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.research.research_engine import get_research_engine
from app.research.research_sources import get_source_manager

router = APIRouter(prefix="/research", tags=["research"])


@router.get("/tasks")
async def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """List research tasks."""
    
    engine = await get_research_engine(session)
    tasks = await engine.get_tasks(status, limit)
    
    return {
        "tasks": [
            {
                "id": str(t.id),
                "topic": t.topic,
                "description": t.description,
                "status": t.status,
                "priority": t.priority,
                "scope": t.scope,
                "progress": t.progress,
                "trigger_source": t.trigger_source,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "started_at": t.started_at.isoformat() if t.started_at else None,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            }
            for t in tasks
        ]
    }


@router.get("/reports")
async def list_reports(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """List research reports."""
    
    engine = await get_research_engine(session)
    reports = await engine.get_reports(limit)
    
    return {
        "reports": [
            {
                "id": str(r.id),
                "task_id": str(r.task_id),
                "topic": r.topic,
                "summary": r.summary[:200] + "..." if len(r.summary) > 200 else r.summary,
                "confidence_score": r.confidence_score,
                "sources_count": r.sources_count,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            }
            for r in reports
        ]
    }


@router.get("/reports/{report_id}")
async def get_report(
    report_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Get research report details."""
    
    engine = await get_research_engine(session)
    report = await engine.get_report(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {
        "id": str(report.id),
        "task_id": str(report.task_id),
        "topic": report.topic,
        "summary": report.summary,
        "key_findings": report.key_findings,
        "supporting_evidence": report.supporting_evidence,
        "risk_analysis": report.risk_analysis,
        "recommended_actions": report.recommended_actions,
        "confidence_score": report.confidence_score,
        "sources_count": report.sources_count,
        "research_scope": report.research_scope,
        "linked_entities": report.linked_entities,
        "created_at": report.created_at.isoformat() if report.created_at else None,
        "completed_at": report.completed_at.isoformat() if report.completed_at else None,
    }


@router.get("/tasks/{task_id}")
async def get_task(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Get research task details."""
    
    engine = await get_research_engine(session)
    task = await engine.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "id": str(task.id),
        "topic": task.topic,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "scope": task.scope,
        "progress": task.progress,
        "current_step": task.current_step,
        "trigger_source": task.trigger_source,
        "sources_queried": task.sources_queried,
        "error_message": task.error_message,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
    }


@router.post("/run")
async def run_research(
    topic: str = Query(..., description="Research topic"),
    scope: str = Query("standard", description="Research scope: quick, standard, deep"),
    priority: str = Query("medium", description="Priority: low, medium, high"),
    description: Optional[str] = Query(None, description="Description"),
    session: AsyncSession = Depends(get_db),
):
    """Run a research task."""
    
    engine = await get_research_engine(session)
    
    try:
        task = await engine.run_research(
            topic=topic,
            scope=scope,
            priority=priority,
            description=description,
            trigger_source="manual",
        )
        
        return {
            "id": str(task.id),
            "topic": task.topic,
            "status": task.status,
            "message": "Research task started",
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Cancel a research task."""
    
    engine = await get_research_engine(session)
    
    try:
        task = await engine.cancel_task(task_id)
        
        return {
            "id": str(task.id),
            "status": task.status,
            "message": "Task cancelled",
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources")
async def get_available_sources():
    """Get available research sources."""
    
    manager = get_source_manager()
    available = manager.get_available_sources()
    
    return {
        "sources": available,
        "all_sources": list(manager.sources.keys()),
    }


@router.get("/statistics")
async def get_research_statistics(
    session: AsyncSession = Depends(get_db),
):
    """Get research statistics."""
    
    engine = await get_research_engine(session)
    
    # Get counts
    all_tasks = await engine.get_tasks(limit=1000)
    completed_tasks = [t for t in all_tasks if t.status == "completed"]
    failed_tasks = [t for t in all_tasks if t.status == "failed"]
    
    reports = await engine.get_reports(limit=1000)
    
    return {
        "total_tasks": len(all_tasks),
        "completed_tasks": len(completed_tasks),
        "failed_tasks": len(failed_tasks),
        "total_reports": len(reports),
        "success_rate": len(completed_tasks) / len(all_tasks) if all_tasks else 0,
    }
