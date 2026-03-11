"""Observability API routes."""
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.session import get_db
from app.observability.metrics_service import get_metrics_service
from app.observability.health_monitor import get_health_monitor
from app.models.observability import SystemMetricSnapshot, AlertEvent, MetricDomain
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/observability", tags=["observability"])


# ===================
# Health Endpoints
# ===================

@router.get("/health")
async def get_health(
    session: AsyncSession = Depends(get_db),
):
    """Get system health status."""
    
    health_monitor = await get_health_monitor(session)
    health = await health_monitor.check_all_health()
    
    return health


@router.get("/health/{component}")
async def get_component_health(
    component: str,
    session: AsyncSession = Depends(get_db),
):
    """Get health status for a specific component."""
    
    health_monitor = await get_health_monitor(session)
    health = await health_monitor.check_all_health()
    
    if component not in health.get("components", {}):
        return {"error": f"Component {component} not found"}
    
    return health["components"][component]


# ===================
# Metrics Endpoints
# ===================

@router.get("/metrics")
async def get_all_metrics():
    """Get all system metrics."""
    
    metrics_service = get_metrics_service()
    return metrics_service.get_all_metrics()


@router.get("/metrics/system")
async def get_system_metrics():
    """Get system metrics."""
    
    metrics_service = get_metrics_service()
    return metrics_service.get_domain_metrics(MetricDomain.SYSTEM)


@router.get("/metrics/workflows")
async def get_workflow_metrics():
    """Get workflow metrics."""
    
    metrics_service = get_metrics_service()
    return metrics_service.get_domain_metrics(MetricDomain.WORKFLOW)


@router.get("/metrics/executions")
async def get_execution_metrics():
    """Get execution metrics."""
    
    metrics_service = get_metrics_service()
    return metrics_service.get_domain_metrics(MetricDomain.EXECUTION)


@router.get("/metrics/connectors")
async def get_connector_metrics():
    """Get connector metrics."""
    
    metrics_service = get_metrics_service()
    return metrics_service.get_domain_metrics(MetricDomain.CONNECTOR)


@router.get("/metrics/security")
async def get_security_metrics():
    """Get security metrics."""
    
    metrics_service = get_metrics_service()
    return metrics_service.get_domain_metrics(MetricDomain.SECURITY)


@router.get("/metrics/agents")
async def get_agent_metrics():
    """Get agent metrics."""
    
    metrics_service = get_metrics_service()
    return metrics_service.get_domain_metrics(MetricDomain.AGENT)


@router.get("/metrics/api")
async def get_api_metrics():
    """Get API metrics."""
    
    metrics_service = get_metrics_service()
    return metrics_service.get_domain_metrics(MetricDomain.API)


# ===================
# Alerts Endpoints
# ===================

@router.get("/alerts")
async def list_alerts(
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    limit: int = Query(50, ge=1, le=500),
    session: AsyncSession = Depends(get_db),
):
    """List alert events."""
    
    query = select(AlertEvent).order_by(desc(AlertEvent.created_at)).limit(limit)
    
    if resolved is not None:
        query = query.where(AlertEvent.is_resolved == resolved)
    
    result = await session.execute(query)
    alerts = result.scalars().all()
    
    return {
        "alerts": [
            {
                "id": str(a.id),
                "alert_type": a.alert_type,
                "severity": a.severity,
                "message": a.message,
                "source": a.source,
                "is_resolved": a.is_resolved,
                "created_at": a.created_at.isoformat(),
                "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None,
            }
            for a in alerts
        ]
    }


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Resolve an alert."""
    
    result = await session.execute(
        select(AlertEvent).where(AlertEvent.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        return {"error": "Alert not found"}
    
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    
    await session.commit()
    
    return {"message": "Alert resolved", "alert_id": str(alert_id)}


# ===================
# Traces Endpoints
# ===================

@router.get("/traces/{correlation_id}")
async def get_trace(
    correlation_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Get trace information for a correlation ID."""
    
    from app.models.orchestration import EventRecord, WorkflowInstance
    
    # Get events with this correlation ID
    result = await session.execute(
        select(EventRecord)
        .where(EventRecord.correlation_id == correlation_id)
        .order_by(EventRecord.timestamp)
    )
    events = result.scalars().all()
    
    # Get workflow if any
    result = await session.execute(
        select(WorkflowInstance)
        .where(WorkflowInstance.id == correlation_id)
    )
    workflow = result.scalar_one_or_none()
    
    return {
        "correlation_id": str(correlation_id),
        "workflow": {
            "id": str(workflow.id),
            "name": workflow.workflow_name,
            "status": workflow.status,
            "current_state": workflow.current_state,
        } if workflow else None,
        "events": [
            {
                "event_id": str(e.event_id),
                "event_type": e.event_type,
                "source": e.source,
                "timestamp": e.timestamp.isoformat(),
            }
            for e in events
        ],
    }
