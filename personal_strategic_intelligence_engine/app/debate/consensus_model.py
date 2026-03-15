"""Consensus Model for calculating debate consensus scores."""
from typing import Optional
from app.models.debate import DebateSession, DebateVote, AgentWeights
from app.core.logging import get_logger

logger = get_logger(__name__)


class ConsensusModel:
    """Calculates consensus scores from debate votes."""
    
    # Consensus thresholds
    STRONG_APPROVAL = 0.75
    MODERATE_AGREEMENT = 0.50
    
    def __init__(self):
        self.agent_weights = {
            "strategy": AgentWeights.STRATEGY,
            "finance": AgentWeights.FINANCE,
            "risk": AgentWeights.RISK,
            "health": AgentWeights.HEALTH,
            "operations": AgentWeights.OPERATIONS,
            "legacy": AgentWeights.LEGACY,
        }
    
    def calculate_consensus(
        self,
        votes: list,
        confidence_scores: list,
    ) -> tuple[float, str]:
        """
        Calculate consensus score from votes.
        
        Returns:
            tuple: (consensus_score, recommendation)
        """
        if not votes:
            return 0.0, "NO_CONSENSUS"
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for vote, confidence in zip(votes, confidence_scores):
            vote_value = self._get_vote_value(vote)
            weight = self._get_agent_weight(vote.get("agent_id", ""))
            
            # Factor in confidence
            effective_weight = weight * confidence
            weighted_sum += vote_value * effective_weight
            total_weight += effective_weight
        
        if total_weight == 0:
            return 0.0, "NO_CONSENSUS"
        
        consensus_score = weighted_sum / total_weight
        
        # Determine recommendation based on score
        if consensus_score >= self.STRONG_APPROVAL:
            recommendation = "APPROVE"
        elif consensus_score >= self.MODERATE_AGREEMENT:
            recommendation = "REVIEW"
        else:
            recommendation = "REJECT"
        
        return consensus_score, recommendation
    
    def _get_vote_value(self, vote: str) -> float:
        """Convert vote to numeric value."""
        vote = vote.upper()
        if vote == "APPROVE":
            return 1.0
        elif vote == "ABSTAIN":
            return 0.0
        elif vote == "REJECT":
            return -0.5
        return 0.0
    
    def _get_agent_weight(self, agent_id: str) -> float:
        """Get weight for an agent."""
        agent_key = agent_id.lower().replace("_agent", "")
        return self.agent_weights.get(agent_key, 1.0)
    
    def calculate_with_risk(
        self,
        consensus_score: float,
        risk_score: float,
    ) -> tuple[float, str]:
        """
        Adjust consensus score based on risk.
        
        High-risk decisions need stronger consensus.
        """
        # If risk is high, require higher consensus
        adjusted_score = consensus_score
        
        if risk_score > 0.7:
            adjusted_score *= 0.8  # Reduce effective consensus for high risk
        elif risk_score > 0.5:
            adjusted_score *= 0.9  # Slight reduction for moderate risk
        
        if adjusted_score >= self.STRONG_APPROVAL:
            return adjusted_score, "APPROVE"
        elif adjusted_score >= self.MODERATE_AGREEMENT:
            return adjusted_score, "REVIEW"
        else:
            return adjusted_score, "REJECT"
    
    def get_consensus_details(
        self,
        votes: list,
        consensus_score: float,
    ) -> dict:
        """Get detailed breakdown of consensus."""
        vote_counts = {
            "APPROVE": 0,
            "REJECT": 0,
            "ABSTAIN": 0,
        }
        
        for vote in votes:
            vote_type = vote.get("vote", "ABSTAIN").upper()
            if vote_type in vote_counts:
                vote_counts[vote_type] += 1
        
        return {
            "consensus_score": consensus_score,
            "vote_counts": vote_counts,
            "total_votes": len(votes),
            "approval_rate": vote_counts["APPROVE"] / len(votes) if votes else 0,
            "rejection_rate": vote_counts["REJECT"] / len(votes) if votes else 0,
        }


def get_consensus_model() -> ConsensusModel:
    """Get consensus model instance."""
    return ConsensusModel()
