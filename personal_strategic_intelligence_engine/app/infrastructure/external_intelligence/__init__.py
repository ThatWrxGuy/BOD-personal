"""External Intelligence Package.

This package provides gateways to external intelligence services.
"""
from app.infrastructure.external_intelligence.openai_gateway import (
    OpenAIReasoningEngine,
    get_openai_reasoning_engine,
)

from app.infrastructure.external_intelligence.openhands_gateway import (
    OpenHandsEngine,
    get_openhands_engine,
)

from app.infrastructure.external_intelligence.github_gateway import (
    GitHubEngine,
    get_github_engine,
)

from app.infrastructure.external_intelligence.intelligence_router import (
    IntelligenceRouter,
    TaskType,
    get_intelligence_router,
    route_task,
)

__all__ = [
    # OpenAI Gateway
    "OpenAIReasoningEngine",
    "get_openai_reasoning_engine",
    
    # OpenHands Gateway
    "OpenHandsEngine",
    "get_openhands_engine",
    
    # GitHub Gateway
    "GitHubEngine",
    "get_github_engine",
    
    # Intelligence Router
    "IntelligenceRouter",
    "TaskType",
    "get_intelligence_router",
    "route_task",
]
