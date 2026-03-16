"""Orchestration Module - BB-CORE-021

Strategic Intelligence Orchestrator for the Busy Bee Finance Platform.

This module provides top-level coordination for all finance intelligence modules:
- State Snapshot Engine: Builds unified system state
- Activation Policy Engine: Controls which engines are active
- Decision Fusion Engine: Resolves conflicts between module outputs
- Capital Deployment Coordinator: Determines capital posture
- Priority Router: Routes important items to executive layers
"""

from app.core.orchestration.orchestration_models import (
    SystemStateSnapshot,
    ActivationDecision,
    FusedDecision,
    CapitalPosture,
    CapitalPositionRecommendation,
    ExecutiveBrief,
    RoutedPriorityItem,
    PriorityLevel,
    SystemStatus,
    RegimeType,
)

from app.core.orchestration.strategic_intelligence_orchestrator import (
    StrategicIntelligenceOrchestrator,
    get_strategic_orchestrator,
)

__all__ = [
    # Models
    "SystemStateSnapshot",
    "ActivationDecision",
    "FusedDecision",
    "CapitalPosture",
    "CapitalPositionRecommendation",
    "ExecutiveBrief",
    "RoutedPriorityItem",
    "PriorityLevel",
    "SystemStatus",
    "RegimeType",
    # Orchestrator
    "StrategicIntelligenceOrchestrator",
    "get_strategic_orchestrator",
]
