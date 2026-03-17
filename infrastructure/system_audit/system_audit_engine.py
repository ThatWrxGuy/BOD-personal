"""
System Audit Engine - BB-AUD-001

The main orchestrator for system audits.

Executes full system audits, aggregates audit results,
produces remediation recommendations, and triggers auto-repair routines.

Location: infrastructure/system_audit/
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from .architecture_validator import (
    ArchitectureValidator,
    ArchitectureValidationResult,
)
from .agent_integrity_scanner import (
    AgentIntegrityScanner,
    AgentIntegrityResult,
)
from .signal_health_monitor import (
    SignalHealthMonitor,
    SignalHealthResult,
)
from .governance_checker import (
    GovernanceComplianceChecker,
    GovernanceComplianceResult,
)
from .decision_trace_analyzer import (
    DecisionTraceAnalyzer,
    DecisionTraceResult,
)
from .data_consistency_validator import (
    DataConsistencyValidator,
    DataConsistencyResult,
)
from .dashboard_integrity_monitor import (
    DashboardIntegrityMonitor,
    DashboardIntegrityResult,
)


class AuditType(Enum):
    """Types of audit cycles."""
    LIGHT_HEALTH_CHECK = "light_health_check"      # hourly
    SYSTEM_INTEGRITY = "system_integrity"            # daily
    ARCHITECTURE_COMPLIANCE = "architecture_compliance"  # weekly
    STRATEGIC_INTELLIGENCE = "strategic_intelligence"    # weekly
    FULL_DEEP_AUDIT = "full_deep_audit"              # monthly


@dataclass
class AuditSchedule:
    """Audit schedule configuration."""
    audit_type: AuditType
    frequency_hours: int
    enabled: bool = True
    last_run: datetime | None = None
    next_run: datetime | None = None


@dataclass
class SystemAuditResult:
    """Complete result of a system audit."""
    audit_type: AuditType
    timestamp: datetime
    duration_ms: float
    
    # Component results
    architecture: ArchitectureValidationResult | None = None
    agent_integrity: AgentIntegrityResult | None = None
    signal_health: SignalHealthResult | None = None
    governance: GovernanceComplianceResult | None = None
    decision_trace: DecisionTraceResult | None = None
    data_consistency: DataConsistencyResult | None = None
    dashboard_integrity: DashboardIntegrityResult | None = None
    
    # Overall scores
    overall_health_score: float = 0.0
    critical_issues_count: int = 0
    warnings_count: int = 0
    
    # Metadata
    passed: bool = True
    recommendations: list[str] = field(default_factory=list)


class SystemAuditEngine:
    """
    Main system audit engine.
    
    Orchestrates all audit modules and produces comprehensive
    system health reports.
    """
    
    # Audit weights for overall score calculation
    AUDIT_WEIGHTS = {
        "architecture": 0.20,
        "agent_integrity": 0.20,
        "signal_health": 0.20,
        "governance": 0.15,
        "data_consistency": 0.15,
        "dashboard_integrity": 0.10,
    }
    
    def __init__(self, base_path: str | Path):
        self.base_path = Path(base_path)
        
        # Initialize audit components
        self.architecture_validator = ArchitectureValidator(base_path)
        self.agent_scanner = AgentIntegrityScanner(base_path)
        self.signal_monitor = SignalHealthMonitor(base_path)
        self.governance_checker = GovernanceComplianceChecker(base_path)
        self.decision_analyzer = DecisionTraceAnalyzer(base_path)
        self.data_validator = DataConsistencyValidator(base_path)
        self.dashboard_monitor = DashboardIntegrityMonitor(base_path)
        
        # Audit schedule
        self.schedule = self._create_default_schedule()
    
    def _create_default_schedule(self) -> dict[AuditType, AuditSchedule]:
        """Create default audit schedule."""
        return {
            AuditType.LIGHT_HEALTH_CHECK: AuditSchedule(
                audit_type=AuditType.LIGHT_HEALTH_CHECK,
                frequency_hours=1,
            ),
            AuditType.SYSTEM_INTEGRITY: AuditSchedule(
                audit_type=AuditType.SYSTEM_INTEGRITY,
                frequency_hours=24,
            ),
            AuditType.ARCHITECTURE_COMPLIANCE: AuditSchedule(
                audit_type=AuditType.ARCHITECTURE_COMPLIANCE,
                frequency_hours=24 * 7,
            ),
            AuditType.STRATEGIC_INTELLIGENCE: AuditSchedule(
                audit_type=AuditType.STRATEGIC_INTELLIGENCE,
                frequency_hours=24 * 7,
            ),
            AuditType.FULL_DEEP_AUDIT: AuditSchedule(
                audit_type=AuditType.FULL_DEEP_AUDIT,
                frequency_hours=24 * 30,
            ),
        }
    
    def run_audit(
        self,
        audit_type: AuditType = AuditType.SYSTEM_INTEGRITY,
        include_components: list[str] | None = None,
    ) -> SystemAuditResult:
        """
        Run a system audit.
        
        Args:
            audit_type: Type of audit to run
            include_components: Optional list of components to include
            
        Returns:
            SystemAuditResult with complete audit findings
        """
        start_time = datetime.now()
        
        # Default to all components
        if include_components is None:
            include_components = list(self.AUDIT_WEIGHTS.keys())
        
        result = SystemAuditResult(
            audit_type=audit_type,
            timestamp=start_time,
            duration_ms=0.0,
        )
        
        # Run selected audits
        if "architecture" in include_components:
            result.architecture = self.architecture_validator.validate()
        
        if "agent_integrity" in include_components:
            result.agent_integrity = self.agent_scanner.validate()
        
        if "signal_health" in include_components:
            result.signal_health = self.signal_monitor.validate()
        
        if "governance" in include_components:
            result.governance = self.governance_checker.validate()
        
        if "decision_trace" in include_components:
            result.decision_trace = self.decision_analyzer.validate()
        
        if "data_consistency" in include_components:
            result.data_consistency = self.data_validator.validate()
        
        if "dashboard_integrity" in include_components:
            result.dashboard_integrity = self.dashboard_monitor.validate()
        
        # Calculate overall score
        result.overall_health_score = self._calculate_overall_score(result)
        
        # Count issues
        result.critical_issues_count = self._count_critical_issues(result)
        result.warnings_count = self._count_warnings(result)
        
        # Determine if passed
        result.passed = result.critical_issues_count == 0
        
        # Generate recommendations
        result.recommendations = self._generate_recommendations(result)
        
        # Calculate duration
        result.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return result
    
    def run_light_health_check(self) -> SystemAuditResult:
        """Run a quick health check (light audit)."""
        return self.run_audit(
            audit_type=AuditType.LIGHT_HEALTH_CHECK,
            include_components=["architecture", "signal_health"],
        )
    
    def run_full_audit(self) -> SystemAuditResult:
        """Run a comprehensive full system audit."""
        return self.run_audit(audit_type=AuditType.FULL_DEEP_AUDIT)
    
    def _calculate_overall_score(self, result: SystemAuditResult) -> float:
        """Calculate weighted overall health score."""
        total_weight = 0.0
        weighted_score = 0.0
        
        for component, weight in self.AUDIT_WEIGHTS.items():
            score = self._get_component_score(result, component)
            weighted_score += score * weight
            total_weight += weight
        
        if total_weight > 0:
            return weighted_score / total_weight
        return 0.0
    
    def _get_component_score(self, result: SystemAuditResult, component: str) -> float:
        """Get score for a specific component."""
        if component == "architecture":
            return result.architecture.health_score if result.architecture else 0.0
        elif component == "agent_integrity":
            return result.agent_integrity.health_score if result.agent_integrity else 0.0
        elif component == "signal_health":
            return result.signal_health.health_score if result.signal_health else 0.0
        elif component == "governance":
            return result.governance.health_score if result.governance else 0.0
        elif component == "data_consistency":
            return result.data_consistency.health_score if result.data_consistency else 0.0
        elif component == "dashboard_integrity":
            return result.dashboard_integrity.health_score if result.dashboard_integrity else 0.0
        return 0.0
    
    def _count_critical_issues(self, result: SystemAuditResult) -> int:
        """Count total critical issues across all components."""
        count = 0
        
        if result.architecture:
            count += len([i for i in result.architecture.issues if i.severity == "critical"])
        if result.agent_integrity:
            count += len([i for i in result.agent_integrity.issues if i.severity == "critical"])
        if result.signal_health:
            count += len([i for i in result.signal_health.issues if i.severity == "critical"])
        if result.governance:
            count += len([i for i in result.governance.issues if i.severity == "critical"])
        if result.data_consistency:
            count += len([i for i in result.data_consistency.issues if i.severity == "critical"])
        if result.dashboard_integrity:
            count += len([i for i in result.dashboard_integrity.issues if i.severity == "critical"])
        
        return count
    
    def _count_warnings(self, result: SystemAuditResult) -> int:
        """Count total warnings across all components."""
        count = 0
        
        if result.architecture:
            count += len([i for i in result.architecture.issues if i.severity == "warning"])
        if result.agent_integrity:
            count += len([i for i in result.agent_integrity.issues if i.severity == "warning"])
        if result.signal_health:
            count += len([i for i in result.signal_health.issues if i.severity == "warning"])
        if result.governance:
            count += len([i for i in result.governance.issues if i.severity == "warning"])
        if result.data_consistency:
            count += len([i for i in result.data_consistency.issues if i.severity == "warning"])
        if result.dashboard_integrity:
            count += len([i for i in result.dashboard_integrity.issues if i.severity == "warning"])
        
        return count
    
    def _generate_recommendations(self, result: SystemAuditResult) -> list[str]:
        """Generate remediation recommendations."""
        recommendations = []
        
        # Architecture recommendations
        if result.architecture and result.architecture.issues:
            for issue in result.architecture.issues:
                if issue.remediation:
                    recommendations.append(f"[Architecture] {issue.remediation}")
        
        # Agent integrity recommendations
        if result.agent_integrity and result.agent_integrity.issues:
            for issue in result.agent_integrity.issues:
                if issue.remediation:
                    recommendations.append(f"[Agent] {issue.remediation}")
        
        # Signal health recommendations
        if result.signal_health and result.signal_health.issues:
            for issue in result.signal_health.issues:
                if issue.remediation:
                    recommendations.append(f"[Signal] {issue.remediation}")
        
        # Governance recommendations
        if result.governance and result.governance.issues:
            for issue in result.governance.issues:
                if issue.remediation:
                    recommendations.append(f"[Governance] {issue.remediation}")
        
        # Data consistency recommendations
        if result.data_consistency and result.data_consistency.issues:
            for issue in result.data_consistency.issues:
                if issue.remediation:
                    recommendations.append(f"[Data] {issue.remediation}")
        
        # Dashboard recommendations
        if result.dashboard_integrity and result.dashboard_integrity.issues:
            for issue in result.dashboard_integrity.issues:
                if issue.remediation:
                    recommendations.append(f"[Dashboard] {issue.remediation}")
        
        return recommendations[:10]  # Limit to top 10
    
    def get_schedule_status(self) -> dict[str, Any]:
        """Get current audit schedule status."""
        return {
            audit_type.value: {
                "frequency_hours": schedule.frequency_hours,
                "enabled": schedule.enabled,
                "last_run": schedule.last_run.isoformat() if schedule.last_run else None,
                "next_run": schedule.next_run.isoformat() if schedule.next_run else None,
            }
            for audit_type, schedule in self.schedule.items()
        }


def create_system_audit_engine(base_path: str | Path) -> SystemAuditEngine:
    """
    Factory function to create a system audit engine.
    
    Args:
        base_path: Path to the BOD-personal directory
        
    Returns:
        SystemAuditEngine instance
    """
    return SystemAuditEngine(base_path)


__all__ = [
    "SystemAuditEngine",
    "SystemAuditResult",
    "AuditType",
    "AuditSchedule",
    "create_system_audit_engine",
]
