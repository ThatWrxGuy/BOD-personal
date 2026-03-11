"""Strategic reviews API routes."""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.session import get_db
from app.reviews.strategic_review_engine import get_strategic_review_engine
from app.reviews.review_scheduler import get_review_scheduler
from app.reviews.review_types import (
    StrategicReview,
    StrategicInsight,
    ReviewDecisionProposal,
    ReviewType,
    REVIEW_TYPE_CONFIG,
)
from app.observability import increment
from app.observability.metrics_service import MetricDomain

router = APIRouter(prefix="/reviews", tags=["reviews"])


# ===================
# Strategic Review Endpoints
# ===================

@router.get("")
async def list_reviews(
    review_type: Optional[str] = Query(None, description="Filter by review type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """List strategic reviews."""
    
    engine = await get_strategic_review_engine(session)
    reviews = await engine.get_reviews(review_type, status, limit)
    
    return {
        "reviews": [
            {
                "id": str(r.id),
                "review_type": r.review_type,
                "status": r.status,
                "scheduled_at": r.scheduled_at.isoformat() if r.scheduled_at else None,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                "domains_analyzed": r.domains_analyzed,
                "agents_involved": r.agents_involved,
            }
            for r in reviews
        ]
    }


@router.get("/types")
async def get_review_types():
    """Get available review types."""
    
    types = []
    
    for review_type in ReviewType:
        config = REVIEW_TYPE_CONFIG.get(review_type)
        if config:
            types.append({
                "id": review_type.value,
                "name": config.get("name"),
                "description": config.get("description"),
                "frequency": config.get("frequency"),
                "domains": config.get("domains"),
                "agents": config.get("agents"),
            })
    
    return {"review_types": types}


@router.get("/schedule")
async def get_review_schedule(session: AsyncSession = Depends(get_db)):
    """Get upcoming review schedule."""
    
    scheduler = await get_review_scheduler(session)
    schedule = await scheduler.get_review_schedule()
    
    return {"schedule": schedule}


@router.get("/{review_id}")
async def get_review(
    review_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Get review details."""
    
    engine = await get_strategic_review_engine(session)
    review = await engine.get_review(review_id)
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return {
        "id": str(review.id),
        "review_type": review.review_type,
        "status": review.status,
        "scheduled_at": review.scheduled_at.isoformat() if review.scheduled_at else None,
        "started_at": review.started_at.isoformat() if review.started_at else None,
        "completed_at": review.completed_at.isoformat() if review.completed_at else None,
        "domains_analyzed": review.domains_analyzed,
        "agents_involved": review.agents_involved,
        "summary": review.summary,
        "metrics_snapshot": review.metrics_snapshot,
        "error_message": review.error_message,
    }


@router.get("/{review_id}/insights")
async def get_review_insights(
    review_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Get insights for a review."""
    
    engine = await get_strategic_review_engine(session)
    insights = await engine.get_review_insights(review_id)
    
    return {
        "insights": [
            {
                "id": str(i.id),
                "domain": i.domain,
                "insight_type": i.insight_type,
                "title": i.title,
                "description": i.description,
                "confidence_score": i.confidence_score,
                "priority": i.priority,
                "status": i.status,
            }
            for i in insights
        ]
    }


@router.get("/{review_id}/decisions")
async def get_review_decisions(
    review_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Get decision proposals for a review."""
    
    engine = await get_strategic_review_engine(session)
    proposals = await engine.get_review_proposals(review_id)
    
    return {
        "decisions": [
            {
                "id": str(p.id),
                "decision_type": p.decision_type,
                "title": p.title,
                "description": p.description,
                "status": p.status,
                "priority": p.priority,
                "expected_impact": p.expected_impact,
            }
            for p in proposals
        ]
    }


@router.post("/run/{review_type}")
async def run_review(
    review_type: str,
    time_range_days: int = Query(30, ge=1, le=365, description="Time range for analysis"),
    session: AsyncSession = Depends(get_db),
):
    """Run a strategic review."""
    
    # Validate review type
    if review_type not in [rt.value for rt in ReviewType]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid review type. Available: {[rt.value for rt in ReviewType]}"
        )
    
    # Run the review
    engine = await get_strategic_review_engine(session)
    
    try:
        review = await engine.run_review(review_type, time_range_days)
        
        # Track metrics
        increment("reviews_started", domain=MetricDomain.SYSTEM)
        increment("reviews_completed", domain=MetricDomain.SYSTEM)
        
        return {
            "id": str(review.id),
            "review_type": review.review_type,
            "status": review.status,
            "message": "Review completed successfully",
        }
        
    except Exception as e:
        increment("reviews_failed", domain=MetricDomain.SYSTEM)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedule/{review_type}")
async def schedule_review(
    review_type: str,
    scheduled_at: Optional[str] = Query(None, description="ISO datetime for scheduling"),
    session: AsyncSession = Depends(get_db),
):
    """Schedule a strategic review."""
    
    from datetime import datetime
    
    # Validate review type
    if review_type not in [rt.value for rt in ReviewType]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid review type"
        )
    
    # Parse scheduled time
    scheduled_time = None
    if scheduled_at:
        try:
            scheduled_time = datetime.fromisoformat(scheduled_at)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid datetime format")
    
    # Schedule
    scheduler = await get_review_scheduler(session)
    review = await scheduler.schedule_review(review_type, scheduled_time)
    
    increment("reviews_scheduled", domain=MetricDomain.SYSTEM)
    
    return {
        "id": str(review.id),
        "review_type": review.review_type,
        "scheduled_at": review.scheduled_at.isoformat() if review.scheduled_at else None,
        "status": review.status,
    }
