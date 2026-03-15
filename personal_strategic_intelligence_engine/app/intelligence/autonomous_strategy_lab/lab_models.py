"""Lab Models for the Autonomous Strategy Lab.

Core models for strategy research and variant management.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class VariantStatus(str, Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    TESTING = "testing"
    VALIDATED = "validated"
    ACTIVE_RESEARCH = "active_research"
    PROMOTED = "promoted"
    REJECTED = "rejected"
    RETIRED = "retired"


class ExperimentStatus(str, Enum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class DecisionType(str, Enum):
    PROMOTED = "promoted"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"
    PAUSED = "paused"


@dataclass
class StrategyTemplate:
    """Canonical strategy family."""
    id: str
    name: str
    domain: str
    description: str
    required_signals: List[str]
    required_features: List[str]
    supported_regimes: List[str]
    parameter_space: Dict[str, Any]
    risk_profile: str
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "description": self.description,
            "required_signals": self.required_signals,
            "required_features": self.required_features,
            "supported_regimes": self.supported_regimes,
            "parameter_space": self.parameter_space,
            "risk_profile": self.risk_profile,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class StrategyVariant:
    """Generated strategy variant."""
    id: str
    template_id: str
    parent_variant_id: Optional[str]
    parameters: Dict[str, Any]
    generated_by: str
    creation_reason: str
    status: VariantStatus
    validation_state: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "template_id": self.template_id,
            "parent_variant_id": self.parent_variant_id,
            "parameters": self.parameters,
            "generated_by": self.generated_by,
            "creation_reason": self.creation_reason,
            "status": self.status.value,
            "validation_state": self.validation_state,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class ExperimentRun:
    """Research test batch."""
    id: str
    variant_ids: List[str]
    regime_scope: List[str]
    date_range: Dict[str, str]
    test_method: str
    sample_size: int
    status: ExperimentStatus
    results: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "variant_ids": self.variant_ids,
            "regime_scope": self.regime_scope,
            "date_range": self.date_range,
            "test_method": self.test_method,
            "sample_size": self.sample_size,
            "status": self.status.value,
            "results": self.results,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class VariantPerformance:
    """Test results for a variant."""
    variant_id: str
    expectancy: float
    win_rate: float
    drawdown: float
    stability_score: float
    regime_fit: Dict[str, float]
    liquidity_feasibility: float
    degradation_risk: float
    confidence_score: float
    sample_size: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "variant_id": self.variant_id,
            "expectancy": self.expectancy,
            "win_rate": self.win_rate,
            "drawdown": self.drawdown,
            "stability_score": self.stability_score,
            "regime_fit": self.regime_fit,
            "liquidity_feasibility": self.liquidity_feasibility,
            "degradation_risk": self.degradation_risk,
            "confidence_score": self.confidence_score,
            "sample_size": self.sample_size,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class PromotionDecision:
    """Promotion tracking."""
    variant_id: str
    decision: DecisionType
    rationale: str
    destination: str
    approval_required: bool
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "variant_id": self.variant_id,
            "decision": self.decision.value,
            "rationale": self.rationale,
            "destination": self.destination,
            "approval_required": self.approval_required,
            "timestamp": self.timestamp.isoformat(),
        }


# Default templates
DEFAULT_TEMPLATES = [
    StrategyTemplate(
        id="tpl-vwap-reclaim",
        name="SPY VWAP Reclaim Continuation",
        domain="finance",
        description="Enter on VWAP reclaim after downside sweep",
        required_signals=["vwap_reclaim", "liquidity_sweep"],
        required_features=["vwap_state", "momentum"],
        supported_regimes=["trend_morning", "trend_day"],
        parameter_space={
            "confirmation_bars": [1, 2, 3],
            "hold_time_minutes": [5, 8, 12],
            "delta_target": [0.25, 0.35, 0.45],
        },
        risk_profile="moderate",
    ),
    StrategyTemplate(
        id="tpl-opening-range",
        name="SPY Opening Range Breakout",
        domain="finance",
        description="Follow through on opening range breakout",
        required_signals=["opening_range", "volume_surge"],
        required_features=["relative_volume", "momentum"],
        supported_regimes=["opening_drive", "trend_morning"],
        parameter_space={
            "breakout_threshold": [0.5, 1.0, 1.5],
            "volume_multiplier": [1.5, 2.0, 2.5],
            "hold_time_minutes": [10, 15, 20],
        },
        risk_profile="high",
    ),
    StrategyTemplate(
        id="tpl-gamma-expansion",
        name="SPY Gamma Expansion Continuation",
        domain="finance",
        description="Trade gamma acceleration events",
        required_signals=["gamma_acceleration", "spy_delta_velocity"],
        required_features=["gamma_exposure", "momentum"],
        supported_regimes=["trend_day", "power_hour"],
        parameter_space={
            "gamma_threshold": [0.05, 0.08, 0.10],
            "confirmation_bars": [1, 2],
            "hold_time_minutes": [5, 10, 15],
        },
        risk_profile="high",
    ),
]
