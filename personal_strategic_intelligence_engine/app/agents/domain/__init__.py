"""Domain expert agents for the Personal Strategic Intelligence Engine.

Domain agents provide specialized advisory analysis within specific domains:
- Strategy: Long-range direction and strategic positioning
- Finance: Resource allocation and financial guidance
- Risk: Risk identification and mitigation
- Health: Health/performance optimization
- Operations: Operational feasibility and execution
- Legacy: Legacy alignment and doctrine consistency

Note: These agents inherit from BaseAgent (base_agent.py) for backward compatibility.
"""
from app.agents.domain.strategy_agent import StrategyAgent
from app.agents.domain.finance_agent import FinanceAgent
from app.agents.domain.risk_agent import RiskAgent
from app.agents.domain.health_agent import HealthAgent
from app.agents.domain.operations_agent import OperationsAgent
from app.agents.domain.legacy_agent import LegacyAgent

__all__ = [
    "StrategyAgent",
    "FinanceAgent",
    "RiskAgent",
    "HealthAgent",
    "OperationsAgent",
    "LegacyAgent",
]
