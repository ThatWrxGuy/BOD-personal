"""Finance Toolkit - Domain toolkit for finance data retrieval.

Provides finance-specific retrieval capabilities through the RetrievalGateway.
"""
from typing import Any, Dict, List, Optional
import logging

from app.agents.toolkits.base import RetrievalToolkit
from app.agents.toolkits.registry import register_domain_toolkit
from app.data_platform.models import RetrievalRequest, AgentType, TrustTier

logger = logging.getLogger(__name__)


@register_domain_toolkit(
    domain="finance",
    capabilities=["retrieve_structured", "retrieve_documents", "retrieve_latest", "summarize"],
    roles=["finance", "strategy", "risk", "executive"]
)
class FinanceToolkit(RetrievalToolkit):
    """Toolkit for finance domain data retrieval."""
    
    @property
    def toolkit_id(self) -> str:
        return "finance_toolkit"
    
    @property
    def domain(self) -> str:
        return "finance"
    
    @property
    def capabilities(self) -> List[str]:
        return [
            "retrieve_structured",
            "retrieve_documents",
            "retrieve_latest",
            "summarize",
        ]
    
    async def search_structured(
        self,
        query: str,
        domain: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search finance structured data.
        
        Examples:
            - Stock prices
            - Economic indicators
            - Financial metrics
        """
        logger.info(f"Finance toolkit: searching structured data for: {query}")
        
        if not self.retrieval_gateway:
            return []
        
        request = RetrievalRequest(
            query=query,
            agent_type=AgentType.DOMAIN,
            agent_domain="finance",
            domains=["finance"],
            trust_tiers=[TrustTier.HIGH, TrustTier.MEDIUM],
            max_results=limit,
            include_structured=True,
            include_documents=False,
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
        """Search finance documents.
        
        Examples:
            - Financial reports
            - Market analysis
            - SEC filings
        """
        logger.info(f"Finance toolkit: searching documents for: {query}")
        
        if not self.retrieval_gateway:
            return []
        
        request = RetrievalRequest(
            query=query,
            agent_type=AgentType.DOMAIN,
            agent_domain="finance",
            domains=["finance"],
            trust_tiers=[TrustTier.HIGH, TrustTier.MEDIUM],
            max_results=limit,
            include_structured=False,
            include_documents=True,
        )
        
        response = await self.retrieval_gateway.search(request)
        return [e.dict() for e in response.evidence]
    
    async def get_latest(
        self,
        domain: str = "finance",
        since: Optional[Any] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get latest finance data."""
        logger.info(f"Finance toolkit: getting latest for domain: {domain}")
        return []
    
    async def summarize_evidence(
        self,
        evidence_ids: List[str],
        summary_type: str = "brief",
    ) -> str:
        """Summarize finance evidence."""
        logger.info(f"Finance toolkit: summarizing {len(evidence_ids)} evidence items")
        return f"Finance summary ({summary_type}) of {len(evidence_ids)} items"


async def get_finance_toolkit(agent_id: str, agent_role: str, retrieval_gateway=None) -> FinanceToolkit:
    """Get a finance toolkit instance."""
    toolkit = FinanceToolkit(agent_id, agent_role, retrieval_gateway)
    await toolkit.initialize()
    return toolkit
