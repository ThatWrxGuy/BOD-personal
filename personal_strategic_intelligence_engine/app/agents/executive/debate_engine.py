"""Debate Engine - facilitates structured debate between executive agents."""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.agents.executive.agent_types import DebatePosition
from app.agents.executive.agent_models import (
    AgentProposal,
    DebateArgument,
    DebateRound,
    DebateSummary,
)


class DebateEngine:
    """Facilitates structured debate between executive agents.
    
    Workflow:
    1. Agents submit proposals
    2. Agents review proposals
    3. Agents submit arguments (support/oppose)
    4. Arguments evaluated
    5. Debate summary generated
    """
    
    def __init__(self):
        self._debates: Dict[str, DebateRound] = {}
    
    def create_debate(self, proposal: AgentProposal) -> DebateRound:
        """Create a new debate for a proposal.
        
        Args:
            proposal: The proposal to debate
            
        Returns:
            Created debate round
        """
        debate_id = f"debate_{uuid.uuid4().hex[:8]}"
        
        debate = DebateRound(
            round_id=debate_id,
            proposal_id=proposal.proposal_id,
            arguments=[],
            started_at=datetime.utcnow(),
        )
        
        self._debates[debate_id] = debate
        return debate
    
    def submit_argument(
        self,
        debate_id: str,
        agent_role: str,
        position: DebatePosition,
        argument_summary: str,
        supporting_evidence: List[Dict[str, Any]],
    ) -> DebateArgument:
        """Submit an argument to a debate.
        
        Args:
            debate_id: ID of the debate
            agent_role: Role of the agent submitting
            position: SUPPORT, OPPOSE, or NEUTRAL
            argument_summary: Summary of the argument
            supporting_evidence: Evidence supporting the argument
            
        Returns:
            Created argument
        """
        if debate_id not in self._debates:
            raise ValueError(f"Debate {debate_id} not found")
        
        argument = DebateArgument(
            argument_id=f"arg_{uuid.uuid4().hex[:8]}",
            agent_role=agent_role,
            target_proposal=self._debates[debate_id].proposal_id,
            position=position,
            argument_summary=argument_summary,
            supporting_evidence=supporting_evidence,
            timestamp=datetime.utcnow(),
        )
        
        self._debates[debate_id].arguments.append(argument)
        return argument
    
    def get_debate(self, debate_id: str) -> Optional[DebateRound]:
        """Get a debate by ID."""
        return self._debates.get(debate_id)
    
    def generate_debate_summary(self, debate_id: str) -> DebateSummary:
        """Generate a summary of the debate.
        
        Args:
            debate_id: ID of the debate
            
        Returns:
            Debate summary
        """
        if debate_id not in self._debates:
            raise ValueError(f"Debate {debate_id} not found")
        
        debate = self._debates[debate_id]
        
        # Separate arguments by position
        arguments_for = [a for a in debate.arguments if a.position == DebatePosition.SUPPORT]
        arguments_against = [a for a in debate.arguments if a.position == DebatePosition.OPPOSE]
        neutral = [a for a in debate.arguments if a.position == DebatePosition.NEUTRAL]
        
        # Determine consensus
        consensus_reached = False
        dominant_position = DebatePosition.NEUTRAL
        
        if arguments_for and arguments_against:
            # Check if one side dominates
            if len(arguments_for) > len(arguments_against) * 1.5:
                consensus_reached = True
                dominant_position = DebatePosition.SUPPORT
            elif len(arguments_against) > len(arguments_for) * 1.5:
                consensus_reached = True
                dominant_position = DebatePosition.OPPOSE
        elif arguments_for and not arguments_against:
            consensus_reached = True
            dominant_position = DebatePosition.SUPPORT
        elif arguments_against and not arguments_for:
            consensus_reached = True
            dominant_position = DebatePosition.OPPOSE
        
        # Calculate strength score
        strength_score = self._calculate_strength(
            arguments_for, arguments_against
        )
        
        # Mark debate as ended
        debate.ended_at = datetime.utcnow()
        
        return DebateSummary(
            debate_id=debate_id,
            proposal_id=debate.proposal_id,
            arguments_for=arguments_for,
            arguments_against=arguments_against,
            neutral_arguments=neutral,
            consensus_reached=consensus_reached,
            dominant_position=dominant_position,
            strength_score=strength_score,
        )
    
    def _calculate_strength(
        self,
        arguments_for: List[DebateArgument],
        arguments_against: List[DebateArgument],
    ) -> float:
        """Calculate overall debate strength."""
        if not arguments_for and not arguments_against:
            return 0.0
        
        # Sum up argument strengths
        for_strength = sum(a.strength for a in arguments_for)
        against_strength = sum(a.strength for a in arguments_against)
        
        total = for_strength + against_strength
        if total == 0:
            return 0.5
        
        # Return ratio favoring support
        return for_strength / total
    
    def conduct_debate(
        self,
        proposals: List[AgentProposal],
        agents: List[Dict[str, Any]],
    ) -> List[DebateSummary]:
        """Conduct a full debate on multiple proposals.
        
        Args:
            proposals: Proposals to debate
            agents: Agents participating
            
        Returns:
            List of debate summaries
        """
        summaries = []
        
        for proposal in proposals:
            # Create debate
            debate = self.create_debate(proposal)
            
            # Have each agent submit arguments
            for agent in agents:
                role = agent.get("role", "unknown")
                
                # Determine position based on agent role and proposal
                position = self._determine_agent_position(role, proposal)
                
                # Generate argument
                argument = self.submit_argument(
                    debate.round_id,
                    role,
                    position,
                    f"Position from {role}: {position.value}",
                    [{"source": role, "proposal": proposal.proposal_id}],
                )
            
            # Generate summary
            summary = self.generate_debate_summary(debate.round_id)
            summaries.append(summary)
            
            # Update proposal status
            if summary.consensus_reached and summary.dominant_position == DebatePosition.SUPPORT:
                proposal.status = "accepted"
            elif summary.dominant_position == DebatePosition.OPPOSE:
                proposal.status = "rejected"
        
        return summaries
    
    def _determine_agent_position(
        self,
        agent_role: str,
        proposal: AgentProposal,
    ) -> DebatePosition:
        """Determine an agent's position on a proposal."""
        # Simple heuristic based on role and proposal
        if agent_role == "cro" and proposal.risk_assessment:
            # CRO opposes high-risk proposals
            exposure = proposal.risk_assessment.get("current_exposure", 0)
            if exposure > 0.6:
                return DebatePosition.OPPOSE
        
        if agent_role == "cfo" and proposal.financial_impact:
            # CFO supports positive financial impact
            return_impact = proposal.financial_impact.get("expected_return", 0)
            if return_impact > 0.05:
                return DebatePosition.SUPPORT
        
        # Default to neutral
        return DebatePosition.NEUTRAL
