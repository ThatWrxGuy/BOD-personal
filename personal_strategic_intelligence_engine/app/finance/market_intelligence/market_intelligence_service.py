"""Market Intelligence Service - BB-FIN-014"""

from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.finance.market_intelligence.data_normalizer import DataNormalizer, get_normalizer
from app.finance.market_intelligence.trend_engine import TrendEngine, get_trend_engine
from app.finance.market_intelligence.breadth_engine import BreadthEngine, get_breadth_engine
from app.finance.market_intelligence.volatility_engine import VolatilityEngine, get_volatility_engine
from app.finance.market_intelligence.correlation_engine import CorrelationEngine, get_correlation_engine
from app.finance.market_intelligence.macro_pressure_engine import MacroPressureEngine, get_macro_pressure_engine
from app.finance.market_intelligence.liquidity_stress_engine import LiquidityStressEngine, get_liquidity_stress_engine
from app.finance.market_intelligence.regime_classifier import RegimeClassifier, get_regime_classifier
from app.finance.market_intelligence.regime_policy_mapper import RegimePolicyMapper, get_regime_policy_mapper
from app.finance.market_intelligence.market_intelligence_models import (
    CrossAssetSnapshot,
    RegimeState,
    RegimeScorecard,
    RegimePolicy,
    MarketIntelligenceReport,
    SignalScore,
    AssetSignal,
    RegimeHistoryEntry,
    RegimeTransitionAlert,
)

logger = logging.getLogger(__name__)


