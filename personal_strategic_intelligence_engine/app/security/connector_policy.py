"""Connector policy engine."""
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.security import ConnectorConfiguration, ConnectorAuditLog, CONNECTOR_REGISTRY
from app.models.identity import User
from app.security.secret_manager import get_secret_manager
from app.core.logging import get_logger

logger = get_logger(__name__)


class ConnectorPolicyEngine:
    """Enforces connector security policies."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.secret_manager = get_secret_manager()
    
    async def can_use_connector(
        self,
        user: Optional[User],
        connector_id: str,
        action: str = "use",
    ) -> Dict[str, Any]:
        """Check if a user can use a connector."""
        
        # Check if connector exists in registry
        if connector_id not in CONNECTOR_REGISTRY:
            return {
                "allowed": False,
                "reason": f"Unknown connector: {connector_id}",
                "code": "UNKNOWN_CONNECTOR",
            }
        
        connector_def = CONNECTOR_REGISTRY[connector_id]
        
        # Check if connector is enabled
        config = await self._get_connector_config(connector_id)
        
        if not config or not config.is_enabled:
            return {
                "allowed": False,
                "reason": "Connector is not enabled",
                "code": "CONNECTOR_DISABLED",
            }
        
        # Check if secrets are present
        required_secrets = connector_def.get("required_secrets", [])
        missing_secrets = []
        
        for secret_name in required_secrets:
            if not self.secret_manager.has_secret(secret_name):
                missing_secrets.append(secret_name)
        
        if missing_secrets:
            return {
                "allowed": False,
                "reason": f"Missing required secrets: {', '.join(missing_secrets)}",
                "code": "MISSING_SECRETS",
                "missing_secrets": missing_secrets,
            }
        
        # Check if validated
        if not config.is_validated:
            return {
                "allowed": False,
                "reason": "Connector has not been validated",
                "code": "NOT_VALIDATED",
            }
        
        # Check user permissions
        if user:
            from app.identity.rbac_engine import RBACEngine
            rbac = RBACEngine(self.session)
            
            required_permissions = connector_def.get("required_permissions", [])
            
            for permission in required_permissions:
                if not await rbac.check_permission(user, permission):
                    return {
                        "allowed": False,
                        "reason": f"Missing required permission: {permission}",
                        "code": "PERMISSION_DENIED",
                        "required_permission": permission,
                    }
        
        return {
            "allowed": True,
            "reason": "All checks passed",
            "code": "ALLOWED",
        }
    
    async def _get_connector_config(
        self,
        connector_id: str,
    ) -> Optional[ConnectorConfiguration]:
        """Get connector configuration from database."""
        
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(ConnectorConfiguration).where(
                ConnectorConfiguration.connector_id == connector_id
            )
        )
        
        return result.scalar_one_or_none()
    
    async def validate_connector(
        self,
        connector_id: str,
    ) -> Dict[str, Any]:
        """Validate a connector's configuration."""
        
        if connector_id not in CONNECTOR_REGISTRY:
            return {
                "valid": False,
                "errors": [f"Unknown connector: {connector_id}"],
            }
        
        connector_def = CONNECTOR_REGISTRY[connector_id]
        required_secrets = connector_def.get("required_secrets", [])
        
        errors = []
        
        # Check each required secret
        for secret_name in required_secrets:
            if not self.secret_manager.has_secret(secret_name):
                errors.append(f"Missing required secret: {secret_name}")
        
        # Update or create configuration
        config = await self._get_connector_config(connector_id)
        
        if not config:
            config = ConnectorConfiguration(
                connector_id=connector_id,
                connector_name=connector_def.get("name", connector_id),
                domain=connector_def.get("domain", "unknown"),
                risk_level=connector_def.get("risk_level", "medium"),
                description=connector_def.get("description"),
            )
            self.session.add(config)
        
        # Update validation status
        if errors:
            config.is_validated = False
            config.validation_errors = errors
        else:
            config.is_validated = True
            config.validation_errors = None
        
        from datetime import datetime
        config.last_validated_at = datetime.utcnow()
        
        await self.session.commit()
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "connector_id": connector_id,
        }
    
    async def enable_connector(
        self,
        connector_id: str,
        user_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, Any]:
        """Enable a connector."""
        
        # Validate first
        validation = await self.validate_connector(connector_id)
        
        if not validation["valid"]:
            await self._log_audit(
                user_id=user_id,
                connector_id=connector_id,
                action="enable_failed",
                status="failure",
                reason="Validation failed: " + "; ".join(validation["errors"]),
            )
            
            return {
                "enabled": False,
                "reason": "Validation failed",
                "errors": validation["errors"],
            }
        
        # Enable the connector
        config = await self._get_connector_config(connector_id)
        
        if not config:
            return {"enabled": False, "reason": "Connector not found"}
        
        config.is_enabled = True
        await self.session.commit()
        
        await self._log_audit(
            user_id=user_id,
            connector_id=connector_id,
            action="enabled",
            status="success",
        )
        
        return {"enabled": True, "reason": "Connector enabled"}
    
    async def disable_connector(
        self,
        connector_id: str,
        user_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, Any]:
        """Disable a connector."""
        
        config = await self._get_connector_config(connector_id)
        
        if not config:
            return {"disabled": False, "reason": "Connector not found"}
        
        config.is_enabled = False
        await self.session.commit()
        
        await self._log_audit(
            user_id=user_id,
            connector_id=connector_id,
            action="disabled",
            status="success",
        )
        
        return {"disabled": True, "reason": "Connector disabled"}
    
    async def _log_audit(
        self,
        user_id: Optional[uuid.UUID],
        connector_id: str,
        action: str,
        status: str,
        reason: Optional[str] = None,
    ) -> None:
        """Log connector audit event."""
        
        log = ConnectorAuditLog(
            user_id=user_id,
            connector_id=connector_id,
            action=action,
            status=status,
            reason=reason,
        )
        
        self.session.add(log)
        await self.session.commit()


async def get_connector_policy_engine(session: AsyncSession) -> ConnectorPolicyEngine:
    """Get connector policy engine instance."""
    return ConnectorPolicyEngine(session)
