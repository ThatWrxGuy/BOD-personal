"""Toolkit Resolver - Resolves and injects toolkits based on agent profile and policy.

The resolver:
1. Reads agent profile
2. Selects matching toolkits based on domains and capabilities
3. Filters by access policy
4. Injects initialized toolkits into the agent
"""
from typing import Dict, List, Optional, Any
import logging

from app.agents.toolkits.agent_profile import AgentProfile, AgentRole, AgentCapability, get_agent_profile_manager
from app.agents.toolkits.base import BaseToolkit, RetrievalToolkit
from app.agents.toolkits.registry import get_toolkit_registry
from app.data_platform.governance.access_policy import get_access_policy_manager, AgentRole as PolicyAgentRole

logger = logging.getLogger(__name__)


class ToolkitResolver:
    """Resolves and manages toolkits for agents based on profile and policy."""
    
    def __init__(self):
        self.profile_manager = get_agent_profile_manager()
        self.toolkit_registry = get_toolkit_registry()
        self.policy_manager = get_access_policy_manager()
    
    async def resolve_toolkits_for_agent(
        self,
        agent_id: str,
        retrieval_gateway=None,
    ) -> Dict[str, BaseToolkit]:
        """Resolve and return toolkits for an agent.
        
        Args:
            agent_id: Agent identifier
            retrieval_gateway: Gateway for data retrieval
            
        Returns:
            Dictionary of toolkit_id -> toolkit instance
        """
        # Get agent profile
        profile = self.profile_manager.get_profile(agent_id)
        
        if not profile:
            logger.warning(f"No profile found for agent: {agent_id}, using default")
            profile = self.profile_manager.get_profile_by_role(AgentRole.INTELLIGENCE)
        
        if not profile:
            logger.error(f"Cannot resolve toolkits: no profile available for agent: {agent_id}")
            return {}
        
        return await self.resolve_toolkits_from_profile(
            profile=profile,
            retrieval_gateway=retrieval_gateway,
        )
    
    async def resolve_toolkits_from_profile(
        self,
        profile: AgentProfile,
        retrieval_gateway=None,
    ) -> Dict[str, BaseToolkit]:
        """Resolve toolkits based on agent profile.
        
        Args:
            profile: Agent profile
            retrieval_gateway: Gateway for data retrieval
            
        Returns:
            Dictionary of toolkit_id -> toolkit instance
        """
        toolkits: Dict[str, BaseToolkit] = {}
        
        # Map agent role to policy role
        policy_role = self._map_to_policy_role(profile.agent_role)
        
        # Get allowed domains from policy
        policy = await self.policy_manager.get_policy(policy_role)
        allowed_domains = policy.allowed_domains if policy else [profile.primary_domain]
        
        logger.info(
            f"Resolving toolkits for agent: {profile.agent_id}, "
            f"role: {profile.agent_role}, domains: {allowed_domains}"
        )
        
        # Resolve toolkits based on capabilities
        if AgentCapability.RETRIEVE_STRUCTURED in profile.capabilities:
            toolkit = await self._create_domain_toolkit(
                domain=profile.primary_domain,
                agent_id=profile.agent_id,
                agent_role=profile.agent_role.value,
                retrieval_gateway=retrieval_gateway,
            )
            if toolkit:
                toolkits[toolkit.toolkit_id] = toolkit
        
        # Add secondary domain toolkits
        for domain in profile.secondary_domains:
            if domain in allowed_domains:
                toolkit = await self._create_domain_toolkit(
                    domain=domain,
                    agent_id=profile.agent_id,
                    agent_role=profile.agent_role.value,
                    retrieval_gateway=retrieval_gateway,
                )
                if toolkit and toolkit.toolkit_id not in toolkits:
                    toolkits[toolkit.toolkit_id] = toolkit
        
        # Add federated toolkit for strategy/risk agents
        if AgentCapability.RETRIEVE_FEDERATED in profile.capabilities:
            federated_toolkit = await self._create_federated_toolkit(
                agent_id=profile.agent_id,
                agent_role=profile.agent_role.value,
                retrieval_gateway=retrieval_gateway,
            )
            if federated_toolkit:
                toolkits[federated_toolkit.toolkit_id] = federated_toolkit
        
        # Check policy enforcement - filter out unauthorized toolkits
        toolkits = await self._filter_by_policy(
            toolkits=toolkits,
            profile=profile,
            policy_role=policy_role,
        )
        
        logger.info(
            f"Resolved {len(toolkits)} toolkits for agent: {profile.agent_id}"
        )
        
        return toolkits
    
    async def _create_domain_toolkit(
        self,
        domain: str,
        agent_id: str,
        agent_role: str,
        retrieval_gateway=None,
    ) -> Optional[BaseToolkit]:
        """Create a domain-specific toolkit."""
        # Get toolkit class from registry
        toolkit_class = self.toolkit_registry.get_toolkit_for_domain(domain)
        
        if not toolkit_class:
            logger.debug(f"No toolkit registered for domain: {domain}")
            return None
        
        # Create toolkit instance
        toolkit = toolkit_class(
            agent_id=agent_id,
            agent_role=agent_role,
            retrieval_gateway=retrieval_gateway,
        )
        
        # Initialize
        await toolkit.initialize()
        
        return toolkit
    
    async def _create_federated_toolkit(
        self,
        agent_id: str,
        agent_role: str,
        retrieval_gateway=None,
    ) -> Optional[BaseToolkit]:
        """Create a federated retrieval toolkit."""
        # Import federated toolkit here to avoid circular imports
        try:
            from app.agents.toolkits.federated import FederatedRetrievalToolkit
            
            toolkit = FederatedRetrievalToolkit(
                agent_id=agent_id,
                agent_role=agent_role,
                retrieval_gateway=retrieval_gateway,
            )
            
            await toolkit.initialize()
            return toolkit
            
        except ImportError:
            logger.warning("FederatedRetrievalToolkit not found")
            return None
    
    async def _filter_by_policy(
        self,
        toolkits: Dict[str, BaseToolkit],
        profile: AgentProfile,
        policy_role: PolicyAgentRole,
    ) -> Dict[str, BaseToolkit]:
        """Filter toolkits based on access policy."""
        filtered: Dict[str, BaseToolkit] = {}
        
        for toolkit_id, toolkit in toolkits.items():
            # Check if domain is allowed by policy
            policy = await self.policy_manager.get_policy(policy_role)
            
            if not policy:
                # No policy = allow all
                filtered[toolkit_id] = toolkit
                continue
            
            # Check domain access
            if toolkit.domain not in policy.allowed_domains and policy.allowed_domains:
                logger.info(
                    f"Blocking toolkit {toolkit_id}: domain {toolkit.domain} "
                    f"not in allowed domains {policy.allowed_domains}"
                )
                continue
            
            # Check trust tier
            if profile.trust_tier_required.value < policy.trust_tier_minimum:
                logger.info(
                    f"Blocking toolkit {toolkit_id}: trust tier "
                    f"{profile.trust_tier_required} below minimum {policy.trust_tier_minimum}"
                )
                continue
            
            filtered[toolkit_id] = toolkit
        
        return filtered
    
    def _map_to_policy_role(self, agent_role: AgentRole) -> PolicyAgentRole:
        """Map agent role to policy role."""
        # Map agent role to access policy role
        role_mapping = {
            AgentRole.STRATEGY: PolicyAgentRole.STRATEGY,
            AgentRole.FINANCE: PolicyAgentRole.FINANCE,
            AgentRole.HEALTH: PolicyAgentRole.HEALTH,
            AgentRole.FITNESS: PolicyAgentRole.FITNESS,
            AgentRole.OPERATIONS: PolicyAgentRole.OPERATIONS,
            AgentRole.RISK: PolicyAgentRole.RISK,
            AgentRole.EXECUTIVE: PolicyAgentRole.EXECUTIVE,
            AgentRole.GOVERNANCE: PolicyAgentRole.GOVERNANCE,
            AgentRole.INTELLIGENCE: PolicyAgentRole.INTELLIGENCE,
            AgentRole.PLANNING: PolicyAgentRole.PLANNING,
            AgentRole.EXECUTION: PolicyAgentRole.EXECUTION,
            AgentRole.LEARNING: PolicyAgentRole.LEARNING,
        }
        
        return role_mapping.get(agent_role, PolicyAgentRole.INTELLIGENCE)


# Singleton
_resolver: Optional[ToolkitResolver] = None


def get_toolkit_resolver() -> ToolkitResolver:
    """Get the toolkit resolver singleton."""
    global _resolver
    if _resolver is None:
        _resolver = ToolkitResolver()
    return _resolver
