"""Governance API routes."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.governance import (
    GoalCreate,
    GoalUpdate,
    GoalResponse,
    GoalProgressCreate,
    GoalProgressResponse,
    PlanCreate,
    PlanUpdate,
    PlanResponse,
    ScheduleResponse,
    TriggerEventResponse,
    ReviewResponse,
    DashboardResponse,
)
from app.services.governance_service import GovernanceService
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/governance", tags=["governance"])


# ========== Goals ==========

@router.post("/goals", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal: GoalCreate,
    session: AsyncSession = Depends(get_db),
):
    """Create a new strategic goal."""
    service = GovernanceService(session)
    result = await service.create_goal(**goal.model_dump())
    
    # Fetch the created goal
    from app.governance.goal_tracker import GoalTracker
    tracker = GoalTracker(session)
    created = await tracker.get_goal(UUID(result["id"]))
    return created


@router.get("/goals", response_model=list[GoalResponse])
async def list_goals(
    status: Optional[str] = None,
    category: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
):
    """List strategic goals."""
    service = GovernanceService(session)
    goals = await service.get_goals(status=status, category=category)
    
    # Convert to response format
    from app.governance.goal_tracker import GoalTracker
    tracker = GoalTracker(session)
    all_goals = await tracker.list_goals(status=status, category=category)
    return all_goals


@router.get("/goals/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    """Get a specific goal."""
    from app.governance.goal_tracker import GoalTracker
    tracker = GoalTracker(session)
    goal = await tracker.get_goal(goal_id)
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    return goal


@router.patch("/goals/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: UUID,
    update: GoalUpdate,
    session: AsyncSession = Depends(get_db),
):
    """Update a goal."""
    from app.governance.goal_tracker import GoalTracker
    tracker = GoalTracker(session)
    goal = await tracker.get_goal(goal_id)
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Apply updates
    if update.title:
        goal.title = update.title
    if update.description:
        goal.description = update.description
    if update.category:
        goal.category = update.category
    if update.priority:
        goal.priority = update.priority
    if update.target_value:
        goal.target_value = update.target_value
    if update.current_value:
        goal.current_value = update.current_value
    if update.unit:
        goal.unit = update.unit
    if update.target_date:
        goal.target_date = update.target_date
    if update.status:
        goal.status = update.status
    
    await session.commit()
    await session.refresh(goal)
    return goal


@router.post("/goals/{goal_id}/progress", status_code=status.HTTP_201_CREATED)
async def record_progress(
    goal_id: UUID,
    progress: GoalProgressCreate,
    session: AsyncSession = Depends(get_db),
):
    """Record progress for a goal."""
    from app.governance.goal_tracker import GoalTracker
    tracker = GoalTracker(session)
    
    try:
        result = await tracker.update_goal_progress(goal_id, progress.value, progress.notes)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/goals/{goal_id}/complete")
async def complete_goal(
    goal_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    """Mark a goal as completed."""
    service = GovernanceService(session)
    await service.complete_goal(goal_id)
    return {"status": "completed"}


@router.post("/goals/{goal_id}/abandon")
async def abandon_goal(
    goal_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    """Mark a goal as abandoned."""
    service = GovernanceService(session)
    await service.abandon_goal(goal_id)
    return {"status": "abandoned"}


# ========== Plans ==========

@router.post("/plans", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan: PlanCreate,
    session: AsyncSession = Depends(get_db),
):
    """Create a new strategic plan."""
    from app.governance.plan_manager import PlanManager
    manager = PlanManager(session)
    created = await manager.create_plan(**plan.model_dump(exclude_none=True))
    return created


@router.get("/plans", response_model=list[PlanResponse])
async def list_plans(
    status: Optional[str] = None,
    goal_id: Optional[UUID] = None,
    session: AsyncSession = Depends(get_db),
):
    """List strategic plans."""
    from app.governance.plan_manager import PlanManager
    manager = PlanManager(session)
    plans = await manager.list_plans(status=status, goal_id=goal_id)
    return plans


@router.get("/plans/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    """Get a specific plan."""
    from app.governance.plan_manager import PlanManager
    manager = PlanManager(session)
    plan = await manager.get_plan(plan_id)
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return plan


@router.post("/plans/{plan_id}/complete")
async def complete_plan(
    plan_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    """Mark a plan as completed."""
    service = GovernanceService(session)
    await service.complete_plan(plan_id)
    return {"status": "completed"}


@router.post("/plans/{plan_id}/pause")
async def pause_plan(
    plan_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    """Pause a plan."""
    service = GovernanceService(session)
    await service.pause_plan(plan_id)
    return {"status": "paused"}


# ========== Schedules ==========

@router.get("/schedules", response_model=list[ScheduleResponse])
async def list_schedules(
    session: AsyncSession = Depends(get_db),
):
    """List board meeting schedules."""
    from app.governance.board_scheduler import BoardScheduler
    scheduler = BoardScheduler(session)
    schedules = await scheduler.get_active_schedules()
    return schedules


# ========== Triggers ==========

@router.get("/triggers", response_model=list[TriggerEventResponse])
async def list_triggers(
    resolved: bool = False,
    session: AsyncSession = Depends(get_db),
):
    """List trigger events."""
    from app.governance.trigger_engine import TriggerEngine
    engine = TriggerEngine(session)
    
    if resolved:
        from sqlalchemy import select, and_
        from app.models.trigger_event import TriggerEvent
        result = await session.execute(
            select(TriggerEvent).where(TriggerEvent.is_resolved == True)
        )
    else:
        result = await engine.get_pending_triggers()
    
    return result


@router.post("/triggers/{trigger_id}/resolve")
async def resolve_trigger(
    trigger_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    """Resolve a trigger event."""
    service = GovernanceService(session)
    await service.resolve_event(trigger_id)
    return {"status": "resolved"}


# ========== Reviews ==========

@router.post("/reviews/{review_type}", response_model=ReviewResponse)
async def run_review(
    review_type: str,
    session: AsyncSession = Depends(get_db),
):
    """Run a governance review."""
    service = GovernanceService(session)
    
    valid_types = ["DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "ANNUAL"]
    if review_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid review type. Must be one of: {valid_types}")
    
    result = await service.run_review(review_type)
    return result


# ========== Dashboard ==========

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    session: AsyncSession = Depends(get_db),
):
    """Get governance dashboard."""
    service = GovernanceService(session)
    dashboard = await service.get_governance_dashboard()
    return dashboard
