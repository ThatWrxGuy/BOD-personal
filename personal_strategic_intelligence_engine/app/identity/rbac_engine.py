"""Role-Based Access Control (RBAC) engine."""
import uuid
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.identity import User, Role, Permission
from app.core.logging import get_logger

logger = get_logger(__name__)


class RBACEngine:
    """Role-Based Access Control engine."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def check_permission(
        self,
        user: User,
        permission: str,
    ) -> bool:
        """Check if a user has a specific permission."""
        
        if user.is_superuser:
            return True
        
        if not user.is_active:
            return False
        
        # Get user role
        if not user.role:
            return False
        
        # Check if role has permission
        role_permissions = await self._get_role_permissions(user.role_id)
        
        return permission in role_permissions
    
    async def check_permissions(
        self,
        user: User,
        permissions: List[str],
    ) -> bool:
        """Check if a user has all specified permissions."""
        
        for permission in permissions:
            if not await self.check_permission(user, permission):
                return False
        
        return True
    
    async def check_any_permission(
        self,
        user: User,
        permissions: List[str],
    ) -> bool:
        """Check if a user has any of the specified permissions."""
        
        for permission in permissions:
            if await self.check_permission(user, permission):
                return True
        
        return False
    
    async def get_user_permissions(self, user: User) -> List[str]:
        """Get all permissions for a user."""
        
        if user.is_superuser:
            # Return all permissions
            result = await self.session.execute(select(Permission))
            return [p.permission_name for p in result.scalars().all()]
        
        if not user.role:
            return []
        
        return await self._get_role_permissions(user.role_id)
    
    async def _get_role_permissions(self, role_id: uuid.UUID) -> List[str]:
        """Get all permissions for a role."""
        
        result = await self.session.execute(
            select(Permission)
            .join(Role.permissions)
            .where(Role.id == role_id)
        )
        
        return [p.permission_name for p in result.scalars().all()]
    
    async def assign_role(self, user: User, role_id: uuid.UUID) -> None:
        """Assign a role to a user."""
        
        user.role_id = role_id
        await self.session.commit()
        
        logger.info(f"Assigned role {role_id} to user {user.id}")
    
    async def create_role(
        self,
        role_name: str,
        description: str,
        permission_ids: List[uuid.UUID],
    ) -> Role:
        """Create a new role with permissions."""
        
        role = Role(
            role_name=role_name,
            description=description,
        )
        
        self.session.add(role)
        await self.session.flush()
        
        # Add permissions
        result = await self.session.execute(
            select(Permission).where(Permission.id.in_(permission_ids))
        )
        permissions = result.scalars().all()
        
        for permission in permissions:
            role.permissions.append(permission)
        
        await self.session.commit()
        await self.session.refresh(role)
        
        logger.info(f"Created role: {role_name}")
        
        return role
    
    async def get_role(self, role_id: uuid.UUID) -> Optional[Role]:
        """Get a role by ID."""
        
        result = await self.session.execute(
            select(Role).where(Role.id == role_id)
        )
        return result.scalar_one_or_none()
    
    async def get_role_by_name(self, role_name: str) -> Optional[Role]:
        """Get a role by name."""
        
        result = await self.session.execute(
            select(Role).where(Role.role_name == role_name)
        )
        return result.scalar_one_or_none()
    
    async def get_all_roles(self) -> List[Role]:
        """Get all roles."""
        
        result = await self.session.execute(select(Role))
        return list(result.scalars().all())
    
    async def get_all_permissions(self) -> List[Permission]:
        """Get all permissions."""
        
        result = await self.session.execute(select(Permission))
        return list(result.scalars().all())


def require_permission(permission: str):
    """Dependency for requiring a specific permission."""
    from fastapi import HTTPException, Depends
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    
    from app.db.session import get_db
    from app.identity.token_service import get_token_service
    from app.identity.auth_service import get_auth_service
    
    security = HTTPBearer()
    
    async def check_permission(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: AsyncSession = Depends(get_db),
    ):
        token_service = get_token_service()
        user_info = token_service.get_user_from_token(credentials.credentials)
        
        if not user_info:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        auth_service = await get_auth_service(session)
        user = await auth_service.get_user(uuid.UUID(user_info["user_id"]))
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        rbac = RBACEngine(session)
        
        if not await rbac.check_permission(user, permission):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: {permission}"
            )
        
        return user
    
    return check_permission


def require_any_permission(permissions: List[str]):
    """Dependency for requiring any of the specified permissions."""
    from fastapi import HTTPException, Depends
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    
    from app.db.session import get_db
    from app.identity.token_service import get_token_service
    from app.identity.auth_service import get_auth_service
    
    security = HTTPBearer()
    
    async def check_permission(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: AsyncSession = Depends(get_db),
    ):
        token_service = get_token_service()
        user_info = token_service.get_user_from_token(credentials.credentials)
        
        if not user_info:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        auth_service = await get_auth_service(session)
        user = await auth_service.get_user(uuid.UUID(user_info["user_id"]))
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        rbac = RBACEngine(session)
        
        if not await rbac.check_any_permission(user, permissions):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: one of {permissions} required"
            )
        
        return user
    
    return check_permission


async def get_rbac_engine(session: AsyncSession) -> RBACEngine:
    """Get RBAC engine instance."""
    return RBACEngine(session)
