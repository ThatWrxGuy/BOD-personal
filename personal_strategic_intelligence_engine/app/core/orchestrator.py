"""Orchestrator for running board meetings."""
import json
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board_meeting import BoardMeeting
from app.models.agent_response import AgentResponse
from app.models.critique_response import CritiqueResponse
from app.models.agent_definition import AgentDefinition
from app.agents.registry import AgentRegistry
from app.core.context_builder import ContextBuilder
from app.core.synthesis import SynthesisEngine
from app.core.logging import get_logger

logger = get_logger(__name__)


class BoardOrchestrator:
    """Orchestrates the full board meeting process."""

    # Define critique relationships
    CRITIQUE_PAIRS = [
        # (critic, target) - who critiques whom
        ("finance", "strategy"),
        ("risk", "strategy"),
        ("risk", "finance"),
        ("health", "strategy"),
        ("health", "operations"),
        ("legacy", "strategy"),
        ("legacy", "finance"),
        ("operations", "strategy"),
    ]

    def __init__(self, session: AsyncSession):
        self.session = session
        self.context_builder = ContextBuilder(session)
        self.synthesis_engine = SynthesisEngine(session)
        self.agent_registry = AgentRegistry(session)

    async def run_meeting(
        self,
        meeting_id: int,
    ) -> BoardMeeting:
        """Run the complete board meeting workflow."""
        logger.info(f"Starting board meeting {meeting_id}")

        # Get meeting
        meeting = await self.session.get(BoardMeeting, meeting_id)
        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")

        try:
            # PHASE 1 & 2: Context is already built when meeting was created
            # Build and store context
            context = await self.context_builder.build_context(
                meeting.question,
                meeting.meeting_type,
            )
            context_snapshot = await self.context_builder.get_context_snapshot(context)
            meeting.context_snapshot = context_snapshot
            await self.session.commit()

            # PHASE 3: Independent Analysis
            await self._run_independent_analysis(meeting, context)

            # PHASE 4: Critique Round
            await self._run_critique_round(meeting)

            # PHASE 5: Synthesis
            await self.synthesis_engine.synthesize(meeting_id)

            # PHASE 6: Meeting is already persisted through updates
            # Reload meeting with all data
            await self.session.refresh(meeting, ["agent_responses", "critique_responses"])

            logger.info(f"Board meeting {meeting_id} completed")
            return meeting

        except Exception as e:
            logger.error(f"Error in board meeting {meeting_id}: {e}")
            meeting.status = "failed"
            await self.session.commit()
            raise

    async def _run_independent_analysis(
        self,
        meeting: BoardMeeting,
        context: dict[str, Any],
    ) -> None:
        """Run independent analysis from all agents."""
        logger.info(f"Running independent analysis for meeting {meeting.id}")

        # Get all agents
        agents = await self.agent_registry.get_all_agents()

        # Run each agent independently
        for agent in agents:
            logger.info(f"Running {agent.name} analysis")
            try:
                await agent.analyze(
                    question=meeting.question,
                    context=context,
                    meeting_id=meeting.id,
                )
            except Exception as e:
                logger.error(f"Error in {agent.name}: {e}")
                # Continue with other agents

    async def _run_critique_round(self, meeting: BoardMeeting) -> None:
        """Run critique round between agents."""
        logger.info(f"Running critique round for meeting {meeting.id}")

        # Get all agent responses
        result = await self.session.execute(
            select(AgentResponse).where(AgentResponse.meeting_id == meeting.id)
        )
        agent_responses = list(result.scalars().all())

        # Build response lookup
        response_by_agent: dict[str, AgentResponse] = {}
        for response in agent_responses:
            if response.agent:
                key = response.agent.name.lower().replace(" agent", "")
                response_by_agent[key] = response

        # Get agent definitions for critic names
        agent_definitions = await self.agent_registry._load_agent_definitions()

        # Run critiques
        for critic_key, target_key in self.CRITIQUE_PAIRS:
            critic_def = agent_definitions.get(critic_key)
            target_def = agent_definitions.get(target_key)
            target_response = response_by_agent.get(target_key)

            if not critic_def or not target_def or not target_response:
                continue

            logger.info(f"{critic_key} critiquing {target_key}")
            try:
                critique = await self._generate_critique(
                    meeting_id=meeting.id,
                    source_agent_id=critic_def.id,
                    target_agent_id=target_def.id,
                    target_response=target_response,
                )

                if critique:
                    self.session.add(critique)
            except Exception as e:
                logger.error(f"Error generating critique: {e}")

        await self.session.commit()

    async def _generate_critique(
        self,
        meeting_id: int,
        source_agent_id: int,
        target_agent_id: int,
        target_response: AgentResponse,
    ) -> Optional[CritiqueResponse]:
        """Generate a critique from one agent to another."""
        # Build critique prompt
        from app.services.llm_client import get_llm_client
        llm_client = get_llm_client()

        target_recommendation = target_response.main_recommendation
        target_risks = json.loads(target_response.main_risks)

        system_prompt = """You are providing a critique of another board agent's recommendation.

Your role is to critically evaluate their recommendation from your perspective.
Focus on:
- What they might have missed
- Potential blind spots
- Risks they underestimated
- Alternative considerations

Be specific and constructive. If you agree, acknowledge what's valid.
"""

        user_prompt = f"""Critique the following recommendation:

Recommendation: {target_recommendation}

Identified Risks: {', '.join(target_risks)}

Provide your critique as JSON:
{{
    "critique_text": "Your detailed critique",
    "severity": "low|medium|high|critical"
}}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            result = await llm_client.complete_with_json(messages)
            return CritiqueResponse(
                meeting_id=meeting_id,
                source_agent_id=source_agent_id,
                target_agent_id=target_agent_id,
                critique_text=result.get("critique_text", ""),
                severity=result.get("severity", "medium"),
            )
        except Exception as e:
            logger.error(f"Error in critique generation: {e}")
            return None


async def get_board_orchestrator(session: AsyncSession) -> BoardOrchestrator:
    """Get a board orchestrator instance."""
    return BoardOrchestrator(session)
