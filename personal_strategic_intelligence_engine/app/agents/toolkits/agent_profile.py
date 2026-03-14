"""Agent Profile - Canonical agent profile model.

Defines agent profiles including role, domains, capabilities, and access requirements.
"""
from typing import List, Optional, Set
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class AgentRole(str, Enum):
    """Agent roles for profile identification."""
    STRATEGY = "strategy"
    FINANCE = "finance"
    HEALTH = "health"
    FITNESS = "fitness"
    OPERATIONS = "operations"
    RISK = "risk"
    EXECUTIVE = "executive"
    GOVERNANCE = "governance"
    INTELLIGENCE = "intelligence"
    PLANNING = "planning"
    EXECUTION = "execution"
    LEARNING = "learning"


class TrustTier(str, Enum):
    """Trust tier requirements."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNVERIFIED = "unverified"


class AgentCapability(str, Enum):
    """Agent capabilities - what the agent can do."""
    # Retrieval capabilities
    RETRIEVE_STRUCTURED = "retrieve_structured"
    RETRIEVE_DOCUMENTS = "retrieve_documents"
    RETRIEVE_LATEST = "retrieve_latest"
    RETRIEVE_SUMMARIZE = "retrieve_summarize"
    RETRIEVE_FEDERATED = "retrieve_federated"
    
    # Analysis capabilities
    ANALYZE_TRENDS = "analyze_trends"
    ANALYZE_RISK = "analyze_risk"
    ANALYZE_OPPORTUNITIES = "analyze_opportunities"
    
    # Execution capabilities
    EXECUTE_ACTION = "execute_action"
    APPROVE_ACTION = "approve_action"


class AgentProfile(BaseModel):
    """Canonical agent profile.
    
    Defines the identity, role, domains, and capabilities of an agent.
    """
    agent_id: str = Field(..., description="Unique agent identifier")
    agent_name: str = Field(..., description="Human-readable agent name")
    agent_role: AgentRole = Field(..., description="Primary agent role")
    
    # Domain focus
    primary_domain: str = Field(..., description="Primary domain (finance, health, etc.)")
    secondary_domains: List[str] = Field(default_factory=list, description="Secondary domains")
    
    # Capabilities
    capabilities: Set[AgentCapability] = Field(
        default_factory=set,
        description="Set of capabilities this agent has"
    )
    
    # Trust requirements
    trust_tier_required: TrustTier = Field(
        TrustTier.MEDIUM,
        description="Minimum trust tier required for data access"
    )
    
    # Action permissions
    allowed_actions: Set[str] = Field(
        default_factory=set,
        description="Allowed action identifiers"
    )
    
    # Metadata
    description: Optional[str] = Field(None, description="Agent description")
    version: str = Field("1.0.0", description="Agent version")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def can_access_domain(self, domain: str) -> bool:
        """Check if agent can access a domain."""
        if domain == self.primary_domain:
            return True
        if domain in self.secondary_domains:
            return True
        return False
    
    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a capability."""
        return capability in self.capabilities


