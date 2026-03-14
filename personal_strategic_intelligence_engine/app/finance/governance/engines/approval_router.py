"""Approval Router - routes governance decisions to the appropriate approval layer."""
from typing import Any, Dict, List, Optional

from app.finance.intelligence.models.financial_recommendation import FinancialRecommendation
from app.finance.governance.models.financial_decision_request import (
    FinancialDecisionRequest,
    DecisionClass,
    DecisionStatus,
)
from app.finance.governance.engines.recommendation_classifier import RecommendationClassifier


class ApprovalRouter:
    """
    Routes governance decisions to the appropriate approval layer.
    
    Responsibilities:
    - Create FinancialDecisionRequest
    - Assign approval class
    - Track decision status
    
    Routing logic:
    - informational → no approval required
    - user_approval → user decision queue
    - board_review → board decision queue
    """

    def __init__(self):
        # In-memory storage (would be database in production)
        self._decision_requests: Dict[str, FinancialDecisionRequest] = {}

    def create_decision_request(
        self,
        recommendation: FinancialRecommendation,
    ) -> FinancialDecisionRequest:
        """
        Create a governance decision request from a recommendation.

        Args:
            recommendation: The financial recommendation

        Returns:
            FinancialDecisionRequest ready for routing
        """
        # Classify the recommendation
        decision_class = RecommendationClassifier.classify(recommendation)
        
        # Create decision request
        decision_request = FinancialDecisionRequest.create(
            recommendation_id=recommendation.recommendation_id,
            profile_id=recommendation.profile_id,
            decision_class=decision_class,
            title=recommendation.title,
            summary=recommendation.summary,
            expected_impact=recommendation.expected_benefit,
            downside_risk=recommendation.downside_risk,
            confidence_score=recommendation.confidence_score,
        )
        
        # Store request
        self._decision_requests[decision_request.decision_id] = decision_request
        
        return decision_request

    def get_pending_decisions(
        self,
        profile_id: int,
        decision_class: Optional[DecisionClass] = None,
    ) -> List[FinancialDecisionRequest]:
        """
        Get pending decisions for a profile.

        Args:
            profile_id: The profile ID
            decision_class: Optional filter by decision class

        Returns:
            List of pending decision requests
        """
        pending = []
        
        for decision in self._decision_requests.values():
            if decision.profile_id != profile_id:
                continue
            
            if decision.status != DecisionStatus.PENDING:
                continue
            
            if decision_class and decision.decision_class != decision_class:
                continue
            
            pending.append(decision)
        
        return pending

    def get_decision_by_id(self, decision_id: str) -> Optional[FinancialDecisionRequest]:
        """
        Get a specific decision request by ID.

        Args:
            decision_id: The decision ID

        Returns:
            FinancialDecisionRequest or None
        """
        return self._decision_requests.get(decision_id)

    def update_decision_status(
        self,
        decision_id: str,
        status: DecisionStatus,
    ) -> bool:
        """
        Update the status of a decision request.

        Args:
            decision_id: The decision ID
            status: New status

        Returns:
            True if updated, False if not found
        """
        decision = self._decision_requests.get(decision_id)
        if not decision:
            return False
        
        decision.status = status
        return True

    def get_routing_summary(self, profile_id: int) -> Dict[str, Any]:
        """
        Get summary of routing for a profile.

        Args:
            profile_id: The profile ID

        Returns:
            Dictionary with routing statistics
        """
        decisions = [
            d for d in self._decision_requests.values()
            if d.profile_id == profile_id
        ]
        
        return {
            "total": len(decisions),
            "pending": len([d for d in decisions if d.status == DecisionStatus.PENDING]),
            "approved": len([d for d in decisions if d.status == DecisionStatus.APPROVED]),
            "rejected": len([d for d in decisions if d.status == DecisionStatus.REJECTED]),
            "deferred": len([d for d in decisions if d.status == DecisionStatus.DEFERRED]),
            "informational": len([d for d in decisions if d.decision_class == DecisionClass.INFORMATIONAL]),
            "user_approval": len([d for d in decisions if d.decision_class == DecisionClass.USER_APPROVAL]),
            "board_review": len([d for d in decisions if d.decision_class == DecisionClass.BOARD_REVIEW]),
        }
