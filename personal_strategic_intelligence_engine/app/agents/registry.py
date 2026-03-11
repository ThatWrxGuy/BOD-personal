"""Agent registry for managing and retrieving board agents."""
import json
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_definition import AgentDefinition
from app.agents.base_agent import BaseAgent
from app.agents.strategy_agent import StrategyAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.risk_agent import RiskAgent
from app.agents.health_agent import HealthAgent
from app.agents.operations_agent import OperationsAgent
from app.agents.legacy_agent import LegacyAgent
from app.core.logging import get_logger

logger = get_logger(__name__)


class AgentRegistry:
    """Registry for managing board agents."""

    # Agent class mapping
    AGENT_CLASSES = {
        "strategy": StrategyAgent,
        "finance": FinanceAgent,
        "risk": RiskAgent,
        "health": HealthAgent,
        "operations": OperationsAgent,
        "legacy": LegacyAgent,
    }

    def __init__(self, session: AsyncSession):
        """Initialize the agent registry."""
        self.session = session
        self._agent_definitions: Optional[dict[str, AgentDefinition]] = None

    async def _load_agent_definitions(self) -> dict[str, AgentDefinition]:
        """Load agent definitions from database."""
        if self._agent_definitions is not None:
            return self._agent_definitions

        result = await self.session.execute(
            select(AgentDefinition).where(AgentDefinition.active == True)
        )
        agents = result.scalars().all()

        self._agent_definitions = {}
        for agent in agents:
            # Map agent name to key
            key = agent.name.lower().replace(" agent", "")
            self._agent_definitions[key] = agent

        return self._agent_definitions

    async def get_agent(self, agent_key: str) -> Optional[BaseAgent]:
        """Get an agent by key (e.g., 'strategy', 'finance')."""
        definitions = await self._load_agent_definitions()
        
        agent_key = agent_key.lower()
        definition = definitions.get(agent_key)
        
        if not definition:
            logger.warning(f"Agent definition not found for key: {agent_key}")
            # Fallback to creating agent without definition
            agent_class = self.AGENT_CLASSES.get(agent_key)
            if agent_class:
                return agent_class(self.session, None)
            return None

        agent_class = self.AGENT_CLASSES.get(agent_key)
        if not agent_class:
            logger.warning(f"Agent class not found for key: {agent_key}")
            return None

        return agent_class(self.session, definition)

    async def get_all_agents(self) -> list[BaseAgent]:
        """Get all active board agents."""
        definitions = await self._load_agent_definitions()
        
        agents = []
        for key, agent_class in self.AGENT_CLASSES.items():
            definition = definitions.get(key)
            if definition:
                agents.append(agent_class(self.session, definition))
            else:
                agents.append(agent_class(self.session, None))

        return agents

    async def get_agent_names(self) -> list[str]:
        """Get list of all agent names."""
        return list(self.AGENT_CLASSES.keys())


async def get_agent_registry(session: AsyncSession) -> AgentRegistry:
    """Get an agent registry instance."""
    return AgentRegistry(session)
