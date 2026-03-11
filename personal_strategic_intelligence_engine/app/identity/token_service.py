"""Token service for JWT authentication."""
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

import jwt
from jwt.exceptions import InvalidTokenError

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class TokenService:
    """Service for JWT token management."""
    
    def __init__(self):
        self.settings = get_settings()
        self.secret_key = self.settings.secret_key
        self.algorithm = "HS256"
        self.access_token_expire_minutes = self.settings.access_token_expire_minutes
    
    def create_access_token(
        self,
        user_id: uuid.UUID,
        username: str,
        role: str,
        permissions: List[str],
    ) -> str:
        """Create a JWT access token."""
        
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": str(user_id),
            "username": username,
            "role": role,
            "permissions": permissions,
            "iat": now,
            "exp": expire,
            "type": "access",
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        logger.debug(f"Created access token for user {username}")
        
        return token
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a JWT token."""
        
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
            
            return payload
            
        except InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def verify_token(self, token: str) -> bool:
        """Verify if a token is valid."""
        
        payload = self.decode_token(token)
        return payload is not None
    
    def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Extract user info from token."""
        
        payload = self.decode_token(token)
        
        if not payload:
            return None
        
        return {
            "user_id": payload.get("sub"),
            "username": payload.get("username"),
            "role": payload.get("role"),
            "permissions": payload.get("permissions", []),
        }
    
    def refresh_token(self, token: str) -> Optional[str]:
        """Refresh an access token."""
        
        payload = self.decode_token(token)
        
        if not payload:
            return None
        
        # Create new token with same user info
        return self.create_access_token(
            user_id=uuid.UUID(payload["sub"]),
            username=payload["username"],
            role=payload["role"],
            permissions=payload.get("permissions", []),
        )


# Global token service
_token_service: Optional[TokenService] = None


def get_token_service() -> TokenService:
    """Get the global token service."""
    global _token_service
    
    if _token_service is None:
        _token_service = TokenService()
    
    return _token_service
