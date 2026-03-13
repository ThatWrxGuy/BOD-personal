"""Audit report builder for generating comprehensive reports.

Generates human-readable and JSON reports from audit data.
"""
import json
from datetime import datetime
from typing import Any, Dict, List

from app.audit.audit_models import (
    AuditCycleRecord,
    AuditFindings,
    AuditMode,
    DecisionInventory,
    GovernanceOutcomeReport,
    LearningReport,
    MasterAuditReport,
    VisionAlignment,
)


class AuditReportBuilder:
    """Builder for audit reports."""
    
    def __init__(self):
        """Initialize audit report builder."""
        pass
    
    def build_master_report(
        self,
        cycle_records: List[AuditCycleRecord],
        audit_modes: List[AuditMode],
        scenarios: List[str],
    ) -> MasterAuditReport:
        """Build the master audit report."""
        # Create runner to build components
        from app.audit.end_to_end_audit_runner import EndToEndAuditRunner
        
        # Create a temporary runner to build components
        runner = EndToEndAuditRunner()
        runner.cycle_records = cycle_records
        runner.confidence_history = [
            r.confidence_after for r in cycle_records
        ]
        
        # Build components
        decision_inventory = runner.build_decision_inventory()
        governance_outcomes = runner.build_governance_outcomes()
        learning_report = runner.build_learning_report()
        
        # Build findings
        findings = self._build_findings(cycle_records, decision_inventory, governance_outcomes)
        
        # Build vision alignment
        vision_alignment = self._build_vision_alignment(findings, decision_inventory, len(cycle_records))
        
        # Determine executive summary
        executive_summary = self._generate_executive_summary(
            findings, vision_alignment, governance_outcomes
        )
        
        # Calculate duration
        if cycle_records:
            start_time = cycle_records[0].timestamp
            end_time = cycle_records[-1].timestamp
            duration_ms = (end_time - start_time).total_seconds() * 1000
        else:
            duration_ms = 0.0
        
        return MasterAuditReport(
            audit_modes=audit_modes,
            scenarios_executed=scenarios,
            total_cycles=len(cycle_records),
            started_at=cycle_records[0].timestamp if cycle_records else datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_ms=duration_ms,
            executive_summary=executive_summary,
            cycle_records=cycle_records,
            decision_inventory=decision_inventory,
            governance_outcomes=governance_outcomes,
            learning_report=learning_report,
            findings=findings,
            vision_alignment=vision_alignment,
        )
    
    def _build_findings(
        self,
        records: List[AuditCycleRecord],
        inventory: DecisionInventory,
        governance: GovernanceOutcomeReport,
    ) -> AuditFindings:
        """Build audit findings."""
        findings = AuditFindings()
        
        # Strategic coherence
        coherent = sum(1 for r in records if r.alignment_level == "aligned")
        incoherent = sum(1 for r in records if r.alignment_level == "misaligned")
        
        findings.coherent_recommendations = coherent
        findings.incoherent_recommendations = incoherent
        
        if coherent > incoherent:
            findings.strategic_coherence_assessment = "Mostly coherent - recommendations align with domain states"
        elif incoherent > coherent:
            findings.strategic_coherence_assessment = "Concerning - many recommendations misaligned"
        else:
            findings.strategic_coherence_assessment = "Mixed - balanced aligned and misaligned"
        
        # Doctrine consistency
        unique_scores = len(set(r.alignment_score for r in records))
        findings.doctrine_consistency_score = 1.0 - (unique_scores / max(1, len(records)))
        
        if unique_scores > len(records) * 0.5:
            findings.inconsistent_assessments = unique_scores
            findings.doctrine_consistency_assessment = "Inconsistent - doctrine produces varied assessments"
        else:
            findings.doctrine_consistency_assessment = "Consistent - doctrine produces similar outcomes"
        
        # Governance quality
        correctly_blocked = governance.doctrine_blocks + governance.policy_blocks + governance.risk_rejections
        findings.correctly_blocked_actions = correctly_blocked
        
        if correctly_blocked > 0:
            findings.governance_quality_assessment = f"Governance working - {correctly_blocked} actions appropriately blocked"
        else:
            findings.governance_quality_assessment = "Review needed - no actions blocked (may indicate overly permissive)"
        
        # Decision quality
        useful = inventory.high_value_decisions
        noisy = inventory.noisy_decisions
        
        findings.specific_useful_decisions = useful
        findings.repetitive_noisy_decisions = noisy
        
        if noisy > useful:
            findings.decision_quality_assessment = f"Concerning - {noisy} repetitive vs {useful} useful"
        else:
            findings.decision_quality_assessment = f"Good - {useful} useful decisions, {noisy} noisy"
        
        # Learning behavior
        bounded = all(abs(r.confidence_after - r.confidence_before) < 0.2 for r in records)
        findings.bounded_confidence_updates = bounded
        
        if bounded:
            findings.learning_behavior_assessment = "Good - confidence updates are bounded"
        else:
            findings.learning_behavior_assessment = "Concerning - some confidence swings detected"
        
        findings.proportional_learning = True  # Assume proportional for now
        
        # Flow integrity
        broken = sum(1 for r in records if not r.recommendations and not r.execution_intents)
        findings.broken_flows = broken
        findings.flow_consistency_score = 1.0 - (broken / max(1, len(records)))
        
        return findings
    
    def _build_vision_alignment(
        self,
        findings: AuditFindings,
        inventory: DecisionInventory,
        total_cycles: int,
    ) -> VisionAlignment:
        """Build vision alignment assessment."""
        alignment = VisionAlignment()
        
        # What's working well
        if findings.strategic_coherence_assessment and "coherent" in findings.strategic_coherence_assessment.lower():
            alignment.aligned_areas.append("Strategic coherence in recommendations")
        
        if findings.governance_quality_assessment and "working" in findings.governance_quality_assessment.lower():
            alignment.aligned_areas.append("Governance gates blocking risky actions")
        
        if findings.bounded_confidence_updates:
            alignment.aligned_areas.append("Bounded confidence learning")
        
        if findings.flow_consistency_score > 0.8:
            alignment.aligned_areas.append("Consistent end-to-end flow")
        
        # What's questionable
        if findings.repetitive_noisy_decisions > 0:
            alignment.questionable_areas.append(
                f"Repetitive recommendations detected ({findings.repetitive_noisy_decisions})"
            )
        
        if findings.doctrine_consistency_score < 0.5:
            alignment.questionable_areas.append("Doctrine assessments vary significantly")
        
        # Major issues
        if findings.incoherent_recommendations > findings.coherent_recommendations:
            alignment.major_issues.append("More misaligned than aligned recommendations")
        
        if total_cycles > 0 and findings.broken_flows > total_cycles * 0.3:
            alignment.major_issues.append("Significant number of empty cycles")
        
        # Overall verdict
        if len(alignment.major_issues) == 0 and len(alignment.questionable_areas) < 2:
            alignment.overall_verdict = "System behaving close to intended vision with minor improvements needed"
        elif len(alignment.major_issues) < 2:
            alignment.overall_verdict = "System largely functional but needs targeted remediation"
        else:
            alignment.overall_verdict = "System requires deeper architectural correction before proceeding"
        
        # Recommendations
        if alignment.questionable_areas:
            alignment.recommendations.append("Review and tune recommendation generation")
        
        if findings.doctrine_consistency_score < 0.5:
            alignment.recommendations.append("Improve doctrine rule consistency")
        
        if findings.repetitive_noisy_decisions > 0:
            alignment.recommendations.append("Implement recommendation deduplication")
        
        return alignment
    
    def _generate_executive_summary(
        self,
        findings: AuditFindings,
        alignment: VisionAlignment,
        governance: GovernanceOutcomeReport,
    ) -> str:
        """Generate executive summary."""
        lines = []
        
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(alignment.overall_verdict)
        lines.append("")
        
        lines.append("### Key Metrics")
        lines.append(f"- Total Cycles: {findings.coherent_recommendations + findings.incoherent_recommendations}")
        lines.append(f"- Aligned Recommendations: {findings.coherent_recommendations}")
        lines.append(f"- Blocked Actions: {governance.doctrine_blocks + governance.policy_blocks + governance.risk_rejections}")
        lines.append(f"- Flow Consistency: {findings.flow_consistency_score:.1%}")
        lines.append("")
        
        if alignment.aligned_areas:
            lines.append("### Strengths")
            for area in alignment.aligned_areas[:3]:
                lines.append(f"- {area}")
            lines.append("")
        
        if alignment.questionable_areas:
            lines.append("### Areas for Improvement")
            for area in alignment.questionable_areas[:3]:
                lines.append(f"- {area}")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_markdown_report(self, report: MasterAuditReport) -> str:
        """Generate markdown report."""
        lines = []
        
        lines.append("# Master Decision Review Report")
        lines.append("")
        lines.append(f"**Report ID:** {report.report_id}")
        lines.append(f"**Generated:** {datetime.utcnow().isoformat()}")
        lines.append("")
        
        lines.append("---")
        lines.append("")
        lines.append("# Executive Summary")
        lines.append("")
        lines.append(report.executive_summary)
        lines.append("")
        
        lines.append("---")
        lines.append("")
        lines.append("# Audit Coverage")
        lines.append("")
        lines.append(f"- **Modes:** {', '.join(m.value for m in report.audit_modes)}")
        lines.append(f"- **Scenarios:** {', '.join(report.scenarios_executed)}")
        lines.append(f"- **Total Cycles:** {report.total_cycles}")
        lines.append(f"- **Duration:** {report.duration_ms:.2f}ms")
        lines.append("")
        
        lines.append("---")
        lines.append("")
        lines.append("# Detailed Cycle Review")
        lines.append("")
        
        for i, record in enumerate(report.cycle_records[:20]):  # Limit to 20 for readability
            lines.append(f"## Cycle {i+1}: {record.scenario_name}")
            lines.append("")
            lines.append(f"**Timestamp:** {record.timestamp.isoformat()}")
            lines.append(f"**Duration:** {record.cycle_duration_ms:.2f}ms")
            lines.append("")
            lines.append(f"**Signal Summary:** {record.signal_summary}")
            lines.append("")
            lines.append(f"**Doctrine Assessment:**")
            lines.append(f"- Alignment: {record.alignment_level} ({record.alignment_score:.2f})")
            lines.append(f"- Confidence: {record.doctrine_assessment.get('confidence', 'N/A') if record.doctrine_assessment else 'N/A'}")
            lines.append(f"- Flags: {', '.join(record.doctrine_flags) or 'None'}")
            lines.append("")
            lines.append(f"**Recommendations:** {record.recommendation_count}")
            lines.append(f"**Execution Intents:** {record.execution_intent_count}")
            lines.append("")
            lines.append(f"**Gate Outcomes:**")
            lines.append(f"- Policy: {record.policy_gate_outcome.value}")
            lines.append(f"- Doctrine: {record.doctrine_gate_outcome.value}")
            lines.append(f"- Risk: {record.risk_gate_outcome.value}")
            lines.append("")
            lines.append(f"**Approval:** {record.approval_status.value} ({record.approval_tier})")
            lines.append("")
            lines.append(f"**Confidence:** {record.confidence_before:.2f} → {record.confidence_after:.2f}")
            lines.append("")
            
            if record.recommendations:
                lines.append("**Key Recommendations:**")
                for rec in record.recommendations[:3]:
                    lines.append(f"- {rec.get('domain', 'unknown')}: {rec.get('action_type', 'N/A')} (priority: {rec.get('priority', 0):.2f})")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # Decision Inventory
        lines.append("# Decision Inventory")
        lines.append("")
        lines.append(f"**Total Recommendations:** {report.decision_inventory.total_recommendations}")
        lines.append("")
        lines.append("### By Domain")
        for domain, count in report.decision_inventory.decisions_by_domain.items():
            lines.append(f"- {domain}: {count}")
        lines.append("")
        
        lines.append("### By Alignment")
        lines.append(f"- Aligned: {report.decision_inventory.aligned_decisions}")
        lines.append(f"- Neutral: {report.decision_inventory.neutral_decisions}")
        lines.append(f"- Misaligned: {report.decision_inventory.misaligned_decisions}")
        lines.append("")
        
        lines.append("### Execution Eligibility")
        lines.append(f"- Eligible: {report.decision_inventory.eligible_for_execution}")
        lines.append(f"- Blocked by Doctrine: {report.decision_inventory.blocked_by_doctrine}")
        lines.append(f"- Blocked by Policy: {report.decision_inventory.blocked_by_policy}")
        lines.append(f"- Blocked by Risk: {report.decision_inventory.blocked_by_risk}")
        lines.append("")
        
        # Governance Outcomes
        lines.append("# Governance Summary")
        lines.append("")
        lines.append(f"**Total Recommendations:** {report.governance_outcomes.total_recommendations}")
        lines.append(f"**Total Execution Intents:** {report.governance_outcomes.total_execution_intents}")
        lines.append("")
        lines.append("### Gate Pass/Block")
        lines.append(f"- Doctrine Passes: {report.governance_outcomes.doctrine_passes}")
        lines.append(f"- Doctrine Blocks: {report.governance_outcomes.doctrine_blocks}")
        lines.append(f"- Policy Passes: {report.governance_outcomes.policy_passes}")
        lines.append(f"- Policy Blocks: {report.governance_outcomes.policy_blocks}")
        lines.append(f"- Risk Passes: {report.governance_outcomes.risk_passes}")
        lines.append(f"- Risk Rejections: {report.governance_outcomes.risk_rejections}")
        lines.append("")
        
        lines.append("### Approval Distribution")
        lines.append(f"- Manual Required: {report.governance_outcomes.approval_required_count}")
        lines.append(f"- Manual Only: {report.governance_outcomes.manual_only_count}")
        lines.append(f"- Fast Path: {report.governance_outcomes.fast_path_count}")
        lines.append(f"- Auto Approved: {report.governance_outcomes.auto_approved_count}")
        lines.append("")
        
        # Learning Report
        lines.append("# Learning Summary")
        lines.append("")
        lines.append(f"**Initial Confidence:** {report.learning_report.initial_confidence:.3f}")
        lines.append(f"**Final Confidence:** {report.learning_report.final_confidence:.3f}")
        lines.append(f"**Drift:** {report.learning_report.confidence_drift:+.3f}")
        lines.append(f"**Range:** {report.learning_report.confidence_min:.3f} - {report.learning_report.confidence_max:.3f}")
        lines.append("")
        
        if report.learning_report.confidence_collapse_events > 0:
            lines.append(f"⚠️ **Confidence Collapse Events:** {report.learning_report.confidence_collapse_events}")
        
        if report.learning_report.oscillating_confidence_events > 0:
            lines.append(f"⚠️ **Oscillating Confidence:** Detected")
        
        lines.append("")
        
        # Findings
        lines.append("# Findings & Vision Alignment")
        lines.append("")
        lines.append("## Strategic Coherence")
        lines.append(f"{report.findings.strategic_coherence_assessment}")
        lines.append("")
        
        lines.append("## Governance Quality")
        lines.append(f"{report.findings.governance_quality_assessment}")
        lines.append("")
        
        lines.append("## Decision Quality")
        lines.append(f"{report.findings.decision_quality_assessment}")
        lines.append("")
        
        lines.append("## Learning Behavior")
        lines.append(f"{report.findings.learning_behavior_assessment}")
        lines.append("")
        
        lines.append("## Overall Verdict")
        lines.append("")
        lines.append(f"**{report.vision_alignment.overall_verdict}**")
        lines.append("")
        
        if report.vision_alignment.aligned_areas:
            lines.append("### What's Working")
            for area in report.vision_alignment.aligned_areas:
                lines.append(f"- {area}")
            lines.append("")
        
        if report.vision_alignment.questionable_areas:
            lines.append("### Questionable Areas")
            for area in report.vision_alignment.questionable_areas:
                lines.append(f"- {area}")
            lines.append("")
        
        if report.vision_alignment.major_issues:
            lines.append("### Major Issues")
            for issue in report.vision_alignment.major_issues:
                lines.append(f"- {issue}")
            lines.append("")
        
        if report.vision_alignment.recommendations:
            lines.append("### Recommended Remediation")
            for rec in report.vision_alignment.recommendations:
                lines.append(f"- {rec}")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_json_report(self, report: MasterAuditReport) -> str:
        """Generate JSON report."""
        return json.dumps(report.model_dump(), indent=2, default=str)


def create_audit_report_builder() -> AuditReportBuilder:
    """Factory function to create audit report builder."""
    return AuditReportBuilder()
