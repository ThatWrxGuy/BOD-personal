"""Detection API routes."""
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.session import get_db
from app.detection.detection_engine import get_detection_engine
from app.detection.detection_types import DetectedEvent
from app.observability import increment
from app.observability.metrics_service import MetricDomain

router = APIRouter(prefix="/detection", tags=["detection"])


@router.get("/events")
async def list_detection_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db),
):
    """List detection events."""
    
    engine = await get_detection_engine(session)
    events = await engine.get_detection_events(event_type, domain, severity, status, limit)
    
    return {
        "events": [
            {
                "id": str(e.id),
                "event_type": e.event_type,
                "domain": e.domain,
                "severity": e.severity,
                "status": e.status,
                "title": e.title,
                "description": e.description,
                "confidence_score": e.confidence_score,
                "detected_at": e.detected_at.isoformat() if e.detected_at else None,
                "resolved_at": e.resolved_at.isoformat() if e.resolved_at else None,
            }
            for e in events
        ]
    }


@router.get("/opportunities")
async def list_opportunities(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """List detected opportunities."""
    
    engine = await get_detection_engine(session)
    events = await engine.get_detection_events(event_type="opportunity", limit=limit)
    
    return {
        "opportunities": [
            {
                "id": str(e.id),
                "domain": e.domain,
                "title": e.title,
                "description": e.description,
                "confidence_score": e.confidence_score,
                "severity": e.severity,
                "detected_at": e.detected_at.isoformat() if e.detected_at else None,
            }
            for e in events
        ]
    }


@router.get("/risks")
async def list_risks(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """List detected risks."""
    
    engine = await get_detection_engine(session)
    events = await engine.get_detection_events(event_type="risk", severity=severity, limit=limit)
    
    return {
        "risks": [
            {
                "id": str(e.id),
                "domain": e.domain,
                "title": e.title,
                "description": e.description,
                "confidence_score": e.confidence_score,
                "severity": e.severity,
                "detected_at": e.detected_at.isoformat() if e.detected_at else None,
            }
            for e in events
        ]
    }


@router.get("/alerts")
async def list_alerts(
    status: Optional[str] = Query("active", description="Filter by status"),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """List active detection alerts."""
    
    engine = await get_detection_engine(session)
    
    # Get high/critical severity events
    events = await engine.get_detection_events(
        severity="high,critical",
        status=status,
        limit=limit,
    )
    
    return {
        "alerts": [
            {
                "id": str(e.id),
                "event_type": e.event_type,
                "domain": e.domain,
                "severity": e.severity,
                "title": e.title,
                "description": e.description,
                "detected_at": e.detected_at.isoformat() if e.detected_at else None,
            }
            for e in events
        ]
    }


@router.get("/statistics")
async def get_detection_statistics(
    session: AsyncSession = Depends(get_db),
):
    """Get detection statistics."""
    
    engine = await get_detection_engine(session)
    stats = await engine.get_detection_statistics()
    
    return stats


@router.post("/run-analysis")
async def run_detection_analysis(
    domains: Optional[List[str]] = Query(None, description="Domains to analyze"),
    time_range_days: int = Query(30, ge=1, le=365, description="Time range for analysis"),
    session: AsyncSession = Depends(get_db),
):
    """Run detection analysis across domains."""
    
    engine = await get_detection_engine(session)
    
    try:
        events = await engine.run_full_analysis(domains, time_range_days)
        
        increment("detection_analysis_run", domain=MetricDomain.SYSTEM)
        
        return {
            "message": "Detection analysis completed",
            "events_detected": len(events) if events else 0,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events/{event_id}/resolve")
async def resolve_detection_event(
    event_id: uuid.UUID,
    resolution: str = Query("addressed", description="Resolution status"),
    session: AsyncSession = Depends(get_db),
):
    """Resolve a detection event."""
    
    engine = await get_detection_engine(session)
    
    try:
        event = await engine.resolve_event(event_id, resolution)
        
        return {
            "message": "Event resolved",
            "id": str(event.id),
            "status": event.status,
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
