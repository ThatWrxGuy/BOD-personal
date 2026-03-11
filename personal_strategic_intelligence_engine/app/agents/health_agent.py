"""Health Agent - Sustainability and performance protection."""
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent
from app.models.agent_definition import AgentDefinition
from app.models.agent_response import AgentResponse


class HealthAgent(BaseAgent):
    """Health/Performance Agent - Chief Health Officer role."""

    def __init__(
        self,
        session: AsyncSession,
        agent_definition: Optional[AgentDefinition] = None,
    ):
        super().__init__(session, agent_definition)

    @property
    def name(self) -> str:
        return "Health Agent"

    @property
    def role(self) -> str:
        return "Chief Health Officer"

    @property
    def mandate(self) -> str:
        return "Protect operating capacity, sustainability, recovery, performance ceiling"

    def get_constitution(self) -> str:
        return """You are the Health/Performance Agent, serving as Chief Health Officer on a personal strategic board of directors.

Your mandate is to protect operating capacity, sustainability, recovery, and performance ceiling.

When analyzing a question, you must focus on:
- Burnout and energy depletion risks
- Physical and cognitive performance constraints
- Sustainability of proposed approaches
- Workload and stress considerations
- Recovery and rest requirements
- Long-term capacity maintenance
- Health-performance tradeoffs

You provide advice. The user remains the final decision authority."""

    async def analyze(
        self,
        question: str,
        context: dict[str, Any],
        meeting_id: int,
    ) -> AgentResponse:
        """Analyze the question from a health/performance perspective."""
        messages = await self._build_messages(question, context)
        
        # Get response from LLM
        response = await self.llm_client.complete_with_json(messages)
        
        # Save response
        return await self._save_response(meeting_id, question, response)
