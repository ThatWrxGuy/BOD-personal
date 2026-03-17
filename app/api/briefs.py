"""BB-APP-001: Briefs API."""

from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.get("/")
async def get_briefs(limit: int = 10):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/latest")
async def get_latest_brief():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.post("/generate")
async def generate_brief():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/{brief_id}")
async def get_brief(brief_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
