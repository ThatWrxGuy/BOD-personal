"""
BB-INT-007: Domain Intelligence Aggregator

Aggregates agent signals into domain-level intelligence.

Responsibilities:
- Compute domain health scores
- Aggregate agent insights
- Detect conflicts between agents
- Generate domain reports

Usage:
    from app.intelligence.executive_brief import DomainIntelligenceAggregator
    
    aggregator = DomainIntelligenceAggregator()
    domain_report = aggregator.build_domain_report("finance", agent_reports)
"""

from typing import Any

from .executive_brief_models import (
    DomainReport,
    DomainHealthOverview,
    SystemStatus,
    AgentReport,
)


class DomainIntelligenceAggregator:
    """
    Aggregates agent signals into domain intelligence.
    
    Computes domain scores and aggregates outputs from all agents.
    """
    
    def __init__(self):
        self.domain_scores: dict[str, float] = {}
    
    def build_domain_report(
        self,
        domain_name: str,
        display_name: str,
        agent_reports: list[AgentReport] | None = None
    ) -> DomainReport:
        """
        Build a complete domain report.
        
        Args:
            domain_name: Internal domain name (e.g., 'finance')
            display_name: Display name (e.g., 'Finance')
            agent_reports: List of agent reports
            
        Returns:
            DomainReport with aggregated intelligence
        """
        agent_reports = agent_reports or []
        
        # Aggregate all insights, recommendations, alerts
        all_insights = []
        all_recommendations = []
        all_alerts = []
        
        for agent in agent_reports:
            all_insights.extend(agent.insights)
            all_recommendations.extend(agent.recommendations)
            all_alerts.extend(agent.alerts)
        
        # Calculate domain score
        score = self.calculate_domain_score(agent_reports)
        
        # Determine status
        status = self._determine_status(score)
        
        # Determine trend
        trend = self._determine_trend(score)
        
        return DomainReport(
            domain_name=domain_name,
            display_name=display_name,
            score=score,
            agents=agent_reports,
            insights=all_insights[:5],  # Top 5 unique insights
            recommendations=all_recommendations[:3],  # Top 3 recommendations
            alerts=all_alerts,
            status=status,
            trend=trend,
            active_signals=len(all_insights),
            pending_actions=len(all_recommendations),
        )
    
    def calculate_domain_score(self, agent_reports: list[AgentReport]) -> float:
        """
        Calculate domain health score (0-100).
        
        Factors:
        - Agent confidence scores
        - Number of active agents
        - Alert count (negative factor)
        - Recommendation count (positive factor)
        """
        if not agent_reports:
            return 50.0  # Default score
        
        # Base score from confidence
        avg_confidence = sum(a.confidence_score for a in agent_reports) / len(agent_reports)
        base_score = 40 + (avg_confidence * 40)  # 40-80 range
        
        # Bonus for agents
        agent_bonus = min(len(agent_reports) * 2, 10)  # Up to +10
        
        # Penalty for alerts
        total_alerts = sum(len(a.alerts) for a in agent_reports)
        alert_penalty = total_alerts * 5  # -5 per alert
        
        # Bonus for recommendations
        total_recs = sum(len(a.recommendations) for a in agent_reports)
        rec_bonus = min(total_recs * 2, 10)  # Up to +10
        
        final_score = base_score + agent_bonus - alert_penalty + rec_bonus
        
        return max(0.0, min(100.0, final_score))
    
    def _determine_status(self, score: float) -> SystemStatus:
        """Determine system status from score."""
        if score >= 70:
            return SystemStatus.HEALTHY
        elif score >= 40:
            return SystemStatus.DEGRADED
        else:
            return SystemStatus.CRITICAL
    
    def _determine_trend(self, score: float) -> str:
        """Determine trend from score (simplified)."""
        if score >= 70:
            return "improving"
        elif score >= 40:
            return "stable"
        else:
            return "declining"
    
    def build_domain_health_overview(
        self,
        domain_reports: list[DomainReport]
    ) -> DomainHealthOverview:
        """
        Build domain health overview from all domain reports.
        
        Args:
            domain_reports: List of all domain reports
            
        Returns:
            DomainHealthOverview with scores for each domain
        """
        scores = {
            "finance": 0.0,
            "health": 0.0,
            "career": 0.0,
            "relationships": 0.0,
            "intelligence": 0.0,
            "life_architecture": 0.0,
        }
        
        for report in domain_reports:
            if report.domain_name in scores:
                scores[report.domain_name] = report.score
        
        return DomainHealthOverview(
            finance_score=scores["finance"],
            health_score=scores["health"],
            career_score=scores["career"],
            relationships_score=scores["relationships"],
            intelligence_score=scores["intelligence"],
            life_architecture_score=scores["life_architecture"],
        )
    
    def detect_conflicts(self, agent_reports: list[AgentReport]) -> list[dict]:
        """
        Detect conflicting recommendations between agents.
        
        Args:
            agent_reports: List of agent reports
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        # Simple conflict detection based on opposing keywords
        for i, agent1 in enumerate(agent_reports):
            for agent2 in agent_reports[i+1:]:
                # Check for opposing recommendations
                recs1 = set(r.lower() for r in agent1.recommendations)
                recs2 = set(r.lower() for r in agent2.recommendations)
                
                # Simple conflict detection (example)
                if any(r in recs2 for r in recs1):
                    conflicts.append({
                        "agent1": agent1.agent_name,
                        "agent2": agent2.agent_name,
                        "type": "overlapping_recommendations",
                        "recommendations": list(recs1.intersection(recs2))
                    })
        
        return conflicts
    
    def aggregate_all_domains(
        self,
        domain_data: dict[str, list[AgentReport]]
    ) -> dict[str, DomainReport]:
        """
        Aggregate all domains.
        
        Args:
            domain_data: Dict mapping domain name to agent reports
            
        Returns:
            Dict mapping domain name to DomainReport
        """
        display_names = {
            "finance": "Finance",
            "health": "Health",
            "career": "Career",
            "relationships": "Relationships",
            "intelligence": "Intelligence",
            "life_architecture": "Life Architecture",
        }
        
        result = {}
        
        for domain_name, agents in domain_data.items():
            result[domain_name] = self.build_domain_report(
                domain_name=domain_name,
                display_name=display_names.get(domain_name, domain_name.title()),
                agent_reports=agents
            )
        
        return result


__all__ = [
    "DomainIntelligenceAggregator",
]
