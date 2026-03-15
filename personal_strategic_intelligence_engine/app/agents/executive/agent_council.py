"""Agent Council - orchestrates executive agent deliberation."""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.agents.executive.agent_types import ExecutiveRole
from app.agents.executive.agent_models import (
    AgentProposal,
    CouncilDecision,
    CouncilCycle,
)
from app.agents.executive.debate_engine import DebateEngine
from app.agents.executive.base_agent import BaseExecutiveAgent
from app.agents.executive.ceo_agent import CEOAgent
from app.agents.executive.cfo_agent import CFOAgent
from app.agents.executive.coo_agent import COOAgent
from app.agents.executive.cso_agent import CSOAgent
from app.agents.executive.cro_agent import CROAgent
from app.agents.executive.cko_agent import CKOAgent
from app.agents.executive.cpo_agent import CPOAgent


class AgentCouncil:
    """Executive Agent Council - manages council cycles and produces decisions.
    
    Core workflow:
    1. Retrieve system state
    2. Agents analyze state
    3. Proposals generated
    4. Debate engine activated
    5. Meta-cognition validation
    6. CEO selects final decision
    """
    
    def __init__(self):
        self.debate_engine = DebateEngine()
        
        # Initialize all executive agents
        self.ceo = CEOAgent()
        self.agents: Dict[ExecutiveRole, BaseExecutiveAgent] = {
            ExecutiveRole.CEO: self.ceo,
            ExecutiveRole.CFO: CFOAgent(),
            ExecutiveRole.COO: COOAgent(),
            ExecutiveRole.CSO: CSOAgent(),
            ExecutiveRole.CRO: CROAgent(),
            ExecutiveRole.CKO: CKOAgent(),
            ExecutiveRole.CPO: CPOAgent(),
        }
    
    def conduct_council_cycle(self) -> CouncilDecision:
        """Conduct a complete council cycle and produce a decision.
        
        Returns:
            Council decision with selected proposal
        """
        cycle_id = f"cycle_{uuid.uuid4().hex[:8]}"
        
        # Step 1: Retrieve system state
        state_snapshot = self.ceo.get_system_state()
        
        # Step 2: Agents analyze state
        analyses = {}
        for role, agent in self.agents.items():
            analyses[role] = agent.analyze_state(state_snapshot)
        
        # Step 3: Generate proposals
        proposals = []
        for role, agent in self.agents.items():
            if role != ExecutiveRole.CEO:  # CEO generates proposal separately
                proposal = agent.generate_proposal(analyses[role])
                proposals.append(proposal)
        
        # Also add CEO proposal
        ceo_proposal = self.ceo.generate_proposal(analyses[ExecutiveRole.CEO])
        proposals.append(ceo_proposal)
        
        # Step 4: Run debate
        debate_summaries = self.debate_engine.conduct_debate(
            proposals=proposals,
            agents=[{"role": r.value} for r in self.agents.keys()],
        )
        
        # Step 5: Meta-cognition validation
        validated_proposals = []
        for proposal in proposals:
            validation = self.ceo.validate_through_meta_cognition(proposal)
            
            if validation.get("is_valid"):
                validated_proposals.append(proposal)
        
        # Step 6: CEO selects final decision
        final_proposal = self.ceo.select_final_strategy(
            debate_summaries=[s.model_dump() for s in debate_summaries],
            proposals=validated_proposals or proposals,
        )
        
        # Build decision
        decision = CouncilDecision(
            decision_id=f"council_{uuid.uuid4().hex[:12]}",
            selected_proposal=final_proposal,
            selected_proposal_id=final_proposal.proposal_id,
            participating_agents=list(self.agents.keys()),
            confidence_score=final_proposal.confidence_score,
            debate_summary=self._generate_debate_summary(debate_summaries),
            alternatives_considered=[p.proposal_id for p in proposals],
        )
        
        return decision
    
    def _generate_debate_summary(self, debate_summaries) -> str:
        """Generate a summary string from debate results."""
        if not debate_summaries:
            return "No debates conducted"
        
        total_debates = len(debate_summaries)
        consensus_count = sum(1 for s in debate_summaries if s.consensus_reached)
        
        return f"Conducted {total_debates} debates, {consensus_count} reached consensus"
    
    def get_council_status(self) -> Dict[str, Any]:
        """Get current council status."""
        return {
            "agents_active": len(self.agents),
            "agent_roles": [r.value for r in self.agents.keys()],
            "ceo_available": self.ceo is not None,
        }
    
    def get_agent(self, role: ExecutiveRole) -> Optional[BaseExecutiveAgent]:
        """Get a specific agent by role."""
        return self.agents.get(role)


# ============= Singleton Access =============

_council_instance: Optional[AgentCouncil] = None


def get_agent_council() -> AgentCouncil:
    """Get the singleton Agent Council instance."""
    global _council_instance
    if _council_instance is None:
        _council_instance = AgentCouncil()
    return _council_instance


def reset_agent_council():
    """Reset the agent council singleton (for testing)."""
    global _council_instance
    _council_instance = None
