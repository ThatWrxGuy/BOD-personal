"""
BB-APP-004: Identity Domain Models

Core identity, authentication, and authorization entities.
Per BB-APP-004 Section 3-14 - Identity Domain Model.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


# ============== Enums ==============

class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    LOCKED = "locked"
    DELETED = "deleted"


class OrganizationStatus(str, Enum):
    """Organization status."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class PlanTier(str, Enum):
    """Organization plan tiers."""
    PERSONAL = "personal"
    FAMILY = "family"
    TEAM = "team"
    ENTERPRISE = "enterprise"


class Role(str, Enum):
    """User roles."""
    OWNER = "owner"
    ADMIN = "admin"
    STRATEGIST = "strategist"
    OPERATOR = "operator"
    VIEWER = "viewer"


class Permission(str, Enum):
    """System permissions."""
    # Dashboard
    READ_DASHBOARD = "read_dashboard"
    
    # Domain data
    READ_DOMAIN_DATA = "read_domain_data"
    WRITE_DOMAIN_DATA = "write_domain_data"
    
    # Recommendations
    READ_RECOMMENDATIONS = "read_recommendations"
    APPROVE_RECOMMENDATION = "approve_recommendation"
    REJECT_RECOMMENDATION = "reject_recommendation"
    DEFER_RECOMMENDATION = "defer_recommendation"
    CONVERT_TO_ACTION = "convert_to_action"
    
    # Actions
    READ_ACTIONS = "read_actions"
    CREATE_ACTION = "create_action"
    COMPLETE_ACTION = "complete_action"
    CANCEL_ACTION = "cancel_action"
    
    # Briefs
    READ_BRIEFS = "read_briefs"
    CREATE_BRIEF = "create_brief"
    
    # System
    CONFIGURE_SYSTEM = "configure_system"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_USERS = "manage_users"
    MANAGE_ORGANIZATION = "manage_organization"


# ============== Permission Maps ==============

# Role to permissions mapping
ROLE_PERMISSIONS = {
    Role.OWNER: [p for p in Permission],
    Role.ADMIN: [
        Permission.READ_DASHBOARD,
        Permission.READ_DOMAIN_DATA,
        Permission.WRITE_DOMAIN_DATA,
        Permission.READ_RECOMMENDATIONS,
        Permission.APPROVE_RECOMMENDATION,
        Permission.REJECT_RECOMMENDATION,
        Permission.DEFER_RECOMMENDATION,
        Permission.CONVERT_TO_ACTION,
        Permission.READ_ACTIONS,
        Permission.CREATE_ACTION,
        Permission.COMPLETE_ACTION,
        Permission.CANCEL_ACTION,
        Permission.READ_BRIEFS,
        Permission.CONFIGURE_SYSTEM,
        Permission.VIEW_AUDIT_LOGS,
        Permission.MANAGE_USERS,
    ],
    Role.STRATEGIST: [
        Permission.READ_DASHBOARD,
        Permission.READ_DOMAIN_DATA,
        Permission.READ_RECOMMENDATIONS,
        Permission.APPROVE_RECOMMENDATION,
        Permission.REJECT_RECOMMENDATION,
        Permission.DEFER_RECOMMENDATION,
        Permission.CONVERT_TO_ACTION,
        Permission.READ_ACTIONS,
        Permission.READ_BRIEFS,
    ],
    Role.OPERATOR: [
        Permission.READ_DASHBOARD,
        Permission.READ_DOMAIN_DATA,
        Permission.READ_RECOMMENDATIONS,
        Permission.READ_ACTIONS,
        Permission.CREATE_ACTION,
        Permission.COMPLETE_ACTION,
        Permission.CANCEL_ACTION,
        Permission.READ_BRIEFS,
    ],
    Role.VIEWER: [
        Permission.READ_DASHBOARD,
        Permission.READ_DOMAIN_DATA,
        Permission.READ_RECOMMENDATIONS,
        Permission.READ_ACTIONS,
        Permission.READ_BRIEFS,
    ],
}


# ============== Models ==============

@dataclass
class User:
    """User entity."""
    id: str
    email: str
    password_hash: str
    display_name: str
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    mfa_enabled: bool = False


@dataclass
class Organization:
    """Organization (tenant) entity."""
    id: str
    name: str
    owner_user_id: str
    plan_tier: PlanTier = PlanTier.PERSONAL
    status: OrganizationStatus = OrganizationStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Membership:
    """User membership in an organization."""
    id: str
    user_id: str
    organization_id: str
    role: Role = Role.VIEWER
    joined_at: datetime = field(default_factory=datetime.now)


@dataclass
class Session:
    """User session."""
    id: str
    user_id: str
    organization_id: str
    role: Role
    permissions: list[Permission]
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=24))
    device_info: str = ""
    ip_address: str = ""


@dataclass
class APIKey:
    """API key for external access."""
    id: str
    organization_id: str
    key_hash: str
    permissions: list[Permission]
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None


@dataclass
class ServiceAccount:
    """Non-human system actor."""
    id: str
    name: str
    organization_id: str
    permissions: list[Permission]
    created_at: datetime = field(default_factory=datetime.now)
    enabled: bool = True


# ============== Actor Context ==============

@dataclass
class ActorContext:
    """Context of an actor performing an action."""
    user_id: str
    organization_id: str
    role: Role
    permissions: list[Permission]
    session_id: Optional[str] = None
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if actor has a specific permission."""
        return permission in self.permissions
    
    def has_any_permission(self, permissions: list[Permission]) -> bool:
        """Check if actor has any of the specified permissions."""
        return any(p in self.permissions for p in permissions)
    
    def has_all_permissions(self, permissions: list[Permission]) -> bool:
        """Check if actor has all of the specified permissions."""
        return all(p in self.permissions for p in permissions)


__all__ = [
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
]
