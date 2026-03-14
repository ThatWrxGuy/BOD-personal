"""Retrieval Gateway - Unified access point for the data platform.

All agents must use this gateway to access data instead of directly
accessing sources. This ensures consistent access control, audit logging,
and proper governance.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import time
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.data_platform.models import (
    RetrievalRequest,
    RetrievalResponse,
    RetrievedEvidence,
    StructuredDataSearchRequest,
    DocumentSearchRequest,
    LatestUpdatesRequest,
    EvidenceSummaryRequest,
    AgentType,
    TrustTier,
)
from app.data_platform.governance.source_registry import get_source_registry
from app.data_platform.storage.structured_store import get_structured_data_store
from app.data_platform.storage.document_store import get_document_store
from app.data_platform.storage.vector_index import get_vector_index_service

logger = logging.getLogger(__name__)


class RetrievalGateway:
    """Unified retrieval gateway for all agent data access.
    
    This gateway provides:
    - Single entry point for all data retrieval
    - Domain-based access control
    - Trust tier filtering
    - Audit logging
    - Rate limiting (future)
    """
    
    def __init__(self, session: AsyncSession):
        """Initialize the retrieval gateway."""
        self.session = session
        self.source_registry = get_source_registry()
        self.structured_store = None
        self.document_store = None
        self.vector_index = None
    
    async def _ensure_initialized(self):
        """Lazy initialization of dependencies."""
        if self.structured_store is None:
            self.structured_store = await get_structured_data_store(self.session)
        if self.document_store is None:
            self.document_store = await get_document_store(self.session)
        if self.vector_index is None:
            self.vector_index = await get_vector_index_service(self.session)
    
    async def search(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResponse:
        """Execute a retrieval request.
        
        This is the main entry point for all retrieval operations.
        
        Args:
            request: Retrieval request with query and filters
            
        Returns:
            Retrieval response with evidence
        """
        await self._ensure_initialized()
        
        start_time = time.time()
        
        # Log the request
        logger.info(
            f"Retrieval request: query='{request.query}', "
            f"agent_type={request.agent_type}, domains={request.domains}"
        )
        
        # Get accessible sources for this agent
        sources = await self.source_registry.get_sources_for_agent(
            agent_type=request.agent_type.value if request.agent_type else "domain",
            agent_domain=request.agent_domain,
            trust_tiers=request.trust_tiers,
        )
        
        if not sources:
            logger.warning(f"No sources available for agent type: {request.agent_type}")
            return RetrievalResponse(
                request_id=request.request_id,
                query=request.query,
                evidence=[],
                total_results=0,
                domains_covered=[],
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        
        # Collect evidence from various sources
        evidence: List[RetrievedEvidence] = []
        domains_covered: set = set()
        
        # Search vector index (semantic search)
        if request.include_documents or request.include_web:
            vector_results = await self.vector_index.search(
                query=request.query,
                domains=request.domains or [s.domain for s in sources],
                trust_tiers=request.trust_tiers,
                source_ids=[s.source_id for s in sources],
                limit=request.max_results,
                min_score=request.min_relevance,
            )
            evidence.extend(vector_results)
            for e in vector_results:
                domains_covered.add(e.domain)
        
        # Search structured data
        if request.include_structured:
            structured_request = StructuredDataSearchRequest(
                query=request.query,
                domain=request.domains[0] if request.domains else None,
            )
            structured_results = await self.structured_store.search(structured_request)
            # Convert to evidence format
            for record in structured_results[:request.max_results]:
                evidence.append(RetrievedEvidence(
                    source_id=record.source_id,
                    source_name=record.source_id,
                    domain=record.domain,
                    evidence_type="structured",
                    content=str(record.content),
                    relevance_score=0.8,  # Placeholder
                    timestamp=record.timestamp,
                ))
                domains_covered.add(record.domain)
        
        # Sort by relevance and limit
        evidence.sort(key=lambda e: e.relevance_score, reverse=True)
        evidence = evidence[:request.max_results]
        
        execution_time = (time.time() - start_time) * 1000
        
        logger.info(
            f"Retrieval complete: {len(evidence)} results in {execution_time:.2f}ms"
        )
        
        return RetrievalResponse(
            request_id=request.request_id,
            query=request.query,
            evidence=evidence,
            total_results=len(evidence),
            domains_covered=list(domains_covered),
            execution_time_ms=execution_time,
        )
    
    async def search_structured_data(
        self,
        request: StructuredDataSearchRequest,
    ) -> List[Dict[str, Any]]:
        """Search structured data sources.
        
        Args:
            request: Search parameters
            
        Returns:
            List of structured records
        """
        await self._ensure_initialized()
        
        results = await self.structured_store.search(request)
        return [r.dict() for r in results]
    
    async def search_documents(
        self,
        request: DocumentSearchRequest,
    ) -> List[RetrievedEvidence]:
        """Search document sources.
        
        Args:
            request: Search parameters
            
        Returns:
            List of retrieved documents
        """
        await self._ensure_initialized()
        
        results = await self.document_store.search(request)
        
        # Convert to evidence format
        evidence = []
        for doc in results:
            evidence.append(RetrievedEvidence(
                source_id=doc.source_id,
                source_name=doc.title,
                domain=doc.domain,
                evidence_type="document",
                content=doc.content,
                relevance_score=0.8,
                timestamp=doc.updated_at,
            ))
        
        return evidence
    
    async def get_latest_updates(
        self,
        request: LatestUpdatesRequest,
    ) -> List[RetrievedEvidence]:
        """Get latest updates across domains.
        
        Args:
            request: Request parameters
            
        Returns:
            List of latest updates
        """
        await self._ensure_initialized()
        
        evidence = []
        
        # Get latest from structured store
        for domain in request.domains:
            latest_structured = await self.structured_store.get_latest_by_domain(
                domain=domain,
                limit=request.limit,
            )
            for record in latest_structured:
                if record.timestamp >= request.since:
                    evidence.append(RetrievedEvidence(
                        source_id=record.source_id,
                        source_name=record.source_id,
                        domain=record.domain,
                        evidence_type="structured",
                        content=str(record.content),
                        relevance_score=1.0,
                        timestamp=record.timestamp,
                    ))
        
        # Get latest documents
        for domain in request.domains:
            latest_docs = await self.document_store.get_latest_documents(
                domain=domain,
                limit=request.limit,
            )
            for doc in latest_docs:
                if doc.updated_at >= request.since:
                    evidence.append(RetrievedEvidence(
                        source_id=doc.source_id,
                        source_name=doc.title,
                        domain=doc.domain,
                        evidence_type="document",
                        content=doc.content,
                        relevance_score=1.0,
                        timestamp=doc.updated_at,
                    ))
        
        # Sort by timestamp
        evidence.sort(key=lambda e: e.timestamp, reverse=True)
        
        return evidence[:request.limit]
    
    async def summarize_evidence(
        self,
        request: EvidenceSummaryRequest,
    ) -> str:
        """Summarize retrieved evidence.
        
        Args:
            request: Summary request
            
        Returns:
            Summary text
        """
        # In production, this would use an LLM to summarize
        evidence_count = len(request.evidence_ids)
        return f"Summary of {evidence_count} evidence items. (Placeholder)"


# Factory function
async def get_retrieval_gateway(session: AsyncSession) -> RetrievalGateway:
    """Get a retrieval gateway instance."""
    return RetrievalGateway(session)
