"""Executive Council Module - BB-CORE-022

Executive Council Intelligence Engine for the Busy Bee Personal Strategic Intelligence System.

This module provides multi-domain strategic coordination:
- Recommendation Aggregator: Collects recommendations from all domains
- Priority Resolution Engine: Ranks recommendations by importance
- Conflict Resolution Engine: Resolves inter-domain conflicts
- Strategic Alignment Engine: Ensures alignment with long-term goals
- Executive Brief Generator: Produces CEO-ready strategic briefing
- Executive Council Engine: Orchestrates the full council process
"""

from app.core.executive_council.council_models import (
    Domain,
    ChiefOfficer,
    PriorityLevel,
    RecommendationStatus,
    DomainRecommendation,
    RankedRecommendation,
    Conflict,
    AlignmentScore,
    CouncilCycleResult,
    StrategicGoal,
    CouncilState,
)

from app.core.executive_council.executive_council_engine import (
    ExecutiveCouncilEngine,
    get_executive_council_engine,
)

__all__ = [
    # Models
    "Domain",
    "ChiefOfficer",
    "PriorityLevel",
    "RecommendationStatus",
    "DomainRecommendation",
    "RankedRecommendation",
    "Conflict",
    "AlignmentScore",
    "CouncilCycleResult",
    "StrategicGoal",
    "CouncilState",
    # Engine
    "ExecutiveCouncilEngine",
    "get_executive_council_engine",
]
