# Agent Data Platform Architecture (V18-001)

**Date:** 2026-03-14  
**Objective:** Establish shared data platform for agent data access

---

## 1. Overview

The Agent Data Platform provides a unified infrastructure for all domain and executive agents to access structured data, documents, and semantic search capabilities through a controlled gateway. This ensures consistent access control, audit logging, and proper governance across all agent interactions with data sources.

---

## 2. Platform Components

### 2.1 Storage Layer

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| **StructuredDataStore** | Relational data storage | PostgreSQL via SQLAlchemy |
| **DocumentStore** | File/document storage | MinIO (S3-compatible) |
| **VectorIndexService** | Semantic search | Weaviate vector database |

### 2.2 Governance Layer

| Component | Purpose |
|-----------|---------|
| **SourceRegistry** | Central source management, trust tiers, access tags |

### 2.3 Retrieval Layer

| Component | Purpose |
|-----------|---------|
| **RetrievalGateway** | Unified entry point for all agent data access |

### 2.4 Ingestion Layer

| Component | Purpose |
|-----------|---------|
| **IngestionCoordinator** | Coordinates data ingestion from external sources |

---

## 3. Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                    AGENTS                                        │
│   Domain Agents (Strategy, Finance, Health, etc.) │ Executive Agents            │
└─────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           RETRIEVAL GATEWAY                                      │
│   Unified access point with:                                                    │
│   - Domain-based access control                                                 │
│   - Trust tier filtering                                                        │
│   - Audit logging                                                               │
│   - Rate limiting                                                               │
└─────────────────────────────────────────────────────────────────────────────────┘
                                         │
              ┌──────────────────────────┼──────────────────────────┐
              ▼                          ▼                          ▼
┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────┐
│  STRUCTURED DATA STORE  │  │    DOCUMENT STORE       │  │  VECTOR INDEX       │
│                         │  │                         │  │                     │
│  PostgreSQL             │  │  MinIO (S3)             │  │  Weaviate           │
│  - Financial records   │  │  - Strategic docs       │  │  - Embeddings       │
│  - Health metrics      │  │  - Policy documents    │  │  - Semantic search  │
│  - Risk registers      │  │  - Meeting notes       │  │                     │
└─────────────────────────┘  └─────────────────────────┘  └─────────────────────┘
              │                          │                          │
              └──────────────────────────┼──────────────────────────┘
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           SOURCE REGISTRY                                        │
│   - Source metadata                                                            │
│   - Trust tier classification                                                  │
│   - Agent access tags                                                          │
│   - Refresh schedules                                                           │
└─────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           INGESTION COORDINATOR                                 │
│   - External source scheduling                                                 │
│   - Data pipeline management                                                   │
│   - Error handling and retry                                                   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Source Governance Model

### 4.1 Source Registry

Each data source is registered with the following metadata:

| Field | Description |
|-------|-------------|
| `source_id` | Unique identifier |
| `source_name` | Human-readable name |
| `domain` | Domain (finance, health, strategy, etc.) |
| `source_type` | relational, vector, document, web, api |
| `license` | License or allowed use |
| `trust_tier` | HIGH, MEDIUM, LOW, UNVERIFIED |
| `refresh_interval` | How often to refresh |
| `enabled` | Whether source is active |
| `agent_access_tags` | Tags controlling agent access |

### 4.2 Trust Tiers

| Tier | Description | Agents |
|------|-------------|--------|
| **HIGH** | Verified, authoritative | Executive, Governance |
| **MEDIUM** | Curated, reliable | Domain, Planning |
| **LOW** | Community sources | Intelligence |
| **UNVERIFIED** | Unknown reliability | Learning only |

### 4.3 Default Sources

```
INTERNAL (HIGH TRUST):
├── internal_strategy     - Strategic Plans Database
├── internal_finance     - Financial Records
├── internal_health      - Health Metrics
├── internal_operations - Operations Data
├── internal_risk       - Risk Register
├── knowledge_graph     - Personal Knowledge Graph
└── strategic_doctrine - Strategy Library

EXTERNAL (MEDIUM TRUST):
├── finance_yahoo       - Yahoo Finance
└── health_nih         - NIH Health Data
```

---

## 5. Agent Access Model

### 5.1 Access Control Flow

