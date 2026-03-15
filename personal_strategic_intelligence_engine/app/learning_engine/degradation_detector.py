"""Degradation Detector - detects deterioration in system performance.

The Degradation Detector monitors performance metrics and identifies when strategies,
agents, or execution patterns start to degrade.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.learning_engine.memory_models import (
    DegradationAlert,
    DegradationLevel,
)
from app.learning_engine.performance_tracker import PerformanceTracker
from app.core.logging import get_logger

logger = get_logger(__name__)


class DegradationDetector:
    """
    Detects deterioration in system performance.
    
    Detection triggers:
    - Declining strategy win rates
    - Increasing drawdowns
    - Repeated execution failures
    - Agent proposal rejection patterns
    - Confidence vs outcome mismatch
    """
    
    # Thresholds for degradation detection
    WIN_RATE_DECLINE_THRESHOLD = 0.15  # 15% decline triggers alert
    DRAWDOWN_INCREASE_THRESHOLD = 0.1  # 10% increase triggers alert
    FAILURE_RATE_THRESHOLD = 0.3  # 30% failure rate triggers alert
    AGENT_REJECTION_THRESHOLD = 0.5  # 50% rejection rate triggers alert
    
    def __init__(self, performance_tracker: Optional[PerformanceTracker] = None):
        self.performance_tracker = performance_tracker
        self._alerts: Dict[str, DegradationAlert] = {}
    
    def check_strategy_degradation(
        self,
        strategy_id: str,
        current_win_rate: float,
        previous_win_rate: float,
        current_drawdown: float,
        previous_drawdown: float,
    ) -> Optional[DegradationAlert]:
        """
        Check if a strategy is degrading.
        
        Args:
            strategy_id: The strategy identifier
            current_win_rate: Current win rate
            previous_win_rate: Previous win rate
            current_drawdown: Current drawdown
            previous_drawdown: Previous drawdown
            
        Returns:
            DegradationAlert if degradation detected, None otherwise
        """
        alerts = []
        
        # Check win rate decline
        win_rate_decline = previous_win_rate - current_win_rate
        if win_rate_decline > self.WIN_RATE_DECLINE_THRESHOLD:
            alert = DegradationAlert(
                alert_type="strategy",
                entity_id=strategy_id,
                entity_type="strategy",
                degradation_level=self._calculate_level(win_rate_decline, self.WIN_RATE_DECLINE_THRESHOLD),
                metric_name="win_rate",
                previous_value=previous_win_rate,
                current_value=current_win_rate,
                threshold=self.WIN_RATE_DECLINE_THRESHOLD,
                description=f"Strategy {strategy_id} win rate declined from {previous_win_rate:.2%} to {current_win_rate:.2%}",
                recommendations=[
                    "Review recent execution outcomes",
                    "Analyze market conditions that may have changed",
                    "Consider temporarily reducing position sizes",
                ],
            )
            alerts.append(alert)
        
        # Check drawdown increase
        drawdown_increase = current_drawdown - previous_drawdown
        if drawdown_increase > self.DRAWDOWN_INCREASE_THRESHOLD:
            alert = DegradationAlert(
                alert_type="strategy",
                entity_id=strategy_id,
                entity_type="strategy",
                degradation_level=self._calculate_level(drawdown_increase, self.DRAWDOWN_INCREASE_THRESHOLD),
                metric_name="drawdown",
                previous_value=previous_drawdown,
                current_value=current_drawdown,
                threshold=self.DRAWDOWN_INCREASE_THRESHOLD,
                description=f"Strategy {strategy_id} drawdown increased from {previous_drawdown:.2%} to {current_drawdown:.2%}",
                recommendations=[
                    "Review risk management parameters",
                    "Consider stopping the strategy temporarily",
                    "Analyze recent losing trades",
                ],
            )
            alerts.append(alert)
        
        # Store alerts
        for alert in alerts:
            self._alerts[alert.id] = alert
            logger.warning(f"Strategy degradation detected: {alert.description}")
        
        return alerts[0] if alerts else None
    
    def check_agent_degradation(
        self,
        agent_id: str,
        current_approval_rate: float,
        previous_approval_rate: float,
        current_confidence_accuracy: float,
    ) -> Optional[DegradationAlert]:
        """
        Check if an agent is degrading.
        
        Args:
            agent_id: The agent identifier
            current_approval_rate: Current approval rate
            previous_approval_rate: Previous approval rate
            current_confidence_accuracy: How accurate agent's confidence scores are
            
        Returns:
            DegradationAlert if degradation detected, None otherwise
        """
        alerts = []
        
        # Check approval rate decline
        approval_decline = previous_approval_rate - current_approval_rate
        if approval_decline > self.AGENT_REJECTION_THRESHOLD:
            alert = DegradationAlert(
                alert_type="agent",
                entity_id=agent_id,
                entity_type="agent",
                degradation_level=self._calculate_level(approval_decline, self.AGENT_REJECTION_THRESHOLD),
                metric_name="approval_rate",
                previous_value=previous_approval_rate,
                current_value=current_approval_rate,
                threshold=self.AGENT_REJECTION_THRESHOLD,
                description=f"Agent {agent_id} approval rate declined from {previous_approval_rate:.2%} to {current_approval_rate:.2%}",
                recommendations=[
                    "Review agent proposal quality",
                    "Analyze rejection reasons",
                    "Consider retraining agent parameters",
                ],
            )
            alerts.append(alert)
        
        # Store alerts
        for alert in alerts:
            self._alerts[alert.id] = alert
            logger.warning(f"Agent degradation detected: {alert.description}")
        
        return alerts[0] if alerts else None
    
    def check_execution_failure_rate(
        self,
        action_type: str,
        total_executions: int,
        failed_executions: int,
    ) -> Optional[DegradationAlert]:
        """
        Check if execution failure rate is too high.
        
        Args:
            action_type: Type of action
            total_executions: Total number of executions
            failed_executions: Number of failed executions
            
        Returns:
            DegradationAlert if degradation detected, None otherwise
        """
        if total_executions == 0:
            return None
        
        failure_rate = failed_executions / total_executions
        
        if failure_rate > self.FAILURE_RATE_THRESHOLD:
            alert = DegradationAlert(
                alert_type="execution",
                entity_id=action_type,
                entity_type="action_type",
                degradation_level=self._calculate_level(failure_rate, self.FAILURE_RATE_THRESHOLD),
                metric_name="failure_rate",
                previous_value=0.0,
                current_value=failure_rate,
                threshold=self.FAILURE_RATE_THRESHOLD,
                description=f"Action type {action_type} has high failure rate: {failure_rate:.2%}",
                recommendations=[
                    "Investigate execution infrastructure",
                    "Review error logs",
                    "Consider retry logic improvements",
                ],
            )
            self._alerts[alert.id] = alert
            logger.warning(f"Execution degradation detected: {alert.description}")
            return alert
        
        return None
    
    def check_confidence_accuracy(
        self,
        entity_id: str,
        entity_type: str,
        confidence_score: float,
        actual_outcome: bool,
    ) -> Optional[DegradationAlert]:
        """
        Check if confidence scores are accurate.
        
        Args:
            entity_id: Entity identifier
            entity_type: Type of entity (strategy, agent)
            confidence_score: Predicted confidence
            actual_outcome: Actual outcome (True = success)
            
        Returns:
            DegradationAlert if mismatch detected, None otherwise
        """
        # Determine if confidence was accurate
        predicted_success = confidence_score > 0.5
        accurate = predicted_success == actual_outcome
        
        if not accurate:
            # Large mismatch between confidence and outcome
            mismatch = abs(confidence_score - (1.0 if actual_outcome else 0.0))
            
            if mismatch > 0.3:  # More than 30% mismatch
                alert = DegradationAlert(
                    alert_type="confidence",
                    entity_id=entity_id,
                    entity_type=entity_type,
                    degradation_level=DegradationLevel.MODERATE,
                    metric_name="confidence_accuracy",
                    previous_value=confidence_score,
                    current_value=1.0 if actual_outcome else 0.0,
                    threshold=0.3,
                    description=f"Entity {entity_id} confidence mismatch: predicted {confidence_score:.2%}, actual: {'success' if actual_outcome else 'failure'}",
                    recommendations=[
                        "Recalibrate confidence scoring",
                        "Review prediction methodology",
                    ],
                )
                self._alerts[alert.id] = alert
                logger.warning(f"Confidence accuracy issue: {alert.description}")
                return alert
        
        return None
    
    def _calculate_level(self, value: float, threshold: float) -> DegradationLevel:
        """Calculate degradation level based on value vs threshold."""
        ratio = value / threshold if threshold > 0 else 0
        
        if ratio >= 2.0:
            return DegradationLevel.CRITICAL
        elif ratio >= 1.5:
            return DegradationLevel.SEVERE
        elif ratio >= 1.0:
            return DegradationLevel.MODERATE
        else:
            return DegradationLevel.MINOR
    
    def get_active_alerts(self) -> List[DegradationAlert]:
        """Get all active (unacknowledged) alerts."""
        return [a for a in self._alerts.values() if not a.acknowledged]
    
    def get_alerts_by_type(self, alert_type: str) -> List[DegradationAlert]:
        """Get alerts by type."""
        return [a for a in self._alerts.values() if a.alert_type == alert_type]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        if alert_id in self._alerts:
            self._alerts[alert_id].acknowledged = True
            logger.info(f"Alert acknowledged: {alert_id}")
            return True
        return False
    
    def clear_resolved_alerts(self) -> int:
        """Clear acknowledged alerts."""
        acknowledged = [a for a in self._alerts.values() if a.acknowledged]
        count = len(acknowledged)
        
        for alert in acknowledged:
            del self._alerts[alert.id]
        
        return count
    
    def get_degradation_summary(self) -> Dict[str, Any]:
        """Get summary of degradation status."""
        active_alerts = self.get_active_alerts()
        
        by_level = {}
        by_type = {}
        
        for alert in active_alerts:
            # By level
            level = alert.degradation_level.value if hasattr(alert.degradation_level, 'value') else str(alert.degradation_level)
            by_level[level] = by_level.get(level, 0) + 1
            
            # By type
            by_type[alert.alert_type] = by_type.get(alert.alert_type, 0) + 1
        
        return {
            "total_active": len(active_alerts),
            "by_level": by_level,
            "by_type": by_type,
            "critical_count": by_level.get("critical", 0),
            "severe_count": by_level.get("severe", 0),
        }


# Singleton instance
_degradation_detector: Optional[DegradationDetector] = None


def get_degradation_detector() -> DegradationDetector:
    """Get the global degradation detector instance."""
    global _degradation_detector
    if _degradation_detector is None:
        _degradation_detector = DegradationDetector()
    return _degradation_detector


def reset_degradation_detector() -> None:
    """Reset the degradation detector (for testing)."""
    global _degradation_detector
    _degradation_detector = None
