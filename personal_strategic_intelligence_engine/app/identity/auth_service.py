"""Authentication service."""
import uuid
from datetime import datetime
from typing import Optional, Tuple

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.identity import User, AccessAuditLog
from app.identity.token_service import TokenService
from app.core.logging import get_logger

logger = get_logger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for user authentication."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.token_service = TokenService()
    
    async def authenticate(
        self,
        username: str,
        password: str,
        ip_address: Optional[str] = None,
    ) -> Optional[Tuple[str, User]]:
        """Authenticate a user with username and password."""
        
        # Find user
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()
        
        # Check if user exists and is active
        if not user:
            await self._log_audit(
                action="login_failed",
                user_id=None,
                resource="auth",
                success=False,
                details=f"User not found: {username}",
                ip_address=ip_address,
            )
            logger.warning(f"Login attempt for non-existent user: {username}")
            return None
        
        if not user.is_active:
            await self._log_audit(
                action="login_failed",
                user_id=user.id,
                resource="auth",
                success=False,
                details="User account is inactive",
                ip_address=ip_address,
            )
            logger.warning(f"Login attempt for inactive user: {username}")
            return None
        
        # Verify password
        if not self._verify_password(password, user.password_hash):
            await self._log_audit(
                action="login_failed",
                user_id=user.id,
                resource="auth",
                success=False,
                details="Invalid password",
                ip_address=ip_address,
            )
            logger.warning(f"Invalid password for user: {username}")
            return None
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        await self.session.commit()
        
        # Generate token
        role_name = user.role.role_name if user.role else "viewer"
        permissions = [p.permission_name for p in user.role.permissions] if user.role else []
        
        token = self.token_service.create_access_token(
            user_id=user.id,
            username=user.username,
            role=role_name,
            permissions=permissions,
        )
        
        await self._log_audit(
            action="login_success",
            user_id=user.id,
            resource="auth",
            success=True,
            details="User logged in successfully",
            ip_address=ip_address,
        )
        
        logger.info(f"User logged in: {username}")
        
        return token, user
    
    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role_id: Optional[uuid.UUID] = None,
    ) -> User:
        """Create a new user."""
        
        password_hash = self._hash_password(password)
        
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role_id=role_id,
            is_active=True,
        )
        
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        
        logger.info(f"Created user: {username}")
        
        return user
    
    async def get_user(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID."""
        
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    def _hash_password(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    async def _log_audit(
        self,
        action: str,
        user_id: Optional[uuid.UUID],
        resource: str,
        success: bool,
        details: str,
        ip_address: Optional[str] = None,
    ) -> None:
        """Log an audit event."""
        
        log = AccessAuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            success=success,
            details=details,
            ip_address=ip_address,
        )
        
        self.session.add(log)
        await self.session.commit()


async def get_auth_service(session: AsyncSession) -> AuthService:
    """Get auth service instance."""
    return AuthService(session)
