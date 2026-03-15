"""Agent Data Platform - Unified data access for all agents.

The data platform provides a shared infrastructure for agents to access
structured data, documents, and semantic search through a controlled gateway.

Components:
- governance/   : Source registry and access control
- storage/      : Structured, document, and vector storage
- retrieval/    : Retrieval gateway for unified access
- ingestion/    : Data ingestion coordination
- audit/        : Logging and metrics

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
from app.data_platform.governance.domain_sources import (
    get_sources_for_domain,
    get_all_domain_sources,
)
from app.data_platform.governance.access_policy import (
    AccessPolicy,
    AccessPolicyManager,
    get_access_policy_manager,
)
from app.data_platform.retrieval.federated_retrieval import (
    FederatedRetrievalService,
    get_federated_retrieval_service,
)
from app.data_platform.audit.retrieval_audit import (
    RetrievalLogEntry,
    RetrievalAuditLogger,
    get_retrieval_audit_logger,
)
from app.data_platform.audit.metrics import (
    PlatformMetrics,
    HumanReviewReport,
    get_platform_metrics,
)

# Domain models
from app.data_platform.models_finance import (
    EconomicSeriesRecord,
    MarketSnapshot,
    FilingRecord,
    FinanceNewsDocument,
)
from app.data_platform.models_health import (
    FoodNutrientRecord,
    SupplementFactRecord,
    HealthEvidenceDocument,
    WellnessGuidanceDocument,
)
from app.data_platform.models_fitness import (
    ExerciseRecord,
    WorkoutTemplate,
    FitnessGuidanceDocument,
    ActivityDataRecord,
)
from app.data_platform.models_operations import (
    ProcedureDocument,
    WorkflowRecord,
    TaskRecord,
    OperationalMetricRecord,
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
    "AccessPolicy",
    "AccessPolicyManager",
    "get_access_policy_manager",
    "FederatedRetrievalService",
    "get_federated_retrieval_service",
    "RetrievalLogEntry",
    "RetrievalAuditLogger",
    "get_retrieval_audit_logger",
    "PlatformMetrics",
    "HumanReviewReport",
    "get_platform_metrics",
    # Domain sources
    "get_sources_for_domain",
    "get_all_domain_sources",
    # Finance models
    "EconomicSeriesRecord",
    "MarketSnapshot",
    "FilingRecord",
    "FinanceNewsDocument",
    # Health models
    "FoodNutrientRecord",
    "SupplementFactRecord",
    "HealthEvidenceDocument",
    "WellnessGuidanceDocument",
    # Fitness models
    "ExerciseRecord",
    "WorkoutTemplate",
    "FitnessGuidanceDocument",
    "ActivityDataRecord",
    # Operations models
    "ProcedureDocument",
    "WorkflowRecord",
    "TaskRecord",
    "OperationalMetricRecord",
]
