"""Strategy Effectiveness Analyzer - Analyzes strategy effectiveness over time."""
from datetime import datetime
from typing import List, Dict, Optional

from app.intelligence.learning.learning_models import (
    StrategyEffectiveness,
    OutcomeEvaluation,
    StrategyType,
    OutcomeStatus,
)


class StrategyEffectivenessAnalyzer:
    """Analyzes effectiveness of different strategy types."""
    
    def __init__(self):
        self.effectiveness: Dict[StrategyType, StrategyEffectiveness] = {}
    
    def analyze_effectiveness(
        self,
        evaluations: List[OutcomeEvaluation],
        decision_mapping: Dict[str, StrategyType],
    ) -> Dict[StrategyType, StrategyEffectiveness]:
        """Analyze effectiveness of strategy types based on evaluations."""
        
        # Initialize effectiveness tracking
        for strategy_type in StrategyType:
            if strategy_type not in self.effectiveness:
                self.effectiveness[strategy_type] = StrategyEffectiveness(
                    strategy_type=strategy_type,
                )
        
        # Group evaluations by strategy type
        evaluations_by_strategy: Dict[StrategyType, List[OutcomeEvaluation]] = {}
        
        for evaluation in evaluations:
            strategy_type = decision_mapping.get(evaluation.decision_id)
            
            if strategy_type:
                if strategy_type not in evaluations_by_strategy:
                    evaluations_by_strategy[strategy_type] = []
                evaluations_by_strategy[strategy_type].append(evaluation)
        
        # Calculate metrics for each strategy type
        for strategy_type, strategy_evals in evaluations_by_strategy.items():
            self._calculate_metrics(
                strategy_type,
                strategy_evals,
            )
        
        return self.effectiveness
    
    def _calculate_metrics(
        self,
        strategy_type: StrategyType,
        evaluations: List[OutcomeEvaluation],
    ) -> None:
        """Calculate effectiveness metrics for a strategy type."""
        
        if not evaluations:
            return
        
        effectiveness = self.effectiveness[strategy_type]
        
        # Count decisions
        effectiveness.total_decisions = len(evaluations)
        
        # Count successes/failures
        successful = sum(
            1 for e in evaluations
            if e.outcome_status in [OutcomeStatus.SUCCESS, OutcomeStatus.PARTIAL_SUCCESS]
        )
        failed = sum(
            1 for e in evaluations
            if e.outcome_status == OutcomeStatus.FAILURE
        )
        
        effectiveness.successful_decisions = successful
        effectiveness.failed_decisions = failed
        
        # Calculate success rate
        effectiveness.success_rate = (
            successful / len(evaluations) if evaluations else 0.0
        )
        
        # Average impact
        impacts = [e.performance_change + e.risk_change for e in evaluations]
        effectiveness.average_impact = (
            sum(impacts) / len(impacts) if impacts else 0.0
        )
        
        # Historical samples
        effectiveness.historical_samples += len(evaluations)
        
        # Last updated
        effectiveness.last_updated = datetime.utcnow()
    
    def get_effectiveness(
        self,
        strategy_type: StrategyType,
    ) -> Optional[StrategyEffectiveness]:
        """Get effectiveness for a specific strategy type."""
        
        return self.effectiveness.get(strategy_type)
    
    def get_all_effectiveness(
        self,
    ) -> Dict[StrategyType, StrategyEffectiveness]:
        """Get effectiveness for all strategy types."""
        
        return self.effectiveness
    
    def get_top_strategies(
        self,
        limit: int = 3,
    ) -> List[StrategyType]:
        """Get top performing strategy types."""
        
        sorted_strategies = sorted(
            self.effectiveness.items(),
            key=lambda x: x[1].success_rate,
            reverse=True,
        )
        
        return [s[0] for s in sorted_strategies[:limit]]
    
    def get_failing_strategies(
        self,
        threshold: float = 0.4,
    ) -> List[StrategyType]:
        """Get strategies with low success rates."""
        
        failing = [
            s[0] for s in self.effectiveness.items()
            if s[1].success_rate < threshold and s[1].total_decisions >= 3
        ]
        
        return failing
    
    def get_recommendations(self) -> List[str]:
        """Generate recommendations based on effectiveness analysis."""
        
        recommendations = []
        
        # Find best strategies
        top = self.get_top_strategies(3)
        if top:
            recommendations.append(
                f"Prioritize strategies: {', '.join(s.value for s in top)}"
            )
        
        # Find failing strategies
        failing = self.get_failing_strategies()
        if failing:
            recommendations.append(
                f"Review or deprioritize: {', '.join(s.value for s in failing)}"
            )
        
        return recommendations
    
    def calculate_confidence_accuracy(
        self,
        evaluations: List[OutcomeEvaluation],
        confidence_mapping: Dict[str, float],
    ) -> Dict[StrategyType, float]:
        """Calculate how accurate confidence predictions are."""
        
        accuracy_by_strategy: Dict[StrategyType, List[float]] = {}
        
        for evaluation in evaluations:
            strategy_type = confidence_mapping.get(evaluation.decision_id)
            
            if not strategy_type:
                continue
            
            if strategy_type not in accuracy_by_strategy:
                accuracy_by_strategy[strategy_type] = []
            
            # Compare confidence to outcome
            decision_confidence = confidence_mapping.get(evaluation.decision_id, 0.5)
            
            # Calculate match (close = accurate)
            diff = abs(decision_confidence - evaluation.success_score)
            accuracy = 1.0 - diff  # 1 = perfect, 0 = completely wrong
            
            accuracy_by_strategy[strategy_type].append(accuracy)
        
        # Average accuracy per strategy
        result = {}
        
        for strategy, accuracies in accuracy_by_strategy.items():
            if accuracies:
                result[strategy] = sum(accuracies) / len(accuracies)
        
        return result


_analyzer: Optional[StrategyEffectivenessAnalyzer] = None


def get_strategy_effectiveness_analyzer() -> StrategyEffectivenessAnalyzer:
    """Get the global strategy effectiveness analyzer."""
    global _analyzer
    if _analyzer is None:
        _analyzer = StrategyEffectivenessAnalyzer()
    return _analyzer
