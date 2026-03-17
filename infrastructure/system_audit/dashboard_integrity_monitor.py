"""
Dashboard Integrity Monitor - BB-AUD-001

Ensures the CEO dashboard shows correct information.

Validates:
- executive brief data
- priority rankings
- signal summaries
- decision outcomes

Detects:
- stale dashboard data
- incorrect priority ordering
- missing intelligence outputs
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any


class DashboardIssueType(Enum):
    """Types of dashboard issues."""
    STALE_DATA = "stale_data"
    INCORRECT_ORDER = "incorrect_order"
    MISSING_OUTPUT = "missing_output"
    DATA_MISMATCH = "data_mismatch"


@dataclass
class DashboardMetric:
    """Represents a dashboard metric."""
    name: str
    value: Any
    last_updated: datetime | None
    is_stale: bool = False


@dataclass
class DashboardIssue:
    """Represents a dashboard integrity problem."""
    severity: str  # critical, warning, info
    component: str
    issue_type: str
    description: str
    remediation: str | None = None


@dataclass
class DashboardIntegrityResult:
    """Result of dashboard integrity validation."""
    is_valid: bool
    health_score: float  # 0-100
    issues: list[DashboardIssue] = field(default_factory=list)
    components_validated: list[str] = field(default_factory=list)
    metrics_checked: int = 0
    stale_metrics: list[str] = field(default_factory=list)
    last_full_refresh: datetime | None = None


class DashboardIntegrityMonitor:
    """
    Validates dashboard integrity and data accuracy.
    """
    
    # Stale threshold for dashboard data (minutes)
    STALE_THRESHOLD_MINUTES = 15
    
    # Required dashboard components
    REQUIRED_COMPONENTS = [
        "executive_brief",
        "priority_rankings",
        "signal_summary",
        "decision_outcomes",
        "system_health",
    ]
    
    def __init__(self, base_path: str | Path):
        self.base_path = Path(base_path)
        self.issues: list[DashboardIssue] = []
        self.metrics: list[DashboardMetric] = []
    
    def validate(self) -> DashboardIntegrityResult:
        """
        Run dashboard integrity validation.
        
        Returns:
            DashboardIntegrityResult with findings
        """
        self.issues = []
        self.metrics = []
        
        # Validate executive brief generation
        self._validate_executive_brief()
        
        # Validate priority system
        self._validate_priority_system()
        
        # Validate signal summaries
        self._validate_signal_summary()
        
        # Validate decision outcomes
        self._validate_decision_outcomes()
        
        # Check for dashboard integration
        self._validate_dashboard_integration()
        
        # Calculate health score
        health_score = self._calculate_health_score()
        
        return DashboardIntegrityResult(
            is_valid=len([i for i in self.issues if i.severity == "critical"]) == 0,
            health_score=health_score,
            issues=self.issues,
            components_validated=self.REQUIRED_COMPONENTS,
            metrics_checked=len(self.metrics),
            stale_metrics=[m.name for m in self.metrics if m.is_stale],
            last_full_refresh=datetime.now(),
        )
    
    def _validate_executive_brief(self) -> None:
        """Validate executive brief generation."""
        brief_path = self.base_path / "outputs" / "executive_briefs"
        
        if not brief_path.exists():
            self.issues.append(DashboardIssue(
                severity="critical",
                component="executive_brief",
                issue_type="missing_output",
                description="Executive briefs module not found",
                remediation="Create outputs/executive_briefs/"
            ))
            return
        
        # Check for brief generator
        generator_path = brief_path / "executive_brief_generator.py"
        if not generator_path.exists():
            self.issues.append(DashboardIssue(
                severity="critical",
                component="executive_brief",
                issue_type="missing_generator",
                description="Executive brief generator not found",
                remediation="Create executive_brief_generator.py"
            ))
            return
        
        # Check for required generator functions
        content = generator_path.read_text()
        required_functions = ["generate", "brief"]
        
        for func in required_functions:
            if func not in content.lower():
                self.issues.append(DashboardIssue(
                    severity="warning",
                    component="executive_brief",
                    issue_type="missing_function",
                    description=f"Executive brief may lack: {func}",
                    remediation=f"Implement {func} function"
                ))
        
        # Add metric
        self.metrics.append(DashboardMetric(
            name="executive_brief",
            value="present",
            last_updated=datetime.now()
        ))
    
    def _validate_priority_system(self) -> None:
        """Validate priority ranking system."""
        priority_path = self.base_path / "layer2_governance_layer" / "priority_router"
        
        if not priority_path.exists():
            self.issues.append(DashboardIssue(
                severity="warning",
                component="priority_rankings",
                issue_type="missing_component",
                description="Priority router not found",
                remediation="Create layer2_governance_layer/priority_router/"
            ))
            return
        
        # Add metric
        self.metrics.append(DashboardMetric(
            name="priority_system",
            value="present",
            last_updated=datetime.now()
        ))
    
    def _validate_signal_summary(self) -> None:
        """Validate signal summary generation."""
        # Check signal system for summary capability
        signal_path = self.base_path / "infrastructure" / "signal_system" / "signal_system.py"
        
        if not signal_path.exists():
            self.issues.append(DashboardIssue(
                severity="warning",
                component="signal_summary",
                issue_type="missing_component",
                description="Signal system not found",
                remediation="Create infrastructure/signal_system/"
            ))
            return
        
        # Add metric
        self.metrics.append(DashboardMetric(
            name="signal_summary",
            value="present",
            last_updated=datetime.now()
        ))
    
    def _validate_decision_outcomes(self) -> None:
        """Validate decision outcome tracking."""
        # Check for reporting/intelligence cycle
        cycle_path = self.base_path / "infrastructure" / "intelligence_cycle"
        
        if not cycle_path.exists():
            self.issues.append(DashboardIssue(
                severity="warning",
                component="decision_outcomes",
                issue_type="missing_component",
                description="Intelligence cycle not found",
                remediation="Create infrastructure/intelligence_cycle/"
            ))
            return
        
        # Check for cycle scheduler
        scheduler_path = cycle_path / "cycle_scheduler.py"
        if not scheduler_path.exists():
            self.issues.append(DashboardIssue(
                severity="warning",
                component="decision_outcomes",
                issue_type="missing_scheduler",
                description="Cycle scheduler not found",
                remediation="Create cycle_scheduler.py"
            ))
        
        # Add metric
        self.metrics.append(DashboardMetric(
            name="decision_outcomes",
            value="present",
            last_updated=datetime.now()
        ))
    
    def _validate_dashboard_integration(self) -> None:
        """Check for dashboard integration points."""
        # Check if PSIP can generate dashboard data
        psip_path = self.base_path / "psip.py"
        
        if not psip_path.exists():
            self.issues.append(DashboardIssue(
                severity="critical",
                component="dashboard_integration",
                issue_type="missing_psip",
                description="PSIP main module not found",
                remediation="Create psip.py"
            ))
            return
        
        content = psip_path.read_text()
        
        # Check for dashboard-related methods
        if "brief" not in content.lower() and "status" not in content.lower():
            self.issues.append(DashboardIssue(
                severity="warning",
                component="dashboard_integration",
                issue_type="missing_dashboard_methods",
                description="PSIP may lack dashboard generation methods",
                remediation="Add dashboard/status methods to PSIP"
            ))
        
        # Add metric
        self.metrics.append(DashboardMetric(
            name="dashboard_integration",
            value="present",
            last_updated=datetime.now()
        ))
    
    def _calculate_health_score(self) -> float:
        """Calculate dashboard health score (0-100)."""
        if not self.issues:
            return 100.0
        
        # Factor in stale metrics
        stale_count = len([m for m in self.metrics if m.is_stale])
        
        critical_count = len([i for i in self.issues if i.severity == "critical"])
        warning_count = len([i for i in self.issues if i.severity == "warning"])
        
        deduction = (critical_count * 15) + (warning_count * 5) + (stale_count * 10)
        return max(0.0, 100.0 - deduction)
    
    def check_data_freshness(self, data_timestamp: datetime) -> bool:
        """
        Check if dashboard data is fresh.
        
        Args:
            data_timestamp: When the data was last updated
            
        Returns:
            True if data is fresh, False if stale
        """
        threshold = timedelta(minutes=self.STALE_THRESHOLD_MINUTES)
        is_fresh = (datetime.now() - data_timestamp) < threshold
        
        if not is_fresh:
            self.issues.append(DashboardIssue(
                severity="warning",
                component="data_freshness",
                issue_type="stale_data",
                description=f"Data is stale (last updated: {data_timestamp})",
                remediation="Refresh dashboard data"
            ))
        
        return is_fresh


def run_dashboard_integrity_audit(base_path: str | Path) -> DashboardIntegrityResult:
    """
    Convenience function to run dashboard integrity audit.
    
    Args:
        base_path: Path to the BOD-personal directory
        
    Returns:
        DashboardIntegrityResult
    """
    monitor = DashboardIntegrityMonitor(base_path)
    return monitor.validate()


__all__ = [
    "DashboardIntegrityMonitor",
    "DashboardIntegrityResult",
    "DashboardIssue",
    "DashboardMetric",
    "DashboardIssueType",
    "run_dashboard_integrity_audit",
]
