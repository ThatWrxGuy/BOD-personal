"""Finance Agent - Resource allocation and financial guidance."""
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent
from app.models.agent_definition import AgentDefinition
from app.models.agent_response import AgentResponse


class FinanceAgent(BaseAgent):
    """Finance Agent - Chief Financial Officer role."""

    def __init__(
        self,
        session: AsyncSession,
        agent_definition: Optional[AgentDefinition] = None,
    ):
        super().__init__(session, agent_definition)

    @property
    def name(self) -> str:
        return "Finance Agent"

    @property
    def role(self) -> str:
        return "Chief Financial Officer"

    @property
    def mandate(self) -> str:
        return "Resource allocation, capital protection, accumulation logic, opportunity cost, resilience"

    def get_constitution(self) -> str:
        return """You are the Finance Agent, serving as Chief Financial Officer on a personal strategic board of directors.

Your mandate is to provide guidance on resource allocation, capital protection, accumulation logic, opportunity cost analysis, and financial resilience.

When analyzing a question, you must focus on:
- Financial efficiency and resource allocation
- Capital protection and preservation
- Income and expense structure fragility
- Long-term wealth implications
- Opportunity cost of different paths
- ROI and value maximization
- Risk-adjusted returns

You provide advice. The user remains the final decision authority."""

    async def analyze(
        self,
        question: str,
        context: dict[str, Any],
        meeting_id: int,
    ) -> AgentResponse:
        """Analyze the question from a financial perspective."""
        messages = await self._build_messages(question, context)
        
        # Get response from LLM
        response = await self.llm_client.complete_with_json(messages)
        
        # Save response
        return await self._save_response(meeting_id, question, response)
