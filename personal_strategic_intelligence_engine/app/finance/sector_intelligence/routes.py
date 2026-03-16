"""Sector Intelligence Routes - BB-FIN-015"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.finance.sector_intelligence.sector_intelligence_service import (
    get_sector_intelligence_service,
    SectorIntelligenceService,
)
from app.finance.sector_intelligence.sector_models import (
    SectorLeadershipRanking,
    SectorIntelligenceReport,
    SectorPolicyRecommendation,
    RotationEvent,
)

router = APIRouter(prefix="/finance/sector-intelligence", tags=["sector-intelligence"])


# Request models
class AnalyzeRequest(BaseModel):
    """Request to run sector intelligence analysis."""
    market_regime: Optional[str] = None
    include_recommendations: bool = True


class RegimeContextRequest(BaseModel):
    """Set market regime context."""
    regime: str
    risk_posture: str


# Endpoints

@router.get("/status", response_model=dict)
async def get_status(
    service: SectorIntelligenceService = Depends(get_sector_intelligence_service),
):
    """Get sector intelligence system status."""
    return {
        "status": "operational",
        "version": "1.0.0",
        "module": "BB-FIN-015",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/rankings", response_model=SectorLeadershipRanking)
async def get_rankings(
    service: SectorIntelligenceService = Depends(get_sector_intelligence_service),
):
    """Get current sector leadership rankings."""
    return service.get_current_rankings()


@router.get("/rotation", response_model=Optional[RotationEvent])
async def get_rotation(
    service: SectorIntelligenceService = Depends(get_sector_intelligence_service),
):
    """Get current rotation status."""
    return service.get_rotation_status()


@router.get("/breadth", response_model=dict)
async def get_breadth(
    service: SectorIntelligenceService = Depends(get_sector_intelligence_service),
):
    """Get sector breadth analysis."""
    report = service.analyze()
    return {
        "timestamp": report.timestamp.isoformat(),
        "breadth_profiles": [
            {
                "symbol": b.symbol,
                "advancing": b.advancing_stocks,
                "declining": b.declining_stocks,
                "participation_pct": b.participation_pct,
                "concentration_risk": b.concentration_risk,
            }
            for b in report.breadth_profiles
        ],
    }


@router.get("/flows", response_model=dict)
async def get_flows(
    service: SectorIntelligenceService = Depends(get_sector_intelligence_service),
):
    """Get capital flow signals."""
    report = service.analyze()
    return {
        "timestamp": report.timestamp.isoformat(),
        "flows": [
            {
                "symbol": f.symbol,
                "direction": f.direction.value,
                "strength": f.strength,
                "description": f.description,
            }
            for f in report.capital_flows
        ],
    }


@router.get("/recommendations", response_model=dict)
async def get_recommendations(
    regime: Optional[str] = None,
    service: SectorIntelligenceService = Depends(get_sector_intelligence_service),
):
    """Get sector allocation recommendations."""
    recommendations = service.get_recommendations(regime)
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "market_regime": regime or service._market_regime or "NEUTRAL_MIXED",
        "recommendations": [
            {
                "symbol": r.symbol,
                "name": r.name,
                "weight": r.weight,
                "adjustment": r.adjustment,
                "rationale": r.rationale,
                "risk_level": r.risk_level,
                "priority": r.priority,
            }
            for r in recommendations
        ],
    }


@router.get("/report", response_model=SectorIntelligenceReport)
async def get_report(
    service: SectorIntelligenceService = Depends(get_sector_intelligence_service),
):
    """Get complete sector intelligence report."""
    return service.analyze()


@router.post("/analyze", response_model=SectorIntelligenceReport)
async def analyze(
    request: AnalyzeRequest,
    service: SectorIntelligenceService = Depends(get_sector_intelligence_service),
):
    """Run sector intelligence analysis."""
    
    # Set regime context if provided
    if request.market_regime:
        service.set_market_context(request.market_regime, "neutral")
    
    return service.analyze()


@router.post("/context", response_model=dict)
async def set_context(
    request: RegimeContextRequest,
    service: SectorIntelligenceService = Depends(get_sector_intelligence_service),
):
    """Set market regime context for sector analysis."""
    service.set_market_context(request.regime, request.risk_posture)
    return {
        "status": "updated",
        "regime": request.regime,
        "risk_posture": request.risk_posture,
    }


# Demo endpoint for testing
@router.post("/demo/analyze", response_model=dict)
async def demo_analyze(
    service: SectorIntelligenceService = Depends(get_sector_intelligence_service),
):
    """Run demo analysis with sample data."""
    report = service.analyze()
    return {
        "status": "success",
        "leader": report.leadership.composite[0].name if report.leadership.composite else None,
        "leader_symbol": report.leadership.composite[0].symbol if report.leadership.composite else None,
        "rotation_detected": report.rotation_detected,
        "rotation": report.rotation.description if report.rotation else None,
        "recommendations": [
            {
                "symbol": r.symbol,
                "adjustment": r.adjustment,
                "weight": r.weight,
            }
            for r in report.recommendations[:5]
        ],
        "timestamp": report.timestamp.isoformat(),
    }
