"""Common data models for the Agent Data Platform.

These models provide a unified interface for structured data, documents,
and semantic retrieval across all agents.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    """Types of data sources."""
    RELATIONAL = "relational"
    VECTOR = "vector"
    DOCUMENT = "document"
    WEB = "web"
    API = "api"


class TrustTier(str, Enum):
    """Trust tiers for source classification."""
    HIGH = "high"        # Verified, authoritative sources
    MEDIUM = "medium"    # Curated, reliable sources
    LOW = "low"          # Community, less verified
    UNVERIFIED = "unverified"


class AgentType(str, Enum):
    """Agent types for access control."""
    DOMAIN = "domain"
    EXECUTIVE = "executive"
    PLANNING = "planning"
    INTELLIGENCE = "intelligence"
    GOVERNANCE = "governance"
    EXECUTION = "execution"
    LEARNING = "learning"


class SourceRecord(BaseModel):
    """Record of a data source in the platform."""
    source_id: str = Field(..., description="Unique source identifier")
    source_name: str = Field(..., description="Human-readable source name")
    domain: str = Field(..., description="Domain (finance, health, strategy, etc.)")
    source_type: SourceType = Field(..., description="Type of source")
    license: Optional[str] = Field(None, description="License or allowed use")
    trust_tier: TrustTier = Field(TrustTier.MEDIUM, description="Trust classification")
    refresh_interval: int = Field(3600, description="Refresh interval in seconds")
    enabled: bool = Field(True, description="Whether source is enabled")
    agent_access_tags: List[str] = Field(default_factory=list, description="Tags for agent access")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StructuredRecord(BaseModel):
    """Structured data record from relational sources."""
    record_id: UUID = Field(default_factory=uuid4)
    source_id: str = Field(..., description="Source this record belongs to")
    domain: str = Field(..., description="Domain classification")
    data_type: str = Field(..., description="Type of structured data")
    content: Dict[str, Any] = Field(..., description="Structured content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    embedding: Optional[List[float]] = Field(None, description="Vector embedding for semantic search")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentRecord(BaseModel):
    """Document record for file/document storage."""
    document_id: UUID = Field(default_factory=uuid4)
    source_id: str = Field(..., description="Source this document belongs to")
    domain: str = Field(..., description="Domain classification")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document text content")
    file_path: Optional[str] = Field(None, description="Path to source file")
    mime_type: str = Field("text/plain", description="MIME type")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding for semantic search")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RetrievedEvidence(BaseModel):
    """Evidence retrieved from the platform."""
    evidence_id: UUID = Field(default_factory=uuid4)
    source_id: str = Field(..., description="Source of evidence")
    source_name: str = Field(..., description="Human-readable source name")
    domain: str = Field(..., description="Domain classification")
    evidence_type: str = Field(..., description="Type: structured, document, or web")
    content: str = Field(..., description="Evidence content")
    relevance_score: float = Field(..., description="Relevance score (0-1)")
    timestamp: datetime = Field(..., description="Evidence timestamp")
    url: Optional[str] = Field(None, description="Source URL if applicable")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RetrievalRequest(BaseModel):
    """Request for retrieving evidence."""
    request_id: UUID = Field(default_factory=uuid4)
    query: str = Field(..., description="Search query")
    agent_type: Optional[AgentType] = Field(None, description="Requesting agent type")
    agent_domain: Optional[str] = Field(None, description="Requesting agent domain")
    domains: List[str] = Field(default_factory=list, description="Domains to search")
    trust_tiers: List[TrustTier] = Field(default_factory=lambda: [TrustTier.HIGH, TrustTier.MEDIUM])
    source_tags: List[str] = Field(default_factory=list, description="Source tags to filter by")
    max_results: int = Field(10, description="Maximum results to return")
    include_documents: bool = Field(True, description="Include document sources")
    include_structured: bool = Field(True, description="Include structured sources")
    include_web: bool = Field(False, description="Include web sources")
    min_relevance: float = Field(0.5, description="Minimum relevance threshold")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RetrievalResponse(BaseModel):
    """Response containing retrieved evidence."""
    request_id: UUID = Field(..., description="Original request ID")
    query: str = Field(..., description="Original query")
    evidence: List[RetrievedEvidence] = Field(..., description="Retrieved evidence")
    total_results: int = Field(..., description="Total results found")
    domains_covered: List[str] = Field(..., description="Domains covered in results")
    execution_time_ms: float = Field(..., description="Execution time in milliseconds")
    response_timestamp: datetime = Field(default_factory=datetime.utcnow)


class StructuredDataSearchRequest(BaseModel):
    """Request for searching structured data."""
    request_id: UUID = Field(default_factory=uuid4)
    query: str = Field(..., description="Search query")
    domain: Optional[str] = Field(None, description="Domain filter")
    data_types: List[str] = Field(default_factory=list, description="Data types to search")
    date_from: Optional[datetime] = Field(None, description="Filter by date from")
    date_to: Optional[datetime] = Field(None, description="Filter by date to")
    limit: int = Field(100, description="Maximum records to return")


class DocumentSearchRequest(BaseModel):
    """Request for searching documents."""
    request_id: UUID = Field(default_factory=uuid4)
    query: str = Field(..., description="Search query")
    domain: Optional[str] = Field(None, description="Domain filter")
    mime_types: List[str] = Field(default_factory=list, description="MIME type filters")
    date_from: Optional[datetime] = Field(None, description="Filter by date from")
    date_to: Optional[datetime] = Field(None, description="Filter by date to")
    limit: int = Field(50, description="Maximum documents to return")


class LatestUpdatesRequest(BaseModel):
    """Request for getting latest updates."""
    request_id: UUID = Field(default_factory=uuid4)
    domains: List[str] = Field(..., description="Domains to get updates from")
    since: datetime = Field(..., description="Get updates since this time")
    limit: int = Field(100, description="Maximum updates to return")


class EvidenceSummaryRequest(BaseModel):
    """Request for summarizing evidence."""
    request_id: UUID = Field(default_factory=uuid4)
    evidence_ids: List[UUID] = Field(..., description="Evidence IDs to summarize")
    summary_type: str = Field("brief", description="Summary type: brief, detailed, or executive")
