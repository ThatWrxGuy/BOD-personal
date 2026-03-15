"""Decision Logger - maintains permanent audit log of all strategy decisions."""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.strategy_pipeline.proposal_models import (
    DebateFeedback,
    GovernanceDecision,
    ProposalStatus,
    SimulationResult,
    StrategyProposal,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class DecisionRecord:
    """
    A permanent record of a strategy decision.
    
    Logged data includes:
    - proposal details
    - debate feedback
    - simulation metrics
    - governance decision
    - timestamps
    """
    
    def __init__(
        self,
        decision_id: str,
        proposal_id: str,
        agent: str,
        risk_level: str,
        proposal_title: str,
        proposal_description: str,
        proposal_category: str,
        proposed_action: Dict[str, Any],
        expected_outcome: Dict[str, Any],
        confidence_score: float,
        status: str,
        simulation_results: Optional[Dict[str, Any]] = None,
        debate_feedback: Optional[List[Dict[str, Any]]] = None,
        governance_decision: Optional[str] = None,
        governance_rationale: Optional[str] = None,
        approval_status: str = "PENDING",
        timestamp: Optional[datetime] = None,
    ):
        self.decision_id = decision_id
        self.proposal_id = proposal_id
        self.agent = agent
        self.risk_level = risk_level
        self.proposal_title = proposal_title
        self.proposal_description = proposal_description
        self.proposal_category = proposal_category
        self.proposed_action = proposed_action
        self.expected_outcome = expected_outcome
        self.confidence_score = confidence_score
        self.status = status
        self.simulation_results = simulation_results or {}
        self.debate_feedback = debate_feedback or []
        self.governance_decision = governance_decision
        self.governance_rationale = governance_rationale
        self.approval_status = approval_status
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "decision_id": self.decision_id,
            "proposal_id": self.proposal_id,
            "agent": self.agent,
            "risk_level": self.risk_level,
            "proposal_title": self.proposal_title,
            "proposal_description": self.proposal_description,
            "proposal_category": self.proposal_category,
            "proposed_action": self.proposed_action,
            "expected_outcome": self.expected_outcome,
            "confidence_score": self.confidence_score,
            "status": self.status,
            "simulation_results": self.simulation_results,
            "debate_feedback": self.debate_feedback,
            "governance_decision": self.governance_decision,
            "governance_rationale": self.governance_rationale,
            "approval_status": self.approval_status,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class DecisionJournal:
    """
    The Decision Journal stores a permanent record of all strategy decisions.
    
    This provides:
    - Audit trail for all decisions
    - Historical lookup by various criteria
    - Compliance and governance tracking
    - Decision analytics
    """
    
    def __init__(self):
        self.decisions: Dict[str, DecisionRecord] = {}
    
    def log_decision(
        self,
        proposal: StrategyProposal,
        simulation_results: Optional[Dict[str, SimulationResult]] = None,
        debate_feedback: Optional[List[DebateFeedback]] = None,
        governance_decision: Optional[GovernanceDecision] = None,
    ) -> DecisionRecord:
        """
        Log a decision to the journal.
        
        Args:
            proposal: The strategy proposal
            simulation_results: Optional simulation results
            debate_feedback: Optional debate feedback
            governance_decision: Optional governance decision
            
        Returns:
            The created decision record
        """
        decision_id = str(uuid.uuid4())
        
        # Convert simulation results to dict
        sim_results_dict = {}
        if simulation_results:
            sim_results_dict = {
                k: {
                    "expected_return": v.expected_return,
                    "max_drawdown": v.max_drawdown,
                    "win_probability": v.win_probability,
                    "risk_metrics": v.risk_metrics,
                    "simulation_type": v.simulation_type,
                }
                for k, v in simulation_results.items()
            }
        
        # Convert debate feedback to dict
        feedback_list = []
        if debate_feedback:
            feedback_list = [
                {
                    "agent_id": f.agent_id,
                    "agent_name": f.agent_name,
                    "role": f.role,
                    "position": f.position,
                    "argument_text": f.argument_text,
                    "recommendation": f.recommendation.value if hasattr(f.recommendation, 'value') else str(f.recommendation),
                    "confidence_score": f.confidence_score,
                }
                for f in debate_feedback
            ]
        
        # Determine approval status
        approval_status = "PENDING"
        if governance_decision:
            approval_status = governance_decision.decision
        
        record = DecisionRecord(
            decision_id=decision_id,
            proposal_id=proposal.id,
            agent=proposal.agent_id,
            risk_level=proposal.risk_level,
            proposal_title=proposal.title,
            proposal_description=proposal.description,
            proposal_category=proposal.category,
            proposed_action=proposal.proposed_action,
            expected_outcome=proposal.expected_outcome,
            confidence_score=proposal.confidence_score,
            status=proposal.status,
            simulation_results=sim_results_dict,
            debate_feedback=feedback_list,
            governance_decision=governance_decision.decision if governance_decision else None,
            governance_rationale=governance_decision.rationale if governance_decision else None,
            approval_status=approval_status,
        )
        
        self.decisions[decision_id] = record
        
        logger.info(f"Logged decision {decision_id} for proposal {proposal.id}")
        
        return record
    
    def get_decision(self, decision_id: str) -> Optional[DecisionRecord]:
        """Get a decision by ID."""
        return self.decisions.get(decision_id)
    
    def get_by_proposal(self, proposal_id: str) -> Optional[DecisionRecord]:
        """Get a decision by proposal ID."""
        for decision in self.decisions.values():
            if decision.proposal_id == proposal_id:
                return decision
        return None
    
    def get_by_agent(self, agent_id: str) -> List[DecisionRecord]:
        """Get all decisions for a specific agent."""
        return [
            d for d in self.decisions.values()
            if d.agent == agent_id
        ]
    
    def get_by_status(self, status: str) -> List[DecisionRecord]:
        """Get all decisions with a specific status."""
        return [
            d for d in self.decisions.values()
            if d.status == status
        ]
    
    def get_by_approval_status(self, approval_status: str) -> List[DecisionRecord]:
        """Get all decisions with a specific approval status."""
        return [
            d for d in self.decisions.values()
            if d.approval_status == approval_status
        ]
    
    def get_by_risk_level(self, risk_level: str) -> List[DecisionRecord]:
        """Get all decisions with a specific risk level."""
        return [
            d for d in self.decisions.values()
            if d.risk_level == risk_level
        ]
    
    def get_history(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[DecisionRecord]:
        """Get decision history with pagination."""
        sorted_decisions = sorted(
            self.decisions.values(),
            key=lambda d: d.timestamp,
            reverse=True,
        )
        return sorted_decisions[offset:offset + limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about logged decisions."""
        if not self.decisions:
            return {
                "total_decisions": 0,
                "by_status": {},
                "by_approval_status": {},
                "by_risk_level": {},
                "average_confidence": 0.0,
            }
        
        by_status = {}
        by_approval = {}
        by_risk = {}
        total_confidence = 0.0
        
        for decision in self.decisions.values():
            # Count by status
            by_status[decision.status] = by_status.get(decision.status, 0) + 1
            
            # Count by approval status
            by_approval[decision.approval_status] = by_approval.get(decision.approval_status, 0) + 1
            
            # Count by risk level
            by_risk[decision.risk_level] = by_risk.get(decision.risk_level, 0) + 1
            
            # Sum confidence
            total_confidence += decision.confidence_score
        
        return {
            "total_decisions": len(self.decisions),
            "by_status": by_status,
            "by_approval_status": by_approval,
            "by_risk_level": by_risk,
            "average_confidence": total_confidence / len(self.decisions),
        }
    
    def search(
        self,
        query: str,
        limit: int = 50,
    ) -> List[DecisionRecord]:
        """Search decisions by query string."""
        results = []
        query_lower = query.lower()
        
        for decision in self.decisions.values():
            if (query_lower in decision.proposal_title.lower() or
                query_lower in decision.proposal_description.lower() or
                query_lower in decision.proposal_category.lower()):
                results.append(decision)
        
        return results[:limit]
    
    def clear_history(self) -> int:
        """Clear all decision history (use with caution)."""
        count = len(self.decisions)
        self.decisions.clear()
        logger.warning(f"Cleared {count} decisions from journal")
        return count


# Singleton instance
_journal: Optional[DecisionJournal] = None


def get_decision_journal() -> DecisionJournal:
    """Get the global decision journal instance."""
    global _journal
    if _journal is None:
        _journal = DecisionJournal()
    return _journal


def reset_journal() -> None:
    """Reset the journal (for testing)."""
    global _journal
    _journal = None
