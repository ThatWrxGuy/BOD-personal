"""Identity and authorization models."""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Table, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


# Role-Permission mapping table
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base, TimestampMixin):
    """User identity model."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Role association
    role_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True,
    )
    role: Mapped[Optional["Role"]] = relationship("Role", back_populates="users")
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class Role(Base, TimestampMixin):
    """Role model for RBAC."""

    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    role_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="role")
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
    )


class Permission(Base, TimestampMixin):
    """Permission model for RBAC."""

    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    permission_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    domain: Mapped[str] = mapped_column(String(50), nullable=False)  # system, signals, debate, execution, etc.
    
    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
    )


class AccessAuditLog(Base, TimestampMixin):
    """Audit log for security-relevant actions."""

    __tablename__ = "access_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # login, logout, create, update, delete
    resource: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # what was accessed
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # ID of the resource
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv6 compatible
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    details: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timestamp is inherited from TimestampMixin


# Predefined roles
class RoleName:
    """Predefined role names."""
    OWNER = "owner"
    ADMINISTRATOR = "administrator"
    OPERATOR = "operator"
    VIEWER = "viewer"
    AUDITOR = "auditor"


# Predefined permission domains
class PermissionDomain:
    """Permission domains."""
    SYSTEM = "system"
    SIGNALS = "signals"
    DEBATE = "debate"
    GOVERNANCE = "governance"
    EXECUTION = "execution"
    LEARNING = "learning"
    CONNECTORS = "connectors"
    ADMINISTRATION = "administration"


# Predefined permission names
class PermissionName:
    """Predefined permission names."""
    # System
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_SYSTEM_HEALTH = "view_system_health"
    
    # Signals
    VIEW_SIGNALS = "view_signals"
    CREATE_SIGNAL = "create_signal"
    MANAGE_SIGNALS = "manage_signals"
    
    # Debate
    VIEW_DEBATES = "view_debates"
    PARTICIPATE_IN_DEBATE = "participate_in_debate"
    CREATE_DEBATE = "create_debate"
    
    # Governance
    VIEW_GOVERNANCE = "view_governance"
    APPROVE_DECISION = "approve_decision"
    REJECT_DECISION = "reject_decision"
    MANAGE_GOVERNANCE = "manage_governance"
    
    # Execution
    VIEW_EXECUTION = "view_execution"
    EXECUTE_ACTION = "execute_action"
    APPROVE_EXECUTION = "approve_execution"
    VIEW_EXECUTION_HISTORY = "view_execution_history"
    
    # Learning
    VIEW_LEARNING_DATA = "view_learning_data"
    MANAGE_LEARNING = "manage_learning"
    
    # Connectors
    VIEW_CONNECTORS = "view_connectors"
    MANAGE_CONNECTORS = "manage_connectors"
    
    # Administration
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_SETTINGS = "manage_settings"
