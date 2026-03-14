"""Health Toolkit - Domain toolkit for health/nutrition data retrieval.

Provides health-specific retrieval capabilities through the RetrievalGateway.
"""
from typing import Any, Dict, List, Optional
import logging

from app.agents.toolkits.base import RetrievalToolkit
from app.agents.toolkits.registry import register_domain_toolkit
from app.data_platform.models import RetrievalRequest, AgentType, TrustTier

logger = logging.getLogger(__name__)


@register_domain_toolkit(
    domain="health",
    capabilities=["retrieve_structured", "retrieve_documents", "retrieve_latest"],
    roles=["health", "fitness"]
)
class HealthToolkit(RetrievalToolkit):
    """Toolkit for health domain data retrieval."""
    
    @property
    def toolkit_id(self) -> str:
        return "health_toolkit"
    
    @property
    def domain(self) -> str:
        return "health"
    
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
        """Search health structured data.
        
        Examples:
            - Food nutrition facts
            - Supplement information
            - Health metrics
        """
        logger.info(f"Health toolkit: searching structured data for: {query}")
        
        if not self.retrieval_gateway:
            return []
        
        request = RetrievalRequest(
            query=query,
            agent_type=AgentType.DOMAIN,
            agent_domain="health",
            domains=["health"],
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
        """Search health documents.
        
        Examples:
            - Medical literature
            - Wellness guidance
            - Health reports
        """
        logger.info(f"Health toolkit: searching documents for: {query}")
        
        if not self.retrieval_gateway:
            return []
        
        request = RetrievalRequest(
            query=query,
            agent_type=AgentType.DOMAIN,
            agent_domain="health",
            domains=["health"],
            trust_tiers=[TrustTier.HIGH, TrustTier.MEDIUM],
            max_results=limit,
            include_documents=True,
        )
        
        response = await self.retrieval_gateway.search(request)
        return [e.dict() for e in response.evidence]
    
    async def get_latest(
        self,
        domain: str = "health",
        since: Optional[Any] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get latest health data."""
        logger.info(f"Health toolkit: getting latest for domain: {domain}")
        return []
    
    async def summarize_evidence(
        self,
        evidence_ids: List[str],
        summary_type: str = "brief",
    ) -> str:
        """Summarize health evidence."""
        logger.info(f"Health toolkit: summarizing {len(evidence_ids)} items")
        return f"Health summary ({summary_type}) of {len(evidence_ids)} items"


async def get_health_toolkit(agent_id: str, agent_role: str, retrieval_gateway=None) -> HealthToolkit:
    """Get a health toolkit instance."""
    toolkit = HealthToolkit(agent_id, agent_role, retrieval_gateway)
    await toolkit.initialize()
    return toolkit
