"""BB-APP-002: Actions API."""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.application import actions_service
from app.read_models import ActionSummaryReadModel, ActionDetailReadModel, ActionStatus
from app.commands import CommandResult

router = APIRouter()


# ============== Request Models ==============

class CreateActionRequest(BaseModel):
    """Request to create a new action."""
    title: str
    description: Optional[str] = ""
    domain: Optional[str] = ""
    due_date: Optional[str] = None
    estimated_minutes: int = 30
    recommendation_id: Optional[str] = None
    brief_id: Optional[str] = None


class UpdateStatusRequest(BaseModel):
    """Request to update action status."""
    status: str
    notes: Optional[str] = ""


class CompleteActionRequest(BaseModel):
    """Request to complete an action."""
    outcome_notes: str = ""
    effectiveness_score: Optional[float] = None


# ============== Response Models ==============

class ActionListResponse(BaseModel):
    """Action list response."""
    actions: List[ActionSummaryReadModel]
    total: int


class CommandResponse(BaseModel):
    """Command execution response."""
    success: bool
    message: str
    entity_id: Optional[str] = None


@router.get("/", response_model=ActionListResponse)
async def get_actions(
    domain: Optional[str] = None,
    status: Optional[str] = None,
    due_today: bool = False,
    overdue: bool = False,
    limit: int = 50,
    user_id: str = "user-1"
):
    """Get list of actions."""
    status_enum = None
    if status:
        try:
            status_enum = ActionStatus(status)
        except ValueError:
            pass
    
    actions = await actions_service.list_actions(
        user_id=user_id,
        domain=domain,
        status=status_enum,
        limit=limit
    )
    return ActionListResponse(actions=actions, total=len(actions))


@router.post("/", response_model=CommandResponse)
async def create_action(
    request: CreateActionRequest,
    user_id: str = "user-1"
):
    """Create a new action."""
    due_date = None
    if request.due_date:
        try:
            due_date = datetime.fromisoformat(request.due_date)
        except ValueError:
            pass
    
    action_id = await actions_service.create_action(
        user_id=user_id,
        title=request.title,
        description=request.description or "",
        domain=request.domain or "",
        due_date=due_date,
        estimated_minutes=request.estimated_minutes,
        recommendation_id=request.recommendation_id,
        brief_id=request.brief_id
    )
    if action_id:
        return CommandResponse(success=True, message="Action created", entity_id=action_id)
    return CommandResponse(success=False, message="Failed to create action")


@router.get("/{action_id}", response_model=ActionDetailReadModel)
async def get_action(action_id: str, user_id: str = "user-1"):
    """Get detailed action."""
    action = await actions_service.get_action(action_id, user_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action


@router.patch("/{action_id}/status", response_model=CommandResponse)
async def update_action_status(
    action_id: str,
    request: UpdateStatusRequest,
    user_id: str = "user-1"
):
    """Update action status."""
    try:
        status_enum = ActionStatus(request.status)
    except ValueError:
        return CommandResponse(success=False, message="Invalid status")
    
    success = await actions_service.update_status(
        action_id=action_id,
        user_id=user_id,
        new_status=status_enum,
        notes=request.notes or ""
    )
    if success:
        return CommandResponse(success=True, message="Status updated", entity_id=action_id)
    return CommandResponse(success=False, message="Failed to update status")


@router.post("/{action_id}/complete", response_model=CommandResponse)
async def complete_action(
    action_id: str,
    request: CompleteActionRequest = CompleteActionRequest(),
    user_id: str = "user-1"
):
    """Complete an action."""
    success = await actions_service.complete_action(
        action_id=action_id,
        user_id=user_id,
        outcome_notes=request.outcome_notes,
        effectiveness_score=request.effectiveness_score
    )
    if success:
        return CommandResponse(success=True, message="Action completed", entity_id=action_id)
    return CommandResponse(success=False, message="Failed to complete action")


@router.post("/{action_id}/outcome", response_model=CommandResponse)
async def attach_outcome(
    action_id: str,
    request: CompleteActionRequest,
    user_id: str = "user-1"
):
    """Attach outcome notes to an action."""
    success = await actions_service.attach_outcome(
        action_id=action_id,
        user_id=user_id,
        outcome_notes=request.outcome_notes,
        effectiveness_score=request.effectiveness_score
    )
    if success:
        return CommandResponse(success=True, message="Outcome attached", entity_id=action_id)
    return CommandResponse(success=False, message="Failed to attach outcome")


@router.get("/effectiveness")
async def get_action_effectiveness(time_range_days: int = 30):
    """Get action effectiveness metrics."""
    # Placeholder - would aggregate from completed actions
    return {
        "completed_count": 5,
        "average_effectiveness": 0.75,
        "completion_rate": 0.85
    }
