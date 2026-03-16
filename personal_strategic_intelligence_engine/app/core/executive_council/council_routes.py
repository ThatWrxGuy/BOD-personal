"""Executive Council API Routes - BB-CORE-022"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException

from app.core.executive_council.executive_council_engine import (
    get_executive_council_engine,
)
from app.core.executive_council.council_models import (
    DomainRecommendation,
    RankedRecommendation,
    Conflict,
    AlignmentScore,
    CouncilCycleResult,
    Domain,
)

router = APIRouter(prefix="/core/council", tags=["Executive Council"])


@router.get("/status")
async def get_council_status():
    """Get council system state."""
    engine = get_executive_council_engine()
    return engine.get_state()


@router.post("/cycle", response_model=CouncilCycleResult)
async def run_council_cycle(
    recommendations: Optional[List[DomainRecommendation]] = None,
    finance_context: Optional[dict] = None,
):
    """Run a complete council decision cycle."""
    engine = get_executive_council_engine()
    
    return engine.run_council_cycle(
        recommendations=recommendations,
        finance_context=finance_context,
    )


@router.get("/recommendations", response_model=List[DomainRecommendation])
async def get_recommendations(
    domain: Optional[str] = Query(None, description="Filter by domain"),
):
    """Get domain recommendations."""
    engine = get_executive_council_engine()
    
    if domain:
        try:
            d = Domain(domain)
            return engine.get_recommendations_by_domain(d)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid domain: {domain}")
    
    result = engine.get_last_result()
    if not result:
        return []
    
    return result.recommendations


@router.get("/priorities", response_model=List[RankedRecommendation])
async def get_priorities():
    """Get ranked priorities."""
    engine = get_executive_council_engine()
    
    result = engine.get_last_result()
    if not result:
        return []
    
    return result.ranked_recommendations


@router.get("/conflicts", response_model=List[Conflict])
async def get_conflicts():
    """Get detected and resolved conflicts."""
    engine = get_executive_council_engine()
    
    result = engine.get_last_result()
    if not result:
        return []
    
    return result.conflicts


@router.get("/alignment", response_model=List[AlignmentScore])
async def get_alignment():
    """Get strategic alignment scores."""
    engine = get_executive_council_engine()
    
    result = engine.get_last_result()
    if not result:
        return []
    
    return result.alignment_scores


@router.get("/brief")
async def get_executive_brief(
    as_text: bool = Query(False, description="Return as formatted text"),
):
    """Get executive strategic brief."""
    engine = get_executive_council_engine()
    
    result = engine.get_last_result()
    if not result:
        raise HTTPException(status_code=404, detail="No brief available. Run council cycle first.")
    
    if as_text:
        return {"text": engine.format_brief_text(result)}
    
    return result


@router.post("/recommendation")
async def add_recommendation(
    domain: str,
    title: str,
    description: str,
    action_items: Optional[List[str]] = None,
    priority: str = "medium",
    confidence: float = 0.5,
):
    """Add a recommendation to the council."""
    engine = get_executive_council_engine()
    
    try:
        d = Domain(domain)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid domain: {domain}")
    
    return engine.add_recommendation(
        domain=d,
        title=title,
        description=description,
        action_items=action_items,
        priority=priority,
        confidence=confidence,
    )
