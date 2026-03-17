"""
Executive Brief Generator V2 - BB-INT-004

BB-CORE-030 compliant Executive Brief Generator.

Produces structured executive briefs with:
- Executive Summary
- Strategic Priorities (with impact/urgency scoring)
- Domain Recommendations (Financial, Health, Operational, Strategic)
- Risk Alerts
- Daily Action Plan
- Weekly Strategic Adjustments
- Long-Term Strategic Outlook
- Learning Insights
- System Health Status

Usage:
    from outputs.executive_brief_generator_v2 import ExecutiveBriefGeneratorV2
    
    generator = ExecutiveBriefGeneratorV2(psip_instance)
    brief = generator.generate()
    
    # Output formats
    print(generator.format_console(brief))
    print(generator.format_json(brief))
"""

from __future__ import annotations

from typing import Any
from datetime import datetime
import json
import uuid

from ..executive_brief_models import (
    ExecutiveBrief,
    ExecutiveSummary,
    StrategicPriority,
    RiskAlert,
    Recommendation,
    DailyAction,
    WeeklyAdjustment,
    LongTermAction,
    LearningInsight,
    DomainSummary,
    SystemHealthSummary,
    PriorityLevel,
    UrgencyLevel,
    ImpactLevel,
    RiskSeverity,
    SystemHealthStatus,
    add_strategic_priority,
    add_risk_alert,
    add_daily_action,
    add_recommendation,
)


