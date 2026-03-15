"""Legacy Agent - Values alignment and purpose preservation."""
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent
from app.models.agent_definition import AgentDefinition
from app.models.agent_response import AgentResponse


class LegacyAgent(BaseAgent):
    """Legacy/Alignment Agent - Chief Alignment Officer role."""

    def __init__(
        self,
        session: AsyncSession,
        agent_definition: Optional[AgentDefinition] = None,
    ):
        super().__init__(session, agent_definition)

    @property
    def name(self) -> str:
        return "Legacy Agent"

    @property
    def role(self) -> str:
        return "Chief Alignment Officer"

    @property
    def mandate(self) -> str:
        return "Protect values, purpose, identity coherence, and long-term meaning"

    def get_constitution(self) -> str:
        return """You are the Legacy/Alignment Agent, serving as Chief Alignment Officer on a personal strategic board of directors.

Your mandate is to protect values, purpose, identity coherence, and long-term meaning.

When analyzing a question, you must focus on:
- Alignment with stated mission and values
- Values conflicts or tradeoffs
- Meaning versus efficiency considerations
- Whether progress is truly worthwhile
- Long-term identity implications
- Purpose alignment
- What you'll be proud of in 10 years

You provide advice. The user remains the final decision authority."""

    async def analyze(
        self,
        question: str,
        context: dict[str, Any],
        meeting_id: int,
    ) -> AgentResponse:
        """Analyze the question from a legacy/alignment perspective."""
        messages = await self._build_messages(question, context)
        
        # Get response from LLM
        response = await self.llm_client.complete_with_json(messages)
        
        # Save response
        return await self._save_response(meeting_id, question, response)
