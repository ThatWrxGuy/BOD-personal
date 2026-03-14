"""Agent Data Platform - Unified data access for all agents.

The data platform provides a shared infrastructure for agents to access
structured data, documents, and semantic search through a controlled gateway.

Components:
- governance/   : Source registry and access control
- storage/      : Structured, document, and vector storage
- retrieval/    : Retrieval gateway for unified access
- ingestion/    : Data ingestion coordination

Usage:
    from app.data_platform import get_retrieval_gateway
    
    gateway = await get_retrieval_gateway(session)
    response = await gateway.search(request)
"""
from app.data_platform.models import (
    # Enums
    SourceType,
    TrustTier,
    AgentType,
    # Models
    SourceRecord,
    StructuredRecord,
    DocumentRecord,
    RetrievedEvidence,
    RetrievalRequest,
    RetrievalResponse,
    StructuredDataSearchRequest,
    DocumentSearchRequest,
    LatestUpdatesRequest,
    EvidenceSummaryRequest,
)
from app.data_platform.retrieval.retrieval_gateway import (
    RetrievalGateway,
    get_retrieval_gateway,
)
from app.data_platform.governance.source_registry import (
    SourceRegistry,
    get_source_registry,
)

__all__ = [
    # Enums
    "SourceType",
    "TrustTier",
    "AgentType",
    # Models
    "SourceRecord",
    "StructuredRecord",
    "DocumentRecord",
    "RetrievedEvidence",
    "RetrievalRequest",
    "RetrievalResponse",
    "StructuredDataSearchRequest",
    "DocumentSearchRequest",
    "LatestUpdatesRequest",
    "EvidenceSummaryRequest",
    # Components
    "RetrievalGateway",
    "get_retrieval_gateway",
    "SourceRegistry",
    "get_source_registry",
]
