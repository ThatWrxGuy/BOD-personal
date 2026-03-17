"""BB-APP-002: Recommendations API."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.application import recommendations_service
from app.read_models import (
    RecommendationSummaryReadModel,
    RecommendationDetailReadModel,
    RecommendationStatus,
)
from app.commands import CommandResult

router = APIRouter()


# ============== Request Models ==============

class RecommendationActionRequest(BaseModel):
    """Request to act on a recommendation."""
    notes: Optional[str] = ""
    reason: Optional[str] = ""


class ConvertToActionRequest(BaseModel):
    """Request to convert recommendation to action."""
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None


# ============== Response Models ==============

class RecommendationListResponse(BaseModel):
    """Recommendation list response."""
    recommendations: List[RecommendationSummaryReadModel]
    total: int


class CommandResponse(BaseModel):
    """Command execution response."""
    success: bool
    message: str
    entity_id: Optional[str] = None


@router.get("/", response_model=RecommendationListResponse)
async def get_recommendations(
    domain: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    user_id: str = "user-1"
):
    """Get list of recommendations."""
    status_enum = None
    if status:
        try:
            status_enum = RecommendationStatus(status)
        except ValueError:
            pass
    
    recommendations = await recommendations_service.list_recommendations(
        user_id=user_id,
        domain=domain,
        status=status_enum,
        limit=limit
    )
    return RecommendationListResponse(recommendations=recommendations, total=len(recommendations))


@router.get("/{recommendation_id}", response_model=RecommendationDetailReadModel)
async def get_recommendation(recommendation_id: str, user_id: str = "user-1"):
    """Get detailed recommendation."""
    recommendation = await recommendations_service.get_recommendation(recommendation_id, user_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return recommendation


@router.get("/{recommendation_id}/explanation")
async def get_recommendation_explanation(recommendation_id: str, user_id: str = "user-1"):
    """Get detailed explanation for a recommendation."""
    recommendation = await recommendations_service.get_recommendation(recommendation_id, user_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return {
        "rationale": recommendation.rationale,
        "expected_benefit": recommendation.expected_benefit,
        "likely_tradeoff": recommendation.likely_tradeoff,
        "supporting_signals": recommendation.supporting_signals,
    }


@router.post("/{recommendation_id}/approve", response_model=CommandResponse)
async def approve_recommendation(
    recommendation_id: str,
    request: RecommendationActionRequest = RecommendationActionRequest(),
    user_id: str = "user-1"
):
    """Approve a recommendation."""
    success = await recommendations_service.approve_recommendation(
        recommendation_id=recommendation_id,
        user_id=user_id,
        notes=request.notes
    )
    if success:
        return CommandResponse(success=True, message="Recommendation approved", entity_id=recommendation_id)
    return CommandResponse(success=False, message="Failed to approve recommendation")


@router.post("/{recommendation_id}/reject", response_model=CommandResponse)
async def reject_recommendation(
    recommendation_id: str,
    request: RecommendationActionRequest = RecommendationActionRequest(),
    user_id: str = "user-1"
):
    """Reject a recommendation."""
    success = await recommendations_service.reject_recommendation(
        recommendation_id=recommendation_id,
        user_id=user_id,
        reason=request.reason or ""
    )
    if success:
        return CommandResponse(success=True, message="Recommendation rejected", entity_id=recommendation_id)
    return CommandResponse(success=False, message="Failed to reject recommendation")


@router.post("/{recommendation_id}/defer", response_model=CommandResponse)
async def defer_recommendation(
    recommendation_id: str,
    request: RecommendationActionRequest = RecommendationActionRequest(),
    user_id: str = "user-1"
):
    """Defer a recommendation."""
    success = await recommendations_service.defer_recommendation(
        recommendation_id=recommendation_id,
        user_id=user_id,
        reason=request.reason or ""
    )
    if success:
        return CommandResponse(success=True, message="Recommendation deferred", entity_id=recommendation_id)
    return CommandResponse(success=False, message="Failed to defer recommendation")


@router.post("/{recommendation_id}/convert", response_model=CommandResponse)
async def convert_to_action(
    recommendation_id: str,
    request: ConvertToActionRequest = ConvertToActionRequest(),
    user_id: str = "user-1"
):
    """Convert recommendation to action."""
    action_id = await recommendations_service.convert_to_action(
        recommendation_id=recommendation_id,
        user_id=user_id,
        title=request.title or "",
        description=request.description or "",
    )
    if action_id:
        return CommandResponse(success=True, message="Action created", entity_id=action_id)
    return CommandResponse(success=False, message="Failed to create action")
