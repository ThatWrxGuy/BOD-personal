"""CFO Agent - Chief Financial Officer."""
from typing import Dict, Any, List
import uuid

from app.agents.executive.base_agent import BaseExecutiveAgent
from app.agents.executive.agent_types import ExecutiveRole, ProposalPriority
from app.agents.executive.agent_models import AgentProposal


class CFOAgent(BaseExecutiveAgent):
    """CFO Agent - evaluates financial impact and capital allocation.
    
    Responsibilities:
    - Evaluate financial impact
    - Assess capital allocation
    - Analyze risk-reward tradeoffs
    """
    
    def __init__(self):
        super().__init__(ExecutiveRole.CFO)
        self.name = "Chief Financial Officer"
        self.description = "Evaluates financial implications of strategies"
    
    def analyze_state(self, state_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze system state from CFO perspective."""
        resource_state = state_snapshot.get("resource_state", {})
        financial = resource_state.get("financial_state", {})
        
        analysis = {
            "role": self.role.value,
            "financial_position": financial,
            "resource_availability": resource_state.get("system_capacity", 1.0),
            "focus_areas": [],
        }
        
        # Assess financial health
        if financial:
            analysis["focus_areas"].append("portfolio_optimization")
        
        # Check resource constraints
        if resource_state.get("system_capacity", 1.0) < 0.5:
            analysis["focus_areas"].append("resource_constraints")
        
        return analysis
    
    def generate_proposal(self, analysis: Dict[str, Any]) -> AgentProposal:
        """Generate financial-focused proposal."""
        summary = "Optimize capital allocation to balance growth and risk management"
        
        proposal = AgentProposal(
            proposal_id=self.generate_proposal_id(),
            origin_agent=self.role,
            strategy_summary=summary,
            supporting_evidence=[
                {"type": "financial_analysis", "data": analysis}
            ],
            confidence_score=0.75,
            priority=ProposalPriority.HIGH,
            financial_impact={
                "expected_return": 0.08,
                "risk_adjusted_value": 0.06,
                "allocation_changes": ["increase_equity", "reduce_debt"],
            },
        )
        
        return proposal
    
    def evaluate_proposal(self, proposal: AgentProposal) -> Dict[str, Any]:
        """Evaluate proposal from CFO perspective."""
        evaluation = {
            "strengths": [],
            "weaknesses": [],
            "recommendation": "neutral",
        }
        
        # Check financial impact
        if proposal.financial_impact:
            expected_return = proposal.financial_impact.get("expected_return", 0)
            if expected_return > 0.05:
                evaluation["strengths"].append("Strong expected returns")
        
        # Check confidence
        if proposal.confidence_score >= 0.7:
            evaluation["strengths"].append("High confidence in projections")
        
        return evaluation
    
    def submit_argument(
        self,
        target_proposal: str,
        position: str,
        argument_summary: str,
        evidence: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Submit financial argument in debate."""
        return {
            "argument_id": f"arg_{uuid.uuid4().hex[:8]}",
            "agent": self.role.value,
            "proposal": target_proposal,
            "position": position,
            "summary": f"[FINANCIAL] {argument_summary}",
            "evidence": evidence,
        }
