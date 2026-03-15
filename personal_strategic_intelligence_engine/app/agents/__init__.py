"""Agents package - Canonical location for all agents.

This package contains:
- domain/ : Domain expert agents (advisory)
- executive/ : Executive governance agents
- base.py : Unified base agent class
- base_agent.py : Legacy base class (backward compatibility)
- registry.py : Agent registry

Import agents from their canonical locations:
- Domain: from app.agents.domain import StrategyAgent, FinanceAgent, etc.
- Executive: from app.agents.executive import CEOAgent, CFOAgent, etc.
"""
from app.agents.base_agent import BaseAgent
from app.agents.domain import StrategyAgent, FinanceAgent, RiskAgent, HealthAgent, OperationsAgent, LegacyAgent
from app.agents.executive import (
    CEOAgent, CFOAgent, COOAgent, CSOAgent, CROAgent, CKOAgent, CPOAgent,
    AgentCouncil, DebateEngine, BaseExecutiveAgent,
)
from app.agents.registry import AgentRegistry, get_agent_registry

__all__ = [
    # Base
    "BaseAgent",
    # Domain agents
    "StrategyAgent",
    "FinanceAgent",
    "RiskAgent",
    "HealthAgent",
    "OperationsAgent",
    "LegacyAgent",
    # Executive agents
    "CEOAgent",
    "CFOAgent",
    "COOAgent",
    "CSOAgent",
    "CROAgent",
    "CKOAgent",
    "CPOAgent",
    # Executive systems
    "AgentCouncil",
    "DebateEngine",
    "BaseExecutiveAgent",
    # Registry
    "AgentRegistry",
    "get_agent_registry",
]
