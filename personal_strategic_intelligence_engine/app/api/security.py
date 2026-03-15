"""Security and connector API routes."""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.session import get_db
from app.models.security import ConnectorAuditLog, ConnectorConfiguration, CONNECTOR_REGISTRY
from app.security.secret_manager import get_secret_manager
from app.security.connector_policy import get_connector_policy_engine
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/security", tags=["security"])


# ===================
# Connector Endpoints
# ===================

@router.get("/connectors")
async def list_connectors(session: AsyncSession = Depends(get_db)):
    """List all available connectors and their status."""
    
    secret_manager = get_secret_manager()
    policy_engine = await get_connector_policy_engine(session)
    
    connectors = []
    
    for connector_id, defn in CONNECTOR_REGISTRY.items():
        # Get config from DB
        result = await session.execute(
            select(ConnectorConfiguration).where(
                ConnectorConfiguration.connector_id == connector_id
            )
        )
        config = result.scalar_one_or_none()
        
        # Check secrets
        required_secrets = defn.get("required_secrets", [])
        secrets_status = {}
        for secret in required_secrets:
            secrets_status[secret] = secret_manager.has_secret(secret)
        
        # Determine readiness
        secrets_ready = all(secrets_status.values())
        is_ready = secrets_ready and config and config.is_enabled and config.is_validated
        
        connectors.append({
            "connector_id": connector_id,
            "name": defn.get("name"),
            "domain": defn.get("domain"),
            "risk_level": defn.get("risk_level"),
            "description": defn.get("description"),
            "is_enabled": config.is_enabled if config else False,
            "is_validated": config.is_validated if config else False,
            "is_ready": is_ready,
            "secrets_status": secrets_status,
            "required_permissions": defn.get("required_permissions", []),
        })
    
    return {"connectors": connectors}


@router.get("/connectors/{connector_id}")
async def get_connector(
    connector_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Get connector details."""
    
    if connector_id not in CONNECTOR_REGISTRY:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    defn = CONNECTOR_REGISTRY[connector_id]
    secret_manager = get_secret_manager()
    
    # Get config
    result = await session.execute(
        select(ConnectorConfiguration).where(
            ConnectorConfiguration.connector_id == connector_id
        )
    )
    config = result.scalar_one_or_none()
    
    # Check secrets
    required_secrets = defn.get("required_secrets", [])
    secrets_status = {}
    for secret in required_secrets:
        secrets_status[secret] = secret_manager.has_secret(secret)
    
    return {
        "connector_id": connector_id,
        "name": defn.get("name"),
        "domain": defn.get("domain"),
        "risk_level": defn.get("risk_level"),
        "description": defn.get("description"),
        "is_enabled": config.is_enabled if config else False,
        "is_validated": config.is_validated if config else False,
        "is_ready": (config.is_enabled and config.is_validated) if config else False,
        "secrets_status": secrets_status,
        "required_permissions": defn.get("required_permissions", []),
        "last_validated": config.last_validated_at.isoformat() if config and config.last_validated_at else None,
        "validation_errors": config.validation_errors if config else None,
    }


@router.get("/connectors/{connector_id}/readiness")
async def get_connector_readiness(
    connector_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Get connector readiness status."""
    
    if connector_id not in CONNECTOR_REGISTRY:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    policy_engine = await get_connector_policy_engine(session)
    validation = await policy_engine.validate_connector(connector_id)
    
    return {
        "connector_id": connector_id,
        "ready": validation["valid"],
        "errors": validation["errors"],
    }


@router.post("/connectors/{connector_id}/validate")
async def validate_connector(
    connector_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Validate a connector's configuration."""
    
    if connector_id not in CONNECTOR_REGISTRY:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    policy_engine = await get_connector_policy_engine(session)
    result = await policy_engine.validate_connector(connector_id)
    
    return result


@router.post("/connectors/{connector_id}/enable")
async def enable_connector(
    connector_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Enable a connector."""
    
    if connector_id not in CONNECTOR_REGISTRY:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    policy_engine = await get_connector_policy_engine(session)
    result = await policy_engine.enable_connector(connector_id)
    
    if not result["enabled"]:
        raise HTTPException(
            status_code=400,
            detail=result.get("reason", "Failed to enable connector")
        )
    
    return result


@router.post("/connectors/{connector_id}/disable")
async def disable_connector(
    connector_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Disable a connector."""
    
    if connector_id not in CONNECTOR_REGISTRY:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    policy_engine = await get_connector_policy_engine(session)
    result = await policy_engine.disable_connector(connector_id)
    
    return result


# ===================
# Audit Endpoints
# ===================

@router.get("/audit/connectors")
async def list_connector_audit_logs(
    connector_id: Optional[str] = None,
    limit: int = 50,
    session: AsyncSession = Depends(get_db),
):
    """List connector audit logs."""
    
    query = select(ConnectorAuditLog).order_by(desc(ConnectorAuditLog.created_at)).limit(limit)
    
    if connector_id:
        query = query.where(ConnectorAuditLog.connector_id == connector_id)
    
    result = await session.execute(query)
    logs = result.scalars().all()
    
    return {
        "logs": [
            {
                "id": str(l.id),
                "connector_id": l.connector_id,
                "action": l.action,
                "status": l.status,
                "reason": l.reason,
                "user_id": str(l.user_id) if l.user_id else None,
                "timestamp": l.created_at.isoformat(),
            }
            for l in logs
        ]
    }


# ===================
# Secrets Readiness
# ===================

@router.get("/secrets/readiness")
async def get_secrets_readiness():
    """Get secrets readiness status."""
    
    secret_manager = get_secret_manager()
    
    # Group secrets by domain
    readiness = {
        "llm": {
            "openai": secret_manager.has_secret("OPENAI_API_KEY"),
            "anthropic": secret_manager.has_secret("ANTHROPIC_API_KEY"),
        },
        "data": {
            "alphavantage": secret_manager.has_secret("ALPHAVANTAGE_API_KEY"),
            "polygon": secret_manager.has_secret("POLYGON_API_KEY"),
            "fred": secret_manager.has_secret("FRED_API_KEY"),
        },
        "email": {
            "google": secret_manager.has_secret("GOOGLE_CLIENT_ID"),
        },
        "calendar": {
            "google": secret_manager.has_secret("GOOGLE_CALENDAR_CLIENT_ID"),
        },
        "tasks": {
            "todoist": secret_manager.has_secret("TODOIST_API_TOKEN"),
            "notion": secret_manager.has_secret("NOTION_API_KEY"),
        },
        "financial": {
            "schwab": secret_manager.has_secret("SCHWAB_CLIENT_ID"),
            "ib": secret_manager.has_secret("INTERACTIVE_BROKERS_HOST"),
            "coinbase": secret_manager.has_secret("COINBASE_API_KEY"),
        },
    }
    
    # Determine overall readiness
    has_llm = readiness["llm"]["openai"] or readiness["llm"]["anthropic"]
    
    return {
        "secrets_ready": has_llm,
        "by_domain": readiness,
    }
