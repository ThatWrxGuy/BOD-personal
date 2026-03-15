"""Strategic Learning Service for memory and learning."""
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.learning import DecisionMemory, AgentScorecard, StrategicLesson, StrategicPattern, OutcomeCategory, LessonType
from app.models.execution_record import ExecutionRecord
from app.models.debate import DebateSession, DebateVote
from app.core.logging import get_logger

logger = get_logger(__name__)


class StrategicLearningService:
    """Unified service for decision memory and learning."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def record_decision_memory(
        self,
        decision_id: uuid.UUID,
        debate_session_id: Optional[uuid.UUID] = None,
        execution_id: Optional[uuid.UUID] = None,
        decision_type: str = "STRATEGIC",
        decision_summary: str = "",
        rationale_summary: str = "",
        predicted_outcome: str = "",
    ) -> DecisionMemory:
        """Record a new decision in memory."""
        
        # Get consensus score from debate
        consensus_score = None
        if debate_session_id:
            debate = await self.session.get(DebateSession, debate_session_id)
            if debate:
                consensus_score = debate.consensus_score
        
        # Get execution result
        execution_result = None
        if execution_id:
            execution = await self.session.get(ExecutionRecord, execution_id)
            if execution:
                execution_result = execution.status
        
        memory = DecisionMemory(
            decision_id=decision_id,
            debate_session_id=debate_session_id,
            execution_id=execution_id,
            decision_type=decision_type,
            decision_summary=decision_summary,
            rationale_summary=rationale_summary,
            consensus_score=consensus_score,
            approval_result="APPROVED",
            execution_result=execution_result,
            predicted_outcome=predicted_outcome,
        )
        
        self.session.add(memory)
        await self.session.commit()
        await self.session.refresh(memory)
        
        logger.info(f"Recorded decision memory: {memory.id}")
        
        return memory
    
    async def evaluate_outcome(
        self,
        decision_memory_id: uuid.UUID,
        actual_outcome: str,
        outcome_delta: float = 0.0,
    ) -> DecisionMemory:
        """Evaluate the outcome of a decision."""
        
        memory = await self.session.get(DecisionMemory, decision_memory_id)
        if not memory:
            raise ValueError("Decision memory not found")
        
        memory.actual_outcome = actual_outcome
        memory.outcome_delta = outcome_delta
        memory.outcome_evaluated = True
        
        # Determine outcome category
        if outcome_delta > 0.2:
            memory.outcome_category = OutcomeCategory.SUCCESS
        elif outcome_delta > 0:
            memory.outcome_category = OutcomeCategory.PARTIAL_SUCCESS
        elif outcome_delta == 0:
            memory.outcome_category = OutcomeCategory.NEUTRAL
        elif outcome_delta > -0.2:
            memory.outcome_category = OutcomeCategory.UNDERPERFORMED
        else:
            memory.outcome_category = OutcomeCategory.FAILED
        
        await self.session.commit()
        await self.session.refresh(memory)
        
        # Update agent scorecards
        await self._update_agent_scores(memory)
        
        # Extract lessons
        await self._extract_lesson(memory)
        
        return memory
    
    async def _update_agent_scores(self, memory: DecisionMemory):
        """Update agent scorecards based on outcome."""
        
        if not memory.debate_session_id:
            return
        
        # Get votes from debate
        result = await self.session.execute(
            select(DebateVote).where(
                DebateVote.debate_session_id == memory.debate_session_id
            )
        )
        votes = list(result.scalars().all())
        
        # Determine outcome direction
        if memory.outcome_category in [OutcomeCategory.SUCCESS, OutcomeCategory.PARTIAL_SUCCESS]:
            outcome_direction = 1
        elif memory.outcome_category in [OutcomeCategory.UNDERPERFORMED, OutcomeCategory.FAILED]:
            outcome_direction = -1
        else:
            outcome_direction = 0
        
        for vote in votes:
            # Get or create scorecard
            scorecard = await self._get_or_create_scorecard(vote.agent_id)
            
            scorecard.total_decisions += 1
            
            # Check if prediction was accurate
            vote_direction = 1 if vote.vote == "APPROVE" else -1 if vote.vote == "REJECT" else 0
            
            if vote_direction == outcome_direction and outcome_direction != 0:
                scorecard.accurate_predictions += 1
            
            # Update accuracy score
            if scorecard.total_decisions > 0:
                scorecard.accuracy_score = scorecard.accurate_predictions / scorecard.total_decisions
            
            # Update confidence tracking
            scorecard.avg_confidence = (scorecard.avg_confidence * (scorecard.total_decisions - 1) + vote.confidence) / scorecard.total_decisions
            
            # Calculate confidence accuracy
            if vote.confidence > 0.7 and outcome_direction == vote_direction:
                scorecard.confidence_accuracy = (scorecard.confidence_accuracy * 0.9 + 0.1)
            else:
                scorecard.confidence_accuracy *= 0.95
            
            scorecard.last_decision_at = datetime.utcnow()
            
            await self.session.commit()
    
    async def _get_or_create_scorecard(self, agent_id: str) -> AgentScorecard:
        """Get or create agent scorecard."""
        
        result = await self.session.execute(
            select(AgentScorecard).where(AgentScorecard.agent_id == agent_id)
        )
        scorecard = result.scalar_one_or_none()
        
        if not scorecard:
            scorecard = AgentScorecard(
                agent_id=agent_id,
                agent_name=agent_id.replace("_", " ").title(),
            )
            self.session.add(scorecard)
            await self.session.commit()
            await self.session.refresh(scorecard)
        
        return scorecard
    
    async def _extract_lesson(self, memory: DecisionMemory):
        """Extract a lesson from the decision."""
        
        if not memory.outcome_evaluated:
            return
        
        # Determine lesson type based on outcome
        if memory.outcome_category in [OutcomeCategory.SUCCESS, OutcomeCategory.PARTIAL_SUCCESS]:
            lesson_type = LessonType.SUCCESS_PATTERN
            title = f"Success: {memory.decision_summary[:50]}"
        else:
            lesson_type = LessonType.FAILURE_PATTERN
            title = f"Lesson: {memory.decision_summary[:50]}"
        
        # Only create lessons for significant outcomes
        if abs(memory.outcome_delta or 0) < 0.1:
            return
        
        # Check if similar lesson exists
        result = await self.session.execute(
            select(StrategicLesson).where(
                StrategicLesson.lesson_type == lesson_type,
                StrategicLesson.domain == memory.decision_type,
            )
        )
        
        lesson = StrategicLesson(
            lesson_type=lesson_type,
            title=title,
            description=f"From {memory.decision_type} decision: {memory.rationale_summary or memory.decision_summary}",
            domain=memory.decision_type,
            related_decisions=[str(memory.id)],
            confidence=abs(memory.outcome_delta or 0.5),
        )
        
        self.session.add(lesson)
        await self.session.commit()
    
    async def retrieve_relevant_memory(self, context: dict, limit: int = 5) -> list[DecisionMemory]:
        """Retrieve relevant historical decisions."""
        
        query = select(DecisionMemory).order_by(DecisionMemory.created_at.desc())
        
        # Filter by decision type if specified
        if context.get("decision_type"):
            query = query.where(DecisionMemory.decision_type == context["decision_type"])
        
        # Only include evaluated memories
        query = query.where(DecisionMemory.outcome_evaluated == True)
        
        result = await self.session.execute(query.limit(limit))
        return list(result.scalars().all())
    
    async def get_agent_performance(self, agent_id: str) -> Optional[AgentScorecard]:
        """Get agent performance scorecard."""
        
        result = await self.session.execute(
            select(AgentScorecard).where(AgentScorecard.agent_id == agent_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_agent_performance(self) -> list[AgentScorecard]:
        """Get all agent scorecards."""
        
        result = await self.session.execute(select(AgentScorecard))
        return list(result.scalars().all())
    
    async def get_lessons(self, limit: int = 20) -> list[StrategicLesson]:
        """Get recent lessons."""
        
        result = await self.session.execute(
            select(StrategicLesson)
            .order_by(StrategicLesson.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_memories(self, limit: int = 20) -> list[DecisionMemory]:
        """Get recent decision memories."""
        
        result = await self.session.execute(
            select(DecisionMemory)
            .order_by(DecisionMemory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


async def get_strategic_learning_service(session: AsyncSession) -> StrategicLearningService:
    """Get learning service instance."""
    return StrategicLearningService(session)
