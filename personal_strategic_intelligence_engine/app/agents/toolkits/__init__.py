"""Agent Toolkits - Domain-specific toolkits for agents.

This package provides:
- AgentProfile: Agent identity and capabilities
- BaseToolkit: Abstract toolkit interfaces
- ToolkitRegistry: Maps domains to toolkit classes
- ToolkitResolver: Resolves toolkits based on profile and policy

Domain Toolkits:
- FinanceToolkit: Finance data retrieval
- HealthToolkit: Health/nutrition data retrieval
- FitnessToolkit: Fitness data retrieval
- OperationsToolkit: Operations data retrieval
- FederatedRetrievalToolkit: Cross-domain retrieval

Usage:
    from app.agents.toolkits import get_toolkit_resolver
    
    resolver = get_toolkit_resolver()
    toolkits = await resolver.resolve_toolkits_for_agent("agent_finance", gateway)
    
    # Use toolkit
    results = await toolkits["finance_toolkit"].search_structured("stock prices")
"""
from app.agents.toolkits.agent_profile import (
    AgentProfile,
    AgentRole,
    AgentCapability,
    TrustTier,
    get_agent_profile_manager,
)
from app.agents.toolkits.base import (
    BaseToolkit,
    RetrievalToolkit,
    FederatedToolkit,
)
from app.agents.toolkits.registry import (
    ToolkitRegistry,
    get_toolkit_registry,
    register_domain_toolkit,
)
from app.agents.toolkits.resolver import (
    ToolkitResolver,
    get_toolkit_resolver,
)

# Import toolkits to register them
# Note: This ensures decorators run and register toolkits
from app.agents.toolkits import finance
from app.agents.toolkits import health
from app.agents.toolkits import fitness
from app.agents.toolkits import operations
from app.agents.toolkits import federated

__all__ = [
    # Profile
    "AgentProfile",
    "AgentRole",
    "AgentCapability",
    "TrustTier",
    "get_agent_profile_manager",
    # Base
    "BaseToolkit",
    "RetrievalToolkit",
    "FederatedToolkit",
    # Registry
    "ToolkitRegistry",
    "get_toolkit_registry",
    "register_domain_toolkit",
    # Resolver
    "ToolkitResolver",
    "get_toolkit_resolver",
]
