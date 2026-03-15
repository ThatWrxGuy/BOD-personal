"""Outcome review API routes."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.reviews import (
    OutcomeReviewCreate,
    OutcomeReviewUpdate,
    OutcomeReviewResponse,
    OutcomeReviewListResponse,
)
from app.memory.decision_memory import ReviewMemory
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/strategic-reviews", tags=["strategic-reviews"])


@router.post("", response_model=OutcomeReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: OutcomeReviewCreate,
    session: AsyncSession = Depends(get_db),
):
    """Create a new outcome review."""
    memory = ReviewMemory(session)
    review = await memory.create(review_data)
    return review


@router.get("", response_model=OutcomeReviewListResponse)
async def list_reviews(
    decision_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
):
    """List outcome reviews."""
    memory = ReviewMemory(session)
    reviews, total = await memory.list(
        decision_id=decision_id,
        limit=limit,
        offset=offset,
    )
    
    return OutcomeReviewListResponse(
        reviews=reviews,
        total=total,
    )


@router.get("/{review_id}", response_model=OutcomeReviewResponse)
async def get_review(
    review_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Get a specific outcome review."""
    memory = ReviewMemory(session)
    review = await memory.get(review_id)
    
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    return review
