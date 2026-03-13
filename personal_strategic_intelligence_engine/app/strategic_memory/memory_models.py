"""Memory Models.

Defines graph structures for strategic memory.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NodeCategory(str, Enum):
    """Categories of memory nodes."""
    SIGNAL = "signal"
    STATE_CONDITION = "state_condition"
    RECOMMENDATION = "recommendation"
    EXECUTION_INTENT = "execution_intent"
    DOCTRINE_ASSESSMENT = "doctrine_assessment"
    OUTCOME = "outcome"
    DOMAIN = "domain"
    RISK_EVENT = "risk_event"
    OPPORTUNITY_EVENT = "opportunity_event"
    INTERVENTION = "intervention"


class EdgeCategory(str, Enum):
    """Categories of relationships between nodes."""
    CONTRIBUTES_TO = "contributes_to"
    PRECEDES = "precedes"
    ASSOCIATED_WITH = "associated_with"
    LED_TO = "led_to"
    MITIGATED = "mitigated"
    CONTRADICTED_BY = "contradicted_by"
    CO_OCCURS_WITH = "co_occurs_with"
    ESCALATES = "escalates"
    STABILIZES = "stabilizes"
    RESOLVED_BY = "resolved_by"


class ChainStrength(str, Enum):
    """Strength classification for recurring chains."""
    EMERGING = "emerging"
    RECURRING = "recurring"
    ESTABLISHED = "established"


class MemoryNode(BaseModel):
    """Represents a node in the strategic memory graph."""
    node_id: str
    node_type: NodeCategory
    domain: str
    
    # Content
    label: str
    description: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    # Evidence
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    occurrence_count: int = 1
    
    # Source
    source_record_ids: List[str] = Field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemoryEdge(BaseModel):
    """Represents a relationship between nodes."""
    edge_id: str
    source_node_id: str
    target_node_id: str
    relationship: EdgeCategory
    
    # Evidence
    evidence_count: int = 1
    confidence: float = 0.5
    
    # Temporal
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    avg_time_gap_hours: float = 0.0
    
    # Source
    supporting_record_ids: List[str] = Field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StrategicPattern(BaseModel):
    """A reusable pattern of related nodes."""
    pattern_id: str
    name: str
    description: str
    
    # Components
    node_ids: List[str] = Field(default_factory=list)
    edge_ids: List[str] = Field(default_factory=list)
    
    # Evidence
    occurrence_count: int = 1
    success_rate: float = 0.0
    
    # Classification
    domains: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)


class RecurringChain(BaseModel):
    """A multi-step recurring sequence of events."""
    chain_id: str
    name: str
    description: str
    
    # Sequence
    node_sequence: List[str] = Field(default_factory=list)
    edge_sequence: List[str] = Field(default_factory=list)
    
    # Evidence
    repetition_count: int = 1
    chain_strength: ChainStrength = ChainStrength.EMERGING
    
    # Timing
    avg_duration_hours: float = 0.0
    
    # Domains
    domains: List[str] = Field(default_factory=list)


class MemoryQuery(BaseModel):
    """A query against the memory graph."""
    query_id: str
    query_type: str  # "what_follows", "what_precedes", "similar_context", "chain", "intervention"
    
    # Parameters
    node_ids: List[str] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    relationship_types: List[str] = Field(default_factory=list)
    
    # Filters
    min_confidence: float = 0.0
    min_evidence_count: int = 0
    max_results: int = 10


class MemoryQueryResult(BaseModel):
    """Results from a memory query."""
    query_id: str
    results: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    total_results: int = 0
    execution_time_ms: float = 0.0
    
    # Evidence
    evidence_summary: Dict[str, Any] = Field(default_factory=dict)


class MemoryRelationshipEvidence(BaseModel):
    """Evidence supporting a relationship."""
    relationship_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: EdgeCategory
    
    # Evidence details
    record_id: str
    timestamp: datetime
    context: Dict[str, Any] = Field(default_factory=dict)
    
    # Confidence
    confidence: float = 0.5
    evidence_strength: str = "partial"  # "weak", "partial", "strong"


class MemoryGraphSnapshot(BaseModel):
    """A snapshot of the memory graph state."""
    snapshot_id: str
    
    # Counts
    node_count: int = 0
    edge_count: int = 0
    pattern_count: int = 0
    chain_count: int = 0
    
    # Domains
    domains_covered: List[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    record_range_start: Optional[datetime] = None
    record_range_end: Optional[datetime] = None


class MemorySummary(BaseModel):
    """Summary of the memory graph."""
    total_nodes: int = 0
    total_edges: int = 0
    total_patterns: int = 0
    total_chains: int = 0
    
    # Node breakdown
    nodes_by_category: Dict[str, int] = Field(default_factory=dict)
    nodes_by_domain: Dict[str, int] = Field(default_factory=dict)
    
    # Edge breakdown
    edges_by_relationship: Dict[str, int] = Field(default_factory=dict)
    
    # Chain info
    established_chains: int = 0
    recurring_chains: int = 0
    emerging_chains: int = 0
    
    # Top patterns
    top_patterns: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Generated at
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# Safety constants
LIVE_EXECUTION_ENABLED = False
MEMORY_MODE = "read_only"
