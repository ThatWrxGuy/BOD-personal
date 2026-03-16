"""Regime Classifier - BB-FIN-014"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

from app.finance.market_intelligence.market_intelligence_models import (
    CrossAssetSnapshot,
    RegimeState,
    RegimeType,
    ConfidenceLevel,
    RiskPosture,
    VolatilityState,
    BreadthState,
    LiquidityState,
    MacroPressureState,
    SignalScore,
    RegimeTransitionAlert,
)

logger = logging.getLogger(__name__)


class RegimeClassifier:
    """Classifies market regime from all signal inputs."""

    # Transition probability thresholds
    TRANSITION_THRESHOLD = 0.3

    def __init__(self):
        self._prior_regime: Optional[RegimeType] = None
        self._regime_stability_counter: int = 0

    def classify_regime(
        self,
        snapshot: CrossAssetSnapshot,
        signal_scores: Dict[str, SignalScore],
    ) -> RegimeState:
        """Classify the current regime from signal scores."""
        
        # Extract key scores
        trend_score = signal_scores.get("trend", SignalScore(family="trend", score=0.0, direction="neutral", confidence=ConfidenceLevel.LOW))
        breadth_score = signal_scores.get("breadth", SignalScore(family="breadth", score=0.0, direction="neutral", confidence=ConfidenceLevel.LOW))
        volatility_score = signal_scores.get("volatility", SignalScore(family="volatility", score=0.0, direction="neutral", confidence=ConfidenceLevel.LOW))
        correlation_score = signal_scores.get("correlation", SignalScore(family="correlation", score=0.0, direction="neutral", confidence=ConfidenceLevel.LOW))
        liquidity_score = signal_scores.get("liquidity", SignalScore(family="liquidity", score=0.0, direction="neutral", confidence=ConfidenceLevel.LOW))
        macro_score = signal_scores.get("macro_pressure", SignalScore(family="macro_pressure", score=0.0, direction="neutral", confidence=ConfidenceLevel.LOW))

        # Calculate aggregate scores
        overall_risk = self._calculate_overall_risk(
            trend_score, volatility_score, liquidity_score, macro_score
        )
        environment_support = self._calculate_environment_support(
            trend_score, breadth_score, correlation_score
        )

        # Determine regime type
        primary_regime = self._determine_regime_type(
            overall_risk, environment_support, volatility_score, trend_score
        )

        # Determine confidence
        confidence = self._determine_confidence(signal_scores)

        # Check for transition
        is_transitioning, transition_prob = self._check_transition(
            primary_regime, signal_scores
        )

        # Determine risk posture
        risk_posture = self._determine_risk_posture(primary_regime, overall_risk)

        # Determine state indicators
        volatility_state = self._infer_volatility_state(volatility_score)
        breadth_state = self._infer_breadth_state(breadth_score)
        liquidity_state = self._infer_liquidity_state(liquidity_score)
        macro_state = self._infer_macro_state(macro_score)

        # Cross-asset confirmation
        cross_asset_confirm = self._check_cross_asset_confirmation(signal_scores)

        # Build factors
        supporting = self._get_supporting_factors(signal_scores)
        risk_factors = self._get_risk_factors(signal_scores)

        # Build flags
        flags = self._build_flags(signal_scores, primary_regime)

        # Build reasoning
        reasoning = self._build_reasoning(primary_regime, overall_risk, signal_scores)

        # Store for transition detection
        if self._prior_regime and self._prior_regime != primary_regime:
            self._regime_stability_counter = 0
        else:
            self._regime_stability_counter += 1

        regime = RegimeState(
            timestamp=datetime.utcnow(),
            primary_regime=primary_regime,
            confidence=confidence,
            is_transitioning=is_transitioning,
            transition_probability=transition_prob,
            prior_regime=self._prior_regime,
            risk_posture=risk_posture,
            volatility_state=volatility_state,
            breadth_state=breadth_state,
            liquidity_state=liquidity_state,
            macro_pressure_state=macro_state,
            cross_asset_confirmation=cross_asset_confirm,
            top_supporting_factors=supporting[:5],
            top_risk_factors=risk_factors[:5],
            flags=flags,
            classification_reasoning=reasoning,
        )

        self._prior_regime = primary_regime
        return regime

    def _calculate_overall_risk(
        self,
        trend: SignalScore,
        volatility: SignalScore,
        liquidity: SignalScore,
        macro: SignalScore,
    ) -> float:
        """Calculate overall risk score (-1 to 1)."""
        weights = {
            "trend": 0.25,
            "volatility": 0.30,
            "liquidity": 0.25,
            "macro": 0.20,
        }

        score = (
            trend.score * weights["trend"]
            + volatility.score * weights["volatility"]
            + liquidity.score * weights["liquidity"]
            + macro.score * weights["macro"]
        )

        return max(-1.0, min(1.0, score))

    def _calculate_environment_support(
        self,
        trend: SignalScore,
        breadth: SignalScore,
        correlation: SignalScore,
    ) -> float:
        """Calculate environment support score (0 to 1)."""
        # Higher = more supportive
        # Trend positive, breadth positive, correlation low = supportive
        support = (
            (trend.score + 1) / 2 * 0.4  # Normalize to 0-1
            + (breadth.score + 1) / 2 * 0.3
            + (correlation.score + 1) / 2 * 0.3  # Low correlation = higher score
        )

        return max(0.0, min(1.0, support))

    def _determine_regime_type(
        self,
        overall_risk: float,
        environment_support: float,
        volatility: SignalScore,
        trend: SignalScore,
    ) -> RegimeType:
        """Determine the primary regime type."""
        
        # Check for crisis conditions first
        if overall_risk < -0.6:
            if volatility.score < -0.7:
                return RegimeType.VOLATILITY_STRESS
            return RegimeType.RISK_OFF_DEFENSIVE

        if environment_support < 0.3:
            return RegimeType.RISK_OFF_DEFENSIVE

        # Check for liquidity dislocation
        if liquidity_state_from_score(volatility) == LiquidityState.STRESSED:
            return RegimeType.LIQUIDITY_DISLOCATION

        # Check for transition/rotation
        if abs(trend.score) < 0.2 and environment_support < 0.5:
            return RegimeType.ROTATION_TRANSITION

        # Risk-on states
        if overall_risk > 0.3 and trend.score > 0.3:
            if abs(trend.score) > 0.6:
                return RegimeType.RISK_ON_TREND
            return RegimeType.RISK_ON_MOMENTUM

        # Neutral/mixed
        if abs(overall_risk) < 0.3:
            if abs(trend.score) < 0.15:
                return RegimeType.RANGE_COMPRESSION
            return RegimeType.NEUTRAL_MIXED

        # Risk-off
        if overall_risk < -0.2:
            return RegimeType.RISK_OFF_DEFENSIVE

        return RegimeType.NEUTRAL_MIXED

    def _determine_confidence(self, signal_scores: Dict[str, SignalScore]) -> ConfidenceLevel:
        """Determine classification confidence."""
        # Count high-confidence signals
        high_conf = sum(
            1 for s in signal_scores.values()
            if s.confidence == ConfidenceLevel.HIGH
        )
        moderate_conf = sum(
            1 for s in signal_scores.values()
            if s.confidence == ConfidenceLevel.MODERATE
        )

        total = len(signal_scores)
        if total == 0:
            return ConfidenceLevel.LOW

        if high_conf >= total * 0.6:
            return ConfidenceLevel.HIGH
        elif (high_conf + moderate_conf) >= total * 0.5:
            return ConfidenceLevel.MODERATE
        else:
            return ConfidenceLevel.LOW

    def _check_transition(
        self,
        current_regime: RegimeType,
        signal_scores: Dict[str, SignalScore],
    ) -> Tuple[bool, float]:
        """Check for potential regime transition."""
        if not self._prior_regime:
            return False, 0.0

        if current_regime == self._prior_regime:
            return False, 0.0

        # Check stability
        if self._regime_stability_counter < 2:
            return True, 0.7  # Likely transition

        # Check signal divergence
        trend_score = signal_scores.get("trend")
        volatility_score = signal_scores.get("volatility")

        if trend_score and volatility_score:
            if abs(trend_score.score - volatility_score.score) > 0.5:
                return True, 0.5

        return False, 0.2

    def _determine_risk_posture(
        self,
        regime: RegimeType,
        overall_risk: float,
    ) -> RiskPosture:
        """Determine recommended risk posture."""
        posture_map = {
            RegimeType.RISK_ON_TREND: RiskPosture.AGGRESSIVE,
            RegimeType.RISK_ON_MOMENTUM: RiskPosture.GROWTH,
            RegimeType.NEUTRAL_MIXED: RiskPosture.NEUTRAL,
            RegimeType.ROTATION_TRANSITION: RiskPosture.NEUTRAL,
            RegimeType.RISK_OFF_DEFENSIVE: RiskPosture.DEFENSIVE,
            RegimeType.VOLATILITY_STRESS: RiskPosture.CRISIS,
            RegimeType.LIQUIDITY_DISLOCATION: RiskPosture.CRISIS,
            RegimeType.RANGE_COMPRESSION: RiskPosture.NEUTRAL,
            RegimeType.MEAN_REVERSION: RiskPosture.GROWTH,
            RegimeType.MACRO_EVENT_UNCERTAINTY: RiskPosture.DEFENSIVE,
        }

        return posture_map.get(regime, RiskPosture.NEUTRAL)

    def _infer_volatility_state(self, score: SignalScore) -> VolatilityState:
        """Infer volatility state from score."""
        if score.score > 0.5:
            return VolatilityState.COMPRESSED
        elif score.score > 0:
            return VolatilityState.NORMAL
        elif score.score > -0.5:
            return VolatilityState.EXPANDING
        else:
            return VolatilityState.STRESSED

    def _infer_breadth_state(self, score: SignalScore) -> BreadthState:
        """Infer breadth state from score."""
        if score.score > 0.6:
            return BreadthState.STRONG_BREADTH
        elif score.score > 0.2:
            return BreadthState.MODERATE_BREADTH
        elif score.score > -0.2:
            return BreadthState.NARROW_LEAD
        else:
            return BreadthState.WEAK_BREADTH

    def _infer_liquidity_state(self, score: SignalScore) -> LiquidityState:
        """Infer liquidity state from score."""
        if score.score > 0.6:
            return LiquidityState.ABUNDANT
        elif score.score > 0.2:
            return LiquidityState.NORMAL
        elif score.score > -0.2:
            return LiquidityState.TIGHT
        else:
            return LiquidityState.STRESSED

    def _infer_macro_state(self, score: SignalScore) -> MacroPressureState:
        """Infer macro state from score."""
        if score.score > 0.3:
            return MacroPressureState.STIMULUS
        elif score.score > -0.3:
            return MacroPressureState.NEUTRAL
        elif score.score > -0.6:
            return MacroPressureState.TIGHTENING
        else:
            return MacroPressureState.STRESS

    def _check_cross_asset_confirmation(self, scores: Dict[str, SignalScore]) -> bool:
        """Check if multiple asset classes confirm the regime."""
        positive = sum(1 for s in scores.values() if s.score > 0.1)
        negative = sum(1 for s in scores.values() if s.score < -0.1)
        
        total = len(scores)
        if total == 0:
            return False

        return abs(positive - negative) >= total * 0.4

    def _get_supporting_factors(self, scores: Dict[str, SignalScore]) -> List[str]:
        """Get list of supporting factors."""
        factors = []
        for name, score in scores.items():
            if score.score > 0.2:
                factors.append(f"{name}: {score.direction} ({score.score:.2f})")
        return factors

    def _get_risk_factors(self, scores: Dict[str, SignalScore]) -> List[str]:
        """Get list of risk factors."""
        factors = []
        for name, score in scores.items():
            if score.score < -0.2:
                factors.append(f"{name}: {score.direction} ({score.score:.2f})")
        return factors

    def _build_flags(self, scores: Dict[str, SignalScore], regime: RegimeType) -> List[str]:
        """Build regime flags."""
        flags = []

        # Check for specific conditions
        vol_score = scores.get("volatility")
        if vol_score and vol_score.score < -0.6:
            flags.append("volatility_expansion")

        breadth_score = scores.get("breadth")
        if breadth_score and breadth_score.score < -0.3:
            flags.append("low_breadth")

        corr_score = scores.get("correlation")
        if corr_score and corr_score.score < -0.3:
            flags.append("high_correlation")

        macro_score = scores.get("macro_pressure")
        if macro_score and macro_score.score < -0.4:
            flags.append("macro_tightening")

        # Add regime-specific flags
        if regime in [RegimeType.RISK_ON_TREND, RegimeType.RISK_ON_MOMENTUM]:
            flags.append("risk_on")
        elif regime in [RegimeType.RISK_OFF_DEFENSIVE, RegimeType.VOLATILITY_STRESS]:
            flags.append("risk_off")

        return flags

    def _build_reasoning(
        self,
        regime: RegimeType,
        overall_risk: float,
        scores: Dict[str, SignalScore],
    ) -> List[str]:
        """Build classification reasoning trace."""
        reasoning = [
            f"Primary regime: {regime.value}",
            f"Overall risk score: {overall_risk:.2f}",
        ]

        # Add key signal contributions
        if "trend" in scores:
            reasoning.append(f"Trend: {scores['trend'].score:.2f}")
        if "volatility" in scores:
            reasoning.append(f"Volatility: {scores['volatility'].score:.2f}")
        if "breadth" in scores:
            reasoning.append(f"Breadth: {scores['breadth'].score:.2f}")

        return reasoning


def liquidity_state_from_score(score: SignalScore) -> LiquidityState:
    """Helper to get liquidity state from score."""
    if score.score > 0.6:
        return LiquidityState.ABUNDANT
    elif score.score > 0.2:
        return LiquidityState.NORMAL
    elif score.score > -0.2:
        return LiquidityState.TIGHT
    else:
        return LiquidityState.STRESSED


# Singleton
_classifier: Optional[RegimeClassifier] = None


def get_regime_classifier() -> RegimeClassifier:
    """Get the singleton RegimeClassifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = RegimeClassifier()
    return _classifier
