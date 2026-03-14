"""CEO Agent - Chief Executive Officer."""
from typing import Dict, Any, List, Optional
import uuid

from app.agents.executive.base_agent import BaseExecutiveAgent
from app.agents.executive.agent_types import ExecutiveRole, ProposalPriority
from app.agents.executive.agent_models import AgentProposal


class CEOAgent(BaseExecutiveAgent):
    """CEO Agent - orchestrates council cycles and selects final strategy.
    
    Responsibilities:
    - Coordinate council cycles
    - Aggregate proposals
    - Initiate debates
    - Select final strategic direction
    """
    
    def __init__(self):
        super().__init__(ExecutiveRole.CEO)
        self.name = "Chief Executive Officer"
        self.description = "Orchestrates strategic decision-making"
    
    def analyze_state(self, state_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze system state from CEO perspective."""
        analysis = {
            "role": self.role.value,
            "focus_areas": [],
            "key_concerns": [],
        }
        
        # Extract key metrics from state
        operational = state_snapshot.get("operational_state", {})
        strategic = state_snapshot.get("strategic_state", {})
        risk = state_snapshot.get("risk_state", {})
        
        # Assess overall system health
        active_tasks = len(operational.get("current_tasks", []))
        active_goals = len(state_snapshot.get("goal_state", {}).get("active_goals", []))
        risk_count = len(risk.get("identified_risks", []))
        
        analysis["system_health"] = {
            "active_tasks": active_tasks,
            "active_goals": active_goals,
            "risk_count": risk_count,
            "confidence": strategic.get("confidence_score", 0.5),
        }
        
        # Identify focus areas
        if active_tasks > 5:
            analysis["focus_areas"].append("task_overload")
        if risk_count > 3:
            analysis["focus_areas"].append("risk_management")
        if strategic.get("confidence_score", 0.5) < 0.6:
            analysis["focus_areas"].append("confidence_building")
        
        return analysis
    
    def generate_proposal(self, analysis: Dict[str, Any]) -> AgentProposal:
        """Generate strategic proposal based on analysis."""
        summary = f"Strategic initiative: Maintain operational excellence while managing {analysis.get('system_health', {}).get('risk_count', 0)} identified risks"
        
        proposal = AgentProposal(
            proposal_id=self.generate_proposal_id(),
            origin_agent=self.role,
            strategy_summary=summary,
            supporting_evidence=[
                {"type": "system_health", "data": analysis.get("system_health", {})}
            ],
            confidence_score=0.7,
            priority=ProposalPriority.MEDIUM,
        )
        
        return proposal
    
    def evaluate_proposal(self, proposal: AgentProposal) -> Dict[str, Any]:
        """Evaluate a proposal from CEO perspective."""
        evaluation = {
            "strengths": [],
            "weaknesses": [],
            "recommendation": "neutral",
        }
        
        # Evaluate based on overall system impact
        if proposal.confidence_score >= 0.7:
            evaluation["strengths"].append("High confidence in proposal")
        
        if proposal.priority == ProposalPriority.CRITICAL:
            evaluation["strengths"].append("Addresses critical priorities")
        
        return evaluation
    
    def submit_argument(
        self,
        target_proposal: str,
        position: str,
        argument_summary: str,
        evidence: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Submit argument in debate."""
        return {
            "argument_id": f"arg_{uuid.uuid4().hex[:8]}",
            "agent": self.role.value,
            "proposal": target_proposal,
            "position": position,
            "summary": argument_summary,
            "evidence": evidence,
        }
    
    def coordinate_council_cycle(
        self,
        all_proposals: List[AgentProposal],
    ) -> Dict[str, Any]:
        """Coordinate the council cycle and select final strategy."""
        # Sort by priority and confidence
        ranked = sorted(
            all_proposals,
            key=lambda p: (p.priority.value, p.confidence_score),
            reverse=True,
        )
        
        return {
            "coordinated_by": self.role.value,
            "proposals_received": len(all_proposals),
            "top_proposal": ranked[0].proposal_id if ranked else None,
            "recommendation": "proceed_with_top" if ranked else "no_valid_proposals",
        }
    
    def select_final_strategy(
        self,
        debate_summaries: List[Dict[str, Any]],
        proposals: List[AgentProposal],
    ) -> AgentProposal:
        """Select final strategy based on debate outcomes."""
        if not proposals:
            # Return default proposal
            return self.generate_proposal({"system_health": {}})
        
        # Select highest-ranked proposal that passed debate
        for proposal in sorted(proposals, key=lambda p: p.confidence_score, reverse=True):
            # Check if proposal was accepted in debate
            status_value = proposal.status.value if hasattr(proposal.status, 'value') else proposal.status
            if status_value == "accepted":
                return proposal
        
        # Fallback to highest confidence proposal
        return max(proposals, key=lambda p: p.confidence_score)