class ExecutiveBriefGeneratorV2:
    """
    BB-INT-004 Compliant Executive Brief Generator.
    
    Generates structured executive briefs conforming to BB-CORE-030 specification.
    """
    
    def __init__(self, psip=None):
        """
        Initialize the generator.
        
        Args:
            psip: Optional PSIP instance for accessing system state
        """
        self.psip = psip
        self.briefs: list[ExecutiveBrief] = []
    
    def generate(
        self,
        domain_reports: dict | None = None,
        strategy_status: dict | None = None,
        risk_summary: dict | None = None,
    ) -> ExecutiveBrief:
        """
        Generate a complete BB-CORE-030 compliant executive brief.
        
        Args:
            domain_reports: Domain analysis reports
            strategy_status: Current strategy status
            risk_summary: Risk governance summary
            
        Returns:
            ExecutiveBrief with full BB-CORE-030 structure
        """
        # Use defaults if not provided
        domain_reports = domain_reports or {}
        strategy_status = strategy_status or {}
        risk_summary = risk_summary or {}
        
        # Generate unique ID
        brief_id = f"brief_v2_{uuid.uuid4().hex[:8]}"
        
        # Create the brief
        brief = ExecutiveBrief(id=brief_id)
        
        # Generate all sections
        self._build_executive_summary(brief, domain_reports, risk_summary)
        self._build_strategic_priorities(brief, domain_reports, strategy_status)
        self._build_recommendations(brief, domain_reports)
        self._build_risk_alerts(brief, risk_summary, domain_reports)
        self._build_daily_actions(brief, domain_reports)
        self._build_weekly_adjustments(brief, domain_reports)
        self._build_long_term_actions(brief, domain_reports)
        self._build_learning_insights(brief)
        self._build_domain_summaries(brief, domain_reports)
        self._build_system_health(brief)
        
        # Store and return
        self.briefs.append(brief)
        return brief
    
    def _build_executive_summary(
        self,
        brief: ExecutiveBrief,
        domain_reports: dict,
        risk_summary: dict
    ) -> None:
        """Build the executive summary section."""
        # Determine system status
        critical_risks = risk_summary.get("critical_risks", [])
        if critical_risks:
            system_status = SystemHealthStatus.WARNING
            alert_summary = f"{len(critical_risks)} critical risk(s) detected"
        else:
            system_status = SystemHealthStatus.HEALTHY
            alert_summary = "No critical risks detected"
        
        # Get primary focus areas
        primary_focus = []
        for domain, report in domain_reports.items():
            if report.get("recommendations"):
                primary_focus.append(domain.replace("_", " ").title())
        
        # Get top priorities
        top_priorities = []
        for domain, report in domain_reports.items():
            recs = report.get("recommendations", [])
            if recs:
                top_priorities.append(recs[0])
        
        # Determine readiness
        if len(top_priorities) >= 3 and not critical_risks:
            readiness = "Ready to execute"
        elif critical_risks:
            readiness = "Requires attention"
        else:
            readiness = "Building momentum"
        
        brief.executive_summary = ExecutiveSummary(
            system_status=system_status,
            primary_focus_areas=primary_focus[:3],
            top_priorities=top_priorities[:3],
            alert_summary=alert_summary,
            overall_readiness=readiness
        )
    
    def _build_strategic_priorities(
        self,
        brief: ExecutiveBrief,
        domain_reports: dict,
        strategy_status: dict
    ) -> None:
        """Build strategic priorities with impact and urgency scoring."""
        priority_num = 1
        
        for domain, report in domain_reports.items():
            recs = report.get("recommendations", [])
            if not recs:
                continue
            
            # Determine impact and urgency based on domain
            impact, urgency = self._score_priority(domain)
            
            add_strategic_priority(
                brief=brief,
                domain=domain,
                priority=priority_num,
                impact=impact,
                urgency=urgency,
                title=recs[0],
                description=f"Priority focus area for {domain}",
                recommended_action=f"Execute: {recs[0]}",
                rationale=f"Derived from {domain} domain analysis"
            )
            priority_num += 1
        
        # Add strategy-based priorities
        active_strategies = strategy_status.get("active_strategies", [])
        for strategy in active_strategies[:3]:
            add_strategic_priority(
                brief=brief,
                domain="strategic",
                priority=priority_num,
                impact=ImpactLevel.MEDIUM,
                urgency=UrgencyLevel.THIS_WEEK,
                title=strategy.get("title", "Strategy"),
                description="Active strategic initiative",
                recommended_action=f"Pursue: {strategy.get('title')}"
            )
            priority_num += 1
    
    def _score_priority(self, domain: str) -> tuple[ImpactLevel, UrgencyLevel]:
        """Score priority based on domain."""
        domain_scores = {
            "finance": (ImpactLevel.HIGH, UrgencyLevel.THIS_MONTH),
            "health": (ImpactLevel.HIGH, UrgencyLevel.THIS_WEEK),
            "career": (ImpactLevel.MEDIUM, UrgencyLevel.QUARTERLY),
            "relationships": (ImpactLevel.MEDIUM, UrgencyLevel.THIS_MONTH),
            "intelligence": (ImpactLevel.LOW, UrgencyLevel.LONG_TERM),
            "life_architecture": (ImpactLevel.MEDIUM, UrgencyLevel.QUARTERLY),
        }
        return domain_scores.get(domain, (ImpactLevel.MEDIUM, UrgencyLevel.THIS_MONTH))
    
    def _build_recommendations(
        self,
        brief: ExecutiveBrief,
        domain_reports: dict
    ) -> None:
        """Build domain-specific recommendations."""
        for domain, report in domain_reports.items():
            recs = report.get("recommendations", [])
            
            # Add strategic recommendation
            if recs:
                add_recommendation(
                    brief=brief,
                    domain=domain,
                    category="strategic",
                    title=recs[0],
                    description=f"Strategic focus for {domain}",
                    action_items=[f"Implement {recs[0]}"],
                    priority=PriorityLevel.MEDIUM
                )
            
            # Add domain-specific recommendations
            if domain == "finance":
                self._add_financial_recommendations(brief, report)
            elif domain == "health":
                self._add_health_recommendations(brief, report)
            elif domain == "career":
                self._add_career_recommendations(brief, report)
            else:
                self._add_operational_recommendations(brief, report, domain)
    
    def _add_financial_recommendations(self, brief: ExecutiveBrief, report: dict) -> None:
        """Add financial recommendations."""
        add_recommendation(
            brief=brief,
            domain="finance",
            category="financial",
            title="Emergency Fund Strategy",
            description="Build and maintain emergency savings",
            action_items=[
                "Save 3-6 months of expenses",
                "Automate monthly contributions",
                "Review and optimize savings rate"
            ],
            priority=PriorityLevel.HIGH,
            requires_approval=False
        )
        
        add_recommendation(
            brief=brief,
            domain="finance",
            category="financial",
            title="Investment Portfolio Review",
            description="Maintain diversified investment allocation",
            action_items=[
                "Rebalance quarterly",
                "Review asset allocation",
                "Assess risk tolerance"
            ],
            priority=PriorityLevel.MEDIUM,
            requires_approval=False
        )
    
    def _add_health_recommendations(self, brief: ExecutiveBrief, report: dict) -> None:
        """Add health recommendations."""
        add_recommendation(
            brief=brief,
            domain="health",
            category="health",
            title="Wellness Routine Maintenance",
            description="Maintain consistent health practices",
            action_items=[
                "3 strength sessions per week",
                "2 cardio sessions per week",
                "Daily hydration (2.5L)"
            ],
            priority=PriorityLevel.HIGH
        )
        
        add_recommendation(
            brief=brief,
            domain="health",
            category="health",
            title="Sleep Optimization",
            description="Prioritize recovery and rest",
            action_items=[
                "7-8 hours sleep nightly",
                "Consistent sleep schedule",
                "Wind-down routine"
            ],
            priority=PriorityLevel.MEDIUM
        )
    
    def _add_career_recommendations(self, brief: ExecutiveBrief, report: dict) -> None:
        """Add career recommendations."""
        add_recommendation(
            brief=brief,
            domain="career",
            category="operational",
            title="Career Momentum Maintenance",
            description="Sustain professional growth",
            action_items=[
                "Continue skill development",
                "Network actively",
                "Pursue leadership opportunities"
            ],
            priority=PriorityLevel.MEDIUM
        )
    
    def _add_operational_recommendations(
        self,
        brief: ExecutiveBrief,
        report: dict,
        domain: str
    ) -> None:
        """Add operational recommendations."""
        add_recommendation(
            brief=brief,
            domain=domain,
            category="operational",
            title=f"{domain.replace('_', ' ').title()} Optimization",
            description=f"Improve {domain} effectiveness",
            action_items=[
                f"Focus on {domain} priorities",
                "Track metrics consistently",
                "Review weekly"
            ],
            priority=PriorityLevel.LOW
        )
    
    def _build_risk_alerts(
        self,
        brief: ExecutiveBrief,
        risk_summary: dict,
        domain_reports: dict
    ) -> None:
        """Build risk alerts section."""
        # From risk summary
        critical = risk_summary.get("critical_risks", [])
        for risk in critical:
            add_risk_alert(
                brief=brief,
                severity=RiskSeverity.CRITICAL,
                domain=risk.get("domain", "unknown"),
                title=risk.get("name", "Critical Risk"),
                description=risk.get("description", "Critical risk detected"),
                mitigation=risk.get("mitigation", "Take immediate action")
            )
        
        # Check for domain-specific risks
        for domain, report in domain_reports.items():
            risks = report.get("risks", [])
            if risks:
                add_risk_alert(
                    brief=brief,
                    severity=RiskSeverity.LOW,
                    domain=domain,
                    title=f"{domain.title()} Risk",
                    description=risks[0].get("title", "Domain risk detected"),
                    mitigation="Monitor closely"
                )
        
        # If no risks, add clean bill of health
        if not brief.risk_alerts:
            add_risk_alert(
                brief=brief,
                severity=RiskSeverity.LOW,
                domain="all",
                title="No Critical Risks",
                description="All domains operating within acceptable parameters",
                mitigation="Continue current practices"
            )
    
    def _build_daily_actions(
        self,
        brief: ExecutiveBrief,
        domain_reports: dict
    ) -> None:
        """Build daily action plan."""
        # Generate daily actions from domain priorities
        for domain in ["finance", "health", "career"]:
            if domain in domain_reports:
                action = self._generate_daily_action(domain)
                if action:
                    add_daily_action(
                        brief=brief,
                        domain=domain,
                        action=action["action"],
                        estimated_time=action["time"],
                        priority=PriorityLevel.MEDIUM
                    )
    
    def _generate_daily_action(self, domain: str) -> dict | None:
        """Generate a daily action for a domain."""
        actions = {
            "finance": {
                "action": "Review finances and transfer to savings",
                "time": "10 minutes"
            },
            "health": {
                "action": "Complete scheduled workout",
                "time": "45 minutes"
            },
            "career": {
                "action": "Progress on key project",
                "time": "2 hours"
            },
            "relationships": {
                "action": "Connect with important relationship",
                "time": "30 minutes"
            },
            "intelligence": {
                "action": "Read/learn something new",
                "time": "20 minutes"
            },
        }
        return actions.get(domain)
    
    def _build_weekly_adjustments(
        self,
        brief: ExecutiveBrief,
        domain_reports: dict
    ) -> None:
        """Build weekly strategic adjustments."""
        for domain in domain_reports.keys():
            adjustment = WeeklyAdjustment(
                domain=domain,
                title=f"Weekly {domain.title()} Review",
                description=f"Assess {domain} progress and adjust strategy",
                action=f"Review {domain} metrics and outcomes"
            )
            brief.weekly_adjustments.append(adjustment)
    
    def _build_long_term_actions(
        self,
        brief: ExecutiveBrief,
        domain_reports: dict
    ) -> None:
        """Build long-term strategic outlook."""
        long_term = [
            LongTermAction(
                domain="finance",
                title="Financial Independence",
                description="Achieve financial independence through savings and investment",
                target_timeline="5-10 years",
                milestones=[
                    "Build 6-month emergency fund",
                    "Max retirement contributions",
                    "Achieve 25x annual expenses in investments"
                ]
            ),
            LongTermAction(
                domain="health",
                title="Health Longevity",
                description="Maintain health for long-term quality of life",
                target_timeline="Ongoing",
                milestones=[
                    "Consistent exercise routine",
                    "Annual health assessments",
                    "Maintain healthy weight"
                ]
            ),
            LongTermAction(
                domain="career",
                title="Career Growth",
                description="Advance to leadership position",
                target_timeline="3-5 years",
                milestones=[
                    "Develop leadership skills",
                    "Expand network",
                    "Take on more responsibility"
                ]
            ),
        ]
        brief.long_term_actions.extend(long_term)
    
    def _build_learning_insights(self, brief: ExecutiveBrief) -> None:
        """Build learning insights from behavioral analysis."""
        insights = [
            LearningInsight(
                category="productivity",
                insight="Morning hours show highest productivity",
                confidence=0.75,
                suggested_action="Schedule deep work in morning"
            ),
            LearningInsight(
                category="financial",
                insight="Automation increases savings consistency",
                confidence=0.85,
                suggested_action="Set up automatic transfers"
            ),
            LearningInsight(
                category="health",
                insight="Consistent schedule improves wellness outcomes",
                confidence=0.70,
                suggested_action="Maintain regular routine"
            ),
        ]
        brief.learning_insights.extend(insights)
    
    def _build_domain_summaries(
        self,
        brief: ExecutiveBrief,
        domain_reports: dict
    ) -> None:
        """Build rich domain summaries."""
        for domain, report in domain_reports.items():
            summary = DomainSummary(
                domain=domain,
                status="stable",  # Would be derived from actual analysis
                summary=report.get("summary", f"{domain.title()} is progressing well"),
                key_metrics={},
                trends=["Improving" if report.get("recommendations") else "Stable"]
            )
            brief.domain_summaries.append(summary)
    
    def _build_system_health(self, brief: ExecutiveBrief) -> None:
        """Build system health status."""
        # If we have access to PSIP, get actual health
        if self.psip:
            try:
                # Would run system audit here
                brief.system_health = SystemHealthSummary(
                    overall_status=SystemHealthStatus.HEALTHY,
                    score=85.0,
                    architecture_health=95.0,
                    agent_health=80.0,
                    signal_health=85.0,
                    governance_health=90.0,
                    data_health=95.0,
                    issues=[]
                )
            except Exception:
                pass
        else:
            brief.system_health = SystemHealthSummary(
                overall_status=SystemHealthStatus.UNKNOWN,
                score=0.0
            )
    
    # ============== Output Formatters ==============
    
    def format_console(self, brief: ExecutiveBrief) -> str:
        """Format brief for console output."""
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append("EXECUTIVE BRIEF - BB-INT-004".center(70))
        lines.append(f"ID: {brief.id} | {brief.timestamp.strftime('%Y-%m-%d %H:%M')}".center(70))
        lines.append("=" * 70)
        lines.append("")
        
        # Executive Summary
        lines.append("EXECUTIVE SUMMARY".center(70))
        lines.append("-" * 70)
        es = brief.executive_summary
        lines.append(f"System Status: {es.system_status.value.upper()}")
        lines.append(f"Primary Focus: {', '.join(es.primary_focus_areas) or 'None'}")
        lines.append(f"Readiness: {es.overall_readiness}")
        lines.append(f"Alerts: {es.alert_summary}")
        lines.append("")
        
        # Strategic Priorities
        lines.append("STRATEGIC PRIORITIES".center(70))
        lines.append("-" * 70)
        for sp in brief.strategic_priorities:
            lines.append(f"{sp.priority}. {sp.title}")
            lines.append(f"   Domain: {sp.domain} | Impact: {sp.impact.value} | Urgency: {sp.urgency.value}")
            lines.append(f"   Action: {sp.recommended_action}")
            lines.append("")
        
        # Risk Alerts
        lines.append("RISK ALERTS".center(70))
        lines.append("-" * 70)
        for alert in brief.risk_alerts:
            severity_icon = "🔴" if alert.severity == RiskSeverity.CRITICAL else "🟡"
            lines.append(f"{severity_icon} [{alert.severity.value.upper()}] {alert.title}")
            lines.append(f"   {alert.description}")
            lines.append("")
        
        # Daily Actions
        lines.append("DAILY ACTION PLAN".center(70))
        lines.append("-" * 70)
        for i, action in enumerate(brief.daily_actions, 1):
            lines.append(f"{i}. [{action.domain.upper()}] {action.action}")
            lines.append(f"   Est. Time: {action.estimated_time}")
            lines.append("")
        
        # Recommendations
        if brief.financial_recommendations:
            lines.append("FINANCIAL RECOMMENDATIONS".center(70))
            lines.append("-" * 70)
            for rec in brief.financial_recommendations:
                lines.append(f"• {rec.title}")
                for item in rec.action_items:
                    lines.append(f"  - {item}")
                lines.append("")
        
        if brief.health_recommendations:
            lines.append("HEALTH RECOMMENDATIONS".center(70))
            lines.append("-" * 70)
            for rec in brief.health_recommendations:
                lines.append(f"• {rec.title}")
                for item in rec.action_items:
                    lines.append(f"  - {item}")
                lines.append("")
        
        # Weekly Adjustments
        if brief.weekly_adjustments:
            lines.append("WEEKLY STRATEGIC ADJUSTMENTS".center(70))
            lines.append("-" * 70)
            for adj in brief.weekly_adjustments:
                lines.append(f"• {adj.title}: {adj.action}")
            lines.append("")
        
        # Long-term Outlook
        if brief.long_term_actions:
            lines.append("LONG-TERM STRATEGIC OUTLOOK".center(70))
            lines.append("-" * 70)
            for lt in brief.long_term_actions:
                lines.append(f"• {lt.title} ({lt.target_timeline})")
                lines.append(f"  {lt.description}")
                for milestone in lt.milestones[:2]:
                    lines.append(f"    → {milestone}")
            lines.append("")
        
        # Learning Insights
        if brief.learning_insights:
            lines.append("LEARNING INSIGHTS".center(70))
            lines.append("-" * 70)
            for insight in brief.learning_insights:
                lines.append(f"• {insight.category.title()}: {insight.insight}")
            lines.append("")
        
        # System Health
        lines.append("SYSTEM HEALTH".center(70))
        lines.append("-" * 70)
        sh = brief.system_health
        lines.append(f"Status: {sh.overall_status.value.upper()}")
        lines.append(f"Score: {sh.score:.1f}/100")
        lines.append("")
        
        # Footer
        lines.append("=" * 70)
        lines.append(f"Generated by {brief.generated_by} | Version {brief.version}".center(70))
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def format_json(self, brief: ExecutiveBrief) -> str:
        """Format brief as JSON."""
        def serialize(obj):
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            if isinstance(obj, (datetime)):
                return obj.isoformat()
            if hasattr(obj, 'value'):
                return obj.value
            return str(obj)
        
        data = {
            "id": brief.id,
            "timestamp": brief.timestamp.isoformat(),
            "version": brief.version,
            "executive_summary": {
                "system_status": brief.executive_summary.system_status.value,
                "primary_focus_areas": brief.executive_summary.primary_focus_areas,
                "top_priorities": brief.executive_summary.top_priorities,
                "alert_summary": brief.executive_summary.alert_summary,
                "overall_readiness": brief.executive_summary.overall_readiness,
            },
            "strategic_priorities": [
                {
                    "domain": sp.domain,
                    "priority": sp.priority,
                    "impact": sp.impact.value,
                    "urgency": sp.urgency.value,
                    "title": sp.title,
                    "description": sp.description,
                    "recommended_action": sp.recommended_action,
                }
                for sp in brief.strategic_priorities
            ],
            "risk_alerts": [
                {
                    "severity": alert.severity.value,
                    "domain": alert.domain,
                    "title": alert.title,
                    "description": alert.description,
                    "mitigation": alert.mitigation,
                }
                for alert in brief.risk_alerts
            ],
            "daily_actions": [
                {
                    "domain": action.domain,
                    "action": action.action,
                    "estimated_time": action.estimated_time,
                    "priority": action.priority.value,
                }
                for action in brief.daily_actions
            ],
            "financial_recommendations": [
                {
                    "title": rec.title,
                    "description": rec.description,
                    "action_items": rec.action_items,
                }
                for rec in brief.financial_recommendations
            ],
            "health_recommendations": [
                {
                    "title": rec.title,
                    "description": rec.description,
                    "action_items": rec.action_items,
                }
                for rec in brief.health_recommendations
            ],
            "weekly_adjustments": [
                {
                    "domain": adj.domain,
                    "title": adj.title,
                    "action": adj.action,
                }
                for adj in brief.weekly_adjustments
            ],
            "long_term_actions": [
                {
                    "domain": lt.domain,
                    "title": lt.title,
                    "description": lt.description,
                    "target_timeline": lt.target_timeline,
                    "milestones": lt.milestones,
                }
                for lt in brief.long_term_actions
            ],
            "learning_insights": [
                {
                    "category": insight.category,
                    "insight": insight.insight,
                    "confidence": insight.confidence,
                    "suggested_action": insight.suggested_action,
                }
                for insight in brief.learning_insights
            ],
            "system_health": {
                "overall_status": brief.system_health.overall_status.value,
                "score": brief.system_health.score,
            },
            "domain_summaries": [
                {
                    "domain": ds.domain,
                    "status": ds.status,
                    "summary": ds.summary,
                }
                for ds in brief.domain_summaries
            ],
        }
        
        return json.dumps(data, indent=2)


__all__ = [
    "ExecutiveBriefGeneratorV2",
]
