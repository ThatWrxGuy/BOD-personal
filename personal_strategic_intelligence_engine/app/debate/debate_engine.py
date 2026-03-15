"""Debate Engine for orchestrating multi-agent strategic debates."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.debate import DebateSession, DebateArgument, DebateVote, DebateHistory, DebateStatus, VoteType
from app.models.agent_definition import AgentDefinition
from app.debate.argument_generator import get_argument_generator
from app.debate.consensus_model import get_consensus_model
from app.core.logging import get_logger

logger = get_logger(__name__)


class DebateEngine:
    """Orchestrates multi-agent strategic debates."""
    
    # Board agents to participate
    BOARD_AGENTS = [
        "strategy_agent",
        "finance_agent", 
        "risk_agent",
        "health_agent",
        "operations_agent",
        "legacy_agent",
    ]
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.argument_generator = get_argument_generator()
        self.consensus_model = get_consensus_model()
    
    async def start_debate(
        self,
        decision_id: Optional[uuid.UUID],
        title: str,
        description: str,
        topic: str,
        context: dict,
    ) -> DebateSession:
        """Start a new debate session."""
        
        # Create debate session
        session = DebateSession(
            decision_id=decision_id,
            title=title,
            description=description,
            topic=topic,
            status=DebateStatus.INITIALIZED,
            max_rounds=4,
            participants=self.BOARD_AGENTS,
        )
        
        self.session.add(session)
        await self.session.commit()
        await self.session.refresh(session)
        
        logger.info(f"Started debate session: {session.id}")
        
        # Start the debate
        await self._run_debate(session, context)
        
        return session
    
    async def _run_debate(self, debate_session: DebateSession, context: dict):
        """Run the debate through all rounds."""
        
        debate_session.status = DebateStatus.IN_PROGRESS
        debate_session.start_time = datetime.utcnow()
        
        await self.session.commit()
        
        try:
            # Round 1: Initial arguments
            await self._run_round(debate_session, 1, context)
            
            # Round 2: Counter-arguments
            await self._run_round(debate_session, 2, context)
            
            # Round 3: Risk analysis
            await self._run_round(debate_session, 3, context)
            
            # Round 4: Voting
            await self._run_voting_round(debate_session, context)
            
            # Complete the debate
            debate_session.status = DebateStatus.COMPLETED
            debate_session.end_time = datetime.utcnow()
            
            await self.session.commit()
            
            logger.info(f"Debate completed: {debate_session.id}")
            
        except Exception as e:
            logger.error(f"Debate failed: {e}")
            debate_session.status = DebateStatus.FAILED
            debate_session.end_time = datetime.utcnow()
            await self.session.commit()
            raise
    
    async def _run_round(self, debate_session: DebateSession, round_number: int, context: dict):
        """Run a single debate round."""
        
        logger.info(f"Running debate round {round_number} for session {debate_session.id}")
        
        # Generate arguments from each agent
        for agent_id in self.BOARD_AGENTS:
            argument_data = await self.argument_generator.generate_argument(
                agent_id=agent_id,
                debate_topic=debate_session.topic,
                context=context,
                round_number=round_number,
            )
            
            argument = DebateArgument(
                debate_session_id=debate_session.id,
                agent_id=argument_data["agent_id"],
                round_number=round_number,
                position=argument_data["position"],
                argument_text=argument_data["argument_text"],
                reasoning=argument_data.get("reasoning"),
                supporting_data=argument_data.get("supporting_data"),
                risk_assessment=argument_data.get("risk_assessment"),
                confidence_score=argument_data.get("confidence_score", 0.5),
                parent_argument_id=argument_data.get("parent_argument_id"),
            )
            
            self.session.add(argument)
            
            # Record history
            await self._record_history(debate_session.id, agent_id, "ARGUMENT", {"round": round_number})
        
        await self.session.commit()
        
        debate_session.rounds_completed = round_number
        await self.session.commit()
    
    async def _run_voting_round(self, debate_session: DebateSession, context: dict):
        """Run the voting round."""
        
        logger.info(f"Running voting round for session {debate_session.id}")
        
        votes = []
        confidences = []
        
        # Get all arguments for context
        result = await self.session.execute(
            select(DebateArgument).where(
                DebateArgument.debate_session_id == debate_session.id
            )
        )
        arguments = list(result.scalars().all())
        
        # Each agent votes
        for agent_id in self.BOARD_AGENTS:
            # Determine vote based on agent's stance
            agent_args = [a for a in arguments if a.agent_id == agent_id]
            
            if agent_args:
                # Vote based on position
                positions = [a.position for a in agent_args]
                if "SUPPORT" in positions:
                    vote_type = VoteType.APPROVE
                elif "OPPOSE" in positions:
                    vote_type = VoteType.REJECT
                else:
                    vote_type = VoteType.ABSTAIN
            else:
                vote_type = VoteType.ABSTAIN
            
            vote = DebateVote(
                debate_session_id=debate_session.id,
                agent_id=agent_id,
                agent_name=agent_id.replace("_", " ").title(),
                vote=vote_type,
                justification=f"Vote based on analysis of {debate_session.topic}",
                confidence=0.7,
                weight=1.0,
                round_number=4,
            )
            
            self.session.add(vote)
            votes.append({"agent_id": agent_id, "vote": vote_type})
            confidences.append(0.7)
            
            await self._record_history(debate_session.id, agent_id, "VOTE", {"vote": vote_type})
        
        await self.session.commit()
        
        # Calculate consensus
        consensus_score, recommendation = self.consensus_model.calculate_consensus(votes, confidences)
        
        # Adjust for risk
        risk_score = context.get("risk_score", 0.5)
        adjusted_score, final_recommendation = self.consensus_model.calculate_with_risk(
            consensus_score, risk_score
        )
        
        debate_session.consensus_score = adjusted_score
        debate_session.final_recommendation = final_recommendation
        
        await self.session.commit()
        
        logger.info(f"Debate consensus: {adjusted_score} - {final_recommendation}")
    
    async def _record_history(
        self,
        session_id: uuid.UUID,
        agent_id: str,
        action_type: str,
        content: dict,
    ):
        """Record debate history."""
        
        history = DebateHistory(
            debate_session_id=session_id,
            agent_id=agent_id,
            action_type=action_type,
            content=content,
            timestamp=datetime.utcnow(),
        )
        
        self.session.add(history)
        await self.session.commit()
    
    async def get_session(self, session_id: uuid.UUID) -> Optional[DebateSession]:
        """Get a debate session."""
        return await self.session.get(DebateSession, session_id)
    
    async def get_arguments(self, session_id: uuid.UUID) -> list[DebateArgument]:
        """Get arguments for a session."""
        result = await self.session.execute(
            select(DebateArgument)
            .where(DebateArgument.debate_session_id == session_id)
            .order_by(DebateArgument.round_number, DebateArgument.agent_id)
        )
        return list(result.scalars().all())
    
    async def get_votes(self, session_id: uuid.UUID) -> list[DebateVote]:
        """Get votes for a session."""
        result = await self.session.execute(
            select(DebateVote)
            .where(DebateVote.debate_session_id == session_id)
        )
        return list(result.scalars().all())
    
    async def list_sessions(self, status: Optional[str] = None) -> list[DebateSession]:
        """List debate sessions."""
        query = select(DebateSession).order_by(DebateSession.created_at.desc())
        if status:
            query = query.where(DebateSession.status == status)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_consensus_details(self, session_id: uuid.UUID) -> dict:
        """Get detailed consensus breakdown."""
        votes = await self.get_votes(session_id)
        
        vote_list = [{"agent_id": v.agent_id, "vote": v.vote} for v in votes]
        confidences = [v.confidence for v in votes]
        
        consensus_score, _ = self.consensus_model.calculate_consensus(vote_list, confidences)
        
        return self.consensus_model.get_consensus_details(vote_list, consensus_score)


async def get_debate_engine(session: AsyncSession) -> DebateEngine:
    """Get debate engine instance."""
    return DebateEngine(session)
