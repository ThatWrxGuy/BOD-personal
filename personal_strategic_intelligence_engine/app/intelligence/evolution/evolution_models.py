"""Evolution Models for Intelligence Evolution Engine.

Models representing quantitative analysis, pattern discovery, and optimization outputs.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class PatternType(str, Enum):
    STRUCTURAL = "structural"
    MOMENTUM = "momentum"
    REVERSAL = "reversal"
    VOLATILITY = "volatility"
    LIQUIDITY = "liquidity"
    TIMING = "timing"


class OptimizationType(str, Enum):
    SCORE_THRESHOLD = "score_threshold"
    SUPPRESSION_ADJUSTMENT = "suppression_adjustment"
    TIMING_CRITERIA = "timing_criteria"
    CONFIDENCE_SCALING = "confidence_scaling"
    PATTERN_FILTER = "pattern_filter"
    REGIME_MODIFIER = "regime_modifier"


class ApprovalLevel(str, Enum):
    AUTO = "auto"
    FINANCE = "finance"
    CEO = "ceo"
    BOARD = "board"


class RegimeType(str, Enum):
    TREND_UP = "trend_up"
    TREND_DOWN = "trend_down"
    RANGE_CHOP = "range_chop"
    VOLATILITY_EXPAND = "volatility_expand"
    VOLATILITY_COMPRESS = "volatility_compress"
    LOW_PARTICIPATION = "low_participation"


@dataclass
class QuantitativeMetrics:
    """Quantitative performance metrics."""
    expectancy: float
    sharpe_ratio: float
    sortino_ratio: float
    win_rate: float
    avg_win: float
    avg_loss: float
    max_drawdown: float
    volatility_adjusted_return: float
    reliability_index: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    
    def to_dict(self) -> dict:
        return {
            "expectancy": self.expectancy,
            "sharpe_ratio": self.sharpe_ratio,
            "sortino_ratio": self.sortino_ratio,
            "win_rate": self.win_rate,
            "avg_win": self.avg_win,
            "avg_loss": self.avg_loss,
            "max_drawdown": self.max_drawdown,
            "volatility_adjusted_return": self.volatility_adjusted_return,
            "reliability_index": self.reliability_index,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
        }


@dataclass
class PatternDiscovery:
    """Discovered pattern in tactical data."""
    pattern_id: str
    pattern_type: PatternType
    description: str
    conditions: Dict[str, Any]
    frequency: float
    win_rate: float
    avg_return: float
    statistical_significance: float
    confidence: float
    discovered_at: datetime
    last_validated: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type.value,
            "description": self.description,
            "conditions": self.conditions,
            "frequency": self.frequency,
            "win_rate": self.win_rate,
            "avg_return": self.avg_return,
            "statistical_significance": self.statistical_significance,
            "confidence": self.confidence,
            "discovered_at": self.discovered_at.isoformat(),
            "last_validated": self.last_validated.isoformat() if self.last_validated else None,
        }


@dataclass
class FeatureImportance:
    """Feature importance ranking."""
    feature_name: str
    importance_score: float
    category: str
    correlation: float
    interaction_effects: List[str] = field(default_factory=list)
    noise_level: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "feature_name": self.feature_name,
            "importance_score": self.importance_score,
            "category": self.category,
            "correlation": self.correlation,
            "interaction_effects": self.interaction_effects,
            "noise_level": self.noise_level,
        }


@dataclass
class OptimizationProposal:
    """Strategy optimization proposal."""
    proposal_id: str
    optimization_type: OptimizationType
    target_parameter: str
    current_value: Any
    proposed_value: Any
    expected_improvement: float
    confidence: float
    required_approval: ApprovalLevel
    rationale: str
    created_at: datetime
    status: str = "pending"
    
    def to_dict(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "optimization_type": self.optimization_type.value,
            "target_parameter": self.target_parameter,
            "current_value": str(self.current_value),
            "proposed_value": str(self.proposed_value),
            "expected_improvement": self.expected_improvement,
            "confidence": self.confidence,
            "required_approval": self.required_approval.value,
            "rationale": self.rationale,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
        }


@dataclass
class RegimeAnalysis:
    """Market regime analysis."""
    regime_type: RegimeType
    start_time: datetime
    characteristics: Dict[str, Any]
    tactical_performance: QuantitativeMetrics
    recommended_modifiers: Dict[str, float]
    confidence_adjustment: float
    
    def to_dict(self) -> dict:
        return {
            "regime_type": self.regime_type.value,
            "start_time": self.start_time.isoformat(),
            "characteristics": self.characteristics,
            "tactical_performance": self.tactical_performance.to_dict(),
            "recommended_modifiers": self.recommended_modifiers,
            "confidence_adjustment": self.confidence_adjustment,
        }


@dataclass
class CalibrationReport:
    """Model calibration report."""
    timestamp: datetime
    calibrated_model: str
    calibration_error: float
    confidence_accuracy: float
    score_reliability: float
    recommended_adjustments: Dict[str, float]
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "calibrated_model": self.calibrated_model,
            "calibration_error": self.calibration_error,
            "confidence_accuracy": self.confidence_accuracy,
            "score_reliability": self.score_reliability,
            "recommended_adjustments": self.recommended_adjustments,
        }


@dataclass
class EvolutionSnapshot:
    """Complete intelligence evolution snapshot."""
    timestamp: datetime
    patterns_discovered: List[PatternDiscovery]
    feature_importance: List[FeatureImportance]
    quantitative_analysis: Dict[str, QuantitativeMetrics]
    regime_analysis: List[RegimeAnalysis]
    calibration_report: Optional[CalibrationReport]
    pending_proposals: List[OptimizationProposal]
    learning_summary: Dict[str, Any]
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "patterns_discovered": [p.to_dict() for p in self.patterns_discovered],
            "feature_importance": [f.to_dict() for f in self.feature_importance],
            "quantitative_analysis": {
                k: v.to_dict() for k, v in self.quantitative_analysis.items()
            },
            "regime_analysis": [r.to_dict() for r in self.regime_analysis],
            "calibration_report": self.calibration_report.to_dict() if self.calibration_report else None,
            "pending_proposals": [p.to_dict() for p in self.pending_proposals],
            "learning_summary": self.learning_summary,
        }


@dataclass
class LearningSchedule:
    """Learning schedule configuration."""
    daily_tasks: List[str] = field(default_factory=lambda: ["signal_performance"])
    weekly_tasks: List[str] = field(default_factory=lambda: ["feature_recalculation"])
    monthly_tasks: List[str] = field(default_factory=lambda: ["strategy_optimization"])
    last_daily_run: Optional[datetime] = None
    last_weekly_run: Optional[datetime] = None
    last_monthly_run: Optional[datetime] = None
