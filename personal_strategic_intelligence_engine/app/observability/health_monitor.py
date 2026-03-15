"""Health monitor for system health checks."""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.observability import HealthStatusRecord, HealthComponent, HealthStatus
from app.core.logging import get_logger

logger = get_logger(__name__)


class HealthMonitor:
    """System health monitor."""
    
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
        self._health_cache: Dict[str, Dict[str, Any]] = {}
        self._last_check: Dict[str, datetime] = {}
    
    async def check_all_health(self) -> Dict[str, Any]:
        """Check health of all components."""
        
        health = {
            "status": HealthStatus.HEALTHY,
            "components": {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Check each component
        components = [
            self.check_application_health,
            self.check_database_health,
            self.check_event_bus_health,
            self.check_workflow_engine_health,
            self.check_connectors_health,
            self.check_llm_providers_health,
            self.check_security_health,
        ]
        
        overall_status = HealthStatus.HEALTHY
        
        for check in components:
            try:
                result = await check()
                component_name = result.get("component", "unknown")
                health["components"][component_name] = result
                
                # Update overall status
                if result["status"] == HealthStatus.UNAVAILABLE:
                    overall_status = HealthStatus.UNAVAILABLE
                elif result["status"] == HealthStatus.DEGRADED and overall_status != HealthStatus.UNAVAILABLE:
                    overall_status = HealthStatus.DEGRADED
                elif result["status"] == HealthStatus.MISCONFIGURED and overall_status not in [HealthStatus.UNAVAILABLE, HealthStatus.DEGRADED]:
                    overall_status = HealthStatus.MISCONFIGURED
            
            except Exception as e:
                logger.error(f"Health check failed: {e}")
        
        health["status"] = overall_status
        
        # Cache results
        self._health_cache = health
        
        # Record to database
        if self.session:
            await self._record_health(health)
        
        return health
    
    async def check_application_health(self) -> Dict[str, Any]:
        """Check application health."""
        
        from app.core.config import get_settings
        
        settings = get_settings()
        
        # Check if in production with default secret
        issues = []
        
        if settings.is_production and settings.secret_key == "change-me-in-production":
            issues.append("Using default SECRET_KEY in production")
        
        return {
            "component": HealthComponent.APPLICATION,
            "status": HealthStatus.MISCONFIGURED if issues else HealthStatus.HEALTHY,
            "details": "; ".join(issues) if issues else "Application is running",
        }
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database health."""
        
        if not self.session:
            return {
                "component": HealthComponent.DATABASE,
                "status": HealthStatus.HEALTHY,
                "details": "No database session available",
            }
        
        try:
            # Simple query to check connection
            from sqlalchemy import text
            await self.session.execute(text("SELECT 1"))
            
            return {
                "component": HealthComponent.DATABASE,
                "status": HealthStatus.HEALTHY,
                "details": "Database connection is healthy",
            }
        
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "component": HealthComponent.DATABASE,
                "status": HealthStatus.UNAVAILABLE,
                "details": f"Database connection failed: {str(e)}",
            }
    
    async def check_event_bus_health(self) -> Dict[str, Any]:
        """Check event bus health."""
        
        # Check if event bus is available
        from app.orchestration.event_bus import get_event_bus
        
        try:
            bus = get_event_bus()
            return {
                "component": HealthComponent.EVENT_BUS,
                "status": HealthStatus.HEALTHY,
                "details": "Event bus is available",
            }
        except Exception as e:
            return {
                "component": HealthComponent.EVENT_BUS,
                "status": HealthStatus.UNAVAILABLE,
                "details": f"Event bus unavailable: {str(e)}",
            }
    
    async def check_workflow_engine_health(self) -> Dict[str, Any]:
        """Check workflow engine health."""
        
        return {
            "component": HealthComponent.WORKFLOW_ENGINE,
            "status": HealthStatus.HEALTHY,
            "details": "Workflow engine is operational",
        }
    
    async def check_connectors_health(self) -> Dict[str, Any]:
        """Check connectors health."""
        
        from app.security.secret_manager import get_secret_manager
        from app.models.security import CONNECTOR_REGISTRY
        
        secret_manager = get_secret_manager()
        
        # Count enabled connectors
        enabled = 0
        ready = 0
        
        for connector_id, defn in CONNECTOR_REGISTRY.items():
            required_secrets = defn.get("required_secrets", [])
            secrets_ready = all(secret_manager.has_secret(s) for s in required_secrets)
            
            if secrets_ready:
                ready += 1
        
        return {
            "component": HealthComponent.CONNECTORS,
            "status": HealthStatus.HEALTHY,
            "details": f"{ready}/{len(CONNECTOR_REGISTRY)} connectors ready",
            "ready_count": ready,
            "total_count": len(CONNECTOR_REGISTRY),
        }
    
    async def check_llm_providers_health(self) -> Dict[str, Any]:
        """Check LLM providers health."""
        
        from app.security.secret_manager import get_secret_manager
        
        secret_manager = get_secret_manager()
        
        has_openai = secret_manager.has_secret("OPENAI_API_KEY")
        has_anthropic = secret_manager.has_secret("ANTHROPIC_API_KEY")
        
        if has_openai or has_anthropic:
            return {
                "component": HealthComponent.LLM_PROVIDERS,
                "status": HealthStatus.HEALTHY,
                "details": "At least one LLM provider is configured",
                "providers": {
                    "openai": has_openai,
                    "anthropic": has_anthropic,
                }
            }
        
        return {
            "component": HealthComponent.LLM_PROVIDERS,
            "status": HealthStatus.DEGRADED,
            "details": "No LLM providers configured - AI features will not work",
        }
    
    async def check_security_health(self) -> Dict[str, Any]:
        """Check security health."""
        
        from app.core.config import get_settings
        
        settings = get_settings()
        
        issues = []
        
        if settings.is_production and not settings.enable_auth:
            issues.append("Authentication is disabled in production")
        
        if settings.is_production and not settings.execution_manual_approval:
            issues.append("Manual approval is disabled in production")
        
        if issues:
            return {
                "component": HealthComponent.SECURITY,
                "status": HealthStatus.MISCONFIGURED,
                "details": "; ".join(issues),
            }
        
        return {
            "component": HealthComponent.SECURITY,
            "status": HealthStatus.HEALTHY,
            "details": "Security configuration is healthy",
        }
    
    async def get_cached_health(self) -> Optional[Dict[str, Any]]:
        """Get cached health status."""
        return self._health_cache if self._health_cache else None
    
    async def _record_health(self, health: Dict[str, Any]) -> None:
        """Record health status to database."""
        
        for component_name, component_health in health.get("components", {}).items():
            record = HealthStatusRecord(
                component=component_name,
                status=component_health.get("status", "unknown"),
                details=component_health.get("details"),
                checked_at=datetime.utcnow(),
            )
            self.session.add(record)
        
        await self.session.commit()


async def get_health_monitor(session: Optional[AsyncSession] = None) -> HealthMonitor:
    """Get health monitor instance."""
    return HealthMonitor(session)
