"""Proposal Registry - manages the lifecycle of strategy proposals."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from app.strategy_pipeline.proposal_models import (
    ProposalStatus,
    StrategyProposal,
    ProposalSummary,
)


class ProposalRegistry:
    """
    The Proposal Registry manages the lifecycle of strategy proposals.
    
    Responsibilities:
    - Registering new proposals
    - Maintaining proposal status
    - Retrieving active proposals
    - Storing historical proposals
    """
    
    def __init__(self):
        self.proposals: Dict[str, StrategyProposal] = {}
    
    def register(self, proposal: StrategyProposal) -> StrategyProposal:
        """Register a new proposal."""
        proposal.id = str(uuid.uuid4())
        proposal.created_at = datetime.utcnow()
        proposal.status = ProposalStatus.DRAFT
        self.proposals[proposal.id] = proposal
        return proposal
    
    def get(self, proposal_id: str) -> Optional[StrategyProposal]:
        """Retrieve a proposal by ID."""
        return self.proposals.get(proposal_id)
    
    def update(self, proposal: StrategyProposal) -> StrategyProposal:
        """Update an existing proposal."""
        proposal.updated_at = datetime.utcnow()
        self.proposals[proposal.id] = proposal
        return proposal
    
    def submit(self, proposal_id: str) -> Optional[StrategyProposal]:
        """Submit a proposal for processing."""
        proposal = self.proposals.get(proposal_id)
        if proposal:
            proposal.status = ProposalStatus.SUBMITTED
            proposal.submitted_at = datetime.utcnow()
            proposal.updated_at = datetime.utcnow()
        return proposal
    
    def get_by_status(self, status: ProposalStatus) -> List[StrategyProposal]:
        """Get all proposals with a specific status."""
        return [
            p for p in self.proposals.values()
            if p.status == status
        ]
    
    def get_active(self) -> List[StrategyProposal]:
        """Get all active proposals (not completed, rejected, or expired)."""
        active_statuses = [
            ProposalStatus.DRAFT,
            ProposalStatus.SUBMITTED,
            ProposalStatus.IN_DEBATE,
            ProposalStatus.SIMULATING,
            ProposalStatus.PENDING_APPROVAL,
        ]
        return [
            p for p in self.proposals.values()
            if p.status in active_statuses
        ]
    
    def get_by_agent(self, agent_id: str) -> List[StrategyProposal]:
        """Get all proposals created by a specific agent."""
        return [
            p for p in self.proposals.values()
            if p.agent_id == agent_id
        ]
    
    def get_history(self, limit: int = 100) -> List[ProposalSummary]:
        """Get historical proposals as summaries."""
        proposals = sorted(
            self.proposals.values(),
            key=lambda p: p.created_at,
            reverse=True
        )[:limit]
        
        return [
            ProposalSummary(
                id=p.id,
                title=p.title,
                description=p.description,
                agent_id=p.agent_id,
                category=p.category,
                risk_level=p.risk_level,
                confidence_score=p.confidence_score,
                status=p.status,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in proposals
        ]
    
    def list_all(self) -> List[ProposalSummary]:
        """List all proposals as summaries."""
        return [
            ProposalSummary(
                id=p.id,
                title=p.title,
                description=p.description,
                agent_id=p.agent_id,
                category=p.category,
                risk_level=p.risk_level,
                confidence_score=p.confidence_score,
                status=p.status,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in self.proposals.values()
        ]
    
    def update_status(self, proposal_id: str, status: ProposalStatus) -> Optional[StrategyProposal]:
        """Update the status of a proposal."""
        proposal = self.proposals.get(proposal_id)
        if proposal:
            proposal.status = status
            proposal.updated_at = datetime.utcnow()
            if status == ProposalStatus.APPROVED or status == ProposalStatus.REJECTED:
                proposal.decided_at = datetime.utcnow()
        return proposal
    
    def delete(self, proposal_id: str) -> bool:
        """Delete a proposal."""
        if proposal_id in self.proposals:
            del self.proposals[proposal_id]
            return True
        return False


# Singleton instance for global access
_registry: Optional[ProposalRegistry] = None


def get_registry() -> ProposalRegistry:
    """Get the global proposal registry instance."""
    global _registry
    if _registry is None:
        _registry = ProposalRegistry()
    return _registry


def reset_registry() -> None:
    """Reset the registry (for testing)."""
    global _registry
    _registry = None
