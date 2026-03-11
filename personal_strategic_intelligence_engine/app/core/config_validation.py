"""Configuration validation module.

Validates configuration before application startup.
"""
from typing import List, Tuple
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


class ConfigValidator:
    """Validates application configuration."""
    
    def __init__(self):
        self.settings = get_settings()
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """Run all validations.
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self._validate_core_required()
        self._validate_optional_connectors()
        self._validate_execution_safety()
        self._validate_workers()
        
        is_valid = len(self.errors) == 0
        
        return is_valid, self.errors, self.warnings
    
    def _validate_core_required(self) -> None:
        """Validate core required settings."""
        
        # Check secret key is not default
        if self.settings.secret_key == "changeme-insecure-default-key":
            self.errors.append(
                "SECRET_KEY is using the default insecure value. "
                "Please set a strong secret key in production."
            )
        
        # Check database URL is configured
        if not self.settings.database_url or "localhost" in self.settings.database_url:
            # This is OK for local dev, just warn
            self.warnings.append(
                "DATABASE_URL appears to be using localhost. "
                "Ensure PostgreSQL is running locally or configure a remote database."
            )
        
        # Check LLM provider
        if not self.settings.has_valid_llm_provider:
            self.errors.append(
                f"No valid LLM provider configured. "
                f"Please set {self.settings.llm_provider.upper()}_API_KEY "
                f"or switch to a configured provider."
            )
    
    def _validate_optional_connectors(self) -> None:
        """Validate optional connector configurations."""
        
        # Email connector
        if self.settings.enable_email_connector:
            if not self.settings.google_client_id:
                self.errors.append("ENABLE_EMAIL_CONNECTOR is true but GOOGLE_CLIENT_ID is missing")
            if not self.settings.google_client_secret:
                self.errors.append("ENABLE_EMAIL_CONNECTOR is true but GOOGLE_CLIENT_SECRET is missing")
            if not self.settings.google_redirect_uri:
                self.warnings.append("ENABLE_EMAIL_CONNECTOR is true but GOOGLE_REDIRECT_URI is not set")
        else:
            self.warnings.append("Email connector is disabled (ENABLE_EMAIL_CONNECTOR=false)")
        
        # Calendar connector
        if self.settings.enable_calendar_connector:
            if not self.settings.google_calendar_client_id:
                self.errors.append("ENABLE_CALENDAR_CONNECTOR is true but GOOGLE_CALENDAR_CLIENT_ID is missing")
            if not self.settings.google_calendar_client_secret:
                self.errors.append("ENABLE_CALENDAR_CONNECTOR is true but GOOGLE_CALENDAR_CLIENT_SECRET is missing")
        else:
            self.warnings.append("Calendar connector is disabled (ENABLE_CALENDAR_CONNECTOR=false)")
        
        # Todoist connector
        if self.settings.enable_todoist_connector:
            if not self.settings.todoist_api_token:
                self.errors.append("ENABLE_TODOIST_CONNECTOR is true but TODOIST_API_TOKEN is missing")
        else:
            self.warnings.append("Todoist connector is disabled (ENABLE_TODOIST_CONNECTOR=false)")
        
        # Notion connector
        if self.settings.enable_notion_connector:
            if not self.settings.notion_api_key:
                self.errors.append("ENABLE_NOTION_CONNECTOR is true but NOTION_API_KEY is missing")
            if not self.settings.notion_database_id:
                self.warnings.append("ENABLE_NOTION_CONNECTOR is true but NOTION_DATABASE_ID is not set")
        else:
            self.warnings.append("Notion connector is disabled (ENABLE_NOTION_CONNECTOR=false)")
        
        # Financial connector
        if self.settings.enable_financial_connector:
            # At least one financial provider should be configured
            has_provider = any([
                self.settings.schwab_client_id,
                self.settings.interactive_brokers_host,
                self.settings.coinbase_api_key,
            ])
            if not has_provider:
                self.warnings.append(
                    "ENABLE_FINANCIAL_CONNECTOR is true but no financial provider "
                    "(Schwab, Interactive Brokers, or Coinbase) is configured"
                )
        else:
            self.warnings.append("Financial connector is disabled (ENABLE_FINANCIAL_CONNECTOR=false)")
    
    def _validate_execution_safety(self) -> None:
        """Validate execution safety settings."""
        
        if self.settings.system_execution_enabled:
            # Execution is enabled - check safety measures
            if not self.settings.manual_approval_required:
                self.warnings.append(
                    "SYSTEM_EXECUTION_ENABLED is true but MANUAL_APPROVAL_REQUIRED is false. "
                    "Consider enabling manual approval for safety."
                )
            
            if not self.settings.enable_kill_switch:
                self.errors.append(
                    "SYSTEM_EXECUTION_ENABLED is true but ENABLE_KILL_SWITCH is false. "
                    "Kill switch must be enabled for safety."
                )
            
            if self.settings.max_daily_actions <= 0:
                self.errors.append("MAX_DAILY_ACTIONS must be greater than 0 when execution is enabled")
            
            if self.settings.max_trade_size <= 0:
                self.warnings.append("MAX_TRADE_SIZE should be greater than 0")
            
            if self.settings.risk_score_threshold <= 0 or self.settings.risk_score_threshold > 1:
                self.errors.append("RISK_SCORE_THRESHOLD must be between 0 and 1")
        else:
            logger.info("Execution is disabled - safe mode active")
    
    def _validate_workers(self) -> None:
        """Validate worker configuration."""
        
        if self.settings.enable_workers:
            if not self.settings.redis_url:
                self.errors.append("ENABLE_WORKERS is true but REDIS_URL is not configured")
            self.warnings.append("Background workers are enabled - ensure Redis is running")
        else:
            logger.info("Background workers are disabled")
    
    def raise_on_errors(self) -> None:
        """Raise exception if there are validation errors."""
        is_valid, errors, warnings = self.validate_all()
        
        for warning in warnings:
            logger.warning(f"Config warning: {warning}")
        
        if not is_valid:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            logger.error(error_msg)
            raise ConfigValidationError(error_msg)
        
        logger.info("Configuration validation passed")


def validate_config() -> Tuple[bool, List[str], List[str]]:
    """Validate configuration.
    
    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    validator = ConfigValidator()
    return validator.validate_all()


def validate_and_raise() -> None:
    """Validate configuration and raise on errors."""
    validator = ConfigValidator()
    validator.raise_on_errors()
