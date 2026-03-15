"""Learning Models for Tactical Learning Subsystem.

Standardized models representing learning and calibration outputs.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class SignalDirection(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class SignalOutcome(str, Enum):
    WIN = "win"
    LOSS = "loss"
    BREAKEVEN = "breakeven"
    PENDING = "pending"
    EXPIRED = "expired"


class ConfidenceBucket(str, Enum):
    VERY_LOW = "very_low"  # 0-30
    LOW = "low"  # 30-50
    MEDIUM = "medium"  # 50-70
    HIGH = "high"  # 70-85
    VERY_HIGH = "very_high"  # 85-100


class MarketRegime(str, Enum):
    TREND_UP = "trend_up"
    TREND_DOWN = "trend_down"
    RANGE_CHOP = "range_chop"
    REVERSAL = "reversal"
    UNKNOWN = "unknown"


class TimingDecision(str, Enum):
    ENTER_NOW = "enter_now"
    WAIT_FOR_PULLBACK = "wait_for_pullback"
    WAIT_FOR_CONFIRMATION = "wait_for_confirmation"
    AVOID_ENTRY = "avoid_entry"
    DEFER_SIGNAL = "defer_signal"


class SuppressionCategory(str, Enum):
    LOW_LIQUIDITY = "low_liquidity"
    WIDE_SPREADS = "wide_spreads"
    STRUCTURE_MISALIGNMENT = "structure_misalignment"
    OVEREXTENSION_RISK = "overextension_risk"
    TIMING_FAILURE = "timing_failure"
    REGIME_CONFLICT = "regime_conflict"
    RISK_BUDGET_VIOLATION = "risk_budget_violation"
    POLICY_REJECTION = "policy_rejection"


@dataclass
class SignalOutcomeRecord:
    """Record of a signal and its outcome."""
    signal_id: str
    timestamp: datetime
    ticker: str
    strike: float
    option_type: str
    direction: SignalDirection
    signal_score: float
    confidence_score: float
    regime: MarketRegime
    vwap_state: str
    day_type: str
    timing_decision: TimingDecision
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    profit_loss: Optional[float] = None
    outcome: SignalOutcome = SignalOutcome.PENDING
    paper_trade: bool = True
    suppressed: bool = False
    suppression_reason: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "signal_id": self.signal_id,
            "timestamp": self.timestamp.isoformat(),
            "ticker": self.ticker,
            "strike": self.strike,
            "option_type": self.option_type,
            "direction": self.direction.value,
            "signal_score": self.signal_score,
            "confidence_score": self.confidence_score,
            "regime": self.regime.value,
            "vwap_state": self.vwap_state,
            "day_type": self.day_type,
            "timing_decision": self.timing_decision.value,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "profit_loss": self.profit_loss,
            "outcome": self.outcome.value,
            "paper_trade": self.paper_trade,
            "suppressed": self.suppressed,
            "suppression_reason": self.suppression_reason,
        }


@dataclass
class FeaturePerformance:
    """Performance metrics for a single feature."""
    feature_name: str
    feature_category: str
    win_rate_when_high: float
    win_rate_when_low: float
    avg_score_when_win: float
    avg_score_when_loss: float
    correlation_to_outcome: float
    predictive_power: float


@dataclass
class FeaturePerformanceReport:
    """Report of feature importance analysis."""
    timestamp: datetime
    top_positive_predictors: List[FeaturePerformance]
    top_negative_predictors: List[FeaturePerformance]
    low_value_features: List[str]
    false_positive_features: List[str]
    strong_expectancy_features: List[str]
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "top_positive_predictors": [
                {"feature_name": f.feature_name, "predictive_power": f.predictive_power}
                for f in self.top_positive_predictors
            ],
            "top_negative_predictors": [
                {"feature_name": f.feature_name, "predictive_power": f.predictive_power}
                for f in self.top_negative_predictors
            ],
            "low_value_features": self.low_value_features,
            "false_positive_features": self.false_positive_features,
            "strong_expectancy_features": self.strong_expectancy_features,
        }


@dataclass
class ConfidenceBucketStats:
    """Statistics for a confidence bucket."""
    bucket: ConfidenceBucket
    min_confidence: int
    max_confidence: int
    signal_count: int
    win_count: int
    loss_count: int
    win_rate: float
    avg_profit_loss: float
    
    @property
    def predicted_vs_actual(self) -> float:
        """Predicted win rate (based on confidence) vs actual."""
        predicted = (self.min_confidence + self.max_confidence) / 2
        return self.win_rate - predicted


@dataclass
class ConfidenceCalibrationReport:
    """Report on confidence score calibration."""
    timestamp: datetime
    buckets: List[ConfidenceBucketStats]
    overall_calibration_error: float
    is_overconfident: bool
    is_underconfident: bool
    recommended_adjustments: Dict[str, float]
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "buckets": [
                {
                    "bucket": b.bucket.value,
                    "min_confidence": b.min_confidence,
                    "max_confidence": b.max_confidence,
                    "signal_count": b.signal_count,
                    "win_rate": b.win_rate,
                    "predicted_vs_actual": b.predicted_vs_actual,
                }
                for b in self.buckets
            ],
            "overall_calibration_error": self.overall_calibration_error,
            "is_overconfident": self.is_overconfident,
            "is_underconfident": self.is_underconfident,
            "recommended_adjustments": self.recommended_adjustments,
        }


@dataclass
class SuppressionEffectivenessRecord:
    """Effectiveness metrics for a suppression rule."""
    category: SuppressionCategory
    suppression_count: int
    protective_rate: float  # How often it prevented a loss
    false_suppression_rate: float  # How often it blocked a winner
    avg_signal_score_when_suppressed: float
    net_effect: float  # Positive = helpful, Negative = harmful
    
    def to_dict(self) -> dict:
        return {
            "category": self.category.value,
            "suppression_count": self.suppression_count,
            "protective_rate": self.protective_rate,
            "false_suppression_rate": self.false_suppression_rate,
            "avg_signal_score_when_suppressed": self.avg_signal_score_when_suppressed,
            "net_effect": self.net_effect,
        }


@dataclass
class SuppressionEffectivenessReport:
    """Report on suppression rule effectiveness."""
    timestamp: datetime
    suppressions: List[SuppressionEffectivenessRecord]
    total_suppressions: int
    protective_suppressions: List[str]
    harmful_suppressions: List[str]
    neutral_suppressions: List[str]
    over_restricted_categories: List[str]
    adjustment_recommendations: Dict[str, str]
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "suppressions": [s.to_dict() for s in self.suppressions],
            "total_suppressions": self.total_suppressions,
            "protective_suppressions": self.protective_suppressions,
            "harmful_suppressions": self.harmful_suppressions,
            "neutral_suppressions": self.neutral_suppressions,
            "over_restricted_categories": self.over_restricted_categories,
            "adjustment_recommendations": self.adjustment_recommendations,
        }


@dataclass
class RegimePerformance:
    """Performance metrics for a specific regime."""
    regime: str
    signal_count: int
    win_count: int
    win_rate: float
    avg_profit_loss: float
    expectancy: float
    best_for_direction: Optional[SignalDirection]
    
    def to_dict(self) -> dict:
        return {
            "regime": self.regime,
            "signal_count": self.signal_count,
            "win_rate": self.win_rate,
            "avg_profit_loss": self.avg_profit_loss,
            "expectancy": self.expectancy,
            "best_for_direction": self.best_for_direction.value if self.best_for_direction else None,
        }


@dataclass
class RegimePerformanceReport:
    """Report on regime-based performance."""
    timestamp: datetime
    day_type_performance: List[RegimePerformance]
    vwap_state_performance: List[RegimePerformance]
    volatility_performance: List[RegimePerformance]
    best_regimes_for_calls: List[str]
    best_regimes_for_puts: List[str]
    worst_environments: List[str]
    regime_confidence_modifiers: Dict[str, float]
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "day_type_performance": [r.to_dict() for r in self.day_type_performance],
            "vwap_state_performance": [r.to_dict() for r in self.vwap_state_performance],
            "volatility_performance": [r.to_dict() for r in self.volatility_performance],
            "best_regimes_for_calls": self.best_regimes_for_calls,
            "best_regimes_for_puts": self.best_regimes_for_puts,
            "worst_environments": self.worst_environments,
            "regime_confidence_modifiers": self.regime_confidence_modifiers,
        }


@dataclass
class TimingPerformance:
    """Performance metrics for a timing decision."""
    timing_decision: TimingDecision
    signal_count: int
    win_count: int
    win_rate: float
    avg_profit_loss: float
    expectancy: float
    
    def to_dict(self) -> dict:
        return {
            "timing_decision": self.timing_decision.value,
            "signal_count": self.signal_count,
            "win_rate": self.win_rate,
            "avg_profit_loss": self.avg_profit_loss,
            "expectancy": self.expectancy,
        }


@dataclass
class TimingPerformanceReport:
    """Report on timing decision performance."""
    timestamp: datetime
    timing_decisions: List[TimingPerformance]
    breakout_entry_performance: Optional[TimingPerformance]
    pullback_entry_performance: Optional[TimingPerformance]
    confirmation_performance: Optional[TimingPerformance]
    avoidance_performance: Optional[TimingPerformance]
    timing_recommendations: Dict[str, str]
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "timing_decisions": [t.to_dict() for t in self.timing_decisions],
            "timing_recommendations": self.timing_recommendations,
        }


@dataclass
class ScoreOptimizationProposal:
    """Advisory proposal for score optimization."""
    proposal_id: str
    timestamp: datetime
    proposal_type: str
    target_feature: Optional[str]
    current_weight: Optional[float]
    proposed_weight: Optional[float]
    expected_improvement: float
    confidence: float
    rationale: str
    requires_approval: bool
    status: str = "pending"
    
    def to_dict(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "timestamp": self.timestamp.isoformat(),
            "proposal_type": self.proposal_type,
            "target_feature": self.target_feature,
            "current_weight": self.current_weight,
            "proposed_weight": self.proposed_weight,
            "expected_improvement": self.expected_improvement,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "requires_approval": self.requires_approval,
            "status": self.status,
        }


@dataclass
class TacticalLearningSnapshot:
    """Complete learning snapshot for the tactical system."""
    timestamp: datetime
    total_signals_analyzed: int
    total_outcomes_resolved: int
    overall_win_rate: float
    overall_expectancy: float
    calibration_report: Optional[ConfidenceCalibrationReport]
    feature_report: Optional[FeaturePerformanceReport]
    suppression_report: Optional[SuppressionEffectivenessReport]
    regime_report: Optional[RegimePerformanceReport]
    timing_report: Optional[TimingPerformanceReport]
    pending_proposals: List[ScoreOptimizationProposal]
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "total_signals_analyzed": self.total_signals_analyzed,
            "total_outcomes_resolved": self.total_outcomes_resolved,
            "overall_win_rate": self.overall_win_rate,
            "overall_expectancy": self.overall_expectancy,
            "calibration_report": self.calibration_report.to_dict() if self.calibration_report else None,
            "feature_report": self.feature_report.to_dict() if self.feature_report else None,
            "suppression_report": self.suppression_report.to_dict() if self.suppression_report else None,
            "regime_report": self.regime_report.to_dict() if self.regime_report else None,
            "timing_report": self.timing_report.to_dict() if self.timing_report else None,
            "pending_proposals": [p.to_dict() for p in self.pending_proposals],
        }
