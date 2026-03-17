"""
BB-APP-002: Settings Service

Per BB-APP-002 Section 8.9 - Settings Integration.
"""

from typing import Optional

from app.read_models import (
    SettingsReadModel,
    UserPreferences,
)
from app.commands import (
    UpdateUserPreferencesCommand,
    SettingsCommandHandler,
)


class SettingsService:
    """Service for user settings."""
    
    # Mock settings store
    _settings = {
        "user-1": {
            "user_id": "user-1",
            "email": "user@example.com",
            "username": "johndoe",
            "preferences": {
                "default_horizon": "weekly",
                "operating_style": "balanced",
                "notification_preference": "digest",
                "theme": "system"
            },
            "integrations": []
        }
    }
    
    async def get_settings(self, user_id: str) -> Optional[SettingsReadModel]:
        """Get user settings."""
        settings = self._settings.get(user_id)
        if not settings:
            return None
        
        return SettingsReadModel(
            user_id=settings["user_id"],
            email=settings["email"],
            username=settings["username"],
            preferences=UserPreferences(**settings["preferences"]),
            integrations=settings.get("integrations", [])
        )
    
    async def update_preferences(
        self,
        user_id: str,
        default_horizon: Optional[str] = None,
        operating_style: Optional[str] = None,
        notification_preference: Optional[str] = None,
        theme: Optional[str] = None
    ) -> bool:
        """Update user preferences."""
        handler = SettingsCommandHandler()
        command = UpdateUserPreferencesCommand(
            user_id=user_id,
            default_horizon=default_horizon,
            operating_style=operating_style,
            notification_preference=notification_preference,
            theme=theme
        )
        result = handler.handle_update_preferences(command)
        
        if result.success and user_id in self._settings:
            prefs = self._settings[user_id]["preferences"]
            if default_horizon:
                prefs["default_horizon"] = default_horizon
            if operating_style:
                prefs["operating_style"] = operating_style
            if notification_preference:
                prefs["notification_preference"] = notification_preference
            if theme:
                prefs["theme"] = theme
        
        return result.success
    
    async def update_profile(
        self,
        user_id: str,
        email: Optional[str] = None,
        username: Optional[str] = None
    ) -> bool:
        """Update user profile."""
        if user_id in self._settings:
            if email:
                self._settings[user_id]["email"] = email
            if username:
                self._settings[user_id]["username"] = username
            return True
        return False


# Singleton instance
settings_service = SettingsService()
