"""
BB-APP-002: Domains Service

Per BB-APP-002 Section 8.3 - Domain Integration.
"""

from datetime import datetime, timedelta
from typing import List, Dict

from app.read_models import (
    DomainOverviewReadModel,
    DomainDetailReadModel,
    DomainScoreHistory,
    DomainSignal,
    DomainRecommendation,
    DomainAction,
    DomainStatus,
    TrendDirection,
    RecommendationStatus,
    ActionStatus,
)


class DomainsService:
    """Service for domain data."""
    
    DOMAINS = {
        "finance": {
            "id": "finance",
            "name": "Finance",
            "description": "Financial health, investments, and wealth building"
        },
        "health": {
            "id": "health", 
            "name": "Health",
            "description": "Physical and mental well-being"
        },
        "career": {
            "id": "career",
            "name": "Career",
            "description": "Professional growth and income"
        },
        "relationships": {
            "id": "relationships",
            "name": "Relationships",
            "description": "Personal connections and social health"
        },
        "intelligence": {
            "id": "intelligence",
            "name": "Intelligence",
            "description": "Knowledge and cognitive development"
        },
        "life-architecture": {
            "id": "life-architecture",
            "name": "Life Architecture",
            "description": "Life design and long-term planning"
        },
    }
    
    async def list_domains(self, user_id: str) -> List[DomainOverviewReadModel]:
        """List all domain overviews."""
        # Mock data - in production, this would query the database
        return [
            DomainOverviewReadModel(
                domain_id="finance",
                domain_name="Finance",
                description=self.DOMAINS["finance"]["description"],
                score=78,
                trend=TrendDirection.UP,
                status=DomainStatus.HEALTHY,
                recommendations_count=3,
                pending_actions_count=2,
                active_signals_count=5
            ),
            DomainOverviewReadModel(
                domain_id="health",
                domain_name="Health",
                description=self.DOMAINS["health"]["description"],
                score=65,
                trend=TrendDirection.DOWN,
                status=DomainStatus.CAUTION,
                recommendations_count=2,
                pending_actions_count=1,
                active_signals_count=3
            ),
            DomainOverviewReadModel(
                domain_id="career",
                domain_name="Career",
                description=self.DOMAINS["career"]["description"],
                score=82,
                trend=TrendDirection.UP,
                status=DomainStatus.HEALTHY,
                recommendations_count=1,
                pending_actions_count=3,
                active_signals_count=4
            ),
            DomainOverviewReadModel(
                domain_id="relationships",
                domain_name="Relationships",
                description=self.DOMAINS["relationships"]["description"],
                score=71,
                trend=TrendDirection.STABLE,
                status=DomainStatus.HEALTHY,
                recommendations_count=2,
                pending_actions_count=0,
                active_signals_count=2
            ),
            DomainOverviewReadModel(
                domain_id="intelligence",
                domain_name="Intelligence",
                description=self.DOMAINS["intelligence"]["description"],
                score=58,
                trend=TrendDirection.DOWN,
                status=DomainStatus.CAUTION,
                recommendations_count=4,
                pending_actions_count=2,
                active_signals_count=6
            ),
            DomainOverviewReadModel(
                domain_id="life-architecture",
                domain_name="Life Architecture",
                description=self.DOMAINS["life-architecture"]["description"],
                score=73,
                trend=TrendDirection.UP,
                status=DomainStatus.HEALTHY,
                recommendations_count=1,
                pending_actions_count=1,
                active_signals_count=3
            ),
        ]
    
    async def get_domain(self, domain_id: str, user_id: str) -> DomainDetailReadModel | None:
        """Get detailed domain data."""
        if domain_id not in self.DOMAINS:
            return None
        
        domain_info = self.DOMAINS[domain_id]
        
        # Generate mock data based on domain
        if domain_id == "finance":
            return DomainDetailReadModel(
                domain_id=domain_id,
                domain_name=domain_info["name"],
                description=domain_info["description"],
                score=78,
                trend=TrendDirection.UP,
                status=DomainStatus.HEALTHY,
                score_history=self._generate_score_history(78),
                active_signals=[
                    DomainSignal(
                        id="sig-1",
                        signal_type="spending",
                        description="Monthly spending under budget",
                        timestamp=datetime.now() - timedelta(days=1),
                        importance=8
                    ),
                    DomainSignal(
                        id="sig-2",
                        signal_type="investment",
                        description="Portfolio gained 3% this month",
                        timestamp=datetime.now() - timedelta(days=2),
                        importance=7
                    ),
                ],
                key_issues=["Debt-to-income ratio slightly elevated"],
                opportunities=["Consider increasing retirement contributions"],
                recommendations=[
                    DomainRecommendation(
                        id="rec-1",
                        title="Increase retirement savings by 5%",
                        confidence=0.85,
                        urgency=3,
                        status=RecommendationStatus.PROPOSED
                    ),
                ],
                open_actions=[
                    DomainAction(
                        id="action-1",
                        title="Review Q1 budget",
                        status=ActionStatus.PROPOSED,
                        due_date=datetime.now() + timedelta(days=3)
                    ),
                ],
                cross_domain_dependencies=["Career (income)", "Life Architecture (goals)"],
                recent_changes=["Budget discipline improved", "Investment returns positive"]
            )
        
        elif domain_id == "health":
            return DomainDetailReadModel(
                domain_id=domain_id,
                domain_name=domain_info["name"],
                description=domain_info["description"],
                score=65,
                trend=TrendDirection.DOWN,
                status=DomainStatus.CAUTION,
                score_history=self._generate_score_history(65),
                active_signals=[
                    DomainSignal(
                        id="sig-3",
                        signal_type="sleep",
                        description="Sleep duration below target",
                        timestamp=datetime.now() - timedelta(hours=6),
                        importance=9
                    ),
                ],
                key_issues=["Sleep deficit accumulating", "Exercise inconsistent"],
                opportunities=["Implement consistent sleep schedule"],
                recommendations=[
                    DomainRecommendation(
                        id="rec-4",
                        title="Optimize sleep schedule",
                        confidence=0.78,
                        urgency=3,
                        status=RecommendationStatus.PROPOSED
                    ),
                ],
                open_actions=[
                    DomainAction(
                        id="action-2",
                        title="Schedule health checkup",
                        status=ActionStatus.PROPOSED,
                        due_date=datetime.now() + timedelta(days=7)
                    ),
                ],
                cross_domain_dependencies=["Career (energy)", "Intelligence (focus)"],
                recent_changes=["Sleep quality declined", "Exercise frequency reduced"]
            )
        
        # Generic response for other domains
        return DomainDetailReadModel(
            domain_id=domain_id,
            domain_name=domain_info["name"],
            description=domain_info["description"],
            score=70,
            trend=TrendDirection.STABLE,
            status=DomainStatus.HEALTHY,
            score_history=self._generate_score_history(70),
            active_signals=[],
            key_issues=[],
            opportunities=[],
            recommendations=[],
            open_actions=[],
            cross_domain_dependencies=[],
            recent_changes=[]
        )
    
    def _generate_score_history(self, current_score: int) -> List[DomainScoreHistory]:
        """Generate mock score history."""
        base_score = current_score
        history = []
        now = datetime.now()
        
        for i in range(30):
            # Add some variation
            variation = (i % 7) - 3
            score = max(0, min(100, base_score + variation))
            history.append(DomainScoreHistory(
                timestamp=now - timedelta(days=i),
                score=score
            ))
        
        return list(reversed(history))


# Singleton instance
domains_service = DomainsService()
