"""
BB-APP-002: Recommendations Service

Per BB-APP-002 Section 8.4 - Recommendations Integration.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from app.read_models import (
    RecommendationDetailReadModel,
    RecommendationSummaryReadModel,
    RecommendationStatus,
    ActionOrigin,
)
from app.commands import (
    ApproveRecommendationCommand,
    RejectRecommendationCommand,
    DeferRecommendationCommand,
    CreateActionFromRecommendationCommand,
    RecommendationCommandHandler,
)


class RecommendationsService:
    """Service for recommendations."""
    
    # Mock recommendation store
    _recommendations = {
        "rec-1": {
            "id": "rec-1",
            "title": "Increase retirement savings by 5%",
            "description": "Based on your current savings rate and retirement goals, increasing your contribution would accelerate your timeline.",
            "domain": "Finance",
            "confidence": 0.85,
            "urgency": 3,
            "status": RecommendationStatus.PROPOSED,
            "rationale": "Your current savings rate is below the recommended threshold for your age and retirement goals.",
            "expected_benefit": "Accelerate retirement timeline by 2-3 years",
            "likely_tradeoff": "Reduced disposable income",
            "supporting_signals": ["Income increased", "Expenses decreased", "Current savings rate below target"],
            "affected_domains": ["Finance", "Life Architecture"],
            "source_brief_id": "brief-001",
            "linked_actions": [],
            "created_at": datetime.now() - timedelta(days=2),
            "expires_at": None,
            "acknowledged_at": None,
        },
        "rec-2": {
            "id": "rec-2",
            "title": "Schedule weekly social connection time",
            "description": "Your relationship domain shows declining engagement. Regular social activities can improve overall well-being.",
            "domain": "Relationships",
            "confidence": 0.72,
            "urgency": 2,
            "status": RecommendationStatus.PROPOSED,
            "rationale": "Social engagement signals have been declining over the past month.",
            "expected_benefit": "Improved well-being and relationship health",
            "likely_tradeoff": "Time commitment",
            "supporting_signals": ["Social events declined", "Contact frequency reduced"],
            "affected_domains": ["Relationships", "Health"],
            "source_brief_id": "brief-001",
            "linked_actions": [],
            "created_at": datetime.now() - timedelta(days=1),
            "expires_at": None,
            "acknowledged_at": None,
        },
        "rec-3": {
            "id": "rec-3",
            "title": "Optimize sleep schedule",
            "description": "Health signals indicate irregular sleep patterns. Consistent sleep timing could improve energy and focus.",
            "domain": "Health",
            "confidence": 0.78,
            "urgency": 3,
            "status": RecommendationStatus.APPROVED,
            "rationale": "Sleep tracking shows inconsistent bedtimes affecting recovery metrics.",
            "expected_benefit": "Improved energy and cognitive performance",
            "likely_tradeoff": "Schedule adjustment required",
            "supporting_signals": ["Sleep duration inconsistent", "Recovery score below baseline"],
            "affected_domains": ["Health", "Career", "Intelligence"],
            "source_brief_id": "brief-001",
            "linked_actions": ["action-4"],
            "created_at": datetime.now() - timedelta(days=3),
            "expires_at": None,
            "acknowledged_at": datetime.now() - timedelta(hours=12),
        },
        "rec-4": {
            "id": "rec-4",
            "title": "Complete skill certification",
            "description": "Career advancement opportunity identified. Certification would strengthen your professional profile.",
            "domain": "Career",
            "confidence": 0.65,
            "urgency": 1,
            "status": RecommendationStatus.PROPOSED,
            "rationale": "Market analysis shows demand for this certification in your field.",
            "expected_benefit": "Career advancement and salary potential",
            "likely_tradeoff": "Learning time investment",
            "supporting_signals": ["Job market demand", "Skill gap identified"],
            "affected_domains": ["Career"],
            "source_brief_id": "brief-001",
            "linked_actions": [],
            "created_at": datetime.now() - timedelta(days=5),
            "expires_at": None,
            "acknowledged_at": None,
        },
    }
    
    async def list_recommendations(
        self,
        user_id: str,
        domain: Optional[str] = None,
        status: Optional[RecommendationStatus] = None,
        limit: int = 50
    ) -> List[RecommendationSummaryReadModel]:
        """List recommendations with optional filters."""
        results = []
        
        for rec in self._recommendations.values():
            # Apply filters
            if domain and rec["domain"].lower() != domain.lower():
                continue
            if status and rec["status"] != status:
                continue
            
            results.append(RecommendationSummaryReadModel(
                id=rec["id"],
                title=rec["title"],
                domain=rec["domain"],
                confidence=rec["confidence"],
                urgency=rec["urgency"],
                status=rec["status"],
                expected_impact="High" if rec["urgency"] >= 3 else "Medium" if rec["urgency"] >= 2 else "Low"
            ))
        
        return results[:limit]
    
    async def get_recommendation(
        self,
        recommendation_id: str,
        user_id: str
    ) -> Optional[RecommendationDetailReadModel]:
        """Get detailed recommendation."""
        rec = self._recommendations.get(recommendation_id)
        if not rec:
            return None
        
        return RecommendationDetailReadModel(
            id=rec["id"],
            title=rec["title"],
            description=rec["description"],
            domain=rec["domain"],
            confidence=rec["confidence"],
            urgency=rec["urgency"],
            status=rec["status"],
            rationale=rec["rationale"],
            expected_benefit=rec["expected_benefit"],
            likely_tradeoff=rec["likely_tradeoff"],
            supporting_signals=rec["supporting_signals"],
            affected_domains=rec["affected_domains"],
            source_brief_id=rec.get("source_brief_id"),
            linked_actions=rec.get("linked_actions", []),
            created_at=rec["created_at"],
            expires_at=rec.get("expires_at"),
            acknowledged_at=rec.get("acknowledged_at"),
        )
    
    async def approve_recommendation(
        self,
        recommendation_id: str,
        user_id: str,
        notes: str = ""
    ) -> bool:
        """Approve a recommendation."""
        handler = RecommendationCommandHandler()
        command = ApproveRecommendationCommand(
            recommendation_id=recommendation_id,
            user_id=user_id,
            notes=notes
        )
        result = handler.handle_approve(command)
        
        if result.success and recommendation_id in self._recommendations:
            self._recommendations[recommendation_id]["status"] = RecommendationStatus.APPROVED
            self._recommendations[recommendation_id]["acknowledged_at"] = datetime.now()
        
        return result.success
    
    async def reject_recommendation(
        self,
        recommendation_id: str,
        user_id: str,
        reason: str = ""
    ) -> bool:
        """Reject a recommendation."""
        handler = RecommendationCommandHandler()
        command = RejectRecommendationCommand(
            recommendation_id=recommendation_id,
            user_id=user_id,
            reason=reason
        )
        result = handler.handle_reject(command)
        
        if result.success and recommendation_id in self._recommendations:
            self._recommendations[recommendation_id]["status"] = RecommendationStatus.REJECTED
            self._recommendations[recommendation_id]["acknowledged_at"] = datetime.now()
        
        return result.success
    
    async def defer_recommendation(
        self,
        recommendation_id: str,
        user_id: str,
        defer_until: Optional[datetime] = None,
        reason: str = ""
    ) -> bool:
        """Defer a recommendation."""
        handler = RecommendationCommandHandler()
        command = DeferRecommendationCommand(
            recommendation_id=recommendation_id,
            user_id=user_id,
            defer_until=defer_until,
            reason=reason
        )
        result = handler.handle_defer(command)
        
        if result.success and recommendation_id in self._recommendations:
            self._recommendations[recommendation_id]["status"] = RecommendationStatus.DEFERRED
            self._recommendations[recommendation_id]["acknowledged_at"] = datetime.now()
        
        return result.success
    
    async def convert_to_action(
        self,
        recommendation_id: str,
        user_id: str,
        title: str,
        description: str = "",
        due_date: Optional[datetime] = None
    ) -> Optional[str]:
        """Convert recommendation to action."""
        handler = RecommendationCommandHandler()
        command = CreateActionFromRecommendationCommand(
            recommendation_id=recommendation_id,
            user_id=user_id,
            title=title or self._recommendations[recommendation_id]["title"],
            description=description or self._recommendations[recommendation_id]["description"],
            domain=self._recommendations[recommendation_id]["domain"],
            due_date=due_date
        )
        result = handler.handle_create_from_recommendation(command)
        
        if result.success:
            action_id = result.entity_id
            if recommendation_id in self._recommendations:
                self._recommendations[recommendation_id]["linked_actions"].append(action_id)
            return action_id
        
        return None


# Singleton instance
recommendations_service = RecommendationsService()
