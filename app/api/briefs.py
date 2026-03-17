"""BB-APP-002: Briefs API."""

from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from app.application import briefs_service
from app.read_models import BriefSummary, BriefDetailReadModel

router = APIRouter()


# ============== Response Models ==============

class BriefListResponse(BaseModel):
    """Brief list response."""
    briefs: List[BriefSummary]
    total: int


@router.get("/", response_model=BriefListResponse)
async def get_briefs(limit: int = 10, user_id: str = "user-1"):
    """Get list of briefs."""
    briefs = await briefs_service.list_briefs(user_id)
    return BriefListResponse(briefs=briefs, total=len(briefs))


@router.get("/latest", response_model=BriefDetailReadModel)
async def get_latest_brief(user_id: str = "user-1"):
    """Get the latest brief."""
    briefs = await briefs_service.list_briefs(user_id)
    if not briefs:
        raise HTTPException(status_code=404, detail="No briefs found")
    brief = await briefs_service.get_brief(briefs[0].id, user_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    return brief


@router.post("/generate")
async def generate_brief(user_id: str = "user-1"):
    """Generate a new brief."""
    # In production, this would trigger the orchestration layer
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/{brief_id}", response_model=BriefDetailReadModel)
async def get_brief(brief_id: str, user_id: str = "user-1"):
    """Get a specific brief by ID."""
    brief = await briefs_service.get_brief(brief_id, user_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    return brief


@router.get("/{brief_id}/compare/{other_brief_id}")
async def compare_briefs(brief_id: str, other_brief_id: str):
    """Compare two briefs."""
    return await briefs_service.compare_briefs(brief_id, other_brief_id)
