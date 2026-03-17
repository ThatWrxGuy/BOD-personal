"""BB-APP-001: Reviews API."""

from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.get("/")
async def get_reviews(
    review_type: str | None = None,
    limit: int = 10
):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/latest")
async def get_latest_review(review_type: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.post("/start")
async def start_review(review_type: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.post("/{review_id}/complete")
async def complete_review(review_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/{review_id}")
async def get_review(review_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
