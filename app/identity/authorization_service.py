"""
BB-APP-004: Authorization Service

Permission and authorization management.
Per BB-APP-004 Section 7-9 - Permission System.
"""

from typing import Optional
from app.identity.models import (
    Permission,
    ActorContext,
    ROLE_PERMISSIONS,
    Role,
)
from app.audit import audit_log_service


class AuthorizationService:
    """Authorization and permission service."""
    
    def require_permission(
        self,
        actor: ActorContext,
        permission: Permission,
    ) -> bool:
        """
        Require a specific permission.
        Raises PermissionError if not authorized.
        """
        if not actor.has_permission(permission):
            audit_log_service.log_event(
                event_type="permission_denied",
                entity_type="authorization",
                entity_id="",
                actor=actor.user_id,
                reason=f"Missing permission: {permission.value}",
                metadata={
                    "required_permission": permission.value,
                    "user_permissions": [p.value for p in actor.permissions],
                }
            )
            raise PermissionError(
                f"Permission denied: {permission.value} required"
            )
        return True
    
    def require_any_permission(
        self,
        actor: ActorContext,
        permissions: list[Permission],
    ) -> bool:
        """
        Require any of the specified permissions.
        """
        if not actor.has_any_permission(permissions):
            audit_log_service.log_event(
                event_type="permission_denied",
                entity_type="authorization",
                entity_id="",
                actor=actor.user_id,
                reason="Missing any required permission",
                metadata={
                    "required_permissions": [p.value for p in permissions],
                }
            )
            raise PermissionError(
                f"Permission denied: one of {[p.value for p in permissions]} required"
            )
        return True
    
    def require_all_permissions(
        self,
        actor: ActorContext,
        permissions: list[Permission],
    ) -> bool:
        """
        Require all of the specified permissions.
        """
        if not actor.has_all_permissions(permissions):
            audit_log_service.log_event(
                event_type="permission_denied",
                entity_type="authorization",
                entity_id="",
                actor=actor.user_id,
                reason="Missing required permissions",
                metadata={
                    "required_permissions": [p.value for p in permissions],
                }
            )
            raise PermissionError(
                f"Permission denied: all of {[p.value for p in permissions]} required"
            )
        return True
    
    def check_permission(
        self,
        actor: ActorContext,
        permission: Permission,
    ) -> bool:
        """
        Check if actor has permission (non-raising).
        """
        return actor.has_permission(permission)
    
    def check_role(
        self,
        actor: ActorContext,
        role: Role,
    ) -> bool:
        """
        Check if actor has specific role.
        """
        return actor.role == role
    
    def require_role(
        self,
        actor: ActorContext,
        role: Role,
    ) -> bool:
        """
        Require a specific role.
        """
        if actor.role != role:
            audit_log_service.log_event(
                event_type="role_denied",
                entity_type="authorization",
                entity_id="",
                actor=actor.user_id,
                reason=f"Required role: {role.value}",
                metadata={
                    "required_role": role.value,
                    "current_role": actor.role.value,
                }
            )
            raise PermissionError(
                f"Role required: {role.value}"
            )
        return True
    
    def require_minimum_role(
        self,
        actor: ActorContext,
        min_role: Role,
    ) -> bool:
        """
        Require minimum role level.
        """
        role_hierarchy = {
            Role.VIEWER: 1,
            Role.OPERATOR: 2,
            Role.STRATEGIST: 3,
            Role.ADMIN: 4,
            Role.OWNER: 5,
        }
        
        if role_hierarchy.get(actor.role, 0) < role_hierarchy.get(min_role, 0):
            raise PermissionError(
                f"Minimum role required: {min_role.value}"
            )
        return True
    
    def get_effective_permissions(
        self,
        role: Role,
    ) -> list[Permission]:
        """
        Get effective permissions for a role.
        """
        return ROLE_PERMISSIONS.get(role, [])


# Decorator for permission enforcement
def require_permission(permission: Permission):
    """Decorator to require permission on a function."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get actor from kwargs or args
            actor = kwargs.get('actor') or (args[0] if args else None)
            if not actor:
                raise PermissionError("Actor context required")
            
            auth_service = AuthorizationService()
            auth_service.require_permission(actor, permission)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Singleton instance
authorization_service = AuthorizationService()


class PermissionDeniedError(Exception):
    """Exception raised when permission is denied."""
    pass
