"""Access Policy - Agent access governance for the data platform.

Defines policies controlling which agents can access which sources.
"""
from typing import List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    """Agent roles for access control."""
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


class AccessPolicy(BaseModel):
    """Access policy for an agent."""
    policy_id: str = Field(..., description="Unique policy identifier")
    agent_id: Optional[str] = Field(None, description="Specific agent ID (optional)")
    agent_role: AgentRole = Field(..., description="Agent role")
    allowed_domains: List[str] = Field(default_factory=list, description="Allowed domains")
    allowed_sources: List[str] = Field(default_factory=list, description="Allowed source IDs")
    blocked_sources: List[str] = Field(default_factory=list, description="Blocked source IDs")
    trust_tier_minimum: str = Field("MEDIUM", description="Minimum trust tier")
    max_results_per_query: int = Field(50, description="Maximum results per query")
    freshness_requirements_hours: Optional[int] = Field(None, description="Max age of data in hours")
    blocked_source_types: List[str] = Field(default_factory=list, description="Blocked source types")
    enabled: bool = Field(True, description="Policy enabled")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Default access policies
DEFAULT_POLICIES = [
    # Finance Agent
    AccessPolicy(
        policy_id="policy_finance_agent",
        agent_role=AgentRole.FINANCE,
        allowed_domains=["finance"],
        trust_tier_minimum="MEDIUM",
        max_results_per_query=20,
    ),
    # Health Agent
    AccessPolicy(
        policy_id="policy_health_agent",
        agent_role=AgentRole.HEALTH,
        allowed_domains=["health"],
        trust_tier_minimum="MEDIUM",
        max_results_per_query=20,
    ),
    # Fitness Agent
    AccessPolicy(
        policy_id="policy_fitness_agent",
        agent_role=AgentRole.FITNESS,
        allowed_domains=["fitness"],
        trust_tier_minimum="MEDIUM",
        max_results_per_query=20,
    ),
    # Operations Agent
    AccessPolicy(
        policy_id="policy_operations_agent",
        agent_role=AgentRole.OPERATIONS,
        allowed_domains=["operations"],
        trust_tier_minimum="MEDIUM",
        max_results_per_query=30,
    ),
    # Strategy Agent - can access multiple domains
    AccessPolicy(
        policy_id="policy_strategy_agent",
        agent_role=AgentRole.STRATEGY,
        allowed_domains=["strategy", "finance", "operations", "risk"],
        trust_tier_minimum="MEDIUM",
        max_results_per_query=50,
        freshness_requirements_hours=168,  # 1 week
    ),
    # Risk Agent - can access multiple domains
    AccessPolicy(
        policy_id="policy_risk_agent",
        agent_role=AgentRole.RISK,
        allowed_domains=["risk", "finance", "operations"],
        trust_tier_minimum="HIGH",
        max_results_per_query=30,
        freshness_requirements_hours=24,  # 1 day
    ),
    # Executive Agents - full access
    AccessPolicy(
        policy_id="policy_executive",
        agent_role=AgentRole.EXECUTIVE,
        allowed_domains=["strategy", "finance", "health", "fitness", "operations", "risk"],
        trust_tier_minimum="MEDIUM",
        max_results_per_query=100,
    ),
    # Governance - high trust only
    AccessPolicy(
        policy_id="policy_governance",
        agent_role=AgentRole.GOVERNANCE,
        allowed_domains=["strategy", "risk", "operations"],
        trust_tier_minimum="HIGH",
        max_results_per_query=50,
    ),
    # Intelligence - can access most sources
    AccessPolicy(
        policy_id="policy_intelligence",
        agent_role=AgentRole.INTELLIGENCE,
        allowed_domains=["finance", "health", "strategy", "risk"],
        trust_tier_minimum="LOW",
        max_results_per_query=50,
    ),
    # Planning - strategy and operations focus
    AccessPolicy(
        policy_id="policy_planning",
        agent_role=AgentRole.PLANNING,
        allowed_domains=["strategy", "operations"],
        trust_tier_minimum="MEDIUM",
        max_results_per_query=30,
    ),
    # Execution - limited access
    AccessPolicy(
        policy_id="policy_execution",
        agent_role=AgentRole.EXECUTION,
        allowed_domains=["operations"],
        trust_tier_minimum="HIGH",
        max_results_per_query=10,
        blocked_source_types=["web"],
    ),
    # Learning - can access all for evaluation
    AccessPolicy(
        policy_id="policy_learning",
        agent_role=AgentRole.LEARNING,
        allowed_domains=["strategy", "finance", "health", "fitness", "operations", "risk"],
        trust_tier_minimum="UNVERIFIED",
        max_results_per_query=100,
    ),
]


class AccessPolicyManager:
    """Manages access policies for agents."""
    
    def __init__(self):
        self._policies: dict[str, AccessPolicy] = {}
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        """Initialize with default policies."""
        for policy in DEFAULT_POLICIES:
            self._policies[policy.policy_id] = policy
    
    async def get_policy(self, agent_role: AgentRole) -> Optional[AccessPolicy]:
        """Get policy for an agent role."""
        policy_id = f"policy_{agent_role.value}"
        return self._policies.get(policy_id)
    
    async def check_access(
        self,
        agent_role: AgentRole,
        source_domain: str,
        source_id: str,
        trust_tier: str,
    ) -> tuple[bool, str]:
        """Check if agent has access to a source.
        
        Returns:
            (allowed, reason)
        """
        policy = await self.get_policy(agent_role)
        
        if not policy:
            return False, f"No policy found for role: {agent_role}"
        
        if not policy.enabled:
            return False, f"Policy disabled for role: {agent_role}"
        
        # Check blocked sources
        if source_id in policy.blocked_sources:
            return False, f"Source {source_id} is blocked"
        
        # Check allowed sources (if specified)
        if policy.allowed_sources and source_id not in policy.allowed_sources:
            return False, f"Source {source_id} not in allowed list"
        
        # Check domain
        if policy.allowed_domains and source_domain not in policy.allowed_domains:
            return False, f"Domain {source_domain} not in allowed domains"
        
        # Check trust tier
        trust_tiers = ["UNVERIFIED", "LOW", "MEDIUM", "HIGH"]
        min_idx = trust_tiers.index(policy.trust_tier_minimum)
        source_idx = trust_tiers.index(trust_tier) if trust_tier in trust_tiers else 0
        
        if source_idx < min_idx:
            return False, f"Trust tier {trust_tier} below minimum {policy.trust_tier_minimum}"
        
        return True, "Access granted"
    
    async def add_policy(self, policy: AccessPolicy) -> None:
        """Add or update a policy."""
        self._policies[policy.policy_id] = policy
    
    async def remove_policy(self, policy_id: str) -> bool:
        """Remove a policy."""
        if policy_id in self._policies:
            del self._policies[policy_id]
            return True
        return False


# Singleton
_policy_manager: Optional[AccessPolicyManager] = None


def get_access_policy_manager() -> AccessPolicyManager:
    """Get the access policy manager singleton."""
    global _policy_manager
    if _policy_manager is None:
        _policy_manager = AccessPolicyManager()
    return _policy_manager
