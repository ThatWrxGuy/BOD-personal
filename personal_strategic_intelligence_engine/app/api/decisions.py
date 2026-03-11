"""Decision API routes."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.decisions import (
    DecisionCreate,
    DecisionUpdate,
    DecisionResponse,
    DecisionListResponse,
)
from app.memory.decision_memory import DecisionMemory
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/decisions", tags=["decisions"])


@router.post("", response_model=DecisionResponse, status_code=status.HTTP_201_CREATED)
async def create_decision(
    decision_data: DecisionCreate,
    session: AsyncSession = Depends(get_db),
):
    """Create a new decision record."""
    memory = DecisionMemory(session)
    decision = await memory.create(decision_data)
    return decision


@router.get("", response_model=DecisionListResponse)
async def list_decisions(
    limit: int = 50,
    offset: int = 0,
    status_filter: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
):
    """List decisions with pagination."""
    memory = DecisionMemory(session)
    decisions, total = await memory.list(
        limit=limit,
        offset=offset,
        status=status_filter,
    )
    
    return DecisionListResponse(
        decisions=decisions,
        total=total,
    )


@router.get("/{decision_id}", response_model=DecisionResponse)
async def get_decision(
    decision_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Get a specific decision with reviews."""
    memory = DecisionMemory(session)
    decision = await memory.get(decision_id)
    
    if not decision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found")
    
    return decision


@router.patch("/{decision_id}", response_model=DecisionResponse)
async def update_decision(
    decision_id: int,
    decision_data: DecisionUpdate,
    session: AsyncSession = Depends(get_db),
):
    """Update a decision record."""
    memory = DecisionMemory(session)
    decision = await memory.update(decision_id, decision_data)
    
    if not decision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found")
    
    return decision
