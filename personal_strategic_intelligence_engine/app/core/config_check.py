"""Configuration readiness checker.

Provides a structured readiness report showing which parts of PSIE are configured.
"""
from enum import Enum
from typing import Dict, List, Any
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ReadinessStatus(str, Enum):
    """System readiness status."""
    READY = "READY"
    PARTIAL = "PARTIAL"
    DISABLED = "DISABLED"
    MISSING = "MISSING"
    UNSAFE = "UNSAFE"


class ConfigChecker:
    """Provides configuration readiness report."""
    
    def __init__(self):
        self.settings = get_settings()
    
    def get_readiness_report(self) -> Dict[str, Any]:
        """Get full readiness report."""
        return {
            "overall": self._get_overall_status(),
            "core": self._check_core(),
            "database": self._check_database(),
            "llm": self._check_llm(),
            "workers": self._check_workers(),
            "connectors": self._check_connectors(),
            "execution": self._check_execution(),
            "debate": self._check_debate(),
            "learning": self._check_learning(),
            "signals": self._check_signals(),
            "safety": self._check_safety(),
        }
    
    def _get_overall_status(self) -> Dict[str, Any]:
        """Determine overall system readiness."""
        issues = []
        
        # Check critical components
        if not self.settings.database_url:
            issues.append("Database not configured")
        
        if not self.settings.has_valid_llm_provider:
            issues.append("No LLM provider configured")
        
        if self.settings.system_execution_enabled and not self.settings.enable_kill_switch:
            issues.append("Execution enabled without kill switch")
        
        if issues:
            return {
                "status": ReadinessStatus.MISSING if len(issues) > 1 else ReadinessStatus.PARTIAL,
                "issues": issues,
                "message": "System has configuration issues that need attention"
            }
        
        return {
            "status": ReadinessStatus.READY,
            "issues": [],
            "message": "System is ready to run"
        }
    
    def _check_core(self) -> Dict[str, Any]:
        """Check core application configuration."""
        issues = []
        
        if self.settings.secret_key == "changeme-insecure-default-key":
            issues.append("SECRET_KEY is using default value")
        
        return {
            "status": ReadinessStatus.WARNING if issues else ReadinessStatus.READY,
            "app_name": self.settings.app_name,
            "app_env": self.settings.app_env,
            "debug": self.settings.debug,
            "issues": issues,
        }
    
    def _check_database(self) -> Dict[str, Any]:
        """Check database configuration."""
        has_database = bool(self.settings.database_url)
        
        return {
            "status": ReadinessStatus.READY if has_database else ReadinessStatus.MISSING,
            "configured": has_database,
            "url_configured": bool(self.settings.database_url),
        }
    
    def _check_llm(self) -> Dict[str, Any]:
        """Check LLM provider configuration."""
        providers = []
        
        if self.settings.openai_api_key:
            providers.append({
                "name": "OpenAI",
                "configured": True,
                "model": self.settings.openai_model,
            })
        else:
            providers.append({
                "name": "OpenAI",
                "configured": False,
            })
        
        if self.settings.anthropic_api_key:
            providers.append({
                "name": "Anthropic",
                "configured": True,
                "model": self.settings.anthropic_model,
            })
        else:
            providers.append({
                "name": "Anthropic",
                "configured": False,
            })
        
        has_provider = self.settings.has_valid_llm_provider
        
        return {
            "status": ReadinessStatus.READY if has_provider else ReadinessStatus.MISSING,
            "default_provider": self.settings.llm_provider,
            "providers": providers,
        }
    
    def _check_workers(self) -> Dict[str, Any]:
        """Check worker configuration."""
        if not self.settings.enable_workers:
            return {
                "status": ReadinessStatus.DISABLED,
                "enabled": False,
            }
        
        return {
            "status": ReadinessStatus.PARTIAL,
            "enabled": True,
            "redis_configured": bool(self.settings.redis_url),
            "concurrency": self.settings.worker_concurrency,
        }
    
    def _check_connectors(self) -> Dict[str, Any]:
        """Check connector configurations."""
        connectors = {
            "email": {
                "enabled": self.settings.enable_email_connector,
                "configured": all([
                    self.settings.google_client_id,
                    self.settings.google_client_secret,
                ]),
            },
            "calendar": {
                "enabled": self.settings.enable_calendar_connector,
                "configured": all([
                    self.settings.google_calendar_client_id,
                    self.settings.google_calendar_client_secret,
                ]),
            },
            "todoist": {
                "enabled": self.settings.enable_todoist_connector,
                "configured": bool(self.settings.todoist_api_token),
            },
            "notion": {
                "enabled": self.settings.enable_notion_connector,
                "configured": bool(self.settings.notion_api_key),
            },
            "financial": {
                "enabled": self.settings.enable_financial_connector,
                "configured": any([
                    self.settings.schwab_client_id,
                    self.settings.interactive_brokers_host,
                    self.settings.coinbase_api_key,
                ]),
            },
        }
        
        enabled = [k for k, v in connectors.items() if v["enabled"]]
        
        return {
            "status": ReadinessStatus.PARTIAL if enabled else ReadinessStatus.DISABLED,
            "connectors": connectors,
            "enabled_count": len(enabled),
        }
    
    def _check_execution(self) -> Dict[str, Any]:
        """Check execution configuration."""
        return {
            "status": ReadinessStatus.READY if not self.settings.system_execution_enabled else ReadinessStatus.PARTIAL,
            "enabled": self.settings.system_execution_enabled,
            "manual_approval_required": self.settings.manual_approval_required,
            "kill_switch_enabled": self.settings.enable_kill_switch,
            "max_daily_actions": self.settings.max_daily_actions,
            "max_trade_size": self.settings.max_trade_size,
            "max_transfer_amount": self.settings.max_transfer_amount,
            "risk_threshold": self.settings.risk_score_threshold,
            "safe_mode": not self.settings.system_execution_enabled,
        }
    
    def _check_debate(self) -> Dict[str, Any]:
        """Check debate engine configuration."""
        return {
            "status": ReadinessStatus.READY,
            "max_rounds": self.settings.debate_max_rounds,
            "agent_timeout": self.settings.debate_agent_timeout_seconds,
            "argument_length_limit": self.settings.debate_max_argument_length,
            "consensus_strong": self.settings.consensus_strong_threshold,
            "consensus_moderate": self.settings.consensus_moderate_threshold,
        }
    
    def _check_learning(self) -> Dict[str, Any]:
        """Check learning layer configuration."""
        return {
            "status": ReadinessStatus.READY,
            "enabled": self.settings.enable_learning,
            "pattern_confidence_threshold": self.settings.pattern_confidence_threshold,
            "max_weight_adjustment": self.settings.max_weight_adjustment_per_cycle,
            "min_data_required": self.settings.min_data_before_recalibration,
        }
    
    def _check_signals(self) -> Dict[str, Any]:
        """Check signal provider configuration."""
        providers = []
        
        if self.settings.alphavantage_api_key:
            providers.append("AlphaVantage")
        if self.settings.polygon_api_key:
            providers.append("Polygon")
        if self.settings.fred_api_key:
            providers.append("FRED")
        
        return {
            "status": ReadinessStatus.PARTIAL if providers else ReadinessStatus.DISABLED,
            "providers": providers,
            "configured_count": len(providers),
        }
    
    def _check_safety(self) -> Dict[str, Any]:
        """Check overall safety posture."""
        issues = []
        
        if self.settings.system_execution_enabled:
            if not self.settings.enable_kill_switch:
                issues.append("Kill switch is disabled")
            if not self.settings.manual_approval_required:
                issues.append("Manual approval is not required")
            if self.settings.risk_score_threshold > 0.9:
                issues.append("Risk score threshold is too high")
        
        if self.settings.secret_key == "changeme-insecure-default-key":
            issues.append("Default secret key in use")
        
        return {
            "status": ReadinessStatus.UNSAFE if issues else ReadinessStatus.READY,
            "issues": issues,
            "execution_enabled": self.settings.system_execution_enabled,
            "auth_enabled": self.settings.enable_auth,
        }


def get_readiness_report() -> Dict[str, Any]:
    """Get configuration readiness report."""
    checker = ConfigChecker()
    return checker.get_readiness_report()
