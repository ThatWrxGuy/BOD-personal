"""BB-APP-001: Users API."""

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter()


@router.get("/{user_id}")
async def get_user(user_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/{user_id}/profile")
async def get_profile(user_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.put("/{user_id}/profile")
async def update_profile(user_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/{user_id}/goals")
async def get_goals(user_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.post("/{user_id}/goals")
async def create_goal(user_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
