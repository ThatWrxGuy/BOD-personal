"""Outcome Evaluator - compares predicted outcomes with real execution results.

The Outcome Evaluator analyzes execution records to determine how well
predictions matched reality, providing insights for learning and improvement.
"""
from typing import Any, Dict, Optional

from app.learning_engine.memory_models import OutcomeRecord
from app.core.logging import get_logger

logger = get_logger(__name__)


class OutcomeEvaluator:
    """
    Compares predicted outcomes with real execution results.
    
    Evaluation metrics:
    - Expected return vs actual: forecast accuracy
    - Expected drawdown vs realized: risk modeling accuracy
    - Timing quality: strategy relevance
    - Approval quality: governance effectiveness
    """
    
    # Thresholds for evaluation
    RETURN_ACCURACY_THRESHOLD = 0.8  # 80% accuracy is good
    RISK_ACCURACY_THRESHOLD = 0.7  # 70% accuracy is good
    
    def __init__(self):
        self._evaluation_history = []
    
    def evaluate(
        self,
        execution_record: Dict[str, Any],
        predictions: Optional[Dict[str, Any]] = None,
    ) -> OutcomeRecord:
        """
        Evaluate an execution outcome.
        
        Args:
            execution_record: The execution result record
            predictions: Optional predictions from simulations
            
        Returns:
            OutcomeRecord with evaluation metrics
        """
        # Extract execution details
        execution_id = execution_record.get("id", execution_record.get("execution_id", "unknown"))
        proposal_id = execution_record.get("proposal_id", "unknown")
        
        # Create outcome record
        outcome = OutcomeRecord(
            execution_id=execution_id,
            proposal_id=proposal_id,
        )
        
        # Extract predictions
        if predictions:
            outcome.predicted_return = predictions.get("expected_return")
            outcome.predicted_drawdown = predictions.get("max_drawdown")
            outcome.predicted_risk_level = predictions.get("risk_level")
            outcome.confidence_score = predictions.get("confidence")
        
        # Extract actual results
        result = execution_record.get("result", {})
        
        # Determine if execution was successful
        outcome.success = execution_record.get("status") == "completed"
        
        # Extract actual values (in a real system, these would come from market data)
        outcome.actual_return = result.get("actual_return", 0.0 if outcome.success else -0.05)
        outcome.actual_drawdown = result.get("actual_drawdown", 0.0)
        
        # Determine actual risk level
        if outcome.actual_return < -0.1:
            outcome.actual_risk_level = "critical"
        elif outcome.actual_return < -0.05:
            outcome.actual_risk_level = "high"
        elif outcome.actual_return < 0:
            outcome.actual_risk_level = "medium"
        else:
            outcome.actual_risk_level = "low"
        
        # Calculate accuracy metrics
        outcome.calculate_accuracy()
        
        # Log evaluation
        logger.info(
            f"Evaluated outcome for {execution_id}: "
            f"return_accuracy={outcome.return_accuracy}, "
            f"risk_accuracy={outcome.risk_accuracy}, "
            f"success={outcome.success}"
        )
        
        self._evaluation_history.append(outcome)
        
        return outcome
    
    def evaluate_with_predictions(
        self,
        execution_record: Dict[str, Any],
        simulation_results: Dict[str, Any],
    ) -> OutcomeRecord:
        """
        Evaluate with full simulation predictions.
        
        Args:
            execution_record: The execution result
            simulation_results: Results from simulation
            
        Returns:
            OutcomeRecord with evaluation
        """
        predictions = {}
        
        # Extract predictions from simulation results
        for sim_type, result in simulation_results.items():
            if isinstance(result, dict):
                if "expected_return" in result:
                    predictions["expected_return"] = result.get("expected_return")
                if "max_drawdown" in result:
                    predictions["max_drawdown"] = result.get("max_drawdown")
                if "win_probability" in result:
                    predictions["confidence"] = result.get("win_probability")
        
        return self.evaluate(execution_record, predictions)
    
    def get_return_accuracy_stats(self) -> Dict[str, float]:
        """Get return accuracy statistics."""
        accuracies = [
            o.return_accuracy for o in self._evaluation_history
            if o.return_accuracy is not None
        ]
        
        if not accuracies:
            return {"mean": 0.0, "min": 0.0, "max": 0.0, "count": 0}
        
        return {
            "mean": sum(accuracies) / len(accuracies),
            "min": min(accuracies),
            "max": max(accuracies),
            "count": len(accuracies),
        }
    
    def get_risk_accuracy_stats(self) -> Dict[str, float]:
        """Get risk accuracy statistics."""
        accuracies = [
            o.risk_accuracy for o in self._evaluation_history
            if o.risk_accuracy is not None
        ]
        
        if not accuracies:
            return {"mean": 0.0, "min": 0.0, "max": 0.0, "count": 0}
        
        return {
            "mean": sum(accuracies) / len(accuracies),
            "min": min(accuracies),
            "max": max(accuracies),
            "count": len(accuracies),
        }
    
    def get_success_rate(self) -> float:
        """Get overall success rate."""
        if not self._evaluation_history:
            return 0.0
        
        successes = sum(1 for o in self._evaluation_history if o.success)
        return successes / len(self._evaluation_history)
    
    def get_evaluation_summary(self) -> Dict[str, Any]:
        """Get a summary of all evaluations."""
        return {
            "total_evaluations": len(self._evaluation_history),
            "success_rate": self.get_success_rate(),
            "return_accuracy": self.get_return_accuracy_stats(),
            "risk_accuracy": self.get_risk_accuracy_stats(),
        }


# Singleton instance
_outcome_evaluator: Optional[OutcomeEvaluator] = None


def get_outcome_evaluator() -> OutcomeEvaluator:
    """Get the global outcome evaluator instance."""
    global _outcome_evaluator
    if _outcome_evaluator is None:
        _outcome_evaluator = OutcomeEvaluator()
    return _outcome_evaluator
