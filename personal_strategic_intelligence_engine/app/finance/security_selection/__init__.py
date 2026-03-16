"""Security Selection Module.

This module provides security selection and ranking capabilities.
"""
from app.finance.security_selection.selection_models import (
    ConvictionLevel,
    RankedOpportunity,
    ScreenCriteria,
    ScreenResult,
    ScreeningResult,
    SecurityCategory,
    SecurityProfile,
    SecurityRecommendation,
    SecurityScore,
    SelectionReport,
    StrategyType,
    UniverseDefinition,
)

from app.finance.security_selection.security_selection_engine import (
    SecuritySelectionEngine,
    get_security_selection_engine,
)

from app.finance.security_selection.universe_manager import (
    UniverseManager,
    get_universe_manager,
)

from app.finance.security_selection.security_screener import (
    SecurityScreener,
    get_screener,
)

from app.finance.security_selection.factor_scoring_engine import (
    FactorScoringEngine,
    get_scoring_engine,
)

from app.finance.security_selection.opportunity_ranker import (
    OpportunityRanker,
    get_ranker,
)

from app.finance.security_selection.conviction_engine import (
    ConvictionEngine,
    get_conviction_engine,
)

from app.finance.security_selection.recommendation_engine import (
    RecommendationEngine,
    get_recommendation_engine,
)

__all__ = [
    # Models
    "ConvictionLevel",
    "RankedOpportunity",
    "ScreenCriteria",
    "ScreenResult",
    "ScreeningResult",
    "SecurityCategory",
    "SecurityProfile",
    "SecurityRecommendation",
    "SecurityScore",
    "SelectionReport",
    "StrategyType",
    "UniverseDefinition",
    
    # Engine
    "SecuritySelectionEngine",
    "get_security_selection_engine",
    
    # Components
    "UniverseManager",
    "get_universe_manager",
    "SecurityScreener",
    "get_screener",
    "FactorScoringEngine",
    "get_scoring_engine",
    "OpportunityRanker",
    "get_ranker",
    "ConvictionEngine",
    "get_conviction_engine",
    "RecommendationEngine",
    "get_recommendation_engine",
]
