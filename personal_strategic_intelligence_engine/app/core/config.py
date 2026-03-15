"""Application configuration module.

Loads configuration from environment variables with sensible defaults.
"""
import os
from functools import lru_cache
from typing import Optional, List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Allow extra env vars without breaking
    )

    # ===================
    # Application
    # ===================
    app_name: str = "Personal Strategic Intelligence Engine"
    app_version: str = "1.0.0"
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    debug: bool = False
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    api_base_url: str = "http://localhost:8000"

    # ===================
    # Security
    # ===================
    secret_key: str = Field(default="psie-secret-key-2026-production", validation_alias="SECRET_KEY")
    access_token_expire_minutes: int = 60
    enable_auth: bool = False
    cors_origins: str = "http://localhost:3000"
    
    # ===================
    # GitHub Integration
    # ===================
    github_token: Optional[str] = Field(default=None, validation_alias="GITHUB_TOKEN")

    # ===================
    # Database
    # ===================
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/strategic_board",
        validation_alias="DATABASE_URL",
    )
    database_url_sync: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/strategic_board",
        validation_alias="DATABASE_URL_SYNC",
    )

    # ===================
    # Redis / Workers
    # ===================
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    enable_workers: bool = False
    worker_concurrency: int = 4

    # ===================
    # LLM Provider
    # ===================
    llm_provider: str = Field(default="openai", validation_alias="LLM_PROVIDER")
    openai_api_key: Optional[str] = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_model: str = "gpt-4-turbo-preview"
    anthropic_api_key: Optional[str] = Field(default=None, validation_alias="ANTHROPIC_API_KEY")
    anthropic_model: str = "claude-3-opus-20240229"
    
    # ===================
    # OpenHands AI Provider
    # ===================
    openhands_api_key: Optional[str] = Field(default=None, validation_alias="OPENHANDS_API_KEY")

    # ===================
    # Signal / Data Providers
    # ===================
    alphavantage_api_key: Optional[str] = Field(default=None, validation_alias="ALPHAVANTAGE_API_KEY")
    polygon_api_key: Optional[str] = Field(default=None, validation_alias="POLYGON_API_KEY")
    fred_api_key: Optional[str] = Field(default=None, validation_alias="FRED_API_KEY")

    # ===================
    # Execution Safety Controls
    # ===================
    system_execution_enabled: bool = Field(default=False, validation_alias="SYSTEM_EXECUTION_ENABLED")
    manual_approval_required: bool = True
    max_daily_actions: int = 50
    max_trade_size: float = 10000.0
    max_transfer_amount: float = 5000.0
    max_daily_financial_exposure: float = 25000.0
    risk_score_threshold: float = 0.7
    enable_kill_switch: bool = True

    # ===================
    # Email Connector
    # ===================
    enable_email_connector: bool = Field(default=False, validation_alias="ENABLE_EMAIL_CONNECTOR")
    google_client_id: Optional[str] = Field(default=None, validation_alias="GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = Field(default=None, validation_alias="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: Optional[str] = Field(default=None, validation_alias="GOOGLE_REDIRECT_URI")
    google_email_sender: Optional[str] = Field(default=None, validation_alias="GOOGLE_EMAIL_SENDER")

    # ===================
    # Calendar Connector
    # ===================
    enable_calendar_connector: bool = Field(default=False, validation_alias="ENABLE_CALENDAR_CONNECTOR")
    google_calendar_client_id: Optional[str] = Field(default=None, validation_alias="GOOGLE_CALENDAR_CLIENT_ID")
    google_calendar_client_secret: Optional[str] = Field(default=None, validation_alias="GOOGLE_CALENDAR_CLIENT_SECRET")
    google_calendar_redirect_uri: Optional[str] = Field(default=None, validation_alias="GOOGLE_CALENDAR_REDIRECT_URI")
    google_calendar_id: Optional[str] = Field(default=None, validation_alias="GOOGLE_CALENDAR_ID")

    # ===================
    # Task Connectors
    # ===================
    enable_todoist_connector: bool = Field(default=False, validation_alias="ENABLE_TODOIST_CONNECTOR")
    todoist_api_token: Optional[str] = Field(default=None, validation_alias="TODOIST_API_TOKEN")
    enable_notion_connector: bool = Field(default=False, validation_alias="ENABLE_NOTION_CONNECTOR")
    notion_api_key: Optional[str] = Field(default=None, validation_alias="NOTION_API_KEY")
    notion_database_id: Optional[str] = Field(default=None, validation_alias="NOTION_DATABASE_ID")

    # ===================
    # Financial Connectors
    # ===================
    enable_financial_connector: bool = Field(default=False, validation_alias="ENABLE_FINANCIAL_CONNECTOR")
    schwab_client_id: Optional[str] = Field(default=None, validation_alias="SCHWAB_CLIENT_ID")
    schwab_client_secret: Optional[str] = Field(default=None, validation_alias="SCHWAB_CLIENT_SECRET")
    schwab_redirect_uri: Optional[str] = Field(default=None, validation_alias="SCHWAB_REDIRECT_URI")
    interactive_brokers_host: Optional[str] = Field(default=None, validation_alias="INTERACTIVE_BROKERS_HOST")
    interactive_brokers_port: Optional[int] = Field(default=None, validation_alias="INTERACTIVE_BROKERS_PORT")
    interactive_brokers_account_id: Optional[str] = Field(default=None, validation_alias="INTERACTIVE_BROKERS_ACCOUNT_ID")
    coinbase_api_key: Optional[str] = Field(default=None, validation_alias="COINBASE_API_KEY")
    coinbase_api_secret: Optional[str] = Field(default=None, validation_alias="COINBASE_API_SECRET")

    # ===================
    # Observability
    # ===================
    log_level: str = "INFO"
    log_format: str = "text"
    enable_structured_logging: bool = True
    sentry_dsn: Optional[str] = Field(default=None, validation_alias="SENTRY_DSN")

    # ===================
    # Debate Engine
    # ===================
    debate_max_rounds: int = 4
    debate_agent_timeout_seconds: int = 60
    debate_max_argument_length: int = 5000
    consensus_strong_threshold: float = 0.75
    consensus_moderate_threshold: float = 0.50

    # ===================
    # Learning Layer
    # ===================
    enable_learning: bool = True
    pattern_confidence_threshold: float = 0.5
    max_weight_adjustment_per_cycle: float = 0.1
    min_data_before_recalibration: int = 5

    # ===================
    # Forecasting / Simulation
    # ===================
    default_forecast_horizon_days: int = 90
    default_simulation_runs: int = 100
    enable_risk_projection: bool = True
    enable_goal_probability_model: bool = True

    # ===================
    # Scheduler
    # ===================
    scheduler_enabled: bool = False

    @field_validator("cors_origins")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in v.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env.lower() == "development"

    @property
    def has_valid_llm_provider(self) -> bool:
        """Check if at least one LLM provider is configured."""
        if self.llm_provider == "openai":
            return bool(self.openai_api_key)
        elif self.llm_provider == "anthropic":
            return bool(self.anthropic_api_key)
        return False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
