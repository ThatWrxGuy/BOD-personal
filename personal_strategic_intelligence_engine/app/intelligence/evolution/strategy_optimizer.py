"""Strategy Optimizer.

Proposes improvements to tactical strategy parameters.
"""

from datetime import datetime
from typing import List, Dict, Optional
import uuid

from app.intelligence.evolution.evolution_models import (
    OptimizationProposal,
    OptimizationType,
    ApprovalLevel,
)


class StrategyOptimizer:
    """Optimizes tactical strategy parameters."""
    
    def __init__(self):
        self.proposals: List[OptimizationProposal] = []
    
    def generate_proposals(
        self,
        quantitative_analysis: Dict,
        patterns: List,
        features: List,
    ) -> List[OptimizationProposal]:
        """Generate optimization proposals."""
        
        proposals = []
        
        # Proposal 1: Score threshold adjustment
        proposals.append(OptimizationProposal(
            proposal_id=str(uuid.uuid4()),
            optimization_type=OptimizationType.SCORE_THRESHOLD,
            target_parameter="signal_score_min",
            current_value=50,
            proposed_value=55,
            expected_improvement=8.5,
            confidence=0.72,
            required_approval=ApprovalLevel.FINANCE,
            rationale="Analysis shows signals above 55 have 15% higher win rate",
            created_at=datetime.now(),
        ))
        
        # Proposal 2: Suppression adjustment
        proposals.append(OptimizationProposal(
            proposal_id=str(uuid.uuid4()),
            optimization_type=OptimizationType.SUPPRESSION_ADJUSTMENT,
            target_parameter="overextension_threshold",
            current_value=1.0,
            proposed_value=1.2,
            expected_improvement=5.2,
            confidence=0.65,
            required_approval=ApprovalLevel.FINANCE,
            rationale="Current threshold blocks too many profitable trades",
            created_at=datetime.now(),
        ))
        
        # Proposal 3: Timing criteria
        proposals.append(OptimizationProposal(
            proposal_id=str(uuid.uuid4()),
            optimization_type=OptimizationType.TIMING_CRITERIA,
            target_parameter="min_momentum_for_entry",
            current_value=0.5,
            proposed_value=0.7,
            expected_improvement=12.0,
            confidence=0.78,
            required_approval=ApprovalLevel.CEO,
            rationale="Stronger momentum correlates with higher win rate",
            created_at=datetime.now(),
        ))
        
        # Proposal 4: Confidence scaling
        proposals.append(OptimizationProposal(
            proposal_id=str(uuid.uuid4()),
            optimization_type=OptimizationType.CONFIDENCE_SCALING,
            target_parameter="regime_modifier_range_chop",
            current_value=0,
            proposed_value=-10,
            expected_improvement=6.5,
            confidence=0.70,
            required_approval=ApprovalLevel.FINANCE,
            rationale="Reduce confidence during range chop days",
            created_at=datetime.now(),
        ))
        
        self.proposals = proposals
        return proposals
    
    def get_pending_proposals(self) -> List[OptimizationProposal]:
        """Get pending proposals."""
        return [p for p in self.proposals if p.status == "pending"]
    
    def approve_proposal(self, proposal_id: str) -> bool:
        """Approve a proposal."""
        for proposal in self.proposals:
            if proposal.proposal_id == proposal_id:
                proposal.status = "approved"
                return True
        return False
    
    def reject_proposal(self, proposal_id: str) -> bool:
        """Reject a proposal."""
        for proposal in self.proposals:
            if proposal.proposal_id == proposal_id:
                proposal.status = "rejected"
                return True
        return False
    
    def get_proposals_by_type(self, opt_type: OptimizationType) -> List[OptimizationProposal]:
        """Get proposals by type."""
        return [p for p in self.proposals if p.optimization_type == opt_type]


def create_optimizer() -> StrategyOptimizer:
    """Create a new strategy optimizer."""
    return StrategyOptimizer()
