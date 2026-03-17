"""BB-APP-001: Signals API."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()


class SignalRequest(BaseModel):
    content: str
    signal_type: str = "event"
    timestamp: Optional[datetime] = None


@router.get("/")
async def get_signals(
    domain: Optional[str] = None,
    limit: int = 100
):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.post("/")
async def create_signal(request: SignalRequest):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/{signal_id}")
async def get_signal(signal_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.delete("/{signal_id}")
async def delete_signal(signal_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
