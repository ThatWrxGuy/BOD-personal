"""Base Toolkit Interface - Abstract base classes for agent toolkits.

All domain toolkits should inherit from these base classes.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseToolkit(ABC):
    """Abstract base class for agent toolkits.
    
    Toolkits provide domain-specific capabilities to agents.
    """
    
    def __init__(self, agent_id: str, agent_role: str):
        """Initialize toolkit.
        
        Args:
            agent_id: ID of the agent using this toolkit
            agent_role: Role of the agent using this toolkit
        """
        self.agent_id = agent_id
        self.agent_role = agent_role
        self._initialized = False
    
    @property
    @abstractmethod
    def toolkit_id(self) -> str:
        """Return unique toolkit identifier."""
        pass
    
    @property
    @abstractmethod
    def domain(self) -> str:
        """Return the domain this toolkit serves."""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """Return list of capabilities this toolkit provides."""
        pass
    
    async def initialize(self) -> bool:
        """Initialize the toolkit.
        
        Returns:
            True if initialization successful
        """
        if self._initialized:
            return True
        
        logger.info(f"Initializing toolkit: {self.toolkit_id} for agent: {self.agent_id}")
        self._initialized = True
        return True
    
    async def cleanup(self):
        """Clean up toolkit resources."""
        logger.info(f"Cleaning up toolkit: {self.toolkit_id}")
        self._initialized = False
    
    def get_info(self) -> Dict[str, Any]:
        """Get toolkit information."""
        return {
            "toolkit_id": self.toolkit_id,
            "domain": self.domain,
            "capabilities": self.capabilities,
            "agent_id": self.agent_id,
            "initialized": self._initialized,
        }


class RetrievalToolkit(BaseToolkit):
    """Base class for retrieval toolkits.
    
    Provides structured and document retrieval capabilities.
    """
    
    def __init__(self, agent_id: str, agent_role: str, retrieval_gateway=None):
        """Initialize retrieval toolkit.
        
        Args:
            agent_id: ID of the agent using this toolkit
            agent_role: Role of the agent using this toolkit
            retrieval_gateway: Gateway for data retrieval
        """
        super().__init__(agent_id, agent_role)
        self.retrieval_gateway = retrieval_gateway
    
    async def search_structured(
        self,
        query: str,
        domain: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search structured data.
        
        Args:
            query: Search query
            domain: Domain to search
            filters: Additional filters
            limit: Maximum results
            
        Returns:
            List of structured records
        """
        raise NotImplementedError("Subclass must implement search_structured")
    
    async def search_documents(
        self,
        query: str,
        domain: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search documents.
        
        Args:
            query: Search query
            domain: Domain to search
            filters: Additional filters
            limit: Maximum results
            
        Returns:
            List of documents
        """
        raise NotImplementedError("Subclass must implement search_documents")
    
    async def get_latest(
        self,
        domain: str,
        since: Optional[datetime] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get latest updates for a domain.
        
        Args:
            domain: Domain to get updates for
            since: Get updates since this time
            limit: Maximum results
            
        Returns:
            List of latest updates
        """
        raise NotImplementedError("Subclass must implement get_latest")
    
    async def summarize_evidence(
        self,
        evidence_ids: List[str],
        summary_type: str = "brief",
    ) -> str:
        """Summarize evidence.
        
        Args:
            evidence_ids: IDs of evidence to summarize
            summary_type: Type of summary (brief, detailed, executive)
            
        Returns:
            Summary text
        """
        raise NotImplementedError("Subclass must implement summarize_evidence")


class FederatedToolkit(RetrievalToolkit):
    """Base class for federated retrieval toolkits.
    
    Used by Strategy and Risk agents for cross-domain search.
    """
    
    @abstractmethod
    async def search_cross_domain(
        self,
        query: str,
        domains: List[str],
        limit_per_domain: int = 5,
    ) -> Dict[str, Any]:
        """Search across multiple domains.
        
        Args:
            query: Search query
            domains: List of domains to search
            limit_per_domain: Maximum results per domain
            
        Returns:
            Dictionary with cross-domain results
        """
        pass
    
    @abstractmethod
    async def build_brief(
        self,
        topics: List[str],
        brief_type: str = "strategy",
    ) -> Dict[str, Any]:
        """Build a brief from multiple domains.
        
        Args:
            topics: Topics to include
            brief_type: Type of brief (strategy, risk)
            
        Returns:
            Brief dictionary
        """
        pass
