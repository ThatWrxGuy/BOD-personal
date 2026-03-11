"""Base agent class for board agents."""
import json
from abc import ABC, abstractmethod
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_definition import AgentDefinition
from app.models.agent_response import AgentResponse
from app.services.llm_client import get_llm_client, LLMClientBase
from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class for board agents."""

    def __init__(
        self,
        session: AsyncSession,
        agent_definition: Optional[AgentDefinition] = None,
    ):
        """Initialize the agent."""
        self.session = session
        self.agent_definition = agent_definition
        self.llm_client: LLMClientBase = get_llm_client()

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the agent name."""
        pass

    @property
    @abstractmethod
    def role(self) -> str:
        """Return the agent role."""
        pass

    @property
    @abstractmethod
    def mandate(self) -> str:
        """Return the agent mandate."""
        pass

    @abstractmethod
    def get_constitution(self) -> str:
        """Return the agent's constitution/prompt."""
        pass

    @abstractmethod
    async def analyze(
        self,
        question: str,
        context: dict[str, Any],
        meeting_id: int,
    ) -> AgentResponse:
        """Analyze a question and return structured response."""
        pass

    async def _build_messages(
        self,
        question: str,
        context: dict[str, Any],
    ) -> list[dict[str, str]]:
        """Build messages for LLM request."""
        # Build context string
        context_parts = []
        
        if "profile" in context:
            profile = context["profile"]
            context_parts.append(
                f"## User Profile\n"
                f"Mission: {profile.get('mission_statement', 'Not set')}\n"
                f"Values: {', '.join(profile.get('values', []))}\n"
                f"Priorities: {', '.join(profile.get('priorities', []))}\n"
                f"Non-negotiables: {', '.join(profile.get('non_negotiables', []))}\n"
                f"Active Goals: {', '.join(profile.get('active_goals', []))}\n"
                f"Risk Tolerance: {profile.get('risk_tolerance', 'moderate')}"
            )

        if "recent_meetings" in context:
            meetings = context["recent_meetings"]
            if meetings:
                context_parts.append(
                    f"## Recent Board Meetings\n" +
                    "\n".join([
                        f"- {m.question} ({m.created_at.strftime('%Y-%m-%d')})"
                        for m in meetings[:5]
                    ])
                )

        if "recent_decisions" in context:
            decisions = context["recent_decisions"]
            if decisions:
                context_parts.append(
                    f"## Recent Decisions\n" +
                    "\n".join([
                        f"- {d.decision_summary}: {d.chosen_action}"
                        for d in decisions[:5]
                    ])
                )

        context_str = "\n\n".join(context_parts)

        system_prompt = f"""{self.get_constitution()}

You are part of a strategic board of directors. The user is the CEO and final decision authority.

## Current Context
{context_str}

## Your Task
Provide your analysis and recommendation for the following question:
{question}

Provide your response in JSON format with the following structure:
{{
    "summary_judgment": "A brief summary of your overall assessment",
    "main_recommendation": "Your primary recommendation",
    "supporting_reasons": ["Reason 1", "Reason 2", "Reason 3"],
    "main_risks": ["Risk 1", "Risk 2"],
    "tradeoffs": ["Tradeoff 1", "Tradeoff 2"],
    "requested_followups": ["Question 1", "Question 2"] or null,
    "confidence_score": 0-10 (your confidence in this recommendation)
}}

Be thorough, specific, and consider multiple angles. Focus on your area of expertise as defined in your mandate."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ]

        return messages

    async def _parse_response(self, response: str) -> dict[str, Any]:
        """Parse JSON response from LLM."""
        try:
            # Try to parse as JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # Return mock response if parsing fails
            logger.warning(f"Failed to parse LLM response as JSON: {response[:200]}")
            return {
                "summary_judgment": "Analysis completed",
                "main_recommendation": "Proceed with careful consideration",
                "supporting_reasons": ["General strategic factors considered"],
                "main_risks": ["Uncertainty in implementation"],
                "tradeoffs": ["Time vs quality tradeoffs"],
                "requested_followups": None,
                "confidence_score": 5.0,
            }

    async def _save_response(
        self,
        meeting_id: int,
        question: str,
        analysis: dict[str, Any],
    ) -> AgentResponse:
        """Save agent response to database."""
        agent_response = AgentResponse(
            meeting_id=meeting_id,
            agent_id=self.agent_definition.id,
            summary_judgment=analysis.get("summary_judgment", ""),
            main_recommendation=analysis.get("main_recommendation", ""),
            supporting_reasons=json.dumps(analysis.get("supporting_reasons", [])),
            main_risks=json.dumps(analysis.get("main_risks", [])),
            tradeoffs=json.dumps(analysis.get("tradeoffs", [])),
            requested_followups=json.dumps(analysis.get("requested_followups")),
            confidence_score=analysis.get("confidence_score"),
            version_id=self.agent_definition.version_id if self.agent_definition else "1.0.0",
            raw_output=json.dumps(analysis),
        )
        
        self.session.add(agent_response)
        await self.session.commit()
        await self.session.refresh(agent_response)
        
        return agent_response
