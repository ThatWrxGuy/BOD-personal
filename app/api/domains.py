"""BB-APP-001: Domains API."""

from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.get("/")
async def get_domains():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/{domain}")
async def get_domain(domain: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/{domain}/state")
async def get_domain_state(domain: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/{domain}/signals")
async def get_domain_signals(domain: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/{domain}/recommendations")
async def get_domain_recommendations(domain: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
