"""Risk Agent - Downside protection and risk analysis."""
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent
from app.models.agent_definition import AgentDefinition
from app.models.agent_response import AgentResponse


class RiskAgent(BaseAgent):
    """Risk Agent - Chief Risk Officer role."""

    def __init__(
        self,
        session: AsyncSession,
        agent_definition: Optional[AgentDefinition] = None,
    ):
        super().__init__(session, agent_definition)

    @property
    def name(self) -> str:
        return "Risk Agent"

    @property
    def role(self) -> str:
        return "Chief Risk Officer"

    @property
    def mandate(self) -> str:
        return "Internal auditor and downside sentinel - identify failure modes, survivability, hidden downside"

    def get_constitution(self) -> str:
        return """You are the Risk Agent, serving as Chief Risk Officer on a personal strategic board of directors.

Your mandate is to be the internal auditor and downside sentinel. You identify failure modes, survivability concerns, hidden downside, overextension risks, and unrealistic assumptions.

When analyzing a question, you must focus on:
- Failure modes and what could go wrong
- Survivability under adverse conditions
- Hidden downside others might miss
- Overextension and concentration risks
- Unrealistic assumptions in plans
- Single points of failure
- Contingency and fallback options

You provide advice. The user remains the final decision authority."""

    async def analyze(
        self,
        question: str,
        context: dict[str, Any],
        meeting_id: int,
    ) -> AgentResponse:
        """Analyze the question from a risk perspective."""
        messages = await self._build_messages(question, context)
        
        # Get response from LLM
        response = await self.llm_client.complete_with_json(messages)
        
        # Save response
        return await self._save_response(meeting_id, question, response)
