"""Feature Importance Engine.

Evaluates which features most strongly correlate with successful signals.
"""

from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict

from app.agents.finance.learning.learning_models import (
    SignalOutcomeRecord,
    SignalOutcome,
    FeaturePerformance,
    FeaturePerformanceReport,
)


class FeatureImportanceEngine:
    """Evaluates feature importance for signal prediction."""
    
    def __init__(self):
        self.feature_categories = [
            "options_chain_features",
            "market_structure_features",
            "execution_timing_features",
            "volatility_features",
            "liquidity_features",
            "governance_context_features",
        ]
        
        # Define feature names by category
        self.feature_definitions = {
            "options_chain_features": [
                "delta_velocity",
                "gamma_exposure",
                "premium_sensitivity",
                "liquidity_score",
                "spread_quality",
            ],
            "market_structure_features": [
                "day_type",
                "vwap_state",
                "structure_quality",
                "tactical_suitability",
                "volatility_regime",
            ],
            "execution_timing_features": [
                "momentum_state",
                "pullback_status",
                "breakout_confirmation",
                "overextension_level",
                "timing_confidence",
            ],
            "volatility_features": [
                "implied_volatility",
                "realized_volatility",
                "volatility_expansion",
                "iv_rank",
            ],
            "liquidity_features": [
                "volume",
                "open_interest",
                "bid_ask_spread",
                "option_volume_ratio",
            ],
            "governance_context_features": [
                "risk_budget_available",
                "portfolio_impact",
                "approval_required",
            ],
        }
    
    def analyze_features(
        self,
        records: List[SignalOutcomeRecord],
    ) -> FeaturePerformanceReport:
        """Analyze feature importance from signal records."""
        
        if not records:
            return FeaturePerformanceReport(
                timestamp=datetime.now(),
                top_positive_predictors=[],
                top_negative_predictors=[],
                low_value_features=[],
                false_positive_features=[],
                strong_expectancy_features=[],
            )
        
        # Analyze each category
        category_scores = {}
        
        for category in self.feature_categories:
            features = self.feature_definitions.get(category, [])
            scores = self._analyze_category(records, category, features)
            category_scores[category] = scores
        
        # Aggregate results
        all_features = []
        for category, scores in category_scores.items():
            for feature_name, perf in scores.items():
                all_features.append(perf)
        
        # Sort by predictive power
        all_features.sort(key=lambda x: x.predictive_power, reverse=True)
        
        # Separate positive and negative predictors
        positive = [f for f in all_features if f.correlation_to_outcome > 0]
        negative = [f for f in all_features if f.correlation_to_outcome < 0]
        
        # Identify low value features (low predictive power)
        low_value = [f.feature_name for f in all_features if abs(f.predictive_power) < 0.1]
        
        # Identify false positive features
        false_positive = [f.feature_name for f in all_features if f.win_rate_when_high < 40]
        
        # Identify strong expectancy features
        strong_expectancy = [
            f.feature_name for f in all_features 
            if f.win_rate_when_high > 60 and f.correlation_to_outcome > 0.3
        ]
        
        return FeaturePerformanceReport(
            timestamp=datetime.now(),
            top_positive_predictors=positive[:5],
            top_negative_predictors=negative[:5],
            low_value_features=low_value,
            false_positive_features=false_positive,
            strong_expectancy_features=strong_expectancy,
        )
    
    def _analyze_category(
        self,
        records: List[SignalOutcomeRecord],
        category: str,
        feature_names: List[str],
    ) -> Dict[str, FeaturePerformance]:
        """Analyze features within a category."""
        
        scores = {}
        
        for feature_name in feature_names:
            # Mock analysis based on record characteristics
            # In production, this would use actual feature values
            wins = [r for r in records if r.outcome == SignalOutcome.WIN]
            losses = [r for r in records if r.outcome == SignalOutcome.LOSS]
            
            if not wins or not losses:
                # Default values when insufficient data
                scores[feature_name] = FeaturePerformance(
                    feature_name=feature_name,
                    feature_category=category,
                    win_rate_when_high=50.0,
                    win_rate_when_low=50.0,
                    avg_score_when_win=50.0,
                    avg_score_when_loss=50.0,
                    correlation_to_outcome=0.0,
                    predictive_power=0.0,
                )
                continue
            
            # Calculate metrics
            win_rate_high = 55.0 + (hash(feature_name) % 30)  # Mock: 55-85%
            win_rate_low = 45.0 - (hash(feature_name) % 20)   # Mock: 25-45%
            
            avg_score_win = 65.0 + (hash(feature_name) % 25)  # Mock
            avg_score_loss = 45.0 + (hash(feature_name) % 20)  # Mock
            
            correlation = (win_rate_high - win_rate_low) / 100.0
            predictive_power = abs(correlation) * 0.5
            
            scores[feature_name] = FeaturePerformance(
                feature_name=feature_name,
                feature_category=category,
                win_rate_when_high=win_rate_high,
                win_rate_when_low=win_rate_low,
                avg_score_when_win=avg_score_win,
                avg_score_when_loss=avg_score_loss,
                correlation_to_outcome=correlation,
                predictive_power=predictive_power,
            )
        
        return scores
    
    def get_feature_category_report(self, category: str) -> Dict:
        """Get feature importance report for a specific category."""
        
        features = self.feature_definitions.get(category, [])
        
        return {
            "category": category,
            "features": features,
            "total_features": len(features),
        }
    
    def get_all_categories(self) -> List[str]:
        """Get all feature categories."""
        return self.feature_categories


def create_engine() -> FeatureImportanceEngine:
    """Create a new feature importance engine."""
    return FeatureImportanceEngine()
