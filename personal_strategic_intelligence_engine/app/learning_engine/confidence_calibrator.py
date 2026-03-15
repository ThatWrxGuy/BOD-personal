"""Confidence Calibrator - adjusts confidence scoring based on historical accuracy.

The Confidence Calibrator recalibrates strategy and agent confidence scores
based on how accurate their predictions have been historically.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.learning_engine.memory_models import ConfidenceAdjustment
from app.learning_engine.outcome_evaluator import OutcomeEvaluator
from app.core.logging import get_logger

logger = get_logger(__name__)


class ConfidenceCalibrator:
    """
    Adjusts confidence scoring based on historical accuracy.
    
    Responsibilities:
    - Recalibrate strategy confidence levels
    - Update agent trust scores
    - Flag overconfident or underconfident models
    - Improve proposal reliability over time
    """
    
    # Calibration factors
    LEARNING_RATE = 0.1  # How quickly to adjust confidence
    MIN_CONFIDENCE = 0.1
    MAX_CONFIDENCE = 0.95
    ACCURACY_SMOOTHING = 0.2
    
    def __init__(self, outcome_evaluator: Optional[OutcomeEvaluator] = None):
        self.outcome_evaluator = outcome_evaluator
        
        # Store confidence scores: entity_id -> confidence
        self._strategy_confidence: Dict[str, float] = {}
        self._agent_confidence: Dict[str, float] = {}
        
        # Store accuracy history for smoothing
        self._accuracy_history: Dict[str, List[float]] = {}
        
        # Store adjustments for audit
        self._adjustments: List[ConfidenceAdjustment] = []
    
    def get_strategy_confidence(self, strategy_id: str) -> float:
        """Get current confidence for a strategy."""
        return self._strategy_confidence.get(strategy_id, 0.5)  # Default 0.5
    
    def get_agent_confidence(self, agent_id: str) -> float:
        """Get current confidence for an agent."""
        return self._agent_confidence.get(agent_id, 0.5)  # Default 0.5
    
    def calibrate_strategy(
        self,
        strategy_id: str,
        actual_outcome: bool,
        predicted_confidence: float,
    ) -> float:
        """
        Calibrate strategy confidence based on prediction accuracy.
        
        Args:
            strategy_id: The strategy identifier
            actual_outcome: Actual outcome (True = success)
            predicted_confidence: The confidence that was predicted
            
        Returns:
            New calibrated confidence
        """
        # Calculate accuracy (did prediction match outcome?)
        predicted_success = predicted_confidence > 0.5
        accurate = predicted_success == actual_outcome
        
        # Calculate accuracy score (1 = perfect, 0 = wrong)
        if accurate:
            accuracy = 1.0 - (abs(predicted_confidence - 0.5) * 2)
        else:
            accuracy = abs(predicted_confidence - 0.5) * 2
        
        # Get previous accuracies for smoothing
        if strategy_id not in self._accuracy_history:
            self._accuracy_history[strategy_id] = []
        
        history = self._accuracy_history[strategy_id]
        history.append(accuracy)
        
        # Keep only recent history
        if len(history) > 20:
            history = history[-20:]
        self._accuracy_history[strategy_id] = history
        
        # Calculate smoothed accuracy
        if history:
            smoothed_accuracy = sum(history) / len(history)
        else:
            smoothed_accuracy = accuracy
        
        # Get current confidence
        current_confidence = self.get_strategy_confidence(strategy_id)
        
        # Calculate adjustment
        # If accuracy is high and confidence is low -> increase confidence
        # If accuracy is low and confidence is high -> decrease confidence
        error = smoothed_accuracy - current_confidence
        adjustment = error * self.LEARNING_RATE
        
        # Apply adjustment
        new_confidence = current_confidence + adjustment
        
        # Clip to valid range
        new_confidence = max(self.MIN_CONFIDENCE, min(self.MAX_CONFIDENCE, new_confidence))
        
        # Store new confidence
        self._strategy_confidence[strategy_id] = new_confidence
        
        # Record adjustment
        adjustment_record = ConfidenceAdjustment(
            entity_id=strategy_id,
            entity_type="strategy",
            previous_confidence=current_confidence,
            new_confidence=new_confidence,
            adjustment_reason=f"Accuracy: {accuracy:.2f}, Smoothed: {smoothed_accuracy:.2f}",
            based_on_samples=len(history),
            accuracy_delta=error,
        )
        self._adjustments.append(adjustment_record)
        
        logger.info(
            f"Calibrated strategy {strategy_id}: "
            f"{current_confidence:.2f} -> {new_confidence:.2f} "
            f"(accuracy: {accuracy:.2f})"
        )
        
        return new_confidence
    
    def calibrate_agent(
        self,
        agent_id: str,
        proposal_accepted: bool,
        predicted_confidence: float,
    ) -> float:
        """
        Calibrate agent confidence based on proposal acceptance.
        
        Args:
            agent_id: The agent identifier
            proposal_accepted: Whether proposal was accepted
            predicted_confidence: The confidence predicted by agent
            
        Returns:
            New calibrated confidence
        """
        # Calculate accuracy
        predicted_acceptance = predicted_confidence > 0.5
        accurate = predicted_acceptance == proposal_accepted
        
        if accurate:
            accuracy = 1.0 - (abs(predicted_confidence - 0.5) * 2)
        else:
            accuracy = abs(predicted_confidence - 0.5) * 2
        
        # Get previous accuracies
        history_key = f"agent_{agent_id}"
        if history_key not in self._accuracy_history:
            self._accuracy_history[history_key] = []
        
        history = self._accuracy_history[history_key]
        history.append(accuracy)
        
        if len(history) > 20:
            history = history[-20:]
        self._accuracy_history[history_key] = history
        
        # Calculate smoothed accuracy
        smoothed_accuracy = sum(history) / len(history) if history else accuracy
        
        # Get current confidence
        current_confidence = self.get_agent_confidence(agent_id)
        
        # Calculate adjustment
        error = smoothed_accuracy - current_confidence
        adjustment = error * self.LEARNING_RATE
        
        # Apply adjustment
        new_confidence = current_confidence + adjustment
        new_confidence = max(self.MIN_CONFIDENCE, min(self.MAX_CONFIDENCE, new_confidence))
        
        # Store new confidence
        self._agent_confidence[agent_id] = new_confidence
        
        # Record adjustment
        adjustment_record = ConfidenceAdjustment(
            entity_id=agent_id,
            entity_type="agent",
            previous_confidence=current_confidence,
            new_confidence=new_confidence,
            adjustment_reason=f"Acceptance: {proposal_accepted}, Smoothed: {smoothed_accuracy:.2f}",
            based_on_samples=len(history),
            accuracy_delta=error,
        )
        self._adjustments.append(adjustment_record)
        
        logger.info(
            f"Calibrated agent {agent_id}: "
            f"{current_confidence:.2f} -> {new_confidence:.2f} "
            f"(accepted: {proposal_accepted})"
        )
        
        return new_confidence
    
    def get_overconfident_strategies(
        self,
        threshold: float = 0.2,
    ) -> List[Dict[str, Any]]:
        """
        Find strategies that are overconfident (high confidence but low accuracy).
        
        Args:
            threshold: Difference threshold to flag overconfidence
            
        Returns:
            List of overconfident strategies
        """
        results = []
        
        for strategy_id, confidence in self._strategy_confidence.items():
            history_key = strategy_id
            if history_key in self._accuracy_history and self._accuracy_history[history_key]:
                recent_accuracy = sum(self._accuracy_history[history_key]) / len(self._accuracy_history[history_key])
                
                # Overconfident if confidence is much higher than accuracy
                if confidence - recent_accuracy > threshold:
                    results.append({
                        "entity_id": strategy_id,
                        "type": "strategy",
                        "confidence": confidence,
                        "recent_accuracy": recent_accuracy,
                        "overconfidence": confidence - recent_accuracy,
                    })
        
        return results
    
    def get_underconfident_strategies(
        self,
        threshold: float = 0.2,
    ) -> List[Dict[str, Any]]:
        """Find strategies that are underconfident."""
        results = []
        
        for strategy_id, confidence in self._strategy_confidence.items():
            history_key = strategy_id
            if history_key in self._accuracy_history and self._accuracy_history[history_key]:
                recent_accuracy = sum(self._accuracy_history[history_key]) / len(self._accuracy_history[history_key])
                
                # Underconfident if accuracy is much higher than confidence
                if recent_accuracy - confidence > threshold:
                    results.append({
                        "entity_id": strategy_id,
                        "type": "strategy",
                        "confidence": confidence,
                        "recent_accuracy": recent_accuracy,
                        "underconfidence": recent_accuracy - confidence,
                    })
        
        return results
    
    def get_adjustment_history(
        self,
        limit: int = 50,
    ) -> List[ConfidenceAdjustment]:
        """Get recent confidence adjustments."""
        return self._adjustments[-limit:]
    
    def get_confidence_summary(self) -> Dict[str, Any]:
        """Get summary of confidence calibration."""
        strategy_confidences = list(self._strategy_confidence.values())
        agent_confidences = list(self._agent_confidence.values())
        
        return {
            "strategies_calibrated": len(self._strategy_confidence),
            "agents_calibrated": len(self._agent_confidence),
            "total_adjustments": len(self._adjustments),
            "average_strategy_confidence": (
                sum(strategy_confidences) / len(strategy_confidences)
                if strategy_confidences else 0.5
            ),
            "average_agent_confidence": (
                sum(agent_confidences) / len(agent_confidences)
                if agent_confidences else 0.5
            ),
            "overconfident_strategies": len(self.get_overconfident_strategies()),
            "underconfident_strategies": len(self.get_underconfident_strategies()),
        }


# Singleton instance
_confidence_calibrator: Optional[ConfidenceCalibrator] = None


def get_confidence_calibrator() -> ConfidenceCalibrator:
    """Get the global confidence calibrator instance."""
    global _confidence_calibrator
    if _confidence_calibrator is None:
        _confidence_calibrator = ConfidenceCalibrator()
    return _confidence_calibrator


def reset_confidence_calibrator() -> None:
    """Reset the confidence calibrator (for testing)."""
    global _confidence_calibrator
    _confidence_calibrator = None
