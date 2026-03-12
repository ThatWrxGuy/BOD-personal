"""Base agent interface for executive agents."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import uuid

from app.executive_agents.agent_types import ExecutiveRole, ProposalPriority
from app.executive_agents.agent_models import AgentProposal
from app.state_engine import StateEngine, get_state_engine
from app.meta_cognition import get_meta_engine


class BaseExecutiveAgent(ABC):
    """Base class for all executive agents.
    
    All agents rely on:
    - State Engine for system state
    - Meta-Cognitive Engine for validation
    - Strategic Doctrine for learned lessons
    
    Agents should not maintain independent state copies.
    """
    
    def __init__(self, role: ExecutiveRole):
        self.role = role
        self.state_engine = get_state_engine()
        self.meta_engine = get_meta_engine()
    
    @abstractmethod
    def analyze_state(self, state_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current system state.
        
        Args:
            state_snapshot: Current system state snapshot
            
        Returns:
            Analysis results from agent's perspective
        """
        pass
    
    @abstractmethod
    def generate_proposal(self, analysis: Dict[str, Any]) -> AgentProposal:
        """Generate a strategic proposal based on analysis.
        
        Args:
            analysis: Results from analyze_state
            
        Returns:
            Strategic proposal
        """
        pass
    
    @abstractmethod
    def evaluate_proposal(self, proposal: AgentProposal) -> Dict[str, Any]:
        """Evaluate another agent's proposal.
        
        Args:
            proposal: Proposal to evaluate
            
        Returns:
            Evaluation results with strengths and weaknesses
        """
        pass
    
    @abstractmethod
    def submit_argument(
        self,
        target_proposal: str,
        position: str,
        argument_summary: str,
        evidence: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Submit an argument in a debate.
        
        Args:
            target_proposal: ID of proposal being debated
            position: SUPPORT, OPPOSE, or NEUTRAL
            argument_summary: Summary of argument
            evidence: Supporting evidence
            
        Returns:
            Argument details
        """
        pass
    
    def get_system_state(self) -> Dict[str, Any]:
        """Get current system state from state engine."""
        state = self.state_engine.get_current_state()
        return state.to_dict()
    
    def validate_through_meta_cognition(
        self,
        proposal: AgentProposal,
    ) -> Dict[str, Any]:
        """Validate proposal through meta-cognition layer.
        
        Args:
            proposal: Proposal to validate
            
        Returns:
            Validation results
        """
        from app.meta_cognition import OriginEngine
        
        # Convert role to origin engine
        engine_map = {
            ExecutiveRole.CEO: OriginEngine.STRATEGY_LOOP,
            ExecutiveRole.CFO: OriginEngine.STRATEGY_LOOP,
            ExecutiveRole.COO: OriginEngine.STRATEGY_LOOP,
            ExecutiveRole.CSO: OriginEngine.STRATEGY_LOOP,
            ExecutiveRole.CRO: OriginEngine.STRATEGY_LOOP,
            ExecutiveRole.CKO: OriginEngine.STRATEGY_LOOP,
            ExecutiveRole.CPO: OriginEngine.STRATEGY_LOOP,
        }
        
        origin = engine_map.get(self.role, OriginEngine.STRATEGY_LOOP)
        
        decision = self.meta_engine.create_decision(
            origin_engine=origin,
            recommendation_type=proposal.strategy_summary[:50],
            recommendation_summary=proposal.strategy_summary,
            supporting_signals=proposal.supporting_evidence,
            context={
                "financial_impact": proposal.financial_impact,
                "risk_assessment": proposal.risk_assessment,
            },
        )
        
        result = self.meta_engine.evaluate_decision(decision)
        
        return {
            "is_valid": result.is_approved(),
            "confidence_score": result.confidence_score,
            "validation_status": result.validation_status.value,
            "contradictions": len(result.contradictions),
            "policy_compliance": result.policy_compliance.value,
        }
    
    def get_doctrine_alignment(self, strategy: str) -> float:
        """Get alignment score with strategic doctrine.
        
        Args:
            strategy: Strategy to check
            
        Returns:
            Alignment score (0-1)
        """
        try:
            from app.state_engine import get_state_engine, MemoryTier
            
            engine = get_state_engine()
            # Would retrieve doctrine memories
            return 0.5  # Default
        except:
            return 0.5
    
    def generate_proposal_id(self) -> str:
        """Generate a unique proposal ID."""
        return f"prop_{self.role.value}_{uuid.uuid4().hex[:8]}"
