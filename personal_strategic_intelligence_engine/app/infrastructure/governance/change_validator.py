"""Change Validator.

This module validates code changes proposed by OpenHands before they can be
applied to the repository. It ensures syntax, security, and architecture compliance.
"""
import ast
import re
from typing import Any, Optional
from dataclasses import dataclass
from enum import Enum

from app.core.logging import get_logger

logger = get_logger(__name__)


class ValidationStatus(Enum):
    """Status of validation."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    check: str
    status: ValidationStatus
    message: str
    details: Optional[dict] = None


class ChangeValidator:
    """Validates code changes before execution."""

    def __init__(self):
        """Initialize the change validator."""
        self.sandbox_dir = "/sandbox/proposals"
        
    async def validate_patch(
        self,
        code: str,
        file_path: Optional[str] = None,
        language: str = "python"
    ) -> dict[str, Any]:
        """Validate a code patch.
        
        Args:
            code: The code to validate
            file_path: Optional file path
            language: Programming language
            
        Returns:
            Validation results
        """
        results = []
        
        # Syntax validation
        syntax_result = self._validate_syntax(code, language)
        results.append(syntax_result)
        
        # Security scan
        security_result = self._validate_security(code)
        results.append(security_result)
        
        # Dependency safety
        dependency_result = self._validate_dependencies(code, language)
        results.append(dependency_result)
        
        # Architecture rules
        architecture_result = self._validate_architecture(code, file_path)
        results.append(architecture_result)
        
        # Overall status
        overall = self._calculate_overall_status(results)
        
        return {
            "valid": overall != ValidationStatus.FAILED,
            "overall_status": overall.value,
            "checks": [self._result_to_dict(r) for r in results],
            "file_path": file_path,
        }

    def _validate_syntax(self, code: str, language: str) -> ValidationResult:
        """Validate syntax of the code."""
        if language.lower() != "python":
            return ValidationResult(
                check="syntax",
                status=ValidationStatus.SKIPPED,
                message=f"Syntax validation not implemented for {language}"
            )
        
        try:
            ast.parse(code)
            return ValidationResult(
                check="syntax",
                status=ValidationStatus.PASSED,
                message="Python syntax is valid"
            )
        except SyntaxError as e:
            return ValidationResult(
                check="syntax",
                status=ValidationStatus.FAILED,
                message=f"Syntax error: {str(e)}",
                details={"line": e.lineno, "offset": e.offset}
            )
        except Exception as e:
            return ValidationResult(
                check="syntax",
                status=ValidationStatus.FAILED,
                message=f"Syntax validation error: {str(e)}"
            )

    def _validate_security(self, code: str) -> ValidationResult:
        """Scan code for security issues."""
        issues = []
        
        # Check for dangerous patterns
        dangerous_patterns = {
            r"eval\s*\(": "Use of eval() is dangerous",
            r"exec\s*\(": "Use of exec() is dangerous",
            r"__import__\s*\(": "Dynamic imports can be dangerous",
            r"subprocess\.call\s*\(": "subprocess.call should be reviewed",
            r"subprocess\.run\s*\(": "subprocess.run should be reviewed",
            r"os\.system\s*\(": "os.system is dangerous",
            r"shutil\.rmtree\s*\(": "rmtree can delete important files",
            r"open\s*\([^)]*['\"]w['\"]": "File write operations should be reviewed",
        }
        
        for pattern, message in dangerous_patterns.items():
            if re.search(pattern, code):
                issues.append(message)
        
        # Check for hardcoded secrets
        secret_patterns = [
            (r"api_key\s*=\s*['\"][^'\"]+['\"]", "Potential hardcoded API key"),
            (r"password\s*=\s*['\"][^'\"]+['\"]", "Potential hardcoded password"),
            (r"token\s*=\s*['\"][^'\"]+['\"]", "Potential hardcoded token"),
            (r"secret\s*=\s*['\"][^'\"]+['\"]", "Potential hardcoded secret"),
        ]
        
        for pattern, message in secret_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for _ in matches:
                issues.append(message)
        
        if issues:
            return ValidationResult(
                check="security",
                status=ValidationStatus.FAILED,
                message="Security issues found",
                details={"issues": issues}
            )
        
        return ValidationResult(
            check="security",
            status=ValidationStatus.PASSED,
            message="No security issues detected"
        )

    def _validate_dependencies(self, code: str, language: str) -> ValidationResult:
        """Validate dependencies are safe."""
        if language.lower() != "python":
            return ValidationResult(
                check="dependencies",
                status=ValidationStatus.SKIPPED,
                message=f"Dependency validation not implemented for {language}"
            )
        
        # Check for imports
        imports = []
        
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except:
            pass
        
        # Check for dangerous imports
        dangerous_imports = {
            "os": "os module can access system resources",
            "sys": "sys module can access system state",
            "subprocess": "subprocess can execute commands",
            "socket": "socket can create network connections",
            "requests": "requests can make HTTP calls",
            "urllib": "urllib can make HTTP calls",
        }
        
        warnings = []
        for imp in imports:
            if imp in dangerous_imports:
                warnings.append(f"{imp}: {dangerous_imports[imp]}")
        
        if warnings:
            return ValidationResult(
                check="dependencies",
                status=ValidationStatus.WARNING,
                message="Review required for system imports",
                details={"warnings": warnings}
            )
        
        return ValidationResult(
            check="dependencies",
            status=ValidationStatus.PASSED,
            message="No dangerous dependencies detected"
        )

    def _validate_architecture(self, code: str, file_path: Optional[str]) -> ValidationResult:
        """Validate architecture rules."""
        if not file_path:
            return ValidationResult(
                check="architecture",
                status=ValidationStatus.WARNING,
                message="File path not provided, skipping architecture validation"
            )
        
        # Check file path follows project conventions
        if ".." in file_path:
            return ValidationResult(
                check="architecture",
                status=ValidationStatus.FAILED,
                message="Path traversal detected (.. not allowed)"
            )
        
        # Check for proper module structure
        if file_path.startswith("app/"):
            # Should be a proper module
            if not file_path.endswith(".py") and not file_path.endswith("__init__.py"):
                # Check if it's a directory that should have __init__.py
                pass  # This is just a warning
        
        return ValidationResult(
            check="architecture",
            status=ValidationStatus.PASSED,
            message="Architecture rules satisfied"
        )

    def _calculate_overall_status(self, results: list[ValidationResult]) -> ValidationStatus:
        """Calculate overall validation status."""
        has_failed = False
        has_warning = False
        
        for result in results:
            if result.status == ValidationStatus.FAILED:
                has_failed = True
            elif result.status == ValidationStatus.WARNING:
                has_warning = True
        
        if has_failed:
            return ValidationStatus.FAILED
        elif has_warning:
            return ValidationStatus.WARNING
        else:
            return ValidationStatus.PASSED

    def _result_to_dict(self, result: ValidationResult) -> dict:
        """Convert validation result to dictionary."""
        return {
            "check": result.check,
            "status": result.status.value,
            "message": result.message,
            "details": result.details,
        }

    async def validate_test_coverage(self, code: str) -> dict[str, Any]:
        """Validate that code has test coverage.
        
        Args:
            code: Code to check
            
        Returns:
            Test coverage validation results
        """
        # Check for test functions
        has_tests = "def test_" in code or "async def test_" in code
        has_asserts = "assert " in code
        
        if has_tests and has_asserts:
            status = ValidationStatus.PASSED
            message = "Test coverage detected"
        elif has_tests:
            status = ValidationStatus.WARNING
            message = "Test functions found but no assertions"
        else:
            status = ValidationStatus.WARNING
            message = "No test coverage detected"
        
        return {
            "check": "test_coverage",
            "status": status.value,
            "message": message,
            "has_tests": has_tests,
            "has_asserts": has_asserts,
        }

    def save_to_sandbox(self, code: str, proposal_id: str, file_path: str) -> dict[str, Any]:
        """Save proposed code to sandbox directory.
        
        Args:
            code: The code to save
            proposal_id: The proposal ID
            file_path: The intended file path
            
        Returns:
            Save result
        """
        import os
        
        # Create sandbox directory if needed
        sandbox_path = os.path.join(self.sandbox_dir, proposal_id)
        
        try:
            os.makedirs(sandbox_path, exist_ok=True)
            
            # Save the code
            actual_path = os.path.join(sandbox_path, file_path.lstrip("/"))
            os.makedirs(os.path.dirname(actual_path), exist_ok=True)
            
            with open(actual_path, "w") as f:
                f.write(code)
            
            return {
                "success": True,
                "sandbox_path": actual_path,
                "message": "Code saved to sandbox"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to save to sandbox"
            }


# Global instance
_change_validator: Optional[ChangeValidator] = None


def get_change_validator() -> ChangeValidator:
    """Get the change validator instance."""
    global _change_validator
    
    if _change_validator is None:
        _change_validator = ChangeValidator()
    
    return _change_validator
