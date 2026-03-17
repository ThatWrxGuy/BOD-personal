"""
Audit Report Generator - BB-AUD-001

Generates executive system audit reports.

Example output:

BUSY BEE SYSTEM AUDIT REPORT

System Health: 93%

Architecture Integrity: PASS
Agent Registry: WARNING
Signal Health: PASS
Governance Compliance: PASS
Dashboard Accuracy: PASS

Issues Detected:
- Finance Risk Agent latency spike
- Missing derived signal: Burnout Probability
- Dashboard refresh delay (8 minutes)

Recommended Actions:
- Restart Finance Risk Agent
- Regenerate derived signal engine
- Optimize dashboard cache
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .system_audit_engine import SystemAuditResult, AuditType


@dataclass
class AuditReport:
    """Executive audit report."""
    title: str
    generated_at: datetime
    system_health_score: float
    audit_type: str
    passed: bool
    critical_issues: int
    warnings: int
    sections: list[dict[str, Any]]
    recommendations: list[str]


class AuditReportGenerator:
    """
    Generates formatted audit reports for executives.
    """
    
    def __init__(self):
        pass
    
    def generate_report(self, result: SystemAuditResult) -> AuditReport:
        """
        Generate an executive audit report.
        
        Args:
            result: System audit result
            
        Returns:
            AuditReport ready for display
        """
        sections = []
        
        # Architecture section
        if result.architecture:
            status = "PASS" if result.architecture.is_valid else "FAIL"
            sections.append({
                "title": "Architecture Integrity",
                "status": status,
                "score": result.architecture.health_score,
                "issues": len(result.architecture.issues),
            })
        
        # Agent integrity section
        if result.agent_integrity:
            status = "PASS" if result.agent_integrity.is_valid else "WARNING"
            sections.append({
                "title": "Agent Registry",
                "status": status,
                "score": result.agent_integrity.health_score,
                "issues": len(result.agent_integrity.issues),
                "details": f"Total agents: {result.agent_integrity.total_agents}",
            })
        
        # Signal health section
        if result.signal_health:
            status = "PASS" if result.signal_health.is_valid else "WARNING"
            sections.append({
                "title": "Signal Health",
                "status": status,
                "score": result.signal_health.health_score,
                "issues": len(result.signal_health.issues),
            })
        
        # Governance section
        if result.governance:
            status = "PASS" if result.governance.is_compliant else "FAIL"
            sections.append({
                "title": "Governance Compliance",
                "status": status,
                "score": result.governance.health_score,
                "issues": len(result.governance.issues),
            })
        
        # Data consistency section
        if result.data_consistency:
            status = "PASS" if result.data_consistency.is_valid else "WARNING"
            sections.append({
                "title": "Data Integrity",
                "status": status,
                "score": result.data_consistency.health_score,
                "issues": len(result.data_consistency.issues),
            })
        
        # Dashboard section
        if result.dashboard_integrity:
            status = "PASS" if result.dashboard_integrity.is_valid else "WARNING"
            sections.append({
                "title": "Dashboard Accuracy",
                "status": status,
                "score": result.dashboard_integrity.health_score,
                "issues": len(result.dashboard_integrity.issues),
            })
        
        return AuditReport(
            title="BUSY BEE SYSTEM AUDIT REPORT",
            generated_at=result.timestamp,
            system_health_score=result.overall_health_score,
            audit_type=result.audit_type.value,
            passed=result.passed,
            critical_issues=result.critical_issues_count,
            warnings=result.warnings_count,
            sections=sections,
            recommendations=result.recommendations,
        )
    
    def format_text(self, report: AuditReport) -> str:
        """
        Format report as plain text.
        
        Args:
            report: AuditReport to format
            
        Returns:
            Formatted text report
        """
        lines = []
        
        # Header
        lines.append("=" * 60)
        lines.append(report.title)
        lines.append("=" * 60)
        lines.append(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Audit Type: {report.audit_type}")
        lines.append("")
        
        # Overall health
        health_emoji = "✅" if report.passed else "❌"
        lines.append(f"System Health: {health_emoji} {report.system_health_score:.1f}%")
        lines.append("")
        
        # Status sections
        lines.append("-" * 40)
        for section in report.sections:
            status_icon = "✅" if section["status"] == "PASS" else "⚠️"
            lines.append(f"{section['title']}: {status_icon} {section['status']}")
            if "details" in section:
                lines.append(f"  {section['details']}")
        lines.append("-" * 40)
        lines.append("")
        
        # Issue summary
        if report.critical_issues > 0 or report.warnings > 0:
            lines.append(f"Issues Detected: {report.critical_issues} critical, {report.warnings} warnings")
            lines.append("")
        
        # Recommendations
        if report.recommendations:
            lines.append("Recommended Actions:")
            for i, rec in enumerate(report.recommendations, 1):
                lines.append(f"  {i}. {rec}")
            lines.append("")
        
        # Footer
        lines.append("=" * 60)
        lines.append(f"Status: {'PASSED' if report.passed else 'FAILED'}")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def format_json(self, report: AuditReport) -> dict:
        """
        Format report as JSON.
        
        Args:
            report: AuditReport to format
            
        Returns:
            Dictionary suitable for JSON serialization
        """
        return {
            "title": report.title,
            "generated_at": report.generated_at.isoformat(),
            "system_health_score": report.system_health_score,
            "audit_type": report.audit_type,
            "passed": report.passed,
            "critical_issues": report.critical_issues,
            "warnings": report.warnings,
            "sections": report.sections,
            "recommendations": report.recommendations,
        }


def generate_audit_report(result: SystemAuditResult) -> AuditReport:
    """
    Convenience function to generate an audit report.
    
    Args:
        result: System audit result
        
    Returns:
        AuditReport
    """
    generator = AuditReportGenerator()
    return generator.generate_report(result)


__all__ = [
    "AuditReportGenerator",
    "AuditReport",
    "generate_audit_report",
]
