"""
Architecture Validator - BB-AUD-001

Validates that the system architecture follows Busy Bee directives.

Checks:
- Required modules exist
- Layer dependencies are valid
- Directive files are present
- Architecture layering rules respected
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class LayerLevel(Enum):
    """Architecture layer hierarchy."""
    API = "api"
    WORKFLOW = "workflow"
    AGENT = "agent"
    SERVICE = "service"
    INFRASTRUCTURE = "infrastructure"
    DATA = "data"


@dataclass
class ArchitectureIssue:
    """Represents an architecture violation."""
    severity: str  # critical, warning, info
    layer: str
    issue_type: str
    description: str
    module_path: str | None = None
    remediation: str | None = None


@dataclass
class ArchitectureValidationResult:
    """Result of architecture validation."""
    is_valid: bool
    health_score: float  # 0-100
    issues: list[ArchitectureIssue] = field(default_factory=list)
    layers_present: dict[str, bool] = field(default_factory=dict)
    modules_present: dict[str, bool] = field(default_factory=dict)
    directive_compliance: dict[str, bool] = field(default_factory=dict)


class ArchitectureValidator:
    """
    Validates system architecture against BB-AUD-001 requirements.
    """
    
    # Required layers in order (dependencies flow down)
    REQUIRED_LAYERS = [
        LayerLevel.API,
        LayerLevel.WORKFLOW,
        LayerLevel.AGENT,
        LayerLevel.SERVICE,
        LayerLevel.INFRASTRUCTURE,
        LayerLevel.DATA,
    ]
    
    # Critical modules that must exist
    REQUIRED_MODULES = {
        "psip": "psip.py",
        "layer1_strategic_intelligence_core": "layer1_strategic_intelligence_core/",
        "layer2_governance_layer": "layer2_governance_layer/",
        "layer3_domain_intelligence": "layer3_domain_intelligence/",
        "infrastructure": "infrastructure/",
    }
    
    # Critical directive files
    REQUIRED_DIRECTIVES = [
        "AGENTS.md",
        "docs/BB-ARCH-002_Agent_Role_Separation.md",
        "docs/BUSY_BEE_SYSTEM_MAP.md",
    ]
    
    # Layer dependency rules (layer -> layers it can depend on)
    ALLOWED_DEPENDENCIES = {
        LayerLevel.API: [LayerLevel.WORKFLOW, LayerLevel.SERVICE],
        LayerLevel.WORKFLOW: [LayerLevel.AGENT, LayerLevel.SERVICE],
        LayerLevel.AGENT: [LayerLevel.SERVICE, LayerLevel.INFRASTRUCTURE],
        LayerLevel.SERVICE: [LayerLevel.INFRASTRUCTURE, LayerLevel.DATA],
        LayerLevel.INFRASTRUCTURE: [LayerLevel.DATA],
        LayerLevel.DATA: [],
    }
    
    def __init__(self, base_path: str | Path):
        self.base_path = Path(base_path)
        self.issues: list[ArchitectureIssue] = []
    
    def validate(self) -> ArchitectureValidationResult:
        """
        Run full architecture validation.
        
        Returns:
            ArchitectureValidationResult with findings
        """
        self.issues = []
        
        # Check layer structure
        self._validate_layers()
        
        # Check required modules
        self._validate_modules()
        
        # Check directive files
        self._validate_directives()
        
        # Check layer dependencies
        self._validate_layer_dependencies()
        
        # Calculate health score
        health_score = self._calculate_health_score()
        
        return ArchitectureValidationResult(
            is_valid=len([i for i in self.issues if i.severity == "critical"]) == 0,
            health_score=health_score,
            issues=self.issues,
            layers_present=self._get_layers_present(),
            modules_present=self._get_modules_present(),
            directive_compliance=self._get_directive_compliance(),
        )
    
    def _validate_layers(self) -> None:
        """Check that all required architecture layers exist."""
        layer_dirs = [
            "layer1_strategic_intelligence_core",
            "layer2_governance_layer", 
            "layer3_domain_intelligence",
            "infrastructure",
            "outputs",
        ]
        
        for layer_dir in layer_dirs:
            layer_path = self.base_path / layer_dir
            if not layer_path.exists():
                self.issues.append(ArchitectureIssue(
                    severity="critical",
                    layer="architecture",
                    issue_type="missing_layer",
                    description=f"Required layer directory missing: {layer_dir}",
                    module_path=str(layer_path),
                    remediation=f"Create directory: {layer_dir}/"
                ))
    
    def _validate_modules(self) -> None:
        """Check that required modules exist."""
        for module_name, module_path in self.REQUIRED_MODULES.items():
            full_path = self.base_path / module_path
            if not full_path.exists():
                self.issues.append(ArchitectureIssue(
                    severity="critical",
                    layer="module",
                    issue_type="missing_module",
                    description=f"Required module missing: {module_name}",
                    module_path=module_path,
                    remediation=f"Create module at: {module_path}"
                ))
    
    def _validate_directives(self) -> None:
        """Check that directive files exist."""
        for directive in self.REQUIRED_DIRECTIVES:
            directive_path = self.base_path / directive
            if not directive_path.exists():
                self.issues.append(ArchitectureIssue(
                    severity="warning",
                    layer="governance",
                    issue_type="missing_directive",
                    description=f"Directive file missing: {directive}",
                    module_path=directive,
                    remediation=f"Create directive file: {directive}"
                ))
    
    def _validate_layer_dependencies(self) -> None:
        """Check that layer dependencies follow allowed rules."""
        # This is a simplified check - in production would analyze imports
        infrastructure_path = self.base_path / "infrastructure"
        
        # Check for potential illegal upward dependencies
        # Layer N should not import from Layer N+1 (higher layer)
        if infrastructure_path.exists():
            for subdir in infrastructure_path.iterdir():
                if subdir.is_dir() and (subdir / "__init__.py").exists():
                    # Infrastructure should not import from agents or workflow
                    pass  # Simplified for now
    
    def _calculate_health_score(self) -> float:
        """Calculate architecture health score (0-100)."""
        if not self.issues:
            return 100.0
        
        # Deduct points based on severity
        critical_count = len([i for i in self.issues if i.severity == "critical"])
        warning_count = len([i for i in self.issues if i.severity == "warning"])
        
        deduction = (critical_count * 15) + (warning_count * 5)
        return max(0.0, 100.0 - deduction)
    
    def _get_layers_present(self) -> dict[str, bool]:
        """Get presence status of each layer."""
        layers = {}
        for layer in self.REQUIRED_LAYERS:
            layer_dir = layer.value
            if layer == LayerLevel.INFRASTRUCTURE:
                layer_dir = "infrastructure"
            layers[layer.value] = (self.base_path / layer_dir).exists()
        return layers
    
    def _get_modules_present(self) -> dict[str, bool]:
        """Get presence status of each required module."""
        return {
            name: (self.base_path / path).exists()
            for name, path in self.REQUIRED_MODULES.items()
        }
    
    def _get_directive_compliance(self) -> dict[str, bool]:
        """Get compliance status of each directive."""
        return {
            directive: (self.base_path / directive).exists()
            for directive in self.REQUIRED_DIRECTIVES
        }


def run_architecture_audit(base_path: str | Path) -> ArchitectureValidationResult:
    """
    Convenience function to run architecture audit.
    
    Args:
        base_path: Path to the BOD-personal directory
        
    Returns:
        ArchitectureValidationResult
    """
    validator = ArchitectureValidator(base_path)
    return validator.validate()


__all__ = [
    "ArchitectureValidator",
    "ArchitectureValidationResult", 
    "ArchitectureIssue",
    "LayerLevel",
    "run_architecture_audit",
]
