"""Secret manager for centralized secret access."""
import os
import re
from typing import Dict, List, Optional, Any

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class SecretManager:
    """Centralized secret access manager."""
    
    # Secret environment variable names to settings mapping
    SECRET_MAPPING = {
        # LLM
        "OPENAI_API_KEY": "openai_api_key",
        "ANTHROPIC_API_KEY": "anthropic_api_key",
        
        # GitHub
        "GITHUB_TOKEN": "github_token",
        
        # OpenHands
        "OPENHANDS_API_KEY": "openhands_api_key",
        
        # Data providers
        "ALPHAVANTAGE_API_KEY": "alphavantage_api_key",
        "POLYGON_API_KEY": "polygon_api_key",
        "FRED_API_KEY": "fred_api_key",
        
        # Email
        "GOOGLE_CLIENT_ID": "google_client_id",
        "GOOGLE_CLIENT_SECRET": "google_client_secret",
        "GOOGLE_REDIRECT_URI": "google_redirect_uri",
        "GOOGLE_EMAIL_SENDER": "google_email_sender",
        
        # Calendar
        "GOOGLE_CALENDAR_CLIENT_ID": "google_calendar_client_id",
        "GOOGLE_CALENDAR_CLIENT_SECRET": "google_calendar_client_secret",
        "GOOGLE_CALENDAR_REDIRECT_URI": "google_calendar_redirect_uri",
        "GOOGLE_CALENDAR_ID": "google_calendar_id",
        
        # Tasks
        "TODOIST_API_TOKEN": "todoist_api_token",
        "NOTION_API_KEY": "notion_api_key",
        "NOTION_DATABASE_ID": "notion_database_id",
        
        # Financial
        "SCHWAB_CLIENT_ID": "schwab_client_id",
        "SCHWAB_CLIENT_SECRET": "schwab_client_secret",
        "SCHWAB_REDIRECT_URI": "schwab_redirect_uri",
        "INTERACTIVE_BROKERS_HOST": "interactive_brokers_host",
        "INTERACTIVE_BROKERS_PORT": "interactive_brokers_port",
        "INTERACTIVE_BROKERS_ACCOUNT_ID": "interactive_brokers_account_id",
        "COINBASE_API_KEY": "coinbase_api_key",
        "COINBASE_API_SECRET": "coinbase_api_secret",
        
        # Security
        "SECRET_KEY": "secret_key",
        "SENTRY_DSN": "sentry_dsn",
    }
    
    def __init__(self):
        self.settings = get_settings()
        self._secret_cache: Dict[str, Optional[str]] = {}
    
    def get_secret(self, secret_name: str) -> Optional[str]:
        """Get a secret value by name."""
        
        # Check cache first
        if secret_name in self._secret_cache:
            return self._secret_cache[secret_name]
        
        # Try to get from settings
        setting_name = self.SECRET_MAPPING.get(secret_name)
        
        if setting_name:
            value = getattr(self.settings, setting_name, None)
            self._secret_cache[secret_name] = value
            return value
        
        # Fall back to environment
        value = os.environ.get(secret_name)
        self._secret_cache[secret_name] = value
        return value
    
    def has_secret(self, secret_name: str) -> bool:
        """Check if a secret is present."""
        
        value = self.get_secret(secret_name)
        return value is not None and value != ""
    
    def get_secrets(self, secret_names: List[str]) -> Dict[str, Optional[str]]:
        """Get multiple secrets."""
        
        return {name: self.get_secret(name) for name in secret_names}
    
    def validate_secret_group(self, secret_names: List[str]) -> Dict[str, bool]:
        """Validate a group of secrets."""
        
        return {name: self.has_secret(name) for name in secret_names}
    
    def is_secret_set(self, secret_name: str) -> bool:
        """Check if a secret is set and non-empty."""
        
        value = self.get_secret(secret_name)
        return bool(value and value.strip())


# Global secret manager
_secret_manager: Optional[SecretManager] = None


def get_secret_manager() -> SecretManager:
    """Get the global secret manager."""
    global _secret_manager
    
    if _secret_manager is None:
        _secret_manager = SecretManager()
    
    return _secret_manager
