"""Synthesis engine for combining agent outputs into final recommendations."""
import json
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board_meeting import BoardMeeting
from app.models.agent_response import AgentResponse
from app.models.critique_response import CritiqueResponse
from app.models.agent_definition import AgentDefinition
from app.services.llm_client import get_llm_client, LLMClientBase
from app.core.logging import get_logger

logger = get_logger(__name__)


class SynthesisEngine:
    """Engine for synthesizing board recommendations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.llm_client: LLMClientBase = get_llm_client()

    async def synthesize(
        self,
        meeting_id: int,
    ) -> dict[str, Any]:
        """Synthesize agent responses into a final recommendation."""
        # Get meeting with all responses
        meeting = await self.session.get(BoardMeeting, meeting_id)
        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")

        # Load agent responses
        result = await self.session.execute(
            select(AgentResponse)
            .where(AgentResponse.meeting_id == meeting_id)
        )
        agent_responses = list(result.scalars().all())

        # Load critiques
        result = await self.session.execute(
            select(CritiqueResponse)
            .where(CritiqueResponse.meeting_id == meeting_id)
        )
        critiques = list(result.scalars().all())

        # Build synthesis context
        synthesis_context = self._build_synthesis_context(
            meeting, agent_responses, critiques
        )

        # Use LLM to synthesize
        synthesis = await self._llm_synthesize(
            meeting.question,
            synthesis_context,
        )

        # Update meeting with synthesis results
        meeting.executive_summary = synthesis.get("executive_summary")
        meeting.consensus_recommendation = synthesis.get("consensus_recommendation")
        meeting.alternatives = json.dumps(synthesis.get("alternatives", []))
        meeting.risks = json.dumps(synthesis.get("major_risks", []))
        meeting.tradeoffs = json.dumps(synthesis.get("tradeoffs", []))
        meeting.confidence_score = synthesis.get("confidence_score")
        meeting.data_gaps = json.dumps(synthesis.get("data_gaps", []))
        meeting.status = "completed"

        await self.session.commit()
        await self.session.refresh(meeting)

        return synthesis

    def _build_synthesis_context(
        self,
        meeting: BoardMeeting,
        agent_responses: list[AgentResponse],
        critiques: list[CritiqueResponse],
    ) -> str:
        """Build context string for synthesis."""
        context_parts = [f"## Question\n{meeting.question}\n"]

        # Add each agent's response
        context_parts.append("## Agent Analyses")
        for response in agent_responses:
            context_parts.append(f"\n### {response.agent.name if response.agent else 'Agent'} Response")
            context_parts.append(f"Summary: {response.summary_judgment}")
            context_parts.append(f"Recommendation: {response.main_recommendation}")
            context_parts.append(f"Supporting Reasons: {', '.join(json.loads(response.supporting_reasons))}")
            context_parts.append(f"Risks: {', '.join(json.loads(response.main_risks))}")
            context_parts.append(f"Tradeoffs: {', '.join(json.loads(response.tradeoffs))}")
            context_parts.append(f"Confidence: {response.confidence_score}/10")

        # Add critiques
        if critiques:
            context_parts.append("\n## Critiques")
            for critique in critiques:
                source = critique.source_agent.name if critique.source_agent else "Agent"
                target = critique.target_agent.name if critique.target_agent else "Agent"
                context_parts.append(f"\n### {source} critiques {target}")
                context_parts.append(f"Critique: {critique.critique_text}")
                context_parts.append(f"Severity: {critique.severity}")

        return "\n".join(context_parts)

    async def _llm_synthesize(
        self,
        question: str,
        context: str,
    ) -> dict[str, Any]:
        """Use LLM to synthesize a final recommendation."""
        system_prompt = """You are the Synthesis Engine for a strategic board of directors.

Your role is to combine independent agent analyses and critiques into a coherent final recommendation.

CRITICAL RULES:
1. NEVER invent fake consensus - preserve genuine disagreements
2. NEVER suppress meaningful disagreement - minority warnings must be escalated
3. NEVER present unjustified certainty - acknowledge uncertainty
4. NEVER discard strong risk objections - serious objections must be included
5. Identify agreement clusters and disagreement clusters
6. Generate one primary recommendation
7. Provide alternatives when certainty is low
8. Identify missing data

Respond with JSON format:
{
    "executive_summary": "2-3 sentence summary of the board's recommendation",
    "consensus_recommendation": "The primary recommendation",
    "alternatives": ["Alternative 1", "Alternative 2"],
    "major_supporting_reasons": ["Reason 1", "Reason 2"],
    "major_risks": ["Risk 1", "Risk 2"],
    "tradeoffs": ["Tradeoff 1", "Tradeoff 2"],
    "disagreement_summary": "Summary of any disagreements",
    "confidence_score": 0-10,
    "next_suggested_actions": ["Action 1", "Action 2"],
    "data_gaps": ["Gap 1", "Gap 2"]
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"## Context\n{context}\n\nSynthesize this into a board recommendation."},
        ]

        try:
            result = await self.llm_client.complete_with_json(messages)
            return result
        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            # Return fallback synthesis
            return {
                "executive_summary": "The board has completed its analysis.",
                "consensus_recommendation": "Review individual agent responses for details.",
                "alternatives": [],
                "major_supporting_reasons": [],
                "major_risks": [],
                "tradeoffs": [],
                "disagreement_summary": "Synthesis unavailable",
                "confidence_score": 5.0,
                "next_suggested_actions": [],
                "data_gaps": [],
            }


async def get_synthesis_engine(session: AsyncSession) -> SynthesisEngine:
    """Get a synthesis engine instance."""
    return SynthesisEngine(session)
