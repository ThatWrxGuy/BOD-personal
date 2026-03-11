"""Authentication middleware for request processing."""
from typing import Optional
import uuid

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.identity.token_service import get_token_service
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for JWT authentication."""
    
    # Public endpoints that don't require authentication
    PUBLIC_PATHS = [
        "/",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/health",
        "/health/config-readiness",
        "/auth/login",
        "/auth/register",
    ]
    
    # Public path prefixes
    PUBLIC_PREFIXES = [
        "/docs",
        "/openapi.json",
        "/redoc",
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public paths
        if self._is_public_path(request.url.path):
            return await call_next(request)
        
        # Skip if auth is disabled
        settings = get_settings()
        if not settings.enable_auth:
            return await call_next(request)
        
        # Get token from header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing authorization header"},
            )
        
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid authorization header format"},
            )
        
        token = auth_header.replace("Bearer ", "")
        
        # Validate token
        token_service = get_token_service()
        user_info = token_service.get_user_from_token(token)
        
        if not user_info:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"},
            )
        
        # Attach user info to request state
        request.state.user_id = user_info["user_id"]
        request.state.username = user_info["username"]
        request.state.role = user_info["role"]
        request.state.permissions = user_info["permissions"]
        
        return await call_next(request)
    
    def _is_public_path(self, path: str) -> bool:
        """Check if path is public."""
        
        # Exact match
        if path in self.PUBLIC_PATHS:
            return True
        
        # Prefix match
        for prefix in self.PUBLIC_PREFIXES:
            if path.startswith(prefix):
                return True
        
        return False


def get_current_user(request: Request) -> dict:
    """Get current user from request state."""
    
    if not hasattr(request.state, "user_id"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "user_id": request.state.user_id,
        "username": request.state.username,
        "role": request.state.role,
        "permissions": request.state.permissions,
    }