class MarketIntelligenceService:
    """Orchestrates the full market intelligence cycle."""

    def __init__(self):
        self.normalizer = get_normalizer()
        self.trend_engine = get_trend_engine()
        self.breadth_engine = get_breadth_engine()
        self.volatility_engine = get_volatility_engine()
        self.correlation_engine = get_correlation_engine()
        self.macro_engine = get_macro_pressure_engine()
        self.liquidity_engine = get_liquidity_stress_engine()
        self.classifier = get_regime_classifier()
        self.policy_mapper = get_regime_policy_mapper()

        self._regime_history: List[RegimeHistoryEntry] = []
        self._last_report: Optional[MarketIntelligenceReport] = None

    def analyze_market(
        self,
        equity_prices: Optional[Dict[str, float]] = None,
        sector_prices: Optional[Dict[str, float]] = None,
        bond_prices: Optional[Dict[str, float]] = None,
        commodity_prices: Optional[Dict[str, float]] = None,
        fx_prices: Optional[Dict[str, float]] = None,
        crypto_prices: Optional[Dict[str, float]] = None,
        vix_level: Optional[float] = None,
        yields: Optional[Dict[str, float]] = None,
        credit_spreads: Optional[Dict[str, float]] = None,
    ) -> MarketIntelligenceReport:
        """Run full market intelligence analysis."""
        
        logger.info("Starting market intelligence analysis")

        # Use defaults for demo data if not provided
        if equity_prices is None:
            equity_prices = {"SPY": 450.0, "QQQ": 380.0, "IWM": 200.0, "DIA": 350.0}
        if sector_prices is None:
            sector_prices = {
                "XLF": 42.0, "XLK": 180.0, "XLE": 85.0, "XLV": 145.0,
                "XLI": 115.0, "XLP": 75.0, "XLY": 165.0, "XLU": 70.0,
            }
        if bond_prices is None:
            bond_prices = {"TLT": 95.0, "IEF": 98.0, "SHY": 82.0}
        if commodity_prices is None:
            commodity_prices = {"GLD": 185.0, "USO": 75.0}
        if fx_prices is None:
            fx_prices = {"UUP": 26.0}
        if crypto_prices is None:
            crypto_prices = {"BTC": 42000.0, "ETH": 2500.0}
        if yields is None:
            yields = {"2Y": 4.5, "10Y": 4.2, "30Y": 4.4}

        # Step 1: Normalize data
        snapshot = self.normalizer.normalize_market_data(
            equity_prices=equity_prices,
            sector_prices=sector_prices,
            bond_prices=bond_prices,
            commodity_prices=commodity_prices,
            fx_prices=fx_prices,
            crypto_prices=crypto_prices,
            vix_level=vix_level,
            yields=yields,
            credit_spreads=credit_spreads,
        )

        # Step 2: Generate signal scores
        signal_scores = self._generate_signal_scores(snapshot)

        # Step 3: Classify regime
        regime = self.classifier.classify_regime(snapshot, signal_scores)

        # Step 4: Map to policy
        policy = self.policy_mapper.map_regime_to_policy(regime)

        # Step 5: Build scorecard
        scorecard = self._build_scorecard(signal_scores)

        # Step 6: Check for transition alerts
        transition_alert = self._check_transition_alert(regime)

        # Step 7: Generate executive summary
        executive_summary = self._generate_executive_summary(regime, policy)

        # Step 8: Update history
        self._update_history(regime)

        # Build report
        report = MarketIntelligenceReport(
            timestamp=datetime.utcnow(),
            executive_summary=executive_summary,
            regime=regime,
            scorecard=scorecard,
            policy=policy,
            cross_asset_snapshot=snapshot,
            transition_alert=transition_alert,
            regime_history=self._regime_history[-10:],
            data_freshness=self._get_data_freshness(),
        )

        self._last_report = report
        logger.info(f"Market intelligence complete: {regime.primary_regime.value}")

        return report

    def _generate_signal_scores(self, snapshot: CrossAssetSnapshot) -> Dict[str, SignalScore]:
        """Generate all signal scores."""
        scores = {}

        # Trend analysis
        trend_score = self.trend_engine.analyze_cross_asset_trends(snapshot)
        scores["trend"] = trend_score

        # Breadth analysis
        breadth_score = self.breadth_engine.generate_breadth_score(snapshot)
        scores["breadth"] = breadth_score

        # Volatility analysis
        volatility_score = self.volatility_engine.generate_volatility_score(snapshot)
        scores["volatility"] = volatility_score

        # Correlation analysis
        correlation_score = self.correlation_engine.generate_correlation_score(snapshot)
        scores["correlation"] = correlation_score

        # Liquidity analysis
        liquidity_score = self.liquidity_engine.generate_liquidity_score(snapshot)
        scores["liquidity"] = liquidity_score

        # Macro pressure analysis
        macro_score = self.macro_engine.generate_macro_pressure_score(snapshot)
        scores["macro_pressure"] = macro_score

        # Cross-asset confirmation
        confirmation_score = self._calculate_cross_asset_confirmation(scores)
        scores["cross_asset_confirmation"] = confirmation_score

        # Risk appetite
        risk_appetite_score = self._calculate_risk_appetite(scores)
        scores["risk_appetite"] = risk_appetite_score

        return scores

    def _calculate_cross_asset_confirmation(self, scores: Dict[str, SignalScore]) -> SignalScore:
        """Calculate cross-asset confirmation score."""
        positive = sum(1 for s in scores.values() if s.score > 0.1)
        negative = sum(1 for s in scores.values() if s.score < -0.1)
        
        if positive > negative:
            score = min(1.0, (positive - negative) / len(scores))
            direction = "positive"
        elif negative > positive:
            score = max(-1.0, -(negative - positive) / len(scores))
            direction = "negative"
        else:
            score = 0.0
            direction = "neutral"

        return SignalScore(
            family="cross_asset_confirmation",
            score=score,
            direction=direction,
            confidence=ConfidenceLevel.MODERATE,
            contributing_factors=["Cross-asset signal alignment"],
            timestamp=datetime.utcnow(),
        )

    def _calculate_risk_appetite(self, scores: Dict[str, SignalScore]) -> SignalScore:
        """Calculate overall risk appetite score."""
        # Weight key factors for risk appetite
        weights = {
            "trend": 0.25,
            "volatility": 0.20,
            "liquidity": 0.20,
            "macro_pressure": 0.15,
            "correlation": 0.10,
            "breadth": 0.10,
        }

        total = 0.0
        for family, weight in weights.items():
            if family in scores:
                total += scores[family].score * weight

        direction = "positive" if total > 0.2 else ("negative" if total < -0.2 else "neutral")

        return SignalScore(
            family="risk_appetite",
            score=total,
            direction=direction,
            confidence=ConfidenceLevel.MODERATE,
            contributing_factors=[f"Composite risk appetite: {total:.2f}"],
            timestamp=datetime.utcnow(),
        )

    def _build_scorecard(self, scores: Dict[str, SignalScore]) -> RegimeScorecard:
        """Build regime scorecard from signal scores."""
        
        # Calculate overall risk score
        overall = sum(s.score for s in scores.values()) / len(scores)
        
        # Calculate environment support
        env_keys = ["trend", "breadth", "correlation"]
        env_scores = [scores[k].score for k in env_keys if k in scores]
        environment = sum(env_scores) / len(env_scores) if env_scores else 0.5

        return RegimeScorecard(
            timestamp=datetime.utcnow(),
            trend_score=scores.get("trend", SignalScore(family="trend", score=0, direction="neutral", confidence=ConfidenceLevel.LOW)),
            breadth_score=scores.get("breadth", SignalScore(family="breadth", score=0, direction="neutral", confidence=ConfidenceLevel.LOW)),
            volatility_score=scores.get("volatility", SignalScore(family="volatility", score=0, direction="neutral", confidence=ConfidenceLevel.LOW)),
            correlation_score=scores.get("correlation", SignalScore(family="correlation", score=0, direction="neutral", confidence=ConfidenceLevel.LOW)),
            liquidity_score=scores.get("liquidity", SignalScore(family="liquidity", score=0, direction="neutral", confidence=ConfidenceLevel.LOW)),
            macro_pressure_score=scores.get("macro_pressure", SignalScore(family="macro_pressure", score=0, direction="neutral", confidence=ConfidenceLevel.LOW)),
            credit_stress_score=SignalScore(family="credit_stress", score=0, direction="neutral", confidence=ConfidenceLevel.LOW),
            cross_asset_confirmation=scores.get("cross_asset_confirmation", SignalScore(family="cross_asset_confirmation", score=0, direction="neutral", confidence=ConfidenceLevel.LOW)),
            risk_appetite_score=scores.get("risk_appetite", SignalScore(family="risk_appetite", score=0, direction="neutral", confidence=ConfidenceLevel.LOW)),
            overall_risk_score=overall,
            environment_support=environment,
        )

    def _check_transition_alert(self, regime: RegimeState) -> Optional[RegimeTransitionAlert]:
        """Check for potential regime transition."""
        if not regime.is_transitioning:
            return None

        return RegimeTransitionAlert(
            timestamp=datetime.utcnow(),
            current_regime=regime.primary_regime,
            potential_regimes=[regime.primary_regime],  # Would be predicted regimes
            transition_probability=regime.transition_probability,
            warning_signals=regime.top_risk_factors,
            severity="moderate" if regime.transition_probability < 0.7 else "high",
        )

    def _generate_executive_summary(self, regime: RegimeState, policy: RegimePolicy) -> str:
        """Generate executive summary."""
        summaries = {
            "RISK_ON_TREND": "Market in strong uptrend with broad participation. Confidence is high. Recommend increasing exposure and riding the trend.",
            "RISK_ON_MOMENTUM": "Market showing positive momentum across asset classes. Supportive environment for growth positions.",
            "NEUTRAL_MIXED": "Market in neutral/mixed state. No clear directional bias. Recommend reduced exposure and quality focus.",
            "ROTATION_TRANSITION": "Market undergoing rotation or transition. Leadership may be shifting. Recommend caution and reduced exposure.",
            "RISK_OFF_DEFENSIVE": "Risk-off environment detected. Defensive posture recommended with minimal exposure.",
            "VOLATILITY_STRESS": "Volatility elevated significantly. Extreme caution advised. Consider hedging all positions.",
            "LIQUIDITY_DISLOCATION": "Liquidity stress detected. Capital preservation priority. Avoid new positions.",
            "RANGE_COMPRESSION": "Low volatility / compressed range. Consider range-bound strategies and volatility selling.",
            "MEAN_REVERSION": "Mean reversion conditions. Look for oversold opportunities.",
            "MACRO_EVENT_UNCERTAINTY": "Macro uncertainty elevated. Reduce exposure ahead of potential events.",
        }

        base = summaries.get(regime.primary_regime.value, "Market conditions unclear.")
        
        return f"{base} Risk posture: {policy.risk_posture.value}. Recommended exposure: {policy.max_gross_exposure:.0%}."

    def _update_history(self, regime: RegimeState) -> None:
        """Update regime history."""
        entry = RegimeHistoryEntry(
            timestamp=regime.timestamp,
            regime=regime.primary_regime,
            confidence=regime.confidence,
            key_factors=regime.top_supporting_factors[:3],
        )
        
        self._regime_history.append(entry)
        
        # Keep only last 100 entries
        if len(self._regime_history) > 100:
            self._regime_history = self._regime_history[-100:]

    def _get_data_freshness(self) -> Dict[str, str]:
        """Get data freshness indicators."""
        return {
            "market_data": "realtime",
            "regime_analysis": "current",
            "policy": "current",
        }

    def get_current_regime(self) -> Optional[RegimeState]:
        """Get the current regime if available."""
        if self._last_report:
            return self._last_report.regime
        return None

    def get_regime_history(self, limit: int = 20) -> List[RegimeHistoryEntry]:
        """Get regime history."""
        return self._regime_history[-limit:]


# Import missing enum
from app.finance.market_intelligence.market_intelligence_models import ConfidenceLevel

# Singleton
_service: Optional[MarketIntelligenceService] = None


def get_market_intelligence_service() -> MarketIntelligenceService:
    """Get the singleton MarketIntelligenceService instance."""
    global _service
    if _service is None:
        _service = MarketIntelligenceService()
    return _service
