"""CSO Agent - Chief Strategy Officer."""
from typing import Dict, Any, List
import uuid

from app.agents.executive.base_agent import BaseExecutiveAgent
from app.agents.executive.agent_types import ExecutiveRole, ProposalPriority
from app.agents.executive.agent_models import AgentProposal


class CSOAgent(BaseExecutiveAgent):
    """CSO Agent - long-term strategic planning and opportunity identification.
    
    Responsibilities:
    - Long-term strategic planning
    - Opportunity identification
    - Scenario alignment
    """
    
    def __init__(self):
        super().__init__(ExecutiveRole.CSO)
        self.name = "Chief Strategy Officer"
        self.description = "Develops long-term strategic vision"
    
    def analyze_state(self, state_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze system state from CSO perspective."""
        strategic = state_snapshot.get("strategic_state", {})
        
        analysis = {
            "role": self.role.value,
            "active_strategies": strategic.get("active_strategies", []),
            "confidence": strategic.get("confidence_score", 0.5),
            "strategic_priority": strategic.get("strategic_priority", "maintain"),
            "focus_areas": [],
        }
        
        return analysis
    
    def generate_proposal(self, analysis: Dict[str, Any]) -> AgentProposal:
        """Generate strategic-focused proposal."""
        summary = "Pursue strategic initiatives aligned with long-term growth objectives"
        
        proposal = AgentProposal(
            proposal_id=self.generate_proposal_id(),
            origin_agent=self.role,
            strategy_summary=summary,
            supporting_evidence=[
                {"type": "strategic_analysis", "data": analysis}
            ],
            confidence_score=0.65,
            priority=ProposalPriority.HIGH,
            alignment_score=0.8,
        )
        
        return proposal
    
    def evaluate_proposal(self, proposal: AgentProposal) -> Dict[str, Any]:
        """Evaluate proposal from CSO perspective."""
        evaluation = {
            "strengths": [],
            "weaknesses": [],
            "recommendation": "neutral",
        }
        
        if proposal.alignment_score and proposal.alignment_score >= 0.7:
            evaluation["strengths"].append("Strong strategic alignment")
        
        return evaluation
    
    def submit_argument(
        self,
        target_proposal: str,
        position: str,
        argument_summary: str,
        evidence: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Submit strategic argument in debate."""
        return {
            "argument_id": f"arg_{uuid.uuid4().hex[:8]}",
            "agent": self.role.value,
            "proposal": target_proposal,
            "position": position,
            "summary": f"[STRATEGIC] {argument_summary}",
            "evidence": evidence,
        }
