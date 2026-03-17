"""
BB-APP-004: Identity Module

Identity, authentication, and authorization components.
"""

from app.identity.models import (
    UserStatus,
    OrganizationStatus,
    PlanTier,
    Role,
    Permission,
    ROLE_PERMISSIONS,
    User,
    Organization,
    Membership,
    Session,
    APIKey,
    ServiceAccount,
    ActorContext,
)
from app.identity.auth_service import (
    AuthenticationService,
    auth_service,
    get_current_actor,
    require_auth,
)
from app.identity.authorization_service import (
    AuthorizationService,
    authorization_service,
    PermissionDeniedError,
    require_permission,
)
from app.identity.api_key_service import (
    APIKeyService,
    api_key_service,
)

__all__ = [
    # Models
    "UserStatus",
    "OrganizationStatus",
    "PlanTier",
    "Role",
    "Permission",
    "ROLE_PERMISSIONS",
    "User",
    "Organization",
    "Membership",
    "Session",
    "APIKey",
    "ServiceAccount",
    "ActorContext",
    # Auth
    "AuthenticationService",
    "auth_service",
    "get_current_actor",
    "require_auth",
    # Authz
    "AuthorizationService",
    "authorization_service",
    "PermissionDeniedError",
    "require_permission",
    # API Keys
    "APIKeyService",
    "api_key_service",
]
