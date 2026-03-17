"""
BB-APP-001: Busy Bee Application Architecture

This document defines the architecture for the Busy Bee Life Operating System.

ARCHITECTURE LAYERS
===================

A. Experience Layer (Web/Mobile)
   └── Next.js Frontend

B. API Layer (FastAPI)
   └── REST Endpoints

C. Application Layer
   └── Workflows & Use Cases

D. Intelligence Layer (Existing)
   ├── Domain Agents
   ├── Chief Officers
   ├── Executive Council
   └── Strategic Engines

E. Services Layer
   └── Reusable Business Services

F. Infrastructure Layer
   └── Database, Cache, Queue

G. Data Layer
   └── PostgreSQL


DEPENDENCY DIRECTION
===================
Experience → API → Application → Intelligence → Services → Infrastructure → Data

FORBIDDEN PATTERNS
==================
• Frontend directly calling intelligence modules
• Intelligence modules directly coupled to web UI
• Agents reading/writing persistence directly
• Reports generated from presentation layer logic
"""

from enum import Enum


class ProductDomain(str, Enum):
    """Product domains for BB-APP-001."""
    IDENTITY = "identity"
    SIGNAL_INTAKE = "signal_intake"
    EXECUTIVE_STATE = "executive_state"
    RECOMMENDATION = "recommendation"
    ACTION = "action"
    MEMORY = "memory"
    REVIEW = "review"
    INTEGRATION = "integration"


class ServiceName(str, Enum):
    """Service layer components."""
    USER_CONTEXT = "UserContextService"
    SIGNAL_INGESTION = "SignalIngestionService"
    SIGNAL_NORMALIZATION = "SignalNormalizationService"
    STATE_SNAPSHOT = "StateSnapshotService"
    DOMAIN_ANALYSIS = "DomainAnalysisService"
    EXECUTIVE_COUNCIL = "ExecutiveCouncilService"
    RECOMMENDATION = "RecommendationService"
    EXECUTIVE_BRIEF = "ExecutiveBriefService"
    MEMORY = "MemoryService"
    REVIEW = "ReviewService"
    ACTION_TRACKING = "ActionTrackingService"
    NOTIFICATION = "NotificationService"
    EXPLAINABILITY = "ExplainabilityService"


__all__ = ["ProductDomain", "ServiceName"]
