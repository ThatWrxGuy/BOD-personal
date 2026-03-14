"""Finance Governance Service - coordinates governance operations."""
from typing import Any, Dict, List, Optional

from app.finance.services.finance_state_service import FinanceStateService
from app.finance.intelligence.services.finance_intelligence_service import FinanceIntelligenceService
from app.finance.simulation.services.finance_simulation_service import FinanceSimulationService
from app.finance.governance.models.financial_board_brief import FinancialBoardBrief
from app.finance.governance.models.financial_decision_request import (
    FinancialDecisionRequest,
    DecisionClass,
    DecisionStatus,
)
from app.finance.governance.models.financial_decision_result import (
    FinancialDecisionResult,
    DecisionOutcome,
)
from app.finance.governance.models.financial_audit_event import AuditEventType
from app.finance.governance.engines.approval_router import ApprovalRouter
from app.finance.governance.engines.board_brief_generator import BoardBriefGenerator
from app.finance.governance.engines.financial_audit_logger import FinancialAuditLogger


class FinanceGovernanceService:
    """
    Coordinates governance operations.
    
    Functions:
    - generate_board_brief(profile_id)
    - submit_recommendation_for_decision(recommendation_id)
    - resolve_decision(decision_id)
    - get_pending_financial_decisions(profile_id)
    - get_financial_audit_log(profile_id)
    """

    def __init__(
        self,
        finance_state_service: FinanceStateService,
        intelligence_service: FinanceIntelligenceService,
        simulation_service: FinanceSimulationService,
    ):
        self.finance_state_service = finance_state_service
        self.intelligence_service = intelligence_service
        self.simulation_service = simulation_service
        
        # Initialize governance components
        self.approval_router = ApprovalRouter()
        self.audit_logger = FinancialAuditLogger()

    async def generate_board_brief(
        self,
        profile_id: int,
    ) -> FinancialBoardBrief:
        """
        Generate a board-ready financial intelligence brief.

        Args:
            profile_id: The profile ID

        Returns:
            FinancialBoardBrief for board presentation
        """
        # Get financial state
        financial_state = await self.finance_state_service.get_financial_state(profile_id)
        if not financial_state:
            financial_state = self._get_demo_financial_state(profile_id)

        # Get risks and opportunities
        risks = await self.intelligence_service.get_financial_risks(profile_id)
        opportunities = await self.intelligence_service.get_financial_opportunities(profile_id)
        
        # Get recommendations
        recommendations = await self.intelligence_service.generate_financial_recommendations(profile_id)
        
        # Get scenario summary (latest simulation results)
        scenario_results = await self.simulation_service.get_scenario_results(profile_id)
        scenario_summary = {}
        if scenario_results:
            latest = scenario_results[0]
            scenario_summary = {
                "last_scenario": latest.scenario_type.value,
                "projected_net_worth": latest.projected_net_worth,
                "risk_classification": latest.risk_classification,
            }

        # Generate board brief
        brief = BoardBriefGenerator.generate(
            financial_state=financial_state,
            risks=risks,
            opportunities=opportunities,
            recommendations=recommendations,
            scenario_summary=scenario_summary,
        )

        # Log board brief generation
        self.audit_logger.log_board_brief_generated(
            profile_id=profile_id,
            brief_id=brief.brief_id,
            financial_status=brief.financial_status.value,
        )

        return brief

    async def submit_recommendation_for_decision(
        self,
        recommendation_id: str,
    ) -> Optional[FinancialDecisionRequest]:
        """
        Submit a recommendation for governance decision.

        Args:
            recommendation_id: The recommendation ID

        Returns:
            FinancialDecisionRequest or None
        """
        # In production, would retrieve recommendation from intelligence service
        # For demo, create a mock recommendation
        recommendation = self._get_mock_recommendation(recommendation_id)
        if not recommendation:
            return None

        # Create decision request
        decision_request = self.approval_router.create_decision_request(recommendation)

        # Log decision request
        self.audit_logger.log_decision_requested(
            profile_id=recommendation.profile_id,
            decision_id=decision_request.decision_id,
            title=decision_request.title,
            decision_class=decision_request.decision_class.value,
        )

        return decision_request

    async def resolve_decision(
        self,
        decision_id: str,
        outcome: DecisionOutcome,
        reviewer: str = "system",
        review_notes: str = "",
    ) -> Optional[FinancialDecisionResult]:
        """
        Resolve a governance decision.

        Args:
            decision_id: The decision ID
            outcome: The decision outcome
            reviewer: Who is resolving the decision
            review_notes: Optional notes

        Returns:
            FinancialDecisionResult or None
        """
        # Get decision
        decision = self.approval_router.get_decision_by_id(decision_id)
        if not decision:
            return None

        # Update status
        if outcome == DecisionOutcome.APPROVED:
            self.approval_router.update_decision_status(decision_id, DecisionStatus.APPROVED)
        elif outcome == DecisionOutcome.REJECTED:
            self.approval_router.update_decision_status(decision_id, DecisionStatus.REJECTED)
        else:
            self.approval_router.update_decision_status(decision_id, DecisionStatus.DEFERRED)

        # Create result
        result = FinancialDecisionResult.create(
            decision_id=decision_id,
            decision_outcome=outcome,
            reviewer=reviewer,
            review_notes=review_notes,
        )

        # Log resolution
        self.audit_logger.log_decision_resolved(
            profile_id=decision.profile_id,
            decision_id=decision_id,
            outcome=outcome.value,
            reviewer=reviewer,
        )

        return result

    async def get_pending_financial_decisions(
        self,
        profile_id: int,
        decision_class: Optional[DecisionClass] = None,
    ) -> List[FinancialDecisionRequest]:
        """
        Get pending financial decisions for a profile.

        Args:
            profile_id: The profile ID
            decision_class: Optional filter by decision class

        Returns:
            List of pending decision requests
        """
        return self.approval_router.get_pending_decisions(profile_id, decision_class)

    async def get_financial_audit_log(
        self,
        profile_id: int,
        event_type: Optional[AuditEventType] = None,
        limit: int = 100,
    ) -> List:
        """
        Get financial audit log for a profile.

        Args:
            profile_id: The profile ID
            event_type: Optional filter by event type
            limit: Maximum number of events

        Returns:
            List of audit events
        """
        return self.audit_logger.get_audit_log(profile_id, event_type, limit)

    def _get_mock_recommendation(self, recommendation_id: str):
        """Get mock recommendation for demo."""
        from app.finance.intelligence.models.financial_recommendation import (
            FinancialRecommendation,
            Priority,
            ActionClass,
        )
        
        return FinancialRecommendation(
            recommendation_id=recommendation_id,
            profile_id=1,
            title="Accelerate Debt Payoff",
            summary="Use available cash flow to reduce high-interest debt faster.",
            rationale="Credit card debt erodes wealth through interest charges.",
            priority=Priority.HIGH,
            confidence_score=0.80,
            expected_benefit="Reduce interest costs and achieve debt freedom sooner.",
            downside_risk="Requires redirecting funds from other uses.",
            action_class=ActionClass.ADVISORY,
        )

    def _get_demo_financial_state(self, profile_id: int) -> Dict[str, Any]:
        """Get demo financial state for testing."""
        return {
            "profile_id": profile_id,
            "net_worth": -75000,
            "total_assets": 180000,
            "total_liabilities": 255000,
            "monthly_income": 6400,
            "monthly_expenses": 6150,
            "free_cash_flow": -1350,
            "liquid_assets": 30000,
            "total_debt": 255000,
            "debt_to_income_ratio": 0.2062,
            "emergency_fund_months": 29.3,
        }
