"""Operations Toolkit - Domain toolkit for operations data retrieval.

Provides operations-specific retrieval capabilities through the RetrievalGateway.
"""
from typing import Any, Dict, List, Optional
import logging

from app.agents.toolkits.base import RetrievalToolkit
from app.agents.toolkits.registry import register_domain_toolkit
from app.data_platform.models import RetrievalRequest, AgentType, TrustTier

logger = logging.getLogger(__name__)


@register_domain_toolkit(
    domain="operations",
    capabilities=["retrieve_structured", "retrieve_documents", "retrieve_latest"],
    roles=["operations", "strategy", "risk", "executive"]
)
class OperationsToolkit(RetrievalToolkit):
    """Toolkit for operations domain data retrieval."""
    
    @property
    def toolkit_id(self) -> str:
        return "operations_toolkit"
    
    @property
    def domain(self) -> str:
        return "operations"
    
    @property
    def capabilities(self) -> List[str]:
        return [
            "retrieve_structured",
            "retrieve_documents",
            "retrieve_latest",
        ]
    
    async def search_structured(
        self,
        query: str,
        domain: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search operations structured data.
        
        Examples:
            - Workflows
            - Tasks
            - Operational metrics
        """
        logger.info(f"Operations toolkit: searching structured data for: {query}")
        
        if not self.retrieval_gateway:
            return []
        
        request = RetrievalRequest(
            query=query,
            agent_type=AgentType.DOMAIN,
            agent_domain="operations",
            domains=["operations"],
            trust_tiers=[TrustTier.HIGH, TrustTier.MEDIUM],
            max_results=limit,
            include_structured=True,
        )
        
        response = await self.retrieval_gateway.search(request)
        return [e.dict() for e in response.evidence]
    
    async def search_documents(
        self,
        query: str,
        domain: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search operations documents.
        
        Examples:
            - SOPs
            - Procedures
            - Operational guides
        """
        logger.info(f"Operations toolkit: searching documents for: {query}")
        
        if not self.retrieval_gateway:
            return []
        
        request = RetrievalRequest(
            query=query,
            agent_type=AgentType.DOMAIN,
            agent_domain="operations",
            domains=["operations"],
            trust_tiers=[TrustTier.HIGH, TrustTier.MEDIUM],
            max_results=limit,
            include_documents=True,
        )
        
        response = await self.retrieval_gateway.search(request)
        return [e.dict() for e in response.evidence]
    
    async def get_latest(
        self,
        domain: str = "operations",
        since: Optional[Any] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get latest operations data."""
        logger.info(f"Operations toolkit: getting latest for domain: {domain}")
        return []
    
    async def summarize_evidence(
        self,
        evidence_ids: List[str],
        summary_type: str = "brief",
    ) -> str:
        """Summarize operations evidence."""
        logger.info(f"Operations toolkit: summarizing {len(evidence_ids)} items")
        return f"Operations summary ({summary_type}) of {len(evidence_ids)} items"


async def get_operations_toolkit(agent_id: str, agent_role: str, retrieval_gateway=None) -> OperationsToolkit:
    """Get an operations toolkit instance."""
    toolkit = OperationsToolkit(agent_id, agent_role, retrieval_gateway)
    await toolkit.initialize()
    return toolkit
