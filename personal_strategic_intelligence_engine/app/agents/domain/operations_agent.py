"""Operations Agent - Execution and implementation feasibility."""
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent
from app.models.agent_definition import AgentDefinition
from app.models.agent_response import AgentResponse


class OperationsAgent(BaseAgent):
    """Operations Agent - Chief Operating Officer role."""

    def __init__(
        self,
        session: AsyncSession,
        agent_definition: Optional[AgentDefinition] = None,
    ):
        super().__init__(session, agent_definition)

    @property
    def name(self) -> str:
        return "Operations Agent"

    @property
    def role(self) -> str:
        return "Chief Operating Officer"

    @property
    def mandate(self) -> str:
        return "Convert strategy into executable systems and realistic workflows"

    def get_constitution(self) -> str:
        return """You are the Operations Agent, serving as Chief Operating Officer on a personal strategic board of directors.

Your mandate is to convert strategy into executable systems and realistic workflows.

When analyzing a question, you must focus on:
- Implementation feasibility
- Bottlenecks and blockers
- Simplification opportunities
- Cadence and rhythm of execution
- Workload realism
- Process efficiency
- Getting things done effectively

You provide advice. The user remains the final decision authority."""

    async def analyze(
        self,
        question: str,
        context: dict[str, Any],
        meeting_id: int,
    ) -> AgentResponse:
        """Analyze the question from an operational perspective."""
        messages = await self._build_messages(question, context)
        
        # Get response from LLM
        response = await self.llm_client.complete_with_json(messages)
        
        # Save response
        return await self._save_response(meeting_id, question, response)
