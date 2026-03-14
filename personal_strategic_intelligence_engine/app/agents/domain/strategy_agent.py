"""Strategy Agent - Long-range direction and strategic positioning."""
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent
from app.models.agent_definition import AgentDefinition
from app.models.agent_response import AgentResponse


class StrategyAgent(BaseAgent):
    """Strategy Agent - Chief Strategy Officer role."""

    def __init__(
        self,
        session: AsyncSession,
        agent_definition: Optional[AgentDefinition] = None,
    ):
        super().__init__(session, agent_definition)

    @property
    def name(self) -> str:
        return "Strategy Agent"

    @property
    def role(self) -> str:
        return "Chief Strategy Officer"

    @property
    def mandate(self) -> str:
        return "Long-range direction, leverage, timing, sequencing, opportunity framing"

    def get_constitution(self) -> str:
        return """You are the Strategy Agent, serving as Chief Strategy Officer on a personal strategic board of directors.

Your mandate is to provide long-range direction, leverage identification, timing guidance, sequencing recommendations, and opportunity framing.

When analyzing a question, you must focus on:
- Strategic positioning and competitive advantage
- What matters most in the long run
- Building long-term leverage over noise
- Prioritization that creates sustainable progress
- Timing and market/opportunity windows
- Growth and expansion opportunities

You provide advice. The user remains the final decision authority."""

    async def analyze(
        self,
        question: str,
        context: dict[str, Any],
        meeting_id: int,
    ) -> AgentResponse:
        """Analyze the question from a strategic perspective."""
        messages = await self._build_messages(question, context)
        
        # Get response from LLM
        response = await self.llm_client.complete_with_json(messages)
        
        # Save response
        return await self._save_response(meeting_id, question, response)
