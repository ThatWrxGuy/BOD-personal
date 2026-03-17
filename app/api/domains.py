"""BB-APP-002: Domains API."""

from typing import List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.application import domains_service
from app.read_models import DomainOverviewReadModel, DomainDetailReadModel

router = APIRouter()


@router.get("/", response_model=List[DomainOverviewReadModel])
async def get_domains(user_id: str = "user-1"):
    """Get list of all domains."""
    return await domains_service.list_domains(user_id)


@router.get("/{domain}", response_model=DomainDetailReadModel)
async def get_domain(domain: str, user_id: str = "user-1"):
    """Get detailed domain information."""
    domain_detail = await domains_service.get_domain(domain, user_id)
    if not domain_detail:
        raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found")
    return domain_detail


@router.get("/{domain}/state")
async def get_domain_state(domain: str, user_id: str = "user-1"):
    """Get domain state."""
    domain_detail = await domains_service.get_domain(domain, user_id)
    if not domain_detail:
        raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found")
    return {
        "domain_id": domain_detail.domain_id,
        "score": domain_detail.score,
        "trend": domain_detail.trend,
        "status": domain_detail.status,
    }


@router.get("/{domain}/signals")
async def get_domain_signals(domain: str, user_id: str = "user-1"):
    """Get domain signals."""
    domain_detail = await domains_service.get_domain(domain, user_id)
    if not domain_detail:
        raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found")
    return domain_detail.active_signals


@router.get("/{domain}/recommendations")
async def get_domain_recommendations(domain: str, user_id: str = "user-1"):
    """Get domain recommendations."""
    domain_detail = await domains_service.get_domain(domain, user_id)
    if not domain_detail:
        raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found")
    return domain_detail.recommendations
