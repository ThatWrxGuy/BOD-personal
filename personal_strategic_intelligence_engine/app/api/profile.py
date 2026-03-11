"""Profile API routes."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.profile import (
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse,
)
from app.memory.profile_memory import ProfileMemory
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/profile", tags=["profile"])


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    session: AsyncSession = Depends(get_db),
):
    """Create a new user profile."""
    memory = ProfileMemory(session)
    try:
        profile = await memory.create(profile_data)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=ProfileResponse)
async def get_profile(
    profile_id: Optional[int] = None,
    session: AsyncSession = Depends(get_db),
):
    """Get the user profile."""
    memory = ProfileMemory(session)
    profile = await memory.get(profile_id)
    
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    
    return profile


@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: int,
    profile_data: ProfileUpdate,
    session: AsyncSession = Depends(get_db),
):
    """Update an existing profile."""
    memory = ProfileMemory(session)
    profile = await memory.update(profile_id, profile_data)
    
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    
    return profile
