"""
BB-INT-007: Executive Brief Generator

Main generator that orchestrates the complete Executive Intelligence Brief.

Responsibilities:
- Coordinate all components
- Generate complete ExecutiveBrief
- Integrate with PSIP

Usage:
    from app.intelligence.executive_brief import ExecutiveBriefGenerator
    
    generator = ExecutiveBriefGenerator()
    brief = generator.generate(psip)
"""

import uuid
from datetime import datetime
from typing import Any

from .executive_brief_models import (
    ExecutiveBrief,
    ExecutiveSummarySection,
    SystemStatus,
    StrategicPosture,
    DailyAction,
    DailyActionPlan,
    WeeklyAdjustment,
    WeeklyAdjustments,
    LongTermOutlook,
    SystemHealth,
)
from .agent_signal_collector import AgentSignalCollector
from .domain_intelligence_aggregator import DomainIntelligenceAggregator
from .spy_trade_brief_engine import SpyTradeBriefEngine


class ExecutiveBriefGenerator:
    """
    Main Executive Brief Generator.
    
    Orchestrates the complete generation of the Executive Intelligence Brief.
    """
    
    def __init__(self):
        self.collector = AgentSignalCollector()
        self.aggregator = DomainIntelligenceAggregator()
        self.trade_engine = SpyTradeBriefEngine()
        self.generated_briefs: list[ExecutiveBrief] = []
    
    def generate(
        self,
        psip: Any | None = None,
        include_trade_brief: bool = False
    ) -> ExecutiveBrief:
        """
        Generate complete Executive Intelligence Brief.
        
        Args:
            psip: Optional PSIP instance
            include_trade_brief: Whether to include SPY trade brief
            
        Returns:
            Complete ExecutiveBrief
        """
        # Generate ID and timestamp
        brief_id = f"EB-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
        
        # Create brief structure
        brief = ExecutiveBrief(
            id=brief_id,
            date=datetime.now(),
            strategic_cycle_id=self._generate_cycle_id(),
            system_status=SystemStatus.HEALTHY,
            strategic_posture=StrategicPosture.NEUTRAL,
        )
        
        # Collect agent signals
        agent_reports = []
        if psip:
            agent_reports = self.collector.collect_all_agents(psip)
        
        # Build domain reports
        self._build_domain_reports(brief, psip, agent_reports)
        
        # Build executive summary
        brief.executive_summary = self._build_executive_summary(brief, agent_reports)
        
        # Build domain overview
        brief.domain_overview = self._build_domain_overview(brief)
        
        # Build action plans
        brief.daily_action_plan = self._build_daily_action_plan(brief)
        brief.weekly_adjustments = self._build_weekly_adjustments(brief)
        brief.long_term_outlook = self._build_long_term_outlook(brief)
        
        # Build system health
        brief.system_health = self._build_system_health(psip)
        
        # Generate trade brief if requested
        if include_trade_brief:
            brief.spy_trade_brief = self.trade_engine.generate_trade_brief()
        
        # Set metrics
        brief.signals_processed = len(agent_reports) * 3  # Estimate
        brief.active_recommendations = sum(len(r.recommendations) for r in agent_reports)
        brief.risk_alerts = sum(len(r.alerts) for r in agent_reports)
        
        # Store and return
        self.generated_briefs.append(brief)
        return brief
    
    def _generate_cycle_id(self) -> str:
        """Generate strategic cycle ID."""
        return f"cycle-{datetime.now().strftime('%Y%m%d')}"
    
    def _build_domain_reports(
        self,
        brief: ExecutiveBrief,
        psip: Any | None,
        agent_reports: list
    ) -> None:
        """Build all domain reports."""
        # If we have PSIP, get reports from chief officers
        if psip and hasattr(psip, 'domains'):
            for domain_name, chief in psip.domains.items():
                # Get agent reports for this domain
                domain_agents = [r for r in agent_reports if r.domain == domain_name]
                
                # Build report using aggregator
                display_names = {
                    "finance": "Finance",
                    "health": "Health",
                    "career": "Career",
                    "relationships": "Relationships",
                    "intelligence": "Intelligence",
                    "life_architecture": "Life Architecture",
                }
                
                report = self.aggregator.build_domain_report(
                    domain_name=domain_name,
                    display_name=display_names.get(domain_name, domain_name.title()),
                    agent_reports=domain_agents
                )
                
                # Assign to appropriate field
                if domain_name == "finance":
                    brief.finance_domain = report
                elif domain_name == "health":
                    brief.health_domain = report
                elif domain_name == "career":
                    brief.career_domain = report
                elif domain_name == "relationships":
                    brief.relationships_domain = report
                elif domain_name == "intelligence":
                    brief.intelligence_domain = report
                elif domain_name == "life_architecture":
                    brief.life_architecture_domain = report
        else:
            # Create default domain reports
            brief.finance_domain = self.aggregator.build_domain_report("finance", "Finance")
            brief.health_domain = self.aggregator.build_domain_report("health", "Health")
            brief.career_domain = self.aggregator.build_domain_report("career", "Career")
            brief.relationships_domain = self.aggregator.build_domain_report("relationships", "Relationships")
            brief.intelligence_domain = self.aggregator.build_domain_report("intelligence", "Intelligence")
            brief.life_architecture_domain = self.aggregator.build_domain_report("life_architecture", "Life Architecture")
    
    def _build_executive_summary(
        self,
        brief: ExecutiveBrief,
        agent_reports: list
    ) -> ExecutiveSummarySection:
        """Build executive summary."""
        # Collect all priorities and alerts
        all_priorities = []
        all_alerts = []
        
        for r in agent_reports:
            all_priorities.extend(r.recommendations[:2])
            all_alerts.extend(r.alerts)
        
        # Determine system status
        if all_alerts:
            system_status = SystemStatus.DEGRADED
            narrative = f"System operating with {len(all_alerts)} active alerts requiring attention."
        else:
            system_status = SystemStatus.HEALTHY
            narrative = "All domains operating within normal parameters."
        
        # Determine posture based on scores
        avg_score = self._calculate_avg_domain_score(brief)
        if avg_score >= 70:
            posture = StrategicPosture.GROWTH
        elif avg_score >= 50:
            posture = StrategicPosture.NEUTRAL
        else:
            posture = StrategicPosture.DEFENSIVE
        
        return ExecutiveSummarySection(
            system_status=system_status,
            strategic_posture=posture,
            top_priorities=all_priorities[:3],
            critical_alerts=all_alerts[:3],
            opportunities=["Market opportunity detected", "Health optimization available"],
            threats=["Budget constraint", "Time limitation"],
            readiness_score=avg_score,
            narrative=narrative
        )
    
    def _calculate_avg_domain_score(self, brief: ExecutiveBrief) -> float:
        """Calculate average domain score."""
        scores = []
        for domain in brief.get_all_domains():
            if domain:
                scores.append(domain.score)
        return sum(scores) / len(scores) if scores else 50.0
    
    def _build_domain_overview(self, brief: ExecutiveBrief):
        """Build domain health overview."""
        return self.aggregator.build_domain_health_overview(brief.get_all_domains())
    
    def _build_daily_action_plan(self, brief: ExecutiveBrief) -> DailyActionPlan:
        """Build daily action plan."""
        plan = DailyActionPlan(date=datetime.now())
        
        # Add domain-specific actions
        actions = [
            DailyAction(
                id="fin-1",
                domain="finance",
                action="Review budget and expenses",
                priority=2,
                estimated_minutes=10,
                category="finance"
            ),
            DailyAction(
                id="hlth-1",
                domain="health",
                action="Complete workout routine",
                priority=1,
                estimated_minutes=45,
                category="health"
            ),
            DailyAction(
                id="career-1",
                domain="career",
                action="Progress on key project",
                priority=2,
                estimated_minutes=120,
                category="career"
            ),
            DailyAction(
                id="rel-1",
                domain="relationships",
                action="Connect with important person",
                priority=2,
                estimated_minutes=30,
                category="relationships"
            ),
            DailyAction(
                id="int-1",
                domain="intelligence",
                action="Learn something new",
                priority=3,
                estimated_minutes=20,
                category="learning"
            ),
        ]
        
        for action in actions:
            plan.add_action(action)
        
        plan.focus_areas = ["Finance", "Health", "Career", "Relationships"]
        
        return plan
    
    def _build_weekly_adjustments(self, brief: ExecutiveBrief) -> WeeklyAdjustments:
        """Build weekly adjustments."""
        adjustments = WeeklyAdjustments(week_start=datetime.now())
        
        weekly_items = [
            WeeklyAdjustment("finance", "Savings", "Review automatic transfers", "Improved savings consistency"),
            WeeklyAdjustment("health", "Training", "Assess weekly progress", "Better fitness outcomes"),
            WeeklyAdjustment("career", "Networking", "Schedule one networking activity", "Career growth"),
            WeeklyAdjustment("relationships", "Quality Time", "Plan weekend activity", "Stronger relationships"),
            WeeklyAdjustment("intelligence", "Learning", "Complete course module", "Knowledge expansion"),
            WeeklyAdjustment("life_architecture", "Goals", "Review quarterly objectives", "Goal alignment"),
        ]
        
        adjustments.adjustments = weekly_items
        return adjustments
    
    def _build_long_term_outlook(self, brief: ExecutiveBrief) -> LongTermOutlook:
        """Build long-term outlook."""
        return LongTermOutlook(
            timeline_1_year=[
                "Build 3-month emergency fund",
                "Achieve promotion or new role",
                "Establish consistent health routine"
            ],
            timeline_3_years=[
                "Reach financial independence milestone (25x expenses)",
                "Advance to leadership position",
                "Master key skills"
            ],
            timeline_5_years=[
                "Achieve financial independence",
                "Career advancement to executive level",
                "Maintain health and relationships"
            ],
            milestones=[
                {"year": 1, "title": "Foundation", "description": "Build base"},
                {"year": 3, "title": "Growth", "description": "Scale up"},
                {"year": 5, "title": "Independence", "description": "Achieve goals"},
            ]
        )
    
    def _build_system_health(self, psip: Any | None) -> SystemHealth:
        """Build system health section."""
        # Try to get actual health from PSIP
        score = 75.0
        
        if psip:
            try:
                from infrastructure.system_audit import SystemAuditEngine, AuditType
                engine = SystemAuditEngine(".")
                result = engine.run_light_health_check()
                score = result.overall_health_score
            except Exception:
                pass
        
        status = SystemStatus.HEALTHY if score >= 70 else SystemStatus.DEGRADED
        
        return SystemHealth(
            overall_score=score,
            architecture_score=90.0,
            agent_registry_score=80.0,
            signal_health_score=75.0,
            governance_score=85.0,
            data_integrity_score=95.0,
            status=status,
            critical_issues=[],
            warnings=["Agent coverage incomplete in some domains"],
        )
    
    def get_latest_brief(self) -> ExecutiveBrief | None:
        """Get the most recently generated brief."""
        if self.generated_briefs:
            return self.generated_briefs[-1]
        return None


__all__ = [
    "ExecutiveBriefGenerator",
]
