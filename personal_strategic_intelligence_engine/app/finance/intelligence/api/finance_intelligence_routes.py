"""Finance Intelligence API routes."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.finance.services.finance_state_service import FinanceStateService
from app.finance.intelligence.services.finance_intelligence_service import FinanceIntelligenceService


router = APIRouter(prefix="/finance/intelligence", tags=["finance-intelligence"])


def get_intelligence_service(session: AsyncSession = Depends(get_db)) -> FinanceIntelligenceService:
    """Get finance intelligence service."""
    finance_service = FinanceStateService(session)
    return FinanceIntelligenceService(finance_service)


@router.get("/signals")
async def get_financial_signals(
    profile_id: int = Query(..., description="Profile ID"),
    session: AsyncSession = Depends(get_db),
):
    """
    Get financial signals for a profile.
    
    Returns detected risks and opportunities as normalized signals.
    """
    service = get_intelligence_service(session)
    signals = await service.generate_financial_signals(profile_id)
    
    return {
        "signals": [signal.to_dict() for signal in signals],
        "count": len(signals),
    }


@router.get("/risks")
async def get_financial_risks(
    profile_id: int = Query(..., description="Profile ID"),
    session: AsyncSession = Depends(get_db),
):
    """
    Get detected financial risks for a profile.
    """
    service = get_intelligence_service(session)
    risks = await service.get_financial_risks(profile_id)
    
    return {
        "risks": [risk.to_dict() for risk in risks],
        "count": len(risks),
    }


@router.get("/opportunities")
async def get_financial_opportunities(
    profile_id: int = Query(..., description="Profile ID"),
    session: AsyncSession = Depends(get_db),
):
    """
    Get detected financial opportunities for a profile.
    """
    service = get_intelligence_service(session)
    opportunities = await service.get_financial_opportunities(profile_id)
    
    return {
        "opportunities": [opp.to_dict() for opp in opportunities],
        "count": len(opportunities),
    }


@router.get("/recommendations")
async def get_financial_recommendations(
    profile_id: int = Query(..., description="Profile ID"),
    session: AsyncSession = Depends(get_db),
):
    """
    Get financial recommendations for a profile.
    
    Returns actionable recommendations with confidence scores.
    """
    service = get_intelligence_service(session)
    recommendations = await service.generate_financial_recommendations(profile_id)
    
    return {
        "recommendations": [rec.to_dict() for rec in recommendations],
        "count": len(recommendations),
    }
