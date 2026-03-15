"""Alpha Models for the Alpha Engine.

Core models for strategy discovery and validation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class AlphaStatus(str, Enum):
    DISCOVERED = "discovered"
    UNDER_TEST = "under_test"
    VALIDATED = "validated"
    ACTIVE = "active"
    DEGRADED = "degraded"
    RETIRED = "retired"


class DeploymentState(str, Enum):
    RESEARCH = "research"
    TESTING = "testing"
    APPROVED = "approved"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class ValidationStatus(str, Enum):
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"
    VALIDATED = "validated"


@dataclass
class AlphaCandidate:
    """Represents a discovered strategy hypothesis."""
    id: str
    name: str
    domain: str
    hypothesis: str
    signal_dependencies: List[str]
    regime_requirements: Dict[str, Any]
    test_results: Optional["AlphaTestResult"] = None
    confidence_score: float = 0.0
    status: AlphaStatus = AlphaStatus.DISCOVERED
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "hypothesis": self.hypothesis,
            "signal_dependencies": self.signal_dependencies,
            "regime_requirements": self.regime_requirements,
            "test_results": self.test_results.to_dict() if self.test_results else None,
            "confidence_score": self.confidence_score,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @staticmethod
    def create(
        name: str,
        domain: str,
        hypothesis: str,
        signal_dependencies: List[str],
        regime_requirements: Optional[Dict[str, Any]] = None,
    ) -> "AlphaCandidate":
        """Create a new alpha candidate."""
        return AlphaCandidate(
            id=str(uuid.uuid4()),
            name=name,
            domain=domain,
            hypothesis=hypothesis,
            signal_dependencies=signal_dependencies,
            regime_requirements=regime_requirements or {},
        )


@dataclass
class AlphaTestResult:
    """Stores validation outcomes."""
    sample_size: int
    win_rate: float
    expectancy: float
    drawdown: float
    sharpe_like_score: float
    regime_performance: Dict[str, float] = field(default_factory=dict)
    stability_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "sample_size": self.sample_size,
            "win_rate": self.win_rate,
            "expectancy": self.expectancy,
            "drawdown": self.drawdown,
            "sharpe_like_score": self.sharpe_like_score,
            "regime_performance": self.regime_performance,
            "stability_score": self.stability_score,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class StrategyFeature:
    """Represents signal features used by strategies."""
    name: str
    description: str
    feature_type: str
    importance_score: float = 0.0
    stability_score: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "feature_type": self.feature_type,
            "importance_score": self.importance_score,
            "stability_score": self.stability_score,
        }


@dataclass
class PatternCandidate:
    """Pattern discovered from signal sequences."""
    id: str
    signal_sequence: List[str]
    frequency: int
    outcome_distribution: Dict[str, int]
    confidence: float = 0.0
    discovered_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "signal_sequence": self.signal_sequence,
            "frequency": self.frequency,
            "outcome_distribution": self.outcome_distribution,
            "confidence": self.confidence,
            "discovered_at": self.discovered_at.isoformat(),
        }


@dataclass
class RegimeAnalysis:
    """Performance analysis by regime."""
    regime: str
    performance_metrics: Dict[str, float]
    sample_size: int
    confidence: float
    
    def to_dict(self) -> dict:
        return {
            "regime": self.regime,
            "performance_metrics": self.performance_metrics,
            "sample_size": self.sample_size,
            "confidence": self.confidence,
        }


@dataclass
class EdgeValidation:
    """Evaluation of strategy edge."""
    status: ValidationStatus
    confidence_score: float
    risk_profile: str
    recommended_use: str
    metrics: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "confidence_score": self.confidence_score,
            "risk_profile": self.risk_profile,
            "recommended_use": self.recommended_use,
            "metrics": self.metrics,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class StrategyRanking:
    """Ranked strategy recommendation."""
    rank: int
    alpha_id: str
    name: str
    score: float
    regime_fit: float
    recent_performance: float
    confidence: float
    recommendation: str
    
    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "alpha_id": self.alpha_id,
            "name": self.name,
            "score": self.score,
            "regime_fit": self.regime_fit,
            "recent_performance": self.recent_performance,
            "confidence": self.confidence,
            "recommendation": self.recommendation,
        }


@dataclass
class DegradationAlert:
    """Strategy degradation detection."""
    strategy_id: str
    strategy_name: str
    expectancy_change: float
    win_rate_change: float
    severity: str
    recommended_action: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "strategy_id": self.strategy_id,
            "strategy_name": self.strategy_name,
            "expectancy_change": self.expectancy_change,
            "win_rate_change": self.win_rate_change,
            "severity": self.severity,
            "recommended_action": self.recommended_action,
            "timestamp": self.timestamp.isoformat(),
        }


# Predefined market regimes
MARKET_REGIMES = [
    "high_iv",
    "low_iv",
    "trend_day",
    "range_day",
    "event_day",
    "opening_drive",
    "midday_compression",
    "power_hour",
]


# Predefined strategy features
STRATEGY_FEATURES = [
    StrategyFeature("vwap_state", "VWAP relative position", "market_structure"),
    StrategyFeature("gamma_acceleration", "Rate of gamma change", "greeks"),
    StrategyFeature("distance_from_strike", "Moneyness", "pricing"),
    StrategyFeature("time_of_day", "Trading session", "temporal"),
    StrategyFeature("relative_volume", "Volume vs average", "liquidity"),
    StrategyFeature("spread_width", "Bid-ask spread", "liquidity"),
    StrategyFeature("iv_rank", "IV relative position", "volatility"),
    StrategyFeature("momentum", "Price momentum", "technical"),
]
