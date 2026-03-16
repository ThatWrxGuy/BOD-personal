"""Credential redaction for safe logging and responses."""
import re
from typing import Any, Dict, List, Optional, Union

from app.core.logging import get_logger

logger = get_logger(__name__)


class CredentialRedactor:
    """Redacts sensitive credentials from logs and responses."""
    
    # Patterns to redact
    SECRET_PATTERNS = [
        # Generic API keys
        (r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_-]{20,})', r'\1[REDACTED]'),
        (r'(secret["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_-]{20,})', r'\1[REDACTED]'),
        (r'(token["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_-]{20,})', r'\1[REDACTED]'),
        
        # GitHub tokens
        (r'(ghp_)[a-zA-Z0-9]{36}', r'\1[REDACTED]'),
        (r'(gho_)[a-zA-Z0-9]{36}', r'\1[REDACTED]'),
        (r'(ghu_)[a-zA-Z0-9]{36}', r'\1[REDACTED]'),
        (r'(ghs_)[a-zA-Z0-9]{36}', r'\1[REDACTED]'),
        (r'(ghr_)[a-zA-Z0-9]{36}', r'\1[REDACTED]'),
        
        # OpenAI keys
        (r'(sk-)[a-zA-Z0-9]{20,}', r'\1[REDACTED]'),
        
        # Anthropic keys
        (r'(sk-ant-)[a-zA-Z0-9_-]{30,}', r'\1[REDACTED]'),
        
        # OpenHands keys
        (r'(ohds_)[a-zA-Z0-9]{32,}', r'\1[REDACTED]'),
        
        # AWS keys
        (r'(AKIA)[A-Z0-9]{16}', r'\1[REDACTED]'),
        
        # JWT tokens
        (r'(Bearer\s+)[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+', r'\1[REDACTED]'),
        
        # Generic bearer tokens
        (r'(bearer["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_-]{30,})', r'\1[REDACTED]'),
    ]
    
    # Keys to redact in dictionaries
    REDACT_KEYS = {
        "api_key", "api-key", "apikey",
        "secret", "secret_key", "secret-key",
        "token", "access_token", "access-token",
        "password", "passwd",
        "client_secret", "client-secret",
        "private_key", "private-key",
        "authorization",
        # GitHub
        "github_token", "github-token", "GITHUB_TOKEN",
        # OpenHands
        "openhands_api_key", "openhands-api-key", "OPENHANDS_API_KEY",
    }
    
    # Fields to partially mask
    PARTIAL_MASK_FIELDS = {
        "email": lambda v: v[:2] + "***" + v[v.find("@"):] if "@" in v else "***",
    }
    
    def redact_string(self, text: str) -> str:
        """Redact secrets from a string."""
        
        if not text:
            return text
        
        result = text
        
        for pattern, replacement in self.SECRET_PATTERNS:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def redact_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact secrets from a dictionary."""
        
        if not isinstance(data, dict):
            return data
        
        result = {}
        
        for key, value in data.items():
            key_lower = key.lower()
            
            # Check if key should be redacted
            if key_lower in self.REDACT_KEYS:
                result[key] = self._redact_value(value)
            
            # Check for partial mask
            elif key_lower in self.PARTIAL_MASK_FIELDS:
                result[key] = self.PARTIAL_MASK_FIELDS[key_lower](str(value))
            
            # Recursively process nested dicts
            elif isinstance(value, dict):
                result[key] = self.redact_dict(value)
            
            # Process lists
            elif isinstance(value, list):
                result[key] = self._redact_list(value)
            
            else:
                result[key] = value
        
        return result
    
    def _redact_value(self, value: Any) -> str:
        """Redact a value."""
        
        if value is None:
            return None
        
        value_str = str(value)
        
        # Check for known patterns
        if value_str.startswith("sk-"):
            return "sk-[REDACTED]"
        if value_str.startswith("sk-ant-"):
            return "sk-ant-[REDACTED]"
        if value_str.startswith("Bearer "):
            return "Bearer [REDACTED]"
        
        return "[REDACTED]"
    
    def _redact_list(self, items: List[Any]) -> List[Any]:
        """Redact secrets from a list."""
        
        result = []
        
        for item in items:
            if isinstance(item, dict):
                result.append(self.redact_dict(item))
            elif isinstance(item, str):
                result.append(self.redact_string(item))
            else:
                result.append(item)
        
        return result
    
    def redact_response(self, response: Any) -> Any:
        """Redact secrets from any response."""
        
        if isinstance(response, dict):
            return self.redact_dict(response)
        elif isinstance(response, list):
            return self._redact_list(response)
        elif isinstance(response, str):
            return self.redact_string(response)
        
        return response


# Global redactor
_redactor = CredentialRedactor()


def get_credential_redactor() -> CredentialRedactor:
    """Get the global credential redactor."""
    return _redactor


def redact_credentials(data: Any) -> Any:
    """Convenience function to redact credentials."""
    return _redactor.redact_response(data)


def redact_log_message(message: str) -> str:
    """Convenience function to redact log messages."""
    return _redactor.redact_string(message)
