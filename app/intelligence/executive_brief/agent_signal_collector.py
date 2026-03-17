"""
BB-INT-007: Agent Signal Collector

Collects signals and insights from all domain agents.

Responsibilities:
- Query all domain agents
- Collect insights, recommendations, alerts
- Normalize outputs to standard format

Usage:
    from app.intelligence.executive_brief import AgentSignalCollector
    
    collector = AgentSignalCollector()
    agent_reports = collector.collect_all_agents(psip)
"""

from typing import Any

from .executive_brief_models import (
    AgentReport,
    create_agent_report,
)


class AgentSignalCollector:
    """
    Collects signals from all domain agents.
    
    Queries each domain's agents and aggregates their outputs.
    """
    
    def __init__(self):
        self.collected_reports: list[AgentReport] = []
    
    def collect_all_agents(self, psip: Any = None) -> list[AgentReport]:
        """
        Collect reports from all agents in the system.
        
        Args:
            psip: Optional PSIP instance
            
        Returns:
            List of AgentReport objects
        """
        self.collected_reports = []
        
        # If we have PSIP, collect from domain chief officers
        if psip and hasattr(psip, 'domains'):
            for domain_name, chief_officer in psip.domains.items():
                domain_reports = self._collect_from_chief(chief_officer, domain_name)
                self.collected_reports.extend(domain_reports)
        
        return self.collected_reports
    
    def _collect_from_chief(self, chief: Any, domain: str) -> list[AgentReport]:
        """Collect agent reports from a chief officer."""
        reports = []
        
        # Create a report for the chief officer itself
        chief_report = create_agent_report(
            agent_name=f"Chief {domain.title()} Officer",
            agent_id=f"chief_{domain}_officer",
            role="executive",
            domain=domain,
            insights=self._get_chief_insights(chief),
            recommendations=self._get_chief_recommendations(chief),
            alerts=self._get_chief_alerts(chief),
            confidence=0.7
        )
        reports.append(chief_report)
        
        # Get strategies from chief (representing domain agents)
        strategies = chief.get_active_strategies() if hasattr(chief, 'get_active_strategies') else []
        
        for strategy in strategies[:3]:  # Top 3 strategies
            strategy_report = create_agent_report(
                agent_name=strategy.title if hasattr(strategy, 'title') else "Strategy Agent",
                agent_id=f"strategy_{domain}_{strategy.id if hasattr(strategy, 'id') else '1'}",
                role="strategist",
                domain=domain,
                insights=[f"Strategy: {strategy.title}"],
                recommendations=[f"Execute: {strategy.title}"],
                confidence=0.6
            )
            reports.append(strategy_report)
        
        return reports
    
    def _get_chief_insights(self, chief: Any) -> list[str]:
        """Extract insights from chief officer."""
        insights = []
        
        if hasattr(chief, 'get_domain_status'):
            status = chief.get_domain_status()
            insights.append(f"Domain status: {status}")
        
        return insights
    
    def _get_chief_recommendations(self, chief: Any) -> list[str]:
        """Extract recommendations from chief officer."""
        recommendations = []
        
        if hasattr(chief, 'create_report'):
            try:
                report = chief.create_report()
                if hasattr(report, 'recommendations'):
                    recommendations = [r for r in report.recommendations[:3]]
            except Exception:
                pass
        
        return recommendations
    
    def _get_chief_alerts(self, chief: Any) -> list[str]:
        """Extract alerts from chief officer."""
        alerts = []
        
        # Check domain status for warnings
        if hasattr(chief, 'get_domain_status'):
            status = chief.get_domain_status()
            # Handle dict status
            if isinstance(status, str):
                if 'attention' in status.lower():
                    alerts.append(f"Domain requires attention: {status}")
            elif isinstance(status, dict):
                # Check for warning indicators in dict
                status_str = str(status)
                if 'attention' in status_str.lower() or 'critical' in status_str.lower():
                    alerts.append(f"Domain requires attention: {status}")
        
        return alerts
    
    def collect_domain_signals(self, domain: str, agents: list[Any]) -> list[AgentReport]:
        """
        Collect signals from a specific domain's agents.
        
        Args:
            domain: Domain name
            agents: List of agent instances
            
        Returns:
            List of AgentReport objects for the domain
        """
        reports = []
        
        for agent in agents:
            report = self._collect_from_agent(agent, domain)
            if report:
                reports.append(report)
        
        return reports
    
    def _collect_from_agent(self, agent: Any, domain: str) -> AgentReport | None:
        """Collect report from a single agent."""
        # This would be implemented based on agent interface
        # For now, return None as agents have varying interfaces
        
        if hasattr(agent, 'generate_insights'):
            try:
                insights = agent.generate_insights()
            except Exception:
                insights = []
        else:
            insights = []
        
        return create_agent_report(
            agent_name=agent.__class__.__name__,
            agent_id=f"{domain}_{agent.__class__.__name__.lower()}",
            role="strategist",
            domain=domain,
            insights=insights if isinstance(insights, list) else [str(insights)],
            confidence=0.5
        )
    
    def get_reports_by_domain(self, domain: str) -> list[AgentReport]:
        """Get all reports for a specific domain."""
        return [r for r in self.collected_reports if r.domain == domain]
    
    def get_all_alerts(self) -> list[str]:
        """Get all alerts from collected reports."""
        alerts = []
        for report in self.collected_reports:
            alerts.extend(report.alerts)
        return alerts
    
    def get_all_recommendations(self) -> list[str]:
        """Get all recommendations from collected reports."""
        recs = []
        for report in self.collected_reports:
            recs.extend(report.recommendations)
        return recs


__all__ = [
    "AgentSignalCollector",
]
