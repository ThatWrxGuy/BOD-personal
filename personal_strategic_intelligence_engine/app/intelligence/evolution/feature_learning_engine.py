"""Feature Learning Engine.

Discovers which features most strongly influence outcomes.
"""

from datetime import datetime
from typing import List, Dict, Optional
import random

from app.intelligence.evolution.evolution_models import (
    FeatureImportance,
)


class FeatureLearningEngine:
    """Learns feature importance from signal data."""
    
    def __init__(self):
        self.feature_categories = [
            "options_chain",
            "market_structure",
            "execution_timing",
            "volatility",
            "liquidity",
            "governance",
        ]
        
        self.feature_definitions = {
            "options_chain": [
                "delta_velocity",
                "gamma_exposure", 
                "premium_sensitivity",
                "liquidity_score",
                "spread_quality",
            ],
            "market_structure": [
                "structure_quality",
                "day_type_score",
                "vwap_distance",
                "level_proximity",
            ],
            "execution_timing": [
                "momentum_strength",
                "pullback_depth",
                "breakout_quality",
                "timing_confidence",
            ],
            "volatility": [
                "implied_volatility",
                "realized_volatility",
                "iv_rank",
                "volatility_trend",
            ],
            "liquidity": [
                "volume_ratio",
                "bid_ask_spread",
                "open_interest",
                "option_volume",
            ],
            "governance": [
                "risk_budget_ratio",
                "portfolio_impact",
                "approval_level",
            ],
        }
    
    def learn_features(
        self,
        signal_records: List[Dict],
    ) -> List[FeatureImportance]:
        """Learn feature importance from signal data."""
        
        features = []
        
        for category, feature_names in self.feature_definitions.items():
            for feature_name in feature_names:
                importance = self._calculate_importance(signal_records, feature_name, category)
                features.append(importance)
        
        # Sort by importance
        features.sort(key=lambda f: f.importance_score, reverse=True)
        
        return features
    
    def _calculate_importance(
        self,
        records: List[Dict],
        feature_name: str,
        category: str,
    ) -> FeatureImportance:
        """Calculate importance for a feature."""
        
        # In production, would use actual statistical analysis
        # Mock implementation based on feature characteristics
        
        base_importance = random.uniform(0.3, 0.9)
        correlation = random.uniform(-0.3, 0.6)
        
        # Determine noise level
        if feature_name in ["bid_ask_spread", "option_volume"]:
            noise = random.uniform(0.2, 0.5)
        else:
            noise = random.uniform(0.05, 0.2)
        
        # Determine interaction effects
        interactions = self._find_interactions(feature_name)
        
        return FeatureImportance(
            feature_name=feature_name,
            importance_score=base_importance,
            category=category,
            correlation=correlation,
            interaction_effects=interactions,
            noise_level=noise,
        )
    
    def _find_interactions(self, feature_name: str) -> List[str]:
        """Find feature interaction effects."""
        
        interactions_map = {
            "delta_velocity": ["structure_quality", "momentum_strength"],
            "gamma_exposure": ["volatility_trend", "liquidity_score"],
            "structure_quality": ["vwap_distance", "day_type_score"],
            "momentum_strength": ["pullback_depth", "breakout_quality"],
            "iv_rank": ["realized_volatility", "volatility_trend"],
        }
        
        return interactions_map.get(feature_name, [])
    
    def get_top_features(self, n: int = 10) -> List[FeatureImportance]:
        """Get top N important features."""
        # This would be called after learn_features
        return []
    
    def detect_redundancy(self, features: List[FeatureImportance]) -> List[str]:
        """Detect redundant features."""
        redundant = []
        
        # In production, would use correlation analysis
        similar_pairs = [
            ("implied_volatility", "realized_volatility"),
            ("volume_ratio", "option_volume"),
        ]
        
        return redundant
    
    def identify_noisy_features(self, features: List[FeatureImportance], threshold: float = 0.3) -> List[str]:
        """Identify noisy features."""
        return [f.feature_name for f in features if f.noise_level > threshold]


def create_engine() -> FeatureLearningEngine:
    """Create a new feature learning engine."""
    return FeatureLearningEngine()
