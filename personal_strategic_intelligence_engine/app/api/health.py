"""Health check and configuration readiness API routes."""
from fastapi import APIRouter, status
from pydantic import BaseModel
from app.core.config_check import get_readiness_report
from app.core.config import get_settings

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


class ConfigReadinessResponse(BaseModel):
    """Configuration readiness response."""
    
    overall: dict
    core: dict
    database: dict
    llm: dict
    workers: dict
    connectors: dict
    execution: dict
    debate: dict
    learning: dict
    signals: dict
    safety: dict


@router.get("", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
    )


@router.get("/config-readiness", response_model=ConfigReadinessResponse)
async def config_readiness():
    """Get configuration readiness report."""
    return ConfigReadinessResponse(**get_readiness_report())
