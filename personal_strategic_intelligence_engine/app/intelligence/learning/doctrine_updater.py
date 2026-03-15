"""Doctrine Updater - Updates strategic doctrine based on learning."""
import uuid
from datetime import datetime
from typing import List, Dict, Optional

from app.intelligence.learning.learning_models import (
    DoctrineUpdate,
    StrategyEffectiveness,
    LearningPolicy,
    StrategyType,
)


class DoctrineUpdater:
    """Updates strategic doctrine based on learning outcomes."""
    
    def __init__(self, policy: Optional[LearningPolicy] = None):
        self.policy = policy or LearningPolicy()
        self.updates: List[DoctrineUpdate] = []
        
        # Current doctrine weights (these would be stored in the kernel)
        self.doctrine_weights = {
            "risk_mitigation": 0.25,
            "opportunity_seizing": 0.20,
            "performance_optimization": 0.25,
            "resource_reallocation": 0.15,
            "balance_adjustment": 0.10,
            "focus_shift": 0.05,
        }
        
        # Confidence multipliers
        self.confidence_multipliers = {
            strategy.value: 1.0 for strategy in StrategyType
        }
    
    def update_doctrine(
        self,
        effectiveness: Dict[StrategyType, StrategyEffectiveness],
    ) -> List[DoctrineUpdate]:
        """Update doctrine based on strategy effectiveness."""
        
        new_updates = []
        
        # Update weights based on success rates
        for strategy_type, metrics in effectiveness.items():
            if metrics.total_decisions < self.policy.minimum_samples_for_update:
                continue
            
            # Update strategy weight
            update = self._update_strategy_weight(
                strategy_type,
                metrics.success_rate,
            )
            
            if update:
                new_updates.append(update)
            
            # Update confidence multiplier
            update = self._update_confidence_multiplier(
                strategy_type,
                metrics.success_rate,
                metrics.average_impact,
            )
            
            if update:
                new_updates.append(update)
        
        self.updates.extend(new_updates)
        
        return new_updates
    
    def _update_strategy_weight(
        self,
        strategy_type: StrategyType,
        success_rate: float,
    ) -> Optional[DoctrineUpdate]:
        """Update the weight of a strategy type."""
        
        strategy_key = strategy_type.value
        current_weight = self.doctrine_weights.get(strategy_key, 0.2)
        
        # Calculate adjustment based on success rate
        # Above threshold = increase, below = decrease
        if success_rate > self.policy.success_rate_threshold:
            # Good performance - increase weight
            change = self.policy.learning_rate * success_rate
        elif success_rate < self.policy.failure_rate_threshold:
            # Poor performance - decrease weight
            change = -self.policy.learning_rate * (1 - success_rate)
        else:
            # Within tolerance - no change
            return None
        
        # Clamp change
        change = max(
            -self.policy.max_weight_change_per_update,
            min(self.policy.max_weight_change_per_update, change)
        )
        
        new_weight = max(0.05, min(0.5, current_weight + change))
        
        update = DoctrineUpdate(
            update_id=str(uuid.uuid4())[:8],
            parameter_name=f"weight_{strategy_key}",
            old_value=current_weight,
            new_value=new_weight,
            change_reason=f"Success rate: {success_rate:.1%}",
            affected_strategies=[strategy_key],
        )
        
        self.doctrine_weights[strategy_key] = new_weight
        
        return update
    
    def _update_confidence_multiplier(
        self,
        strategy_type: StrategyType,
        success_rate: float,
        average_impact: float,
    ) -> Optional[DoctrineUpdate]:
        """Update confidence multiplier for a strategy type."""
        
        strategy_key = strategy_type.value
        current_mult = self.confidence_multipliers.get(strategy_key, 1.0)
        
        # Adjust based on how accurate confidence has been
        # If success rate matches confidence, multiplier stays
        # If success rate > confidence, increase multiplier
        # If success rate < confidence, decrease multiplier
        
        expected_confidence = current_mult * 0.7  # Assume ~70% success at 1.0 multiplier
        
        if success_rate > expected_confidence + self.policy.confidence_tolerance:
            # Confidence was too conservative - increase
            change = self.policy.learning_rate
        elif success_rate < expected_confidence - self.policy.confidence_tolerance:
            # Confidence was too optimistic - decrease
            change = -self.policy.learning_rate
        else:
            return None
        
        new_mult = max(0.5, min(1.5, current_mult + change))
        
        update = DoctrineUpdate(
            update_id=str(uuid.uuid4())[:8],
            parameter_name=f"confidence_{strategy_key}",
            old_value=current_mult,
            new_value=new_mult,
            change_reason=f"Impact: {average_impact:.2f}, Success: {success_rate:.1%}",
            affected_strategies=[strategy_key],
        )
        
        self.confidence_multipliers[strategy_key] = new_mult
        
        return update
    
    def get_current_doctrine(self) -> Dict[str, float]:
        """Get current doctrine weights."""
        
        return self.doctrine_weights.copy()
    
    def get_confidence_multipliers(self) -> Dict[str, float]:
        """Get current confidence multipliers."""
        
        return self.confidence_multipliers.copy()
    
    def get_recent_updates(
        self,
        limit: int = 10,
    ) -> List[DoctrineUpdate]:
        """Get recent doctrine updates."""
        
        return self.updates[-limit:]
    
    def get_applied_updates(self) -> List[DoctrineUpdate]:
        """Get all applied updates."""
        
        return self.updates
    
    def apply_update(self, update: DoctrineUpdate) -> bool:
        """Apply a doctrine update."""
        
        param = update.parameter_name
        
        if param.startswith("weight_"):
            strategy = param.replace("weight_", "")
            self.doctrine_weights[strategy] = update.new_value
        elif param.startswith("confidence_"):
            strategy = param.replace("confidence_", "")
            self.confidence_multipliers[strategy] = update.new_value
        else:
            return False
        
        return True


_updater: Optional[DoctrineUpdater] = None


def get_doctrine_updater() -> DoctrineUpdater:
    """Get the global doctrine updater."""
    global _updater
    if _updater is None:
        _updater = DoctrineUpdater()
    return _updater
