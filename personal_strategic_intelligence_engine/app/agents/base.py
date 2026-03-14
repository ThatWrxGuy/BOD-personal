"""Unified base class for all agents in the Personal Strategic Intelligence Engine.

This module provides a common base class for both domain expert agents and executive
governance agents, establishing a consistent interface and shared functionality.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class AgentCategory(str, Enum):
    """Categories of agents in the system."""
    DOMAIN = "domain"      # Domain expert agents (advisory)
    EXECUTIVE = "executive"  # Executive governance agents


class AgentRole(str, Enum):
    """Agent roles in the system."""
    # Domain roles
    STRATEGY = "strategy"
    FINANCE = "finance"
    RISK = "risk"
    HEALTH = "health"
    OPERATIONS = "operations"
    LEGACY = "legacy"
    
    # Executive roles
    CEO = "ceo"
    CFO = "cfo"
    COO = "coo"
    CSO = "cso"
    CRO = "cro"
    CKO = "cko"
    CPO = "cpo"


class BaseAgent(ABC):
    """Unified base class for all agents.
    
    This class provides:
    - Agent identity and metadata
    - Standardized interface
    - Context handling
    - Orchestration compatibility
    - Logging utilities
    
    Subclasses should inherit from this and implement required abstract methods.
    """
    
    def __init__(
        self,
        role: AgentRole,
        name: Optional[str] = None,
        mandate: Optional[str] = None,
    ):
        """Initialize the agent.
        
        Args:
            role: The agent's role from AgentRole enum
            name: Optional custom name (defaults to role-based name)
            mandate: Optional mandate description
        """
        self._role = role
        self._name = name or self._default_name()
        self._mandate = mandate or self._default_mandate()
        self._category = self._determine_category()
        
    @property
    def role(self) -> AgentRole:
        """Return the agent's role."""
        return self._role
    
    @property
    def name(self) -> str:
        """Return the agent's name."""
        return self._name
    
    @property
    def mandate(self) -> str:
        """Return the agent's mandate."""
        return self._mandate
    
    @property
    def category(self) -> AgentCategory:
        """Return the agent's category (domain or executive)."""
        return self._category
    
    @property
    def agent_type(self) -> str:
        """Return a string identifier for the agent type."""
        return f"{self.category.value}_{self.role.value}"
    
    def _determine_category(self) -> AgentCategory:
        """Determine the agent's category based on role."""
        executive_roles = {
            AgentRole.CEO, AgentRole.CFO, AgentRole.COO,
            AgentRole.CSO, AgentRole.CRO, AgentRole.CKO, AgentRole.CPO
        }
        if self._role in executive_roles:
            return AgentCategory.EXECUTIVE
        return AgentCategory.DOMAIN
    
    def _default_name(self) -> str:
        """Generate default name based on role."""
        role_names = {
            AgentRole.STRATEGY: "Strategy Agent",
            AgentRole.FINANCE: "Finance Agent",
            AgentRole.RISK: "Risk Agent",
            AgentRole.HEALTH: "Health Agent",
            AgentRole.OPERATIONS: "Operations Agent",
            AgentRole.LEGACY: "Legacy Agent",
            AgentRole.CEO: "CEO Agent",
            AgentRole.CFO: "CFO Agent",
            AgentRole.COO: "COO Agent",
            AgentRole.CSO: "CSO Agent",
            AgentRole.CRO: "CRO Agent",
            AgentRole.CKO: "CKO Agent",
            AgentRole.CPO: "CPO Agent",
        }
        return role_names.get(self._role, "Unknown Agent")
    
    def _default_mandate(self) -> str:
        """Generate default mandate based on role."""
        mandates = {
            AgentRole.STRATEGY: "Long-range direction, leverage, timing, sequencing, opportunity framing",
            AgentRole.FINANCE: "Resource allocation, capital protection, accumulation logic, opportunity cost, resilience",
            AgentRole.RISK: "Risk identification, assessment, mitigation strategies, and monitoring",
            AgentRole.HEALTH: "Health optimization, performance management, wellbeing strategies",
            AgentRole.OPERATIONS: "Operational feasibility, execution planning, process optimization",
            AgentRole.LEGACY: "Legacy alignment, doctrine consistency, strategic continuity",
            AgentRole.CEO: "Strategic leadership, council orchestration, final decision authority",
            AgentRole.CFO: "Financial impact evaluation, capital allocation, investment decisions",
            AgentRole.COO: "Operational feasibility assessment, execution planning",
            AgentRole.CSO: "Long-term strategic planning, opportunity identification, market positioning",
            AgentRole.CRO: "Risk management, threat assessment, mitigation strategies",
            AgentRole.CKO: "Knowledge management, doctrine alignment, institutional memory",
            AgentRole.CPO: "System capability improvement, product strategy, innovation",
        }
        return mandates.get(self._role, "Provide strategic guidance")
    
    @abstractmethod
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the given context and return results.
        
        This is the main method that all agents must implement.
        
        Args:
            context: Dictionary containing analysis context
            
        Returns:
            Dictionary containing analysis results
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent metadata.
        
        Returns:
            Dictionary containing agent information
        """
        return {
            "role": self.role.value,
            "name": self.name,
            "mandate": self.mandate,
            "category": self.category.value,
            "agent_type": self.agent_type,
        }
    
    def log_info(self, message: str) -> None:
        """Log an info message with agent context."""
        logger.info(f"[{self.name}] {message}")
    
    def log_warning(self, message: str) -> None:
        """Log a warning message with agent context."""
        logger.warning(f"[{self.name}] {message}")
    
    def log_error(self, message: str) -> None:
        """Log an error message with agent context."""
        logger.error(f"[{self.name}] {message}")
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(role={self.role.value}, name='{self.name}')>"


class DomainAgent(BaseAgent):
    """Base class for domain expert agents.
    
    Domain agents provide specialized advisory analysis within specific domains
    such as finance, health, operations, etc. They focus on "What should we consider?"
    """
    
    def __init__(self, role: AgentRole, mandate: Optional[str] = None):
        super().__init__(role, mandate=mandate)
        if self.category != AgentCategory.DOMAIN:
            raise ValueError(f"DomainAgent requires a domain role, got {role}")


class ExecutiveAgent(BaseAgent):
    """Base class for executive governance agents.
    
    Executive agents provide strategic oversight and decision authority.
    They focus on "What should we decide?" and participate in governance cycles.
    """
    
    def __init__(self, role: AgentRole, mandate: Optional[str] = None):
        super().__init__(role, mandate=mandate)
        if self.category != AgentCategory.EXECUTIVE:
            raise ValueError(f"ExecutiveAgent requires an executive role, got {role}")
