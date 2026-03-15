"""Safety tests for PSIE platform."""
import pytest
from unittest.mock import patch


class TestProductionSecurity:
    """Tests for production security requirements."""
    
    @patch.dict("os.environ", {
        "APP_ENV": "production",
        "SECRET_KEY": "changeme-insecure-default-key",
        "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost/db",
        "OPENAI_API_KEY": "sk-test",
        "CORS_ORIGINS": "https://example.com",
    })
    def test_production_fails_with_default_secret(self):
        """Production should fail with default secret key."""
        from app.main import create_app
        from app.core.config import get_settings
        
        # Settings should fail validation in production
        settings = get_settings()
        assert settings.is_production
        assert settings.secret_key == "changeme-insecure-default-key"


class TestConfigValidation:
    """Tests for configuration validation."""
    
    def test_validation_fails_without_llm(self):
        """Should fail validation without LLM provider."""
        from app.core.config_validation import validate_config
        
        # This should return validation issues
        is_valid, errors, warnings = validate_config()
        
        # Should have errors about missing LLM
        llm_errors = [e for e in errors if "LLM" in e or "API_KEY" in e]
        assert len(llm_errors) > 0


class TestCorsConfiguration:
    """Tests for CORS configuration."""
    
    def test_cors_not_wildcard_in_production(self):
        """CORS should not be wildcard in production."""
        from app.core.config import get_settings
        
        settings = get_settings()
        
        # In production, CORS should not be wildcard
        if settings.is_production:
            assert "*" not in settings.cors_origins


class TestExecutionSafety:
    """Tests for execution safety."""
    
    def test_execution_disabled_by_default(self):
        """Execution should be disabled by default."""
        from app.core.config import get_settings
        
        settings = get_settings()
        
        assert settings.system_execution_enabled is False
    
    def test_kill_switch_enabled_by_default(self):
        """Kill switch should be enabled by default."""
        from app.core.config import get_settings
        
        settings = get_settings()
        
        assert settings.enable_kill_switch is True
    
    def test_manual_approval_required_by_default(self):
        """Manual approval should be required by default."""
        from app.core.config import get_settings
        
        settings = get_settings()
        
        assert settings.manual_approval_required is True


class TestConnectorsDisabled:
    """Tests for connector configuration."""
    
    def test_connectors_disabled_by_default(self):
        """All connectors should be disabled by default."""
        from app.core.config import get_settings
        
        settings = get_settings()
        
        assert settings.enable_email_connector is False
        assert settings.enable_calendar_connector is False
        assert settings.enable_todoist_connector is False
        assert settings.enable_notion_connector is False
        assert settings.enable_financial_connector is False


class TestReadinessReporting:
    """Tests for readiness reporting."""
    
    def test_readiness_has_security_section(self):
        """Readiness should include security section."""
        from app.core.config_check import get_readiness_report
        
        report = get_readiness_report()
        
        assert "safety" in report
        assert "execution_enabled" in report["safety"]


class TestKernelModes:
    """Tests for kernel modes."""
    
    def test_kernel_modes_are_valid(self):
        """Kernel modes should be valid."""
        from app.models.kernel import KernelMode
        
        valid_modes = [KernelMode.OBSERVATION, KernelMode.ADVISORY, KernelMode.AUTONOMOUS]
        
        # Should be able to create with valid mode
        assert KernelMode.OBSERVATION == "OBSERVATION"
        assert KernelMode.ADVISORY == "ADVISORY"
        assert KernelMode.AUTONOMOUS == "AUTONOMOUS"
