"""Signal Calibration Module.

Provides signal weighting, freshness, persistence, and cross-domain calibration.
"""
from app.signal_calibration.calibration_models import (
    CalibratedSignal,
    CalibrationSummary,
    CalibrationSummary,
    CrossSignalBalanceResult,
    FreshnessLevel,
    PersistenceLevel,
    SeverityLevel,
    SignalFreshnessScore,
    SignalPersistenceProfile,
    SignalSeverityScore,
    SignalWeightProfile,
    SourceReliabilityScore,
    TemporalContext,
    TemporalSignalContext,
    LIVE_EXECUTION_ENABLED,
    CALIBRATION_MODE,
)
from app.signal_calibration.calibration_controller import (
    CalibrationController,
    get_calibration_controller,
)
from app.signal_calibration.calibration_store import (
    CalibrationStore,
    get_calibration_store,
)
from app.signal_calibration.cross_signal_balancer import (
    CrossSignalBalancer,
    get_cross_signal_balancer,
)
from app.signal_calibration.freshness_evaluator import (
    FreshnessEvaluator,
    get_freshness_evaluator,
)
from app.signal_calibration.persistence_tracker import (
    PersistenceTracker,
    get_persistence_tracker,
)
from app.signal_calibration.severity_scorer import (
    SeverityScorer,
    get_severity_scorer,
)
from app.signal_calibration.signal_weight_engine import (
    SignalWeightEngine,
    get_signal_weight_engine,
)
from app.signal_calibration.source_reliability_adjuster import (
    SourceReliabilityAdjuster,
    get_source_reliability_adjuster,
)
from app.signal_calibration.temporal_context_analyzer import (
    TemporalContextAnalyzer,
    get_temporal_context_analyzer,
)

__all__ = [
    # Models
    "CalibratedSignal",
    "CalibrationSummary",
    "CrossSignalBalanceResult",
    "FreshnessLevel",
    "PersistenceLevel",
    "SeverityLevel",
    "SignalFreshnessScore",
    "SignalPersistenceProfile",
    "SignalSeverityScore",
    "SignalWeightProfile",
    "SourceReliabilityScore",
    "TemporalContext",
    "TemporalSignalContext",
    # Safety
    "LIVE_EXECUTION_ENABLED",
    "CALIBRATION_MODE",
    # Components
    "CalibrationController",
    "get_calibration_controller",
    "CalibrationStore",
    "get_calibration_store",
    "CrossSignalBalancer",
    "get_cross_signal_balancer",
    "FreshnessEvaluator",
    "get_freshness_evaluator",
    "PersistenceTracker",
    "get_persistence_tracker",
    "SeverityScorer",
    "get_severity_scorer",
    "SignalWeightEngine",
    "get_signal_weight_engine",
    "SourceReliabilityAdjuster",
    "get_source_reliability_adjuster",
    "TemporalContextAnalyzer",
    "get_temporal_context_analyzer",
]