```
Agent Request
     │
     ▼
┌──────────────────┐
│ Check Agent Type │──────────┐
└──────────────────┘          │
     │                        │
     ▼                        ▼
┌──────────────────┐    ┌──────────────────┐
│ Domain Match?    │───▶│ Filter by Tags   │
└──────────────────┘    └──────────────────┘
     │                        │
     ▼                        ▼
┌──────────────────┐    ┌──────────────────┐
│ Trust Tier OK?   │───▶│ Check Trust Tier │
└──────────────────┘    └──────────────────┘
     │                        │
     ▼                        ▼
┌──────────────────┐    ┌──────────────────┐
│  Allow Access    │    │    Deny Access   │
└──────────────────┘    └──────────────────┘
```

### 5.2 Access by Agent Type

| Agent Type | Access Level |
|------------|-------------|
| **Executive** | All HIGH and MEDIUM trust, all domains |
| **Domain** | MEDIUM trust, specific domain |
| **Planning** | MEDIUM trust, planning-relevant sources |
| **Intelligence** | All tiers, research sources |
| **Governance** | HIGH trust, policy sources |
| **Execution** | Limited to approved execution sources |
| **Learning** | All sources for evaluation |

---

## 6. Retrieval Gateway API

### 6.1 Main Methods

```python
# Unified search (main entry point)
async def search(request: RetrievalRequest) -> RetrievalResponse

# Search specific source types
async def search_structured_data(request: StructuredDataSearchRequest) -> List[Dict]
async def search_documents(request: DocumentSearchRequest) -> List[RetrievedEvidence]

# Get latest updates
async def get_latest_updates(request: LatestUpdatesRequest) -> List[RetrievedEvidence]

# Summarize evidence
async def summarize_evidence(request: EvidenceSummaryRequest) -> str
```

### 6.2 Retrieval Request

```python
class RetrievalRequest:
    query: str                          # Search query
    agent_type: Optional[AgentType]     # Requesting agent type
    agent_domain: Optional[str]         # Requesting domain
    domains: List[str]                  # Domains to search
    trust_tiers: List[TrustTier]       # Trust tiers to include
    source_tags: List[str]              # Source tags to filter
    max_results: int                    # Maximum results
    include_documents: bool             # Include document sources
    include_structured: bool            # Include structured sources
    include_web: bool                   # Include web sources
    min_relevance: float                # Minimum relevance score
```

---

## 7. Directory Structure

```
app/data_platform/
├── __init__.py              # Public API exports
├── models.py                # Common data models
├── governance/
│   └── source_registry.py   # Source registration and lookup
├── storage/
│   ├── structured_store.py # Relational data storage
│   ├── document_store.py    # Document/file storage
│   └── vector_index.py      # Semantic search
├── retrieval/
│   └── retrieval_gateway.py # Unified retrieval gateway
└── ingestion/
    └── ingestion_coordinator.py # Data ingestion coordination
```

---

## 8. Infrastructure Requirements

### Docker Services

| Service | Purpose | Port |
|---------|---------|------|
| **PostgreSQL** | Structured data | 5432 |
| **Redis** | Caching, workers | 6379 |
| **Weaviate** | Vector database | 8080 |
| **MinIO** | Object storage | 9000/9001 |

### Configuration

Environment variables required:
- `POSTGRES_*` - Database configuration
- `REDIS_*` - Redis configuration  
- `WEAVIATE_*` - Vector DB configuration
- `MINIO_*` - Object storage configuration

---

## 9. Usage Example

```python
from app.data_platform import get_retrieval_gateway, RetrievalRequest, AgentType

# Get gateway
gateway = await get_retrieval_gateway(session)

# Search with access control
request = RetrievalRequest(
    query="revenue forecast Q4",
    agent_type=AgentType.DOMAIN,
    agent_domain="finance",
    domains=["finance"],
    trust_tiers=[TrustTier.HIGH, TrustTier.MEDIUM],
    max_results=10,
)

response = await gateway.search(request)

# Access results
for evidence in response.evidence:
    print(f"Source: {evidence.source_name}")
    print(f"Content: {evidence.content}")
    print(f"Relevance: {evidence.relevance_score}")
```

---

## 10. Next Steps

1. **Implement Storage Backends**: Connect actual PostgreSQL, Weaviate, MinIO
2. **Add Embedding Generation**: Integrate LLM for vector embeddings
3. **Implement Ingestion Pipelines**: Build connectors for external sources
4. **Add Audit Logging**: Track all retrieval requests
5. **Add Rate Limiting**: Prevent abuse
6. **Integrate with Agents**: Update agents to use gateway

---

*End of Architecture Document*
