"""Fitness Toolkit - Domain toolkit for fitness data retrieval.

Provides fitness-specific retrieval capabilities through the RetrievalGateway.
"""
from typing import Any, Dict, List, Optional
import logging

from app.agents.toolkits.base import RetrievalToolkit
from app.agents.toolkits.registry import register_domain_toolkit
from app.data_platform.models import RetrievalRequest, AgentType, TrustTier

logger = logging.getLogger(__name__)


@register_domain_toolkit(
    domain="fitness",
    capabilities=["retrieve_structured", "retrieve_documents", "retrieve_latest"],
    roles=["fitness"]
)
class FitnessToolkit(RetrievalToolkit):
    """Toolkit for fitness domain data retrieval."""
    
    @property
    def toolkit_id(self) -> str:
        return "fitness_toolkit"
    
    @property
    def domain(self) -> str:
        return "fitness"
    
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
        """Search fitness structured data.
        
        Examples:
            - Exercise records
            - Workout templates
            - Activity data
        """
        logger.info(f"Fitness toolkit: searching structured data for: {query}")
        
        if not self.retrieval_gateway:
            return []
        
        request = RetrievalRequest(
            query=query,
            agent_type=AgentType.DOMAIN,
            agent_domain="fitness",
            domains=["fitness"],
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
        """Search fitness documents.
        
        Examples:
            - Exercise guides
            - Training plans
            - Fitness advice
        """
        logger.info(f"Fitness toolkit: searching documents for: {query}")
        
        if not self.retrieval_gateway:
            return []
        
        request = RetrievalRequest(
            query=query,
            agent_type=AgentType.DOMAIN,
            agent_domain="fitness",
            domains=["fitness"],
            trust_tiers=[TrustTier.HIGH, TrustTier.MEDIUM],
            max_results=limit,
            include_documents=True,
        )
        
        response = await self.retrieval_gateway.search(request)
        return [e.dict() for e in response.evidence]
    
    async def get_latest(
        self,
        domain: str = "fitness",
        since: Optional[Any] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get latest fitness data."""
        logger.info(f"Fitness toolkit: getting latest for domain: {domain}")
        return []
    
    async def summarize_evidence(
        self,
        evidence_ids: List[str],
        summary_type: str = "brief",
    ) -> str:
        """Summarize fitness evidence."""
        logger.info(f"Fitness toolkit: summarizing {len(evidence_ids)} items")
        return f"Fitness summary ({summary_type}) of {len(evidence_ids)} items"


async def get_fitness_toolkit(agent_id: str, agent_role: str, retrieval_gateway=None) -> FitnessToolkit:
    """Get a fitness toolkit instance."""
    toolkit = FitnessToolkit(agent_id, agent_role, retrieval_gateway)
    await toolkit.initialize()
    return toolkit
