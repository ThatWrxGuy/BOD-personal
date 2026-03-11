"""Planning API routes."""
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.session import get_db
from app.planning.strategic_planner import get_strategic_planner
from app.planning.plan_types import PlanStatus, PlanType

router = APIRouter(prefix="/planning", tags=["planning"])


@router.get("/plans")
async def list_plans(
    status: Optional[str] = Query(None, description="Filter by status"),
    plan_type: Optional[str] = Query(None, description="Filter by plan type"),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """List strategic plans."""
    
    planner = await get_strategic_planner(session)
    plans = await planner.get_plans(status, plan_type, limit)
    
    return {
        "plans": [
            {
                "id": str(p.id),
                "plan_type": p.plan_type,
                "time_horizon": p.time_horizon,
                "status": p.status,
                "title": p.title,
                "domains_involved": p.domains_involved,
                "confidence_score": p.confidence_score,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "start_date": p.start_date.isoformat() if p.start_date else None,
                "end_date": p.end_date.isoformat() if p.end_date else None,
            }
            for p in plans
        ]
    }


@router.get("/plans/{plan_id}")
async def get_plan(
    plan_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Get plan details."""
    
    planner = await get_strategic_planner(session)
    plan = await planner.get_plan(plan_id)
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return {
        "id": str(plan.id),
        "plan_type": plan.plan_type,
        "time_horizon": plan.time_horizon,
        "status": plan.status,
        "title": plan.title,
        "description": plan.description,
        "domains_involved": plan.domains_involved,
        "insights_summary": plan.insights_summary,
        "tradeoff_analysis": plan.tradeoff_analysis,
        "risk_assessment": plan.risk_assessment,
        "confidence_score": plan.confidence_score,
        "created_at": plan.created_at.isoformat() if plan.created_at else None,
        "start_date": plan.start_date.isoformat() if plan.start_date else None,
        "end_date": plan.end_date.isoformat() if plan.end_date else None,
    }


@router.get("/plans/{plan_id}/actions")
async def get_plan_actions(
    plan_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Get actions for a plan."""
    
    planner = await get_strategic_planner(session)
    actions = await planner.get_plan_actions(plan_id)
    
    return {
        "actions": [
            {
                "id": str(a.id),
                "action_type": a.action_type,
                "description": a.description,
                "priority": a.priority,
                "status": a.status,
                "domain": a.domain,
                "expected_outcome": a.expected_outcome,
                "scheduled_date": a.scheduled_date.isoformat() if a.scheduled_date else None,
                "completed_at": a.completed_at.isoformat() if a.completed_at else None,
            }
            for a in actions
        ]
    }


@router.post("/generate")
async def generate_plan(
    scope: str = Query("monthly", description="Plan scope: weekly, monthly, quarterly"),
    domains: Optional[List[str]] = Query(None, description="Domains to include"),
    session: AsyncSession = Depends(get_db),
):
    """Generate a strategic plan."""
    
    planner = await get_strategic_planner(session)
    
    try:
        plan = await planner.generate_plan(scope, domains)
        
        return {
            "id": str(plan.id),
            "plan_type": plan.plan_type,
            "status": plan.status,
            "title": plan.title,
            "message": "Plan generated successfully",
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plans/{plan_id}/approve")
async def approve_plan(
    plan_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Approve a strategic plan."""
    
    planner = await get_strategic_planner(session)
    
    try:
        plan = await planner.approve_plan(plan_id)
        
        return {
            "id": str(plan.id),
            "status": plan.status,
            "message": "Plan approved",
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plans/{plan_id}/reject")
async def reject_plan(
    plan_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Reject a strategic plan."""
    
    planner = await get_strategic_planner(session)
    
    try:
        plan = await planner.reject_plan(plan_id)
        
        return {
            "id": str(plan.id),
            "status": plan.status,
            "message": "Plan rejected",
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/actions/{action_id}/complete")
async def complete_action(
    action_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Mark an action as completed."""
    
    planner = await get_strategic_planner(session)
    
    try:
        from app.planning.plan_types import ActionStatus
        action = await planner.update_action_status(action_id, ActionStatus.COMPLETED.value)
        
        return {
            "id": str(action.id),
            "status": action.status,
            "message": "Action completed",
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
