"""
BB-APP-002: Dashboard Aggregator

Aggregates data from multiple sources into a unified executive view.
Per BB-APP-002 Section 14 - Dashboard Aggregation Architecture.
"""

from datetime import datetime, timedelta
from dataclasses import asdict

from app.read_models import (
    DashboardReadModel,
    DomainHealthSummary,
    PriorityItem,
    UrgentRecommendation,
    PendingAction,
    SystemStatusInfo,
    BriefSummary,
    SystemStatus,
    StrategicPosture,
    DomainStatus,
    TrendDirection,
    RecommendationStatus,
    ActionStatus,
    RecommendationUrgency,
)


class DashboardAggregator:
    """Aggregates dashboard data from multiple sources."""
    
    async def get_dashboard(self, user_id: str) -> DashboardReadModel:
        """
        Get the complete dashboard read model.
        
        In production, this would pull from:
        - Orchestration state snapshot
        - Strategic posture
        - Current brief
        - Priority router outputs
        - Urgent recommendations
        - Pending actions
        - Domain summaries
        - Recent changes
        """
        
        # Mock data - in production, these would be service calls
        system_status = SystemStatusInfo(
            status=SystemStatus.HEALTHY,
            posture=StrategicPosture.NEUTRAL,
            readiness_score=85,
            risk_alerts=2,
            last_updated=datetime.now()
        )
        
        brief = BriefSummary(
            id="brief-001",
            title="Executive Brief - Week 12, 2024",
            generated_at=datetime.now() - timedelta(hours=2),
            posture=StrategicPosture.NEUTRAL,
            readiness_score=85
        )
        
        domain_health = [
            DomainHealthSummary(
                domain_id="finance",
                domain_name="Finance",
                score=78,
                trend=TrendDirection.UP,
                status=DomainStatus.HEALTHY,
                active_recommendations=3,
                pending_actions=2
            ),
            DomainHealthSummary(
                domain_id="health",
                domain_name="Health",
                score=65,
                trend=TrendDirection.DOWN,
                status=DomainStatus.CAUTION,
                active_recommendations=2,
                pending_actions=1
            ),
            DomainHealthSummary(
                domain_id="career",
                domain_name="Career",
                score=82,
                trend=TrendDirection.UP,
                status=DomainStatus.HEALTHY,
                active_recommendations=1,
                pending_actions=3
            ),
            DomainHealthSummary(
                domain_id="relationships",
                domain_name="Relationships",
                score=71,
                trend=TrendDirection.STABLE,
                status=DomainStatus.HEALTHY,
                active_recommendations=2,
                pending_actions=0
            ),
            DomainHealthSummary(
                domain_id="intelligence",
                domain_name="Intelligence",
                score=58,
                trend=TrendDirection.DOWN,
                status=DomainStatus.CAUTION,
                active_recommendations=4,
                pending_actions=2
            ),
            DomainHealthSummary(
                domain_id="life-architecture",
                domain_name="Life Architecture",
                score=73,
                trend=TrendDirection.UP,
                status=DomainStatus.HEALTHY,
                active_recommendations=1,
                pending_actions=1
            ),
        ]
        
        priorities = [
            PriorityItem(
                id="priority-1",
                title="Complete quarterly career review",
                domain="Career",
                urgency=RecommendationUrgency.HIGH,
                recommendation_id="rec-1"
            ),
            PriorityItem(
                id="priority-2",
                title="Schedule health checkup",
                domain="Health",
                urgency=RecommendationUrgency.MEDIUM,
                recommendation_id="rec-2"
            ),
            PriorityItem(
                id="priority-3",
                title="Review investment rebalancing",
                domain="Finance",
                urgency=RecommendationUrgency.LOW,
                recommendation_id="rec-3"
            ),
        ]
        
        urgent_recommendations = [
            UrgentRecommendation(
                id="rec-1",
                title="Increase retirement savings by 5%",
                domain="Finance",
                confidence=0.85,
                urgency=3,
                status=RecommendationStatus.PROPOSED
            ),
            UrgentRecommendation(
                id="rec-2",
                title="Schedule weekly social connection time",
                domain="Relationships",
                confidence=0.72,
                urgency=2,
                status=RecommendationStatus.PROPOSED
            ),
        ]
        
        pending_actions = [
            PendingAction(
                id="action-1",
                title="Complete weekly review",
                domain="Review",
                due_date=datetime.now(),
                status=ActionStatus.PROPOSED
            ),
            PendingAction(
                id="action-2",
                title="Update career goals",
                domain="Career",
                due_date=datetime.now() + timedelta(days=1),
                status=ActionStatus.PROPOSED
            ),
            PendingAction(
                id="action-3",
                title="Review Q1 budget",
                domain="Finance",
                due_date=datetime.now() + timedelta(days=3),
                status=ActionStatus.PROPOSED
            ),
        ]
        
        recent_changes = [
            "Career score improved by 5 points",
            "New recommendation: Optimize sleep schedule",
            "Health domain moved to caution status",
        ]
        
        return DashboardReadModel(
            system_status=system_status,
            brief=brief,
            domain_health=domain_health,
            priorities=priorities,
            urgent_recommendations=urgent_recommendations,
            pending_actions=pending_actions,
            recent_changes=recent_changes
        )
    
    def to_dict(self, model: DashboardReadModel) -> dict:
        """Convert to dictionary for JSON serialization."""
        def serialize_value(v):
            if hasattr(v, '__dict__'):
                return asdict(v)
            elif isinstance(v, list):
                return [serialize_value(i) for i in v]
            elif isinstance(v, datetime):
                return v.isoformat()
            elif hasattr(v, 'value'):
                return v.value
            return v
        
        return serialize_value(model)


# Singleton instance
dashboard_aggregator = DashboardAggregator()
