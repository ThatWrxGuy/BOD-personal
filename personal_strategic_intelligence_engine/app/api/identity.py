"""Identity and authentication API routes."""
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.session import get_db
from app.identity.auth_service import AuthService, get_auth_service
from app.identity.rbac_engine import RBACEngine, get_rbac_engine
from app.identity.token_service import get_token_service
from app.models.identity import User, Role, Permission, AccessAuditLog
from app.models.identity import RoleName, PermissionName, PermissionDomain
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])
user_router = APIRouter(prefix="/users", tags=["users"])
admin_router = APIRouter(prefix="/admin", tags=["administration"])

security = HTTPBearer()


# ===================
# Auth Models
# ===================

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role_id: Optional[uuid.UUID] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role_id: Optional[uuid.UUID] = None
    is_active: Optional[bool] = None


class RoleCreate(BaseModel):
    role_name: str
    description: Optional[str] = None
    permission_ids: list[uuid.UUID] = []


# ===================
# Auth Endpoints
# ===================

@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    """Authenticate user and return access token."""
    
    # Get client IP
    ip_address = request.client.host if request.client else None
    
    auth_service = await get_auth_service(session)
    result = await auth_service.authenticate(
        username=credentials.username,
        password=credentials.password,
        ip_address=ip_address,
    )
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token, user = result
    
    return LoginResponse(
        access_token=token,
        user={
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role.role_name if user.role else None,
            "is_active": user.is_active,
        },
    )


@router.post("/logout")
async def logout(
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    """Logout user (client should discard token)."""
    
    # Get user from request state
    if hasattr(request.state, "user_id"):
        auth_service = await get_auth_service(session)
        # Log the logout
        pass
    
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    """Get current authenticated user."""
    
    if not hasattr(request.state, "user_id"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    auth_service = await get_auth_service(session)
    user = await auth_service.get_user(uuid.UUID(request.state.user_id))
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    rbac = await get_rbac_engine(session)
    permissions = await rbac.get_user_permissions(user)
    
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role.role_name if user.role else None,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "permissions": permissions,
        "last_login": user.last_login_at.isoformat() if user.last_login_at else None,
    }


@router.post("/refresh")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Refresh access token."""
    
    token_service = get_token_service()
    new_token = token_service.refresh_token(credentials.credentials)
    
    if not new_token:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"access_token": new_token, "token_type": "bearer"}


# ===================
# User Endpoints
# ===================

@user_router.get("")
async def list_users(
    session: AsyncSession = Depends(get_db),
):
    """List all users."""
    
    result = await session.execute(
        select(User).order_by(desc(User.created_at))
    )
    users = result.scalars().all()
    
    return {
        "users": [
            {
                "id": str(u.id),
                "username": u.username,
                "email": u.email,
                "role": u.role.role_name if u.role else None,
                "is_active": u.is_active,
                "last_login": u.last_login_at.isoformat() if u.last_login_at else None,
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ]
    }


@user_router.get("/{user_id}")
async def get_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Get user by ID."""
    
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    rbac = await get_rbac_engine(session)
    permissions = await rbac.get_user_permissions(user)
    
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role.role_name if user.role else None,
        "role_id": str(user.role_id) if user.role_id else None,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "permissions": permissions,
        "last_login": user.last_login_at.isoformat() if user.last_login_at else None,
        "created_at": user.created_at.isoformat(),
    }


@user_router.post("")
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db),
):
    """Create a new user."""
    
    auth_service = await get_auth_service(session)
    
    # Check if username exists
    existing = await auth_service.get_user_by_username(user_data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user = await auth_service.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        role_id=user_data.role_id,
    )
    
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "message": "User created successfully",
    }


@user_router.patch("/{user_id}")
async def update_user(
    user_id: uuid.UUID,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_db),
):
    """Update user details."""
    
    auth_service = await get_auth_service(session)
    user = await auth_service.get_user(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_data.email:
        user.email = user_data.email
    if user_data.role_id:
        user.role_id = user_data.role_id
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    await session.commit()
    await session.refresh(user)
    
    return {
        "id": str(user.id),
        "username": user.username,
        "message": "User updated successfully",
    }


@user_router.delete("/{user_id}")
async def delete_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
):
    """Delete a user."""
    
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await session.delete(user)
    await session.commit()
    
    return {"message": "User deleted successfully"}


# ===================
# Role & Permission Endpoints
# ===================

@admin_router.get("/roles")
async def list_roles(session: AsyncSession = Depends(get_db)):
    """List all roles."""
    
    rbac = await get_rbac_engine(session)
    roles = await rbac.get_all_roles()
    
    return {
        "roles": [
            {
                "id": str(r.id),
                "role_name": r.role_name,
                "description": r.description,
                "permissions": [p.permission_name for p in r.permissions],
                "user_count": len(r.users),
            }
            for r in roles
        ]
    }


@admin_router.post("/roles")
async def create_role(
    role_data: RoleCreate,
    session: AsyncSession = Depends(get_db),
):
    """Create a new role."""
    
    rbac = await get_rbac_engine(session)
    
    role = await rbac.create_role(
        role_name=role_data.role_name,
        description=role_data.description or "",
        permission_ids=role_data.permission_ids,
    )
    
    return {
        "id": str(role.id),
        "role_name": role.role_name,
        "message": "Role created successfully",
    }


@admin_router.get("/permissions")
async def list_permissions(session: AsyncSession = Depends(get_db)):
    """List all permissions."""
    
    rbac = await get_rbac_engine(session)
    permissions = await rbac.get_all_permissions()
    
    # Group by domain
    by_domain = {}
    for p in permissions:
        domain = p.domain
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append({
            "id": str(p.id),
            "name": p.permission_name,
            "description": p.description,
        })
    
    return {"permissions_by_domain": by_domain}


@admin_router.get("/audit-logs")
async def list_audit_logs(
    limit: int = 50,
    session: AsyncSession = Depends(get_db),
):
    """List audit logs."""
    
    result = await session.execute(
        select(AccessAuditLog)
        .order_by(desc(AccessAuditLog.created_at))
        .limit(limit)
    )
    logs = result.scalars().all()
    
    return {
        "logs": [
            {
                "id": str(l.id),
                "user_id": str(l.user_id) if l.user_id else None,
                "action": l.action,
                "resource": l.resource,
                "success": l.success,
                "ip_address": l.ip_address,
                "details": l.details,
                "timestamp": l.created_at.isoformat(),
            }
            for l in logs
        ]
    }