# Default agent profiles
DEFAULT_PROFILES = {
    AgentRole.STRATEGY: AgentProfile(
        agent_id="agent_strategy",
        agent_name="Strategy Agent",
        agent_role=AgentRole.STRATEGY,
        primary_domain="strategy",
        secondary_domains=["finance", "operations", "risk"],
        capabilities={
            AgentCapability.RETRIEVE_STRUCTURED,
            AgentCapability.RETRIEVE_DOCUMENTS,
            AgentCapability.RETRIEVE_LATEST,
            AgentCapability.RETRIEVE_SUMMARIZE,
            AgentCapability.RETRIEVE_FEDERATED,
            AgentCapability.ANALYZE_TRENDS,
            AgentCapability.ANALYZE_OPPORTUNITIES,
        },
        trust_tier_required=TrustTier.MEDIUM,
        allowed_actions={"create_plan", "recommend_strategy"},
    ),
    AgentRole.FINANCE: AgentProfile(
        agent_id="agent_finance",
        agent_name="Finance Agent",
        agent_role=AgentRole.FINANCE,
        primary_domain="finance",
        capabilities={
            AgentCapability.RETRIEVE_STRUCTURED,
            AgentCapability.RETRIEVE_DOCUMENTS,
            AgentCapability.RETRIEVE_LATEST,
            AgentCapability.RETRIEVE_SUMMARIZE,
            AgentCapability.ANALYZE_TRENDS,
        },
        trust_tier_required=TrustTier.MEDIUM,
        allowed_actions={"analyze_financials"},
    ),
    AgentRole.HEALTH: AgentProfile(
        agent_id="agent_health",
        agent_name="Health Agent",
        agent_role=AgentRole.HEALTH,
        primary_domain="health",
        capabilities={
            AgentCapability.RETRIEVE_STRUCTURED,
            AgentCapability.RETRIEVE_DOCUMENTS,
            AgentCapability.RETRIEVE_LATEST,
            AgentCapability.RETRIEVE_SUMMARIZE,
        },
        trust_tier_required=TrustTier.MEDIUM,
        allowed_actions={"analyze_health"},
    ),
    AgentRole.FITNESS: AgentProfile(
        agent_id="agent_fitness",
        agent_name="Fitness Agent",
        agent_role=AgentRole.FITNESS,
        primary_domain="fitness",
        capabilities={
            AgentCapability.RETRIEVE_STRUCTURED,
            AgentCapability.RETRIEVE_DOCUMENTS,
            AgentCapability.RETRIEVE_LATEST,
        },
        trust_tier_required=TrustTier.MEDIUM,
        allowed_actions={"analyze_fitness"},
    ),
    AgentRole.OPERATIONS: AgentProfile(
        agent_id="agent_operations",
        agent_name="Operations Agent",
        agent_role=AgentRole.OPERATIONS,
        primary_domain="operations",
        capabilities={
            AgentCapability.RETRIEVE_STRUCTURED,
            AgentCapability.RETRIEVE_DOCUMENTS,
            AgentCapability.RETRIEVE_LATEST,
            AgentCapability.ANALYZE_TRENDS,
        },
        trust_tier_required=TrustTier.MEDIUM,
        allowed_actions={"analyze_operations"},
    ),
    AgentRole.RISK: AgentProfile(
        agent_id="agent_risk",
        agent_name="Risk Agent",
        agent_role=AgentRole.RISK,
        primary_domain="risk",
        secondary_domains=["finance", "operations"],
        capabilities={
            AgentCapability.RETRIEVE_STRUCTURED,
            AgentCapability.RETRIEVE_DOCUMENTS,
            AgentCapability.RETRIEVE_LATEST,
            AgentCapability.RETRIEVE_SUMMARIZE,
            AgentCapability.RETRIEVE_FEDERATED,
            AgentCapability.ANALYZE_RISK,
        },
        trust_tier_required=TrustTier.HIGH,
        allowed_actions={"assess_risk"},
    ),
    AgentRole.EXECUTIVE: AgentProfile(
        agent_id="agent_executive",
        agent_name="Executive Agent",
        agent_role=AgentRole.EXECUTIVE,
        primary_domain="strategy",
        secondary_domains=["finance", "health", "fitness", "operations", "risk"],
        capabilities={
            AgentCapability.RETRIEVE_STRUCTURED,
            AgentCapability.RETRIEVE_DOCUMENTS,
            AgentCapability.RETRIEVE_LATEST,
            AgentCapability.RETRIEVE_SUMMARIZE,
            AgentCapability.RETRIEVE_FEDERATED,
            AgentCapability.APPROVE_ACTION,
        },
        trust_tier_required=TrustTier.MEDIUM,
        allowed_actions={"approve", "veto", "delegate"},
    ),
}


class AgentProfileManager:
    """Manages agent profiles."""
    
    def __init__(self):
        self._profiles: dict[str, AgentProfile] = {}
        self._initialize_defaults()
    
    def _initialize_defaults(self):
        """Initialize with default profiles."""
        for role, profile in DEFAULT_PROFILES.items():
            self._profiles[profile.agent_id] = profile
    
    def get_profile(self, agent_id: str) -> Optional[AgentProfile]:
        """Get agent profile by ID."""
        return self._profiles.get(agent_id)
    
    def get_profile_by_role(self, role: AgentRole) -> Optional[AgentProfile]:
        """Get profile by role."""
        for profile in self._profiles.values():
            if profile.agent_role == role:
                return profile
        return None
    
    def register_profile(self, profile: AgentProfile):
        """Register a new profile or update existing."""
        self._profiles[profile.agent_id] = profile
    
    def list_profiles(self) -> List[AgentProfile]:
        """List all profiles."""
        return list(self._profiles.values())


# Singleton
_profile_manager: Optional[AgentProfileManager] = None


def get_agent_profile_manager() -> AgentProfileManager:
    """Get agent profile manager singleton."""
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = AgentProfileManager()
    return _profile_manager
