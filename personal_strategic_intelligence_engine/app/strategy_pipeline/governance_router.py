"""Governance Router - submits proposals to the Intelligence Governor for approval."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from app.strategy_pipeline.proposal_models import (
    DebateFeedback,
    GovernanceDecision,
    RiskLevel,
    SimulationResult,
    StrategyProposal,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class ApprovalLevel(str, Enum):
    """Approval levels based on risk."""
    AUTOMATIC = "automatic"  # LOW risk
    EXECUTIVE = "executive"  # MEDIUM risk
    GOVERNANCE = "governance"  # HIGH risk
    CEO = "ceo"  # CRITICAL risk


class GovernanceRouter:
    """
    The Governance Router submits proposals to the Intelligence Governor for approval.
    
    Approval rules:
    - LOW: Automatic approval
    - MEDIUM: Executive review
    - HIGH: Governance approval
    - CRITICAL: CEO approval required
    """
    
    # Risk to approval level mapping
    RISK_APPROVAL_MAP = {
        RiskLevel.LOW: ApprovalLevel.AUTOMATIC,
        RiskLevel.MEDIUM: ApprovalLevel.EXECUTIVE,
        RiskLevel.HIGH: ApprovalLevel.GOVERNANCE,
        RiskLevel.CRITICAL: ApprovalLevel.CEO,
    }
    
    # Approval level weights (for decision calculation)
    APPROVAL_WEIGHTS = {
        ApprovalLevel.AUTOMATIC: 1.0,
        ApprovalLevel.EXECUTIVE: 0.8,
        ApprovalLevel.GOVERNANCE: 0.6,
        ApprovalLevel.CEO: 0.4,
    }
    
    def __init__(self):
        self.decision_history: Dict[str, GovernanceDecision] = {}
    
    async def submit(
        self,
        proposal: StrategyProposal,
        simulation_results: Dict[str, SimulationResult],
        debate_feedback: Optional[List[DebateFeedback]] = None,
    ) -> GovernanceDecision:
        """
        Submit a proposal to governance for approval.
        
        Args:
            proposal: The strategy proposal
            simulation_results: Results from simulation
            debate_feedback: Optional debate feedback
            
        Returns:
            Governance decision
        """
        logger.info(f"Submitting proposal {proposal.id} to governance")
        
        # Determine required approval level
        approval_level = self._get_approval_level(proposal.risk_level)
        
        # Evaluate proposal based on simulations and debate
        decision = await self._evaluate(
            proposal=proposal,
            simulation_results=simulation_results,
            debate_feedback=debate_feedback,
            approval_level=approval_level,
        )
        
        # Store decision
        self.decision_history[decision.decision_id] = decision
        
        logger.info(
            f"Governance decision for proposal {proposal.id}: "
            f"{decision.decision} (approved by: {decision.approver_level})"
        )
        
        return decision
    
    def _get_approval_level(self, risk_level: RiskLevel) -> ApprovalLevel:
        """Get the required approval level for a risk level."""
        return self.RISK_APPROVAL_MAP.get(risk_level, ApprovalLevel.EXECUTIVE)
    
    async def _evaluate(
        self,
        proposal: StrategyProposal,
        simulation_results: Dict[str, SimulationResult],
        debate_feedback: Optional[List[DebateFeedback]],
        approval_level: ApprovalLevel,
    ) -> GovernanceDecision:
        """
        Evaluate a proposal and make a decision.
        
        Args:
            proposal: The strategy proposal
            simulation_results: Simulation results
            debate_feedback: Debate feedback
            approval_level: Required approval level
            
        Returns:
            Governance decision
        """
        # Aggregate simulation metrics
        from app.strategy_pipeline.simulation_router import get_simulation_router
        router = get_simulation_router()
        aggregated = router.get_aggregated_metrics(simulation_results)
        
        # Evaluate based on criteria
        should_approve = True
        rationale_parts = []
        conditions = []
        
        # Check risk level
        if proposal.risk_level == RiskLevel.CRITICAL:
            should_approve = False
            rationale_parts.append("Critical risk level requires CEO approval")
        elif proposal.risk_level == RiskLevel.HIGH:
            if aggregated.get("max_drawdown", 0) > 0.15:
                should_approve = False
                rationale_parts.append("High drawdown risk exceeds acceptable threshold")
        
        # Check confidence score
        if proposal.confidence_score < 0.5:
            should_approve = False
            rationale_parts.append("Confidence score below threshold")
            conditions.append("Improve confidence through additional analysis")
        
        # Check simulation results
        if aggregated.get("expected_return") is not None:
            if aggregated["expected_return"] < 0:
                should_approve = False
                rationale_parts.append("Negative expected return from simulations")
        
        # Check debate outcomes
        if debate_feedback:
            rejections = sum(
                1 for f in debate_feedback
                if f.recommendation.value == "reject"
            )
            if rejections > len(debate_feedback) / 2:
                should_approve = False
                rationale_parts.append("Majority of debate participants rejected the proposal")
        
        # Auto-approve LOW risk
        if proposal.risk_level == RiskLevel.LOW:
            should_approve = True
            rationale_parts.append("Low risk - automatic approval")
        
        # Build decision
        decision = GovernanceDecision(
            decision_id=str(uuid.uuid4()),
            proposal_id=proposal.id,
            approver_level=approval_level.value,
            decision="APPROVED" if should_approve else "REJECTED",
            rationale="; ".join(rationale_parts) if rationale_parts else "Proposal meets all governance criteria",
            conditions=conditions,
            risk_level=proposal.risk_level,
            simulation_summary=aggregated,
            debate_summary=[
                {
                    "agent_id": f.agent_id,
                    "agent_name": f.agent_name,
                    "recommendation": f.recommendation.value if hasattr(f.recommendation, 'value') else str(f.recommendation),
                    "confidence": f.confidence_score,
                }
                for f in (debate_feedback or [])
            ],
            decided_at=datetime.utcnow(),
            decided_by=approval_level.value,
        )
        
        return decision
    
    async def evaluate_automatic(
        self,
        proposal: StrategyProposal,
    ) -> GovernanceDecision:
        """
        Perform automatic evaluation for LOW risk proposals.
        
        Args:
            proposal: The strategy proposal
            
        Returns:
            Governance decision
        """
        logger.info(f"Auto-evaluating proposal: {proposal.id}")
        
        decision = GovernanceDecision(
            decision_id=str(uuid.uuid4()),
            proposal_id=proposal.id,
            approver_level=ApprovalLevel.AUTOMATIC.value,
            decision="APPROVED",
            rationale="Automatic approval - Low risk proposal meets all criteria",
            conditions=[],
            risk_level=proposal.risk_level,
            simulation_summary={},
            debate_summary=[],
            decided_at=datetime.utcnow(),
            decided_by="SYSTEM",
        )
        
        self.decision_history[decision.decision_id] = decision
        return decision
    
    def get_decision(self, decision_id: str) -> Optional[GovernanceDecision]:
        """Get a governance decision by ID."""
        return self.decision_history.get(decision_id)
    
    def get_decisions_by_proposal(
        self,
        proposal_id: str,
    ) -> List[GovernanceDecision]:
        """Get all decisions for a proposal."""
        return [
            d for d in self.decision_history.values()
            if d.proposal_id == proposal_id
        ]
    
    def get_pending_decisions(
        self,
        approval_level: Optional[ApprovalLevel] = None,
    ) -> List[GovernanceDecision]:
        """Get pending decisions (for manual review)."""
        # In a full implementation, this would query a database
        return []


# Singleton instance
_governance_router: Optional[GovernanceRouter] = None


def get_governance_router() -> GovernanceRouter:
    """Get the global governance router instance."""
    global _governance_router
    if _governance_router is None:
        _governance_router = GovernanceRouter()
    return _governance_router
