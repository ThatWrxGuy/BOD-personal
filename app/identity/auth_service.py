"""
BB-APP-004: Authentication Service

JWT-based authentication system.
Per BB-APP-004 Section 11 - Authentication System.
"""

import hashlib
import hmac
import json
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional

from app.identity.models import (
    User,
    Organization,
    Membership,
    Session,
    Role,
    Permission,
    ROLE_PERMISSIONS,
    ActorContext,
    UserStatus,
    OrganizationStatus,
)
from app.audit import audit_log_service


# In-memory storage for demo (would be database in production)
_users_db: dict[str, User] = {}
_organizations_db: dict[str, Organization] = {}
_memberships_db: dict[str, Membership] = {}
_sessions_db: dict[str, Session] = {}

# JWT secret (would be env var in production)
JWT_SECRET = secrets.token_urlsafe(32)
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 24


class AuthenticationService:
    """JWT-based authentication service."""
    
    def __init__(self):
        self._setup_default_org()
    
    def _setup_default_org(self):
        """Create default personal organization."""
        org_id = "org-default"
        if org_id not in _organizations_db:
            _organizations_db[org_id] = Organization(
                id=org_id,
                name="Personal System",
                owner_user_id="",
                plan_tier="personal",
            )
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 (simplified - would use bcrypt in production)."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        return self._hash_password(password) == password_hash
    
    def _generate_token(self, session: Session) -> str:
        """Generate JWT token."""
        payload = {
            "sid": session.id,
            "uid": session.user_id,
            "oid": session.organization_id,
            "rol": session.role.value,
            "per": [p.value for p in session.permissions],
            "exp": int(session.expires_at.timestamp()),
            "iat": int(datetime.now().timestamp()),
        }
        # Simple JWT-like token using base64
        import base64
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
        signature = hmac.new(
            JWT_SECRET.encode(),
            payload_b64.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{payload_b64}.{signature}"
    
    def _parse_token(self, token: str) -> Optional[dict]:
        """Parse and validate JWT token."""
        try:
            parts = token.split(".")
            if len(parts) != 2:
                return None
            
            payload_b64, signature = parts
            
            # Verify signature
            expected_sig = hmac.new(
                JWT_SECRET.encode(),
                payload_b64.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_sig):
                return None
            
            # Decode payload
            import base64
            payload_json = base64.urlsafe_b64decode(payload_b64.encode()).decode()
            payload = json.loads(payload_json)
            
            # Check expiration
            exp = datetime.fromtimestamp(payload.get("exp", 0))
            if datetime.now() > exp:
                return None
            
            return payload
        except Exception:
            return None
    
    def register_user(
        self,
        email: str,
        password: str,
        display_name: str,
    ) -> tuple[Optional[User], str]:
        """Register a new user."""
        # Check if email exists
        for user in _users_db.values():
            if user.email == email:
                return None, "Email already registered"
        
        # Create user
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            password_hash=self._hash_password(password),
            display_name=display_name,
            status=UserStatus.ACTIVE,
        )
        _users_db[user.id] = user
        
        # Create default organization for user
        org = Organization(
            id=f"org-{user.id[:8]}",
            name=f"{display_name}'s System",
            owner_user_id=user.id,
            plan_tier="personal",
        )
        _organizations_db[org.id] = org
        
        # Create membership
        membership = Membership(
            id=str(uuid.uuid4()),
            user_id=user.id,
            organization_id=org.id,
            role=Role.OWNER,
        )
        _memberships_db[membership.id] = membership
        
        # Log audit
        audit_log_service.log_event(
            event_type="user_registered",
            entity_type="user",
            entity_id=user.id,
            actor="system",
            new_state="active",
            metadata={"email": email, "org_id": org.id},
        )
        
        return user, "User registered successfully"
    
    def authenticate(
        self,
        email: str,
        password: str,
        device_info: str = "",
        ip_address: str = "",
    ) -> tuple[Optional[Session], str]:
        """Authenticate user and create session."""
        # Find user by email
        user = None
        for u in _users_db.values():
            if u.email == email:
                user = u
                break
        
        if not user:
            return None, "Invalid email or password"
        
        # Check password
        if not self._verify_password(password, user.password_hash):
            return None, "Invalid email or password"
        
        # Check status
        if user.status != UserStatus.ACTIVE:
            return None, f"Account is {user.status.value}"
        
        # Get user's organization and role
        membership = None
        for m in _memberships_db.values():
            if m.user_id == user.id:
                membership = m
                break
        
        if not membership:
            return None, "No organization membership found"
        
        org = _organizations_db.get(membership.organization_id)
        if not org or org.status != OrganizationStatus.ACTIVE:
            return None, "Organization is not active"
        
        # Get permissions
        permissions = ROLE_PERMISSIONS.get(membership.role, [])
        
        # Create session
        session = Session(
            id=str(uuid.uuid4()),
            user_id=user.id,
            organization_id=membership.organization_id,
            role=membership.role,
            permissions=permissions,
            expires_at=datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS),
            device_info=device_info,
            ip_address=ip_address,
        )
        _sessions_db[session.id] = session
        
        # Update last login
        user.last_login = datetime.now()
        
        # Generate token
        token = self._generate_token(session)
        
        # Log audit
        audit_log_service.log_event(
            event_type="user_login",
            entity_type="user",
            entity_id=user.id,
            actor=user.id,
            new_state="logged_in",
            metadata={
                "session_id": session.id,
                "org_id": membership.organization_id,
            },
        )
        
        return session, token
    
    def verify_token(self, token: str) -> Optional[ActorContext]:
        """Verify token and return actor context."""
        payload = self._parse_token(token)
        
        if not payload:
            return None
        
        session_id = payload.get("sid") or payload.get("session_id")
        session = _sessions_db.get(session_id)
        
        if not session:
            return None
        
        # Refresh session expiration
        session.expires_at = datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)
        
        # Build permissions - support both old and new key names
        perms = payload.get("per") or payload.get("permissions", [])
        permissions = [Permission(p) for p in perms]
        
        return ActorContext(
            user_id=payload.get("uid") or payload.get("user_id", ""),
            organization_id=payload.get("oid") or payload.get("org_id", ""),
            role=Role(payload.get("rol") or payload.get("role", "viewer")),
            permissions=permissions,
            session_id=session_id,
        )
    
    def logout(self, session_id: str, user_id: str) -> bool:
        """Logout user and invalidate session."""
        session = _sessions_db.pop(session_id, None)
        
        if session:
            audit_log_service.log_event(
                event_type="user_logout",
                entity_type="user",
                entity_id=user_id,
                actor=user_id,
                previous_state="logged_in",
                new_state="logged_out",
            )
            return True
        
        return False
    
    def revoke_session(self, session_id: str, actor_id: str) -> bool:
        """Revoke a session."""
        session = _sessions_db.pop(session_id, None)
        
        if session:
            audit_log_service.log_event(
                event_type="session_revoked",
                entity_type="session",
                entity_id=session_id,
                actor=actor_id,
                previous_state="active",
                new_state="revoked",
            )
            return True
        
        return False
    
    def get_user_sessions(self, user_id: str) -> list[Session]:
        """Get all active sessions for a user."""
        return [
            s for s in _sessions_db.values()
            if s.user_id == user_id and s.expires_at > datetime.now()
        ]
    
    def create_user(self, user: User, organization_id: str, role: Role = Role.VIEWER) -> User:
        """Create a user (internal)."""
        _users_db[user.id] = user
        
        membership = Membership(
            id=str(uuid.uuid4()),
            user_id=user.id,
            organization_id=organization_id,
            role=role,
        )
        _memberships_db[membership.id] = membership
        
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return _users_db.get(user_id)
    
    def get_organization(self, org_id: str) -> Optional[Organization]:
        """Get organization by ID."""
        return _organizations_db.get(org_id)
    
    def get_membership(self, user_id: str, org_id: str) -> Optional[Membership]:
        """Get user's membership in organization."""
        for m in _memberships_db.values():
            if m.user_id == user_id and m.organization_id == org_id:
                return m
        return None


# Singleton instance
auth_service = AuthenticationService()


# ============== Helper Functions ==============

def get_current_actor(token: str) -> Optional[ActorContext]:
    """Get current actor from token."""
    return auth_service.verify_token(token)


def require_auth(token: str) -> ActorContext:
    """Require authentication or raise exception."""
    actor = auth_service.verify_token(token)
    if not actor:
        raise PermissionError("Authentication required")
    return actor
