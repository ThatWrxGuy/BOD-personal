"""Strategy Debate Engine - enables multiple agents to evaluate strategy proposals."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from app.strategy_pipeline.proposal_models import (
    DebateFeedback,
    DebateOutcome,
    RiskLevel,
    StrategyProposal,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class DebateAgentRole(str, Enum):
    """Roles for debate participant agents."""
    RISK_AGENT = "risk_agent"
    FINANCE_AGENT = "finance_agent"
    MARKET_AGENT = "market_agent"
    STRATEGY_AGENT = "strategy_agent"


class DebateAgent:
    """Represents an agent participating in strategy debate."""
    
    def __init__(self, agent_id: str, name: str, role: DebateAgentRole):
        self.agent_id = agent_id
        self.name = name
        self.role = role
    
    async def review(self, proposal: StrategyProposal) -> DebateFeedback:
        """
        Review a strategy proposal and provide feedback.
        
        This is a placeholder implementation. In production, this would
        invoke the actual agent to perform analysis.
        """
        # Simulate agent review based on role
        if self.role == DebateAgentRole.RISK_AGENT:
            return await self._risk_review(proposal)
        elif self.role == DebateAgentRole.FINANCE_AGENT:
            return await self._finance_review(proposal)
        elif self.role == DebateAgentRole.MARKET_AGENT:
            return await self._market_review(proposal)
        elif self.role == DebateAgentRole.STRATEGY_AGENT:
            return await self._strategy_review(proposal)
        else:
            return await self._default_review(proposal)
    
    async def _risk_review(self, proposal: StrategyProposal) -> DebateFeedback:
        """Risk Agent evaluates downside risk."""
        risk_factors = []
        
        if proposal.risk_level == RiskLevel.HIGH:
            risk_factors.append("High risk level identified")
        if proposal.risk_level == RiskLevel.CRITICAL:
            risk_factors.append("Critical risk - requires immediate attention")
        
        # Simulate confidence based on proposal attributes
        confidence = 0.7
        if proposal.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            confidence = 0.5
        
        recommendation = DebateOutcome.APPROVE
        if proposal.risk_level == RiskLevel.CRITICAL:
            recommendation = DebateOutcome.REJECT
        elif not proposal.expected_outcome:
            recommendation = DebateOutcome.REQUEST_MORE_DATA
        
        return DebateFeedback(
            agent_id=self.agent_id,
            agent_name=self.name,
            role=self.role.value,
            position="risk_evaluation",
            argument_text=f"Risk assessment: {', '.join(risk_factors) if risk_factors else 'No significant risks identified'}",
            reasoning=f"Evaluated risk level: {proposal.risk_level}. Expected outcome confidence: {proposal.confidence_score}",
            risk_assessment=str(proposal.risk_level),
            confidence_score=confidence,
            recommendation=recommendation,
            round_number=1,
        )
    
    async def _finance_review(self, proposal: StrategyProposal) -> DebateFeedback:
        """Finance Agent assesses capital impact."""
        proposed_action = proposal.proposed_action
        
        # Analyze capital requirements
        capital_impact = "moderate"
        if "amount" in proposed_action:
            capital_impact = "significant"
        
        recommendation = DebateOutcome.APPROVE
        if proposal.risk_level == RiskLevel.HIGH:
            recommendation = DebateOutcome.MODIFY
        
        return DebateFeedback(
            agent_id=self.agent_id,
            agent_name=self.name,
            role=self.role.value,
            position="capital_impact",
            argument_text=f"Capital impact assessment: {capital_impact}",
            reasoning=f"Proposal requires analysis of financial resources and capital allocation",
            risk_assessment=str(proposal.risk_level),
            confidence_score=0.75,
            recommendation=recommendation,
            round_number=1,
        )
    
    async def _market_review(self, proposal: StrategyProposal) -> DebateFeedback:
        """Market Agent evaluates market conditions."""
        recommendation = DebateOutcome.APPROVE
        
        # Market analysis
        market_conditions = "favorable"
        if proposal.category in ["trading", "market_entry"]:
            market_conditions = "requires careful timing"
        
        return DebateFeedback(
            agent_id=self.agent_id,
            agent_name=self.name,
            role=self.role.value,
            position="market_conditions",
            argument_text=f"Market conditions analysis: {market_conditions}",
            reasoning=f"Current market environment supports strategic decision",
            risk_assessment=str(proposal.risk_level),
            confidence_score=0.7,
            recommendation=recommendation,
            round_number=1,
        )
    
    async def _strategy_review(self, proposal: StrategyProposal) -> DebateFeedback:
        """Strategy Agent assesses alignment with goals."""
        
        recommendation = DebateOutcome.APPROVE
        reasoning = "Proposal aligns with strategic objectives"
        
        # Check for alignment issues
        if proposal.confidence_score < 0.5:
            recommendation = DebateOutcome.REQUEST_MORE_DATA
            reasoning = "Insufficient confidence in proposal outcomes"
        
        return DebateFeedback(
            agent_id=self.agent_id,
            agent_name=self.name,
            role=self.role.value,
            position="strategic_alignment",
            argument_text="Strategic alignment assessment completed",
            reasoning=reasoning,
            risk_assessment=str(proposal.risk_level),
            confidence_score=proposal.confidence_score,
            recommendation=recommendation,
            round_number=1,
        )
    
    async def _default_review(self, proposal: StrategyProposal) -> DebateFeedback:
        """Default review for unknown roles."""
        return DebateFeedback(
            agent_id=self.agent_id,
            agent_name=self.name,
            role=self.role.value,
            position="general_review",
            argument_text="General review completed",
            reasoning="Standard evaluation performed",
            risk_assessment=str(proposal.risk_level),
            confidence_score=0.6,
            recommendation=DebateOutcome.APPROVE,
            round_number=1,
        )


class DebateEngine:
    """
    The Debate Engine enables multiple agents to evaluate strategy proposals
    prior to simulation.
    
    Participating agents include:
    - Risk Agent: Evaluate downside risk
    - Finance Agent: Assess capital impact
    - Market Agent: Evaluate market conditions
    - Strategy Agent: Assess alignment with goals
    
    Debate outcomes may include:
    - approve
    - reject
    - request_more_data
    - modify
    """
    
    # Default debate agents
    DEFAULT_AGENTS = [
        DebateAgent("risk_agent_001", "Risk Agent", DebateAgentRole.RISK_AGENT),
        DebateAgent("finance_agent_001", "Finance Agent", DebateAgentRole.FINANCE_AGENT),
        DebateAgent("market_agent_001", "Market Agent", DebateAgentRole.MARKET_AGENT),
        DebateAgent("strategy_agent_001", "Strategy Agent", DebateAgentRole.STRATEGY_AGENT),
    ]
    
    def __init__(self, agents: Optional[List[DebateAgent]] = None):
        self.agents = agents or self.DEFAULT_AGENTS
        self.debate_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def evaluate(self, proposal: StrategyProposal) -> List[DebateFeedback]:
        """
        Evaluate a proposal through multi-agent debate.
        
        Args:
            proposal: The strategy proposal to evaluate
            
        Returns:
            List of feedback from all participating agents
        """
        logger.info(f"Starting debate for proposal: {proposal.id}")
        
        feedback = []
        for agent in self.agents:
            logger.debug(f"Agent {agent.name} reviewing proposal")
            agent_feedback = await agent.review(proposal)
            feedback.append(agent_feedback)
        
        # Log debate results
        self._log_debate_results(proposal.id, feedback)
        
        return feedback
    
    async def evaluate_with_context(
        self,
        proposal: StrategyProposal,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[DebateFeedback]:
        """
        Evaluate a proposal with additional context.
        
        Args:
            proposal: The strategy proposal to evaluate
            context: Additional context for evaluation
            
        Returns:
            List of feedback from all participating agents
        """
        logger.info(f"Starting contextual debate for proposal: {proposal.id}")
        
        feedback = []
        for agent in self.agents:
            # In a full implementation, context would influence the review
            agent_feedback = await agent.review(proposal)
            feedback.append(agent_feedback)
        
        return feedback
    
    def get_consensus(
        self,
        feedback: List[DebateFeedback],
    ) -> DebateOutcome:
        """
        Determine consensus from agent feedback.
        
        Args:
            feedback: List of feedback from debate agents
            
        Returns:
            Consensus outcome
        """
        if not feedback:
            return DebateOutcome.REJECT
        
        # Count recommendations
        recommendations = {}
        for f in feedback:
            rec = f.recommendation.value if hasattr(f.recommendation, 'value') else f.recommendation
            recommendations[rec] = recommendations.get(rec, 0) + 1
        
        # Find majority
        max_count = max(recommendations.values())
        consensus = [
            k for k, v in recommendations.items()
            if v == max_count
        ][0]
        
        return DebateOutcome(consensus) if isinstance(consensus, str) else consensus
    
    def get_average_confidence(
        self,
        feedback: List[DebateFeedback],
    ) -> float:
        """Calculate average confidence score from feedback."""
        if not feedback:
            return 0.0
        
        total = sum(f.confidence_score for f in feedback)
        return total / len(feedback)
    
    def _log_debate_results(
        self,
        proposal_id: str,
        feedback: List[DebateFeedback],
    ) -> None:
        """Log debate results for auditing."""
        session_id = str(uuid.uuid4())
        self.debate_sessions[session_id] = {
            "proposal_id": proposal_id,
            "timestamp": datetime.utcnow(),
            "feedback": [
                {
                    "agent_id": f.agent_id,
                    "agent_name": f.agent_name,
                    "recommendation": f.recommendation.value if hasattr(f.recommendation, 'value') else f.recommendation,
                    "confidence": f.confidence_score,
                }
                for f in feedback
            ],
        }
        
        logger.info(
            f"Debate session {session_id} completed for proposal {proposal_id}. "
            f"Consensus: {self.get_consensus(feedback)}"
        )
    
    def get_debate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific debate session."""
        return self.debate_sessions.get(session_id)


# Singleton instance
_debate_engine: Optional[DebateEngine] = None


def get_debate_engine() -> DebateEngine:
    """Get the global debate engine instance."""
    global _debate_engine
    if _debate_engine is None:
        _debate_engine = DebateEngine()
    return _debate_engine
