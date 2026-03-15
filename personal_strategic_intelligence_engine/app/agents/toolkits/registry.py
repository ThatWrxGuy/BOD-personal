"""Toolkit Registry - Maps domains and capabilities to toolkit classes.

The registry maintains a mapping of:
- Domain -> Toolkit class
- Capability -> Toolkit class
- Agent role -> Default toolkits
"""
from typing import Dict, List, Type, Optional, Any
import logging

from app.agents.toolkits.base import BaseToolkit, RetrievalToolkit, FederatedToolkit

logger = logging.getLogger(__name__)


class ToolkitRegistry:
    """Registry for mapping domains and capabilities to toolkit classes."""
    
    def __init__(self):
        # Domain -> Toolkit class mapping
        self._domain_toolkits: Dict[str, Type[BaseToolkit]] = {}
        
        # Capability -> Toolkit class mapping
        self._capability_toolkits: Dict[str, Type[BaseToolkit]] = {}
        
        # Agent role -> List of toolkit classes
        self._role_toolkits: Dict[str, List[Type[BaseToolkit]]] = {}
        
        # Initialize with registered toolkits
        self._initialize_defaults()
    
    def _initialize_defaults(self):
        """Initialize with default toolkit registrations."""
        # Import toolkits to register them
        # Note: In production, toolkits would be registered via decorator or config
        pass
    
    def register_toolkit(
        self,
        toolkit_class: Type[BaseToolkit],
        domain: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        roles: Optional[List[str]] = None,
    ):
        """Register a toolkit class.
        
        Args:
            toolkit_class: Toolkit class to register
            domain: Domain this toolkit serves
            capabilities: Capabilities this toolkit provides
            roles: Agent roles this toolkit is for
        """
        # Register by domain
        if domain:
            self._domain_toolkits[domain] = toolkit_class
            logger.info(f"Registered toolkit {toolkit_class.__name__} for domain: {domain}")
        
        # Register by capabilities
        if capabilities:
            for cap in capabilities:
                self._capability_toolkits[cap] = toolkit_class
        
        # Register by roles
        if roles:
            for role in roles:
                if role not in self._role_toolkits:
                    self._role_toolkits[role] = []
                self._role_toolkits[role].append(toolkit_class)
    
    def get_toolkit_for_domain(self, domain: str) -> Optional[Type[BaseToolkit]]:
        """Get toolkit class for a domain."""
        return self._domain_toolkits.get(domain)
    
    def get_toolkit_for_capability(self, capability: str) -> Optional[Type[BaseToolkit]]:
        """Get toolkit class for a capability."""
        return self._capability_toolkits.get(capability)
    
    def get_toolkits_for_role(self, role: str) -> List[Type[BaseToolkit]]:
        """Get toolkit classes for an agent role."""
        return self._role_toolkits.get(role, [])
    
    def get_all_domains(self) -> List[str]:
        """Get all registered domains."""
        return list(self._domain_toolkits.keys())
    
    def get_all_capabilities(self) -> List[str]:
        """Get all registered capabilities."""
        return list(self._capability_toolkits.keys())
    
    def get_all_roles(self) -> List[str]:
        """Get all registered roles."""
        return list(self._role_toolkits.keys())


# Global registry instance
_registry: Optional[ToolkitRegistry] = None


def get_toolkit_registry() -> ToolkitRegistry:
    """Get the toolkit registry singleton."""
    global _registry
    if _registry is None:
        _registry = ToolkitRegistry()
    return _registry


def register_domain_toolkit(
    domain: str,
    capabilities: Optional[List[str]] = None,
    roles: Optional[List[str]] = None,
):
    """Decorator to register a toolkit for a domain.
    
    Usage:
        @register_domain_toolkit("finance", capabilities=["retrieve_structured"])
        class FinanceToolkit(RetrievalToolkit):
            ...
    """
    def decorator(toolkit_class: Type[BaseToolkit]) -> Type[BaseToolkit]:
        registry = get_toolkit_registry()
        registry.register_toolkit(
            toolkit_class,
            domain=domain,
            capabilities=capabilities,
            roles=roles,
        )
        return toolkit_class
    return decorator
