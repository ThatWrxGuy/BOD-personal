"""
BB-APP-004: API Key Management

API key creation and validation.
Per BB-APP-004 Section 14 - API Keys.
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional

from app.identity.models import (
    APIKey,
    Permission,
    ActorContext,
)
from app.audit import audit_log_service


# In-memory storage (would be database in production)
_api_keys_db: dict[str, APIKey] = {}
_key_lookup: dict[str, str] = {}  # key_hash -> api_key_id


class APIKeyService:
    """API key management service."""
    
    def _generate_key(self) -> tuple[str, str]:
        """Generate API key and hash."""
        key = f"bb_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return key, key_hash
    
    def _hash_key(self, key: str) -> str:
        """Hash an API key."""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def create_api_key(
        self,
        organization_id: str,
        permissions: list[Permission],
        expires_in_days: int = 90,
    ) -> tuple[APIKey, str]:
        """
        Create a new API key.
        Returns (APIKey object, plain_text_key)
        """
        key, key_hash = self._generate_key()
        
        expires_at = None
        if expires_in_days > 0:
            expires_at = datetime.now() + timedelta(days=expires_in_days)
        
        api_key = APIKey(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            key_hash=key_hash,
            permissions=permissions,
            expires_at=expires_at,
        )
        
        _api_keys_db[api_key.id] = api_key
        _key_lookup[key_hash] = api_key.id
        
        # Log audit
        audit_log_service.log_event(
            event_type="api_key_created",
            entity_type="api_key",
            entity_id=api_key.id,
            actor=organization_id,
            metadata={
                "organization_id": organization_id,
                "permissions": [p.value for p in permissions],
            }
        )
        
        return api_key, key
    
    def validate_key(self, key: str) -> Optional[ActorContext]:
        """
        Validate an API key and return actor context.
        """
        key_hash = self._hash_key(key)
        api_key_id = _key_lookup.get(key_hash)
        
        if not api_key_id:
            return None
        
        api_key = _api_keys_db.get(api_key_id)
        
        if not api_key:
            return None
        
        # Check expiration
        if api_key.expires_at and datetime.now() > api_key.expires_at:
            return None
        
        # Update last used
        api_key.last_used = datetime.now()
        
        # Create actor context from API key
        return ActorContext(
            user_id=f"api_key:{api_key.id}",
            organization_id=api_key.organization_id,
            role=Role.VIEWER,  # API keys get base permissions
            permissions=api_key.permissions,
        )
    
    def revoke_key(self, api_key_id: str, actor_id: str) -> bool:
        """Revoke an API key."""
        api_key = _api_keys_db.pop(api_key_id, None)
        
        if api_key:
            # Remove from lookup
            for k, v in list(_key_lookup.items()):
                if v == api_key_id:
                    del _key_lookup[k]
            
            audit_log_service.log_event(
                event_type="api_key_revoked",
                entity_type="api_key",
                entity_id=api_key_id,
                actor=actor_id,
                previous_state="active",
                new_state="revoked",
            )
            return True
        
        return False
    
    def get_organization_keys(self, organization_id: str) -> list[APIKey]:
        """Get all API keys for an organization."""
        return [
            k for k in _api_keys_db.values()
            if k.organization_id == organization_id
        ]
    
    def get_key_info(self, api_key_id: str) -> Optional[APIKey]:
        """Get API key info (without the key)."""
        return _api_keys_db.get(api_key_id)


# Need to import Role
from app.identity.models import Role

# Singleton instance
api_key_service = APIKeyService()
