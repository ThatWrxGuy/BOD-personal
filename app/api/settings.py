"""BB-APP-001: Settings API."""

from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.get("/")
async def get_settings():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.put("/")
async def update_settings():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/notifications")
async def get_notification_settings():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.put("/notifications")
async def update_notification_settings():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
