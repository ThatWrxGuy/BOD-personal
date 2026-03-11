"""Signal API routes."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.signals import (
    SignalCreate,
    SignalResponse,
    SignalListResponse,
    SignalSummaryResponse,
)
from app.services.signal_service import SignalService
from app.models.strategic_signal import SignalCategory
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("", response_model=SignalListResponse)
async def list_signals(
    hours: int = Query(default=24, ge=1, le=168),
    category: Optional[str] = None,
    min_urgency: Optional[int] = Query(default=None, ge=1, le=10),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db),
):
    """List strategic signals with optional filtering."""
    service = SignalService(session)

    if category:
        signals = await service.get_signals_by_category(
            category=category,
            hours=hours,
            limit=limit,
        )
        total = len(signals)
    elif min_urgency:
        signals = await service.get_high_urgency_signals(
            threshold=min_urgency,
            hours=hours,
        )
        total = len(signals)
    else:
        signals = await service.get_recent_signals(hours=hours, limit=limit)
        total = len(signals)

    return SignalListResponse(signals=signals, total=total)


@router.get("/summary", response_model=SignalSummaryResponse)
async def get_signal_summary(
    hours: int = Query(default=24, ge=1, le=168),
    session: AsyncSession = Depends(get_db),
):
    """Get summary of recent signals."""
    service = SignalService(session)
    summary = await service.get_signal_summary(hours=hours)
    return SignalSummaryResponse(**summary)


@router.get("/urgency", response_model=SignalListResponse)
async def get_high_urgency_signals(
    threshold: int = Query(default=7, ge=1, le=10),
    hours: int = Query(default=24, ge=1, le=168),
    session: AsyncSession = Depends(get_db),
):
    """Get high urgency signals."""
    service = SignalService(session)
    signals = await service.get_high_urgency_signals(
        threshold=threshold,
        hours=hours,
    )
    return SignalListResponse(signals=signals, total=len(signals))


@router.get("/ranked", response_model=SignalListResponse)
async def get_ranked_signals(
    by: str = Query(default="urgency", pattern="^(urgency|strength)$"),
    hours: int = Query(default=24, ge=1, le=168),
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """Get ranked signals by urgency or strength."""
    service = SignalService(session)

    if by == "urgency":
        signals = await service.rank_by_urgency(hours=hours, limit=limit)
    else:
        signals = await service.rank_by_strength(hours=hours, limit=limit)

    return SignalListResponse(signals=signals, total=len(signals))


@router.get("/categories")
async def get_categories():
    """Get available signal categories."""
    return {"categories": SignalCategory.ALL}
