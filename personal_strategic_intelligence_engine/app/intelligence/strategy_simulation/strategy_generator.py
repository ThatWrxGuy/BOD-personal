"""Strategy Generator.

Generates tactical strategy variations.
"""

from datetime import datetime
from typing import List, Dict
import uuid

from app.intelligence.strategy_simulation.simulation_models import (
    StrategyConfig,
    StrategyType,
)


class StrategyGenerator:
    """Generates tactical strategy variations."""
    
    def __init__(self):
        self.parameter_templates = {
            "signal_thresholds": {
                "min_signal_score": {"min": 40, "max": 70, "default": 50},
                "min_confidence_score": {"min": 40, "max": 70, "default": 50},
            },
            "structure_thresholds": {
                "min_structure_quality": {"min": 30, "max": 80, "default": 50},
                "min_tactical_suitability": {"min": 30, "max": 80, "default": 50},
            },
            "timing_rules": {
                "require_momentum_confirmation": [True, False],
                "allow_immediate_entry": [True, False],
                "max_pullback_depth_pct": {"min": 0.2, "max": 1.5, "default": 0.5},
            },
            "suppression_rules": {
                "max_spread_width": {"min": 0.10, "max": 0.50, "default": 0.30},
                "min_liquidity_score": {"min": 20, "max": 60, "default": 40},
                "allow_overextension": [True, False],
            },
            "entry_conditions": {
                "require_vwap_acceptance": [True, False],
                "require_breakout_confirmation": [True, False],
                "min_volume_ratio": {"min": 0.8, "max": 2.0, "default": 1.0},
            },
            "exit_rules": {
                "profit_target_pct": {"min": 0.5, "max": 2.0, "default": 1.0},
                "stop_loss_pct": {"min": 0.3, "max": 1.0, "default": 0.5},
                "time_based_exit_minutes": {"min": 5, "max": 60, "default": 30},
            },
        }
    
    def generate_strategies(
        self,
        count: int = 10,
    ) -> List[StrategyConfig]:
        """Generate strategy variations."""
        
        strategies = []
        
        # Always include baseline strategy
        strategies.append(self._create_baseline_strategy())
        
        # Generate variations
        for i in range(count - 1):
            strategy = self._create_variation(i)
            strategies.append(strategy)
        
        return strategies
    
    def _create_baseline_strategy(self) -> StrategyConfig:
        """Create baseline strategy."""
        
        return StrategyConfig(
            strategy_id="strat-baseline-001",
            strategy_name="Baseline 0DTE Strategy",
            strategy_type=StrategyType.MOMENTUM,
            parameters={
                "min_signal_score": 50,
                "min_confidence_score": 50,
                "min_structure_quality": 50,
                "min_tactical_suitability": 50,
                "require_momentum_confirmation": True,
                "allow_immediate_entry": False,
                "max_pullback_depth_pct": 0.5,
                "max_spread_width": 0.30,
                "min_liquidity_score": 40,
                "allow_overextension": False,
                "require_vwap_acceptance": True,
                "require_breakout_confirmation": True,
                "min_volume_ratio": 1.0,
                "profit_target_pct": 1.0,
                "stop_loss_pct": 0.5,
                "time_based_exit_minutes": 30,
            },
            hypothesis="Standard 0DTE momentum strategy with structure and timing filters",
            created_at=datetime.now(),
        )
    
    def _create_variation(self, index: int) -> StrategyConfig:
        """Create a strategy variation."""
        
        params = {}
        
        # Signal thresholds
        params["min_signal_score"] = self._random_choice([45, 50, 55, 60])
        params["min_confidence_score"] = self._random_choice([45, 50, 55])
        
        # Structure thresholds
        params["min_structure_quality"] = self._random_choice([40, 50, 60])
        params["min_tactical_suitability"] = self._random_choice([40, 50, 60])
        
        # Timing rules
        params["require_momentum_confirmation"] = self._random_choice([True, False])
        params["allow_immediate_entry"] = self._random_choice([True, False])
        params["max_pullback_depth_pct"] = self._random_choice([0.3, 0.5, 0.7, 1.0])
        
        # Suppression rules
        params["max_spread_width"] = self._random_choice([0.20, 0.30, 0.40])
        params["min_liquidity_score"] = self._random_choice([30, 40, 50])
        params["allow_overextension"] = self._random_choice([True, False])
        
        # Entry conditions
        params["require_vwap_acceptance"] = self._random_choice([True, False])
        params["require_breakout_confirmation"] = self._random_choice([True, False])
        params["min_volume_ratio"] = self._random_choice([0.8, 1.0, 1.2])
        
        # Exit rules
        params["profit_target_pct"] = self._random_choice([0.8, 1.0, 1.5])
        params["stop_loss_pct"] = self._random_choice([0.3, 0.5, 0.7])
        params["time_based_exit_minutes"] = self._random_choice([15, 30, 45])
        
        # Determine strategy type based on parameters
        strategy_type = self._determine_strategy_type(params)
        
        return StrategyConfig(
            strategy_id=f"strat-var-{index:03d}",
            strategy_name=f"Strategy Variation {index + 1}",
            strategy_type=strategy_type,
            parameters=params,
            hypothesis=self._generate_hypothesis(params),
            created_at=datetime.now(),
        )
    
    def _determine_strategy_type(self, params: Dict) -> StrategyType:
        """Determine strategy type from parameters."""
        
        if params.get("require_breakout_confirmation"):
            return StrategyType.BREAKOUT
        elif params.get("allow_overextension"):
            return StrategyType.REVERSAL
        elif params.get("require_momentum_confirmation"):
            return StrategyType.MOMENTUM
        else:
            return StrategyType.HYBRID
    
    def _generate_hypothesis(self, params: Dict) -> str:
        """Generate hypothesis for strategy."""
        
        hypotheses = []
        
        if params.get("min_signal_score", 50) > 55:
            hypotheses.append("Higher signal threshold reduces false positives")
        
        if params.get("allow_overextension"):
            hypotheses.append("Allowing overextension captures reversal opportunities")
        
        if params.get("allow_immediate_entry"):
            hypotheses.append("Immediate entry captures momentum bursts")
        
        if params.get("require_vwap_acceptance"):
            hypotheses.append("VWAP acceptance filter ensures trend alignment")
        
        return " | ".join(hypotheses) if hypotheses else "Standard momentum approach"
    
    def _random_choice(self, options: list):
        """Random choice from options."""
        import random
        return random.choice(options)


def create_generator() -> StrategyGenerator:
    """Create a new strategy generator."""
    return StrategyGenerator()
