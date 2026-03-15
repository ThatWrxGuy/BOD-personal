"""Feature Scoring Engine.

Determines which features have the greatest influence on outcomes.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass

from app.intelligence.alpha_engine.alpha_models import StrategyFeature


@dataclass
class FeatureImportance:
    """Feature importance score."""
    feature_name: str
    impact_score: float
    confidence: float
    sample_size: int


class FeatureScoringEngine:
    """Determines feature importance."""
    
    def __init__(self):
        self.feature_history = []
    
    def score_features(
        self,
        trades: List[Dict],
        features: List[str],
    ) -> List[FeatureImportance]:
        """Score features based on trade outcomes."""
        
        importance_scores = []
        
        for feature in features:
            # Calculate correlation with profit
            feature_values = [t.get(feature, 0) for t in trades]
            pnl_values = [t.get("pnl", 0) for t in trades]
            
            # Simple correlation
            if len(feature_values) > 10:
                correlation = self._calculate_correlation(feature_values, pnl_values)
                impact_score = abs(correlation)
                
                importance_scores.append(FeatureImportance(
                    feature_name=feature,
                    impact_score=impact_score,
                    confidence=min(0.9, len(trades) / 100),
                    sample_size=len(trades),
                ))
        
        # Sort by impact
        importance_scores.sort(key=lambda x: x.impact_score, reverse=True)
        
        return importance_scores
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation."""
        
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denom_x = sum((x[i] - mean_x) ** 2 for i in range(n)) ** 0.5
        denom_y = sum((y[i] - mean_y) ** 2 for i in range(n)) ** 0.5
        
        if denom_x == 0 or denom_y == 0:
            return 0.0
        
        return numerator / (denom_x * denom_y)
    
    def identify_key_features(
        self,
        trades: List[Dict],
    ) -> List[StrategyFeature]:
        """Identify key features from trade history."""
        
        # Standard features to evaluate
        features_to_evaluate = [
            "vwap_distance",
            "gamma_exposure",
            "distance_from_strike",
            "time_of_day",
            "relative_volume",
            "spread_width",
            "iv_rank",
            "momentum",
        ]
        
        # Score each feature
        importance_scores = self.score_features(trades, features_to_evaluate)
        
        # Convert to StrategyFeature objects
        key_features = []
        for imp in importance_scores:
            if imp.impact_score > 0.1:  # Only significant features
                feature = StrategyFeature(
                    name=imp.feature_name,
                    description=f"Feature: {imp.feature_name}",
                    feature_type="market",
                    importance_score=imp.impact_score,
                    stability_score=imp.confidence,
                )
                key_features.append(feature)
        
        return key_features
    
    def track_feature_performance(
        self,
        feature_name: str,
        performance: List[Dict],
    ) -> Dict:
        """Track feature performance over time."""
        
        return {
            "feature": feature_name,
            "sample_size": len(performance),
            "average_impact": sum(p.get("impact", 0) for p in performance) / len(performance) if performance else 0,
            "trend": "improving" if len(performance) > 5 else "stable",
        }


def create_engine() -> FeatureScoringEngine:
    """Create feature scoring engine."""
    return FeatureScoringEngine()
