"""COO Agent - Chief Operating Officer."""
from typing import Dict, Any, List
import uuid

from app.executive_agents.base_agent import BaseExecutiveAgent
from app.executive_agents.agent_types import ExecutiveRole, ProposalPriority
from app.executive_agents.agent_models import AgentProposal


class COOAgent(BaseExecutiveAgent):
    """COO Agent - evaluates operational feasibility and execution.
    
    Responsibilities:
    - Evaluate operational feasibility
    - Assess resource constraints
    - Design execution workflows
    """
    
    def __init__(self):
        super().__init__(ExecutiveRole.COO)
        self.name = "Chief Operating Officer"
        self.description = "Evaluates operational feasibility"
    
    def analyze_state(self, state_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze system state from COO perspective."""
        operational = state_snapshot.get("operational_state", {})
        
        analysis = {
            "role": self.role.value,
            "current_tasks": len(operational.get("current_tasks", [])),
            "active_priorities": operational.get("active_priorities", []),
            "execution_capacity": 1.0 - (len(operational.get("current_tasks", [])) * 0.1),
            "focus_areas": [],
        }
        
        # Assess operational load
        if analysis["current_tasks"] > 10:
            analysis["focus_areas"].append("capacity_constraints")
        
        return analysis
    
    def generate_proposal(self, analysis: Dict[str, Any]) -> AgentProposal:
        """Generate operational-focused proposal."""
        summary = "Streamline execution workflow to improve operational efficiency"
        
        proposal = AgentProposal(
            proposal_id=self.generate_proposal_id(),
            origin_agent=self.role,
            strategy_summary=summary,
            supporting_evidence=[
                {"type": "operational_analysis", "data": analysis}
            ],
            confidence_score=0.8,
            priority=ProposalPriority.MEDIUM,
            operational_feasibility=analysis.get("execution_capacity", 0.8),
        )
        
        return proposal
    
    def evaluate_proposal(self, proposal: AgentProposal) -> Dict[str, Any]:
        """Evaluate proposal from COO perspective."""
        evaluation = {
            "strengths": [],
            "weaknesses": [],
            "recommendation": "neutral",
        }
        
        # Check feasibility
        if proposal.operational_feasibility and proposal.operational_feasibility >= 0.7:
            evaluation["strengths"].append("High operational feasibility")
        
        return evaluation
    
    def submit_argument(
        self,
        target_proposal: str,
        position: str,
        argument_summary: str,
        evidence: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Submit operational argument in debate."""
        return {
            "argument_id": f"arg_{uuid.uuid4().hex[:8]}",
            "agent": self.role.value,
            "proposal": target_proposal,
            "position": position,
            "summary": f"[OPERATIONAL] {argument_summary}",
            "evidence": evidence,
        }
