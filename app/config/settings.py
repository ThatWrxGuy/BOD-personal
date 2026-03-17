"""
BB-APP-001: Application Configuration

Environment-based configuration following BB-APP-001 Section 13.
"""

import os
from functools import lru_cache
from typing import Optional


class Settings:
    """Application settings."""
    
    # App
    APP_NAME: str = "Busy Bee"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://busybee:busybee@localhost:5432/busybee"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
    ]
    
    # Email (for notifications)
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    
    # External APIs
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Feature flags
    ENABLE_SCHEDULER: bool = os.getenv("ENABLE_SCHEDULER", "false").lower() == "true"
    ENABLE_NOTIFICATIONS: bool = os.getenv("ENABLE_NOTIFICATIONS", "true").lower() == "true"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    def __init__(self):
        """Validate settings."""
        # Validate required settings
        if self.DEBUG:
            self.CORS_ORIGINS = ["*"]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings()


# Export convenience
settings = get_settings()
