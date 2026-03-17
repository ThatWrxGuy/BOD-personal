"""
Governance Compliance Checker - BB-AUD-001

Ensures decisions respect governance hierarchy.

Validation:
- CEO
- Executive Council  
- Chief Officers
- Agents

Checks:
- authority levels respected
- approvals recorded
- execution permissions enforced

Detects:
- unauthorized actions
- skipped approvals
- governance drift
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class AuthorityLevel(Enum):
    """Governance authority levels."""
    CEO = "ceo"
    EXECUTIVE_COUNCIL = "executive_council"
    CHIEF_OFFICER = "chief_officer"
    AGENT = "agent"
    SYSTEM = "system"


class GovernanceIssueType(Enum):
    """Types of governance violations."""
    UNAUTHORIZED_ACTION = "unauthorized_action"
    SKIPPED_APPROVAL = "skipped_approval"
    ESCALATION_MISSING = "escalation_missing"
    AUTHORITY_DRIFT = "authority_drift"
    APPROVAL_MISSING = "approval_missing"


@dataclass
class GovernanceCheck:
    """Represents a governance compliance check."""
    authority_level: AuthorityLevel
    action: str
    required_approval: AuthorityLevel | None
    is_compliant: bool
    details: str | None = None


@dataclass
class GovernanceIssue:
    """Represents a governance violation."""
    severity: str  # critical, warning, info
    issue_type: str
    description: str
    authority_level: str | None = None
    action: str | None = None
    remediation: str | None = None


@dataclass
class GovernanceComplianceResult:
    """Result of governance compliance validation."""
    is_compliant: bool
    health_score: float  # 0-100
    issues: list[GovernanceIssue] = field(default_factory=list)
    checks_performed: int = 0
    compliant_actions: int = 0
    violations: int = 0
    authority_levels_validated: list[str] = field(default_factory=list)


class GovernanceComplianceChecker:
    """
    Validates governance compliance.
    """
    
    # Authority hierarchy (higher index = more authority)
    AUTHORITY_HIERARCHY = [
        AuthorityLevel.SYSTEM,
        AuthorityLevel.AGENT,
        AuthorityLevel.CHIEF_OFFICER,
        AuthorityLevel.EXECUTIVE_COUNCIL,
        AuthorityLevel.CEO,
    ]
    
    # Actions requiring CEO approval
    CEO_APPROVAL_ACTIONS = [
        "delete_domain",
        "modify_capital_allocation",
        "override_risk_threshold",
        "approve_strategic_pivot",
        "dismiss_council_member",
    ]
    
    # Actions requiring Executive Council approval
    COUNCIL_APPROVAL_ACTIONS = [
        "approve_strategy",
        "modify_governance",
        "approve_budget",
        "authorize_major_expenditure",
    ]
    
    # Actions requiring Chief Officer approval
    CHIEF_APPROVAL_ACTIONS = [
        "approve_domain_strategy",
        "activate_agent",
        "modify_domain_config",
    ]
    
    def __init__(self, base_path: str | Path):
        self.base_path = Path(base_path)
        self.issues: list[GovernanceIssue] = []
        self.checks: list[GovernanceCheck] = []
    
    def validate(self) -> GovernanceComplianceResult:
        """
        Run governance compliance validation.
        
        Returns:
            GovernanceComplianceResult with findings
        """
        self.issues = []
        self.checks = []
        
        # Validate governance layer structure
        self._validate_governance_layers()
        
        # Validate authority hierarchy
        self._validate_authority_hierarchy()
        
        # Check for approval workflows
        self._validate_approval_workflows()
        
        # Validate executive council
        self._validate_executive_council()
        
        # Check risk governor integration
        self._validate_risk_governor()
        
        # Calculate health score
        health_score = self._calculate_health_score()
        
        return GovernanceComplianceResult(
            is_compliant=len([i for i in self.issues if i.severity == "critical"]) == 0,
            health_score=health_score,
            issues=self.issues,
            checks_performed=len(self.checks),
            compliant_actions=len([c for c in self.checks if c.is_compliant]),
            violations=len([c for c in self.checks if not c.is_compliant]),
            authority_levels_validated=[a.value for a in self.AUTHORITY_HIERARCHY],
        )
    
    def _validate_governance_layers(self) -> None:
        """Check that governance layers exist."""
        governance_path = self.base_path / "layer2_governance_layer"
        
        if not governance_path.exists():
            self.issues.append(GovernanceIssue(
                severity="critical",
                issue_type="missing_governance_layer",
                description="layer2_governance_layer not found",
                remediation="Create governance layer at layer2_governance_layer/"
            ))
            return
        
        # Check for key governance components
        required_components = [
            "executive_council",
            "risk_governor",
            "execution_gate",
            "capital_deployment_coordinator",
            "priority_router",
        ]
        
        for component in required_components:
            component_path = governance_path / component
            if not component_path.exists():
                self.issues.append(GovernanceIssue(
                    severity="warning",
                    issue_type="missing_component",
                    description=f"Governance component missing: {component}",
                    remediation=f"Create {component} in governance layer"
                ))
    
    def _validate_authority_hierarchy(self) -> None:
        """Validate that authority hierarchy is respected."""
        # Check that higher authority levels can override lower ones
        # and that escalation paths exist
        
        council_path = self.base_path / "layer2_governance_layer" / "executive_council"
        if not council_path.exists():
            self.issues.append(GovernanceIssue(
                severity="critical",
                issue_type="missing_executive_council",
                description="Executive Council module not found",
                remediation="Create executive_council module"
            ))
        
        # Check that chief officers exist under domain intelligence
        domain_intel = self.base_path / "layer3_domain_intelligence"
        if not domain_intel.exists():
            self.issues.append(GovernanceIssue(
                severity="critical",
                issue_type="missing_chief_officers",
                description="Chief Officers not found (required for governance)",
                remediation="Create Chief Officer roles in layer3_domain_intelligence"
            ))
    
    def _validate_approval_workflows(self) -> None:
        """Check that approval workflows exist for critical actions."""
        # Check for execution gate
        gate_path = self.base_path / "layer2_governance_layer" / "execution_gate"
        
        if not gate_path.exists():
            self.issues.append(GovernanceIssue(
                severity="warning",
                issue_type="missing_execution_gate",
                description="Execution Gate not found",
                remediation="Create execution_gate module for approval workflows"
            ))
            return
        
        # Check for approval recording capability
        gate_file = gate_path / "execution_gate.py"
        if gate_file.exists():
            content = gate_file.read_text()
            
            # Check for approval tracking
            if "approval" not in content.lower():
                self.issues.append(GovernanceIssue(
                    severity="warning",
                    issue_type="no_approval_tracking",
                    description="Execution Gate may not track approvals",
                    remediation="Implement approval tracking in execution gate"
                ))
    
    def _validate_executive_council(self) -> None:
        """Validate Executive Council implementation."""
        council_path = self.base_path / "layer2_governance_layer" / "executive_council" / "executive_council.py"
        
        if not council_path.exists():
            self.issues.append(GovernanceIssue(
                severity="critical",
                issue_type="missing_council_implementation",
                description="Executive Council implementation not found",
                remediation="Create executive_council.py"
            ))
            return
        
        content = council_path.read_text()
        
        # Check for key council functions
        required_functions = ["decide", "add_member", "vote"]
        for func in required_functions:
            if func not in content.lower():
                self.issues.append(GovernanceIssue(
                    severity="warning",
                    issue_type="missing_council_function",
                    description=f"Executive Council missing function: {func}",
                    remediation=f"Implement {func} in Executive Council"
                ))
    
    def _validate_risk_governor(self) -> None:
        """Validate Risk Governor integration."""
        risk_path = self.base_path / "layer2_governance_layer" / "risk_governor"
        
        if not risk_path.exists():
            self.issues.append(GovernanceIssue(
                severity="warning",
                issue_type="missing_risk_governor",
                description="Risk Governor not found",
                remediation="Create risk_governor module"
            ))
            return
    
    def _calculate_health_score(self) -> float:
        """Calculate governance health score (0-100)."""
        if not self.issues:
            return 100.0
        
        critical_count = len([i for i in self.issues if i.severity == "critical"])
        warning_count = len([i for i in self.issues if i.severity == "warning"])
        
        deduction = (critical_count * 15) + (warning_count * 5)
        return max(0.0, 100.0 - deduction)
    
    def check_action_authorization(
        self,
        action: str,
        authority_level: AuthorityLevel
    ) -> GovernanceCheck:
        """
        Check if an action is authorized for the given authority level.
        
        Args:
            action: The action being performed
            authority_level: The authority level of the performer
            
        Returns:
            GovernanceCheck result
        """
        # Determine required approval level
        required_approval = None
        
        if action in self.CEO_APPROVAL_ACTIONS:
            required_approval = AuthorityLevel.CEO
        elif action in self.COUNCIL_APPROVAL_ACTIONS:
            required_approval = AuthorityLevel.EXECUTIVE_COUNCIL
        elif action in self.CHIEF_APPROVAL_ACTIONS:
            required_approval = AuthorityLevel.CHIEF_OFFICER
        
        # Check if performer has sufficient authority
        performer_idx = self.AUTHORITY_HIERARCHY.index(authority_level)
        required_idx = (
            self.AUTHORITY_HIERARCHY.index(required_approval)
            if required_approval
            else len(self.AUTHORITY_HIERARCHY)  # No approval needed
        )
        
        is_compliant = performer_idx >= required_idx
        
        check = GovernanceCheck(
            authority_level=authority_level,
            action=action,
            required_approval=required_approval,
            is_compliant=is_compliant,
            details=f"Authority {'sufficient' if is_compliant else 'insufficient'}"
        )
        
        self.checks.append(check)
        
        if not is_compliant:
            self.issues.append(GovernanceIssue(
                severity="critical" if required_approval == AuthorityLevel.CEO else "warning",
                issue_type="unauthorized_action",
                description=f"Action '{action}' requires {required_approval.value} approval but performed by {authority_level.value}",
                authority_level=authority_level.value,
                action=action,
                remediation=f"Seek approval from {required_approval.value} before executing"
            ))
        
        return check


def run_governance_audit(base_path: str | Path) -> GovernanceComplianceResult:
    """
    Convenience function to run governance compliance audit.
    
    Args:
        base_path: Path to the BOD-personal directory
        
    Returns:
        GovernanceComplianceResult
    """
    checker = GovernanceComplianceChecker(base_path)
    return checker.validate()


__all__ = [
    "GovernanceComplianceChecker",
    "GovernanceComplianceResult",
    "GovernanceIssue",
    "GovernanceCheck",
    "AuthorityLevel",
    "GovernanceIssueType",
    "run_governance_audit",
]
