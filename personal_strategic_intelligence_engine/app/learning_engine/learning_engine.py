"""Learning Engine - central orchestration for learning processes.

The Learning Engine ingests execution outcomes, triggers evaluations, updates metrics,
detects degradation, and emits learning signals.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.learning_engine.memory_models import (
    DegradationAlert,
    LearningInsight,
    LearningStatistics,
    MemoryCategory,
    SourceType,
)
from app.learning_engine.strategic_memory import StrategicMemoryStore, get_strategic_memory
from app.learning_engine.outcome_evaluator import OutcomeEvaluator, get_outcome_evaluator
from app.learning_engine.performance_tracker import PerformanceTracker, get_performance_tracker
from app.learning_engine.degradation_detector import DegradationDetector, get_degradation_detector
from app.learning_engine.confidence_calibrator import ConfidenceCalibrator, get_confidence_calibrator
from app.core.logging import get_logger

logger = get_logger(__name__)


class LearningEngine:
    """
    Central orchestration engine for learning processes.
    
    Responsibilities:
    - Ingest new execution outcomes
    - Trigger evaluation processes
    - Update strategy performance metrics
    - Detect degradation
    - Recalibrate confidence
    - Emit learning signals
    """
    
    def __init__(
        self,
        strategic_memory: Optional[StrategicMemoryStore] = None,
        outcome_evaluator: Optional[OutcomeEvaluator] = None,
        performance_tracker: Optional[PerformanceTracker] = None,
        degradation_detector: Optional[DegradationDetector] = None,
        confidence_calibrator: Optional[ConfidenceCalibrator] = None,
    ):
        self.strategic_memory = strategic_memory or get_strategic_memory()
        self.outcome_evaluator = outcome_evaluator or get_outcome_evaluator()
        self.performance_tracker = performance_tracker or get_performance_tracker()
        self.degradation_detector = degradation_detector or get_degradation_detector()
        self.confidence_calibrator = confidence_calibrator or get_confidence_calibrator()
        
        # Track learning cycles
        self._learning_cycles = 0
    
    async def process_execution_outcome(
        self,
        execution_record: Dict[str, Any],
        predictions: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a completed execution and learn from the outcome.
        
        This is the main entry point for learning from execution results.
        
        Args:
            execution_record: The execution result record
            predictions: Optional predictions from simulations
            
        Returns:
            Dictionary with evaluation results and any alerts generated
        """
        self._learning_cycles += 1
        
        logger.info(f"Processing execution outcome: {execution_record.get('id', 'unknown')}")
        
        results = {
            "execution_id": execution_record.get("id"),
            "evaluation": None,
            "alerts": [],
            "insights": [],
        }
        
        # Step 1: Store execution in memory
        memory_record = self.strategic_memory.store(
            source_type=SourceType.EXECUTION_ENGINE,
            source_id=execution_record.get("id", "unknown"),
            category=MemoryCategory.EXECUTION,
            summary=f"Execution of type {execution_record.get('action_type')} for proposal {execution_record.get('proposal_id')}",
            metadata={
                "status": execution_record.get("status"),
                "action_type": execution_record.get("action_type"),
                "proposal_id": execution_record.get("proposal_id"),
                "result": execution_record.get("result"),
            },
            tags=[execution_record.get("action_type", "unknown")],
        )
        
        # Step 2: Evaluate outcome
        evaluation = self.outcome_evaluator.evaluate(execution_record, predictions)
        results["evaluation"] = {
            "success": evaluation.success,
            "return_accuracy": evaluation.return_accuracy,
            "risk_accuracy": evaluation.risk_accuracy,
            "overall_score": evaluation.overall_score,
        }
        
        # Store outcome record in memory
        self.strategic_memory.store(
            source_type=SourceType.EXECUTION_ENGINE,
            source_id=evaluation.id,
            category=MemoryCategory.OUTCOME,
            summary=f"Outcome evaluation for execution {evaluation.execution_id}",
            metadata={
                "predicted_return": evaluation.predicted_return,
                "actual_return": evaluation.actual_return,
                "return_accuracy": evaluation.return_accuracy,
                "success": evaluation.success,
            },
        )
        
        # Step 3: Update performance metrics
        proposal_id = execution_record.get("proposal_id", "unknown")
        
        self.performance_tracker.update_strategy_performance(
            strategy_id=proposal_id,
            category="general",
            success=evaluation.success,
            return_value=evaluation.actual_return,
            drawdown=evaluation.actual_drawdown,
        )
        
        # Update action type performance
        self.performance_tracker.update_action_type_performance(
            action_type=execution_record.get("action_type", "unknown"),
            success=evaluation.success,
            execution_time_ms=execution_record.get("execution_duration_ms"),
        )
        
        # Step 4: Check for degradation
        alerts = await self._check_degradation(proposal_id, evaluation)
        results["alerts"] = [a.dict() for a in alerts]
        
        # Step 5: Recalibrate confidence
        if predictions and evaluation.confidence_score is not None:
            self.confidence_calibrator.calibrate_strategy(
                strategy_id=proposal_id,
                actual_outcome=evaluation.success,
                predicted_confidence=evaluation.confidence_score or 0.5,
            )
        
        # Step 6: Generate insights
        insights = await self._generate_insights(evaluation)
        results["insights"] = insights
        
        logger.info(
            f"Completed learning cycle {self._learning_cycles}: "
            f"evaluation={evaluation.overall_score}, alerts={len(alerts)}, insights={len(insights)}"
        )
        
        return results
    
    async def process_agent_proposal(
        self,
        agent_id: str,
        agent_name: str,
        proposal_id: str,
        proposal_accepted: bool,
        confidence_score: float,
        governance_overridden: bool = False,
    ) -> Dict[str, Any]:
        """
        Process an agent proposal outcome.
        
        Args:
            agent_id: The agent identifier
            agent_name: The agent name
            proposal_id: The proposal identifier
            proposal_accepted: Whether proposal was accepted
            confidence_score: Agent's confidence in the proposal
            governance_overridden: Whether governance overrode the proposal
            
        Returns:
            Dictionary with results
        """
        logger.info(f"Processing agent proposal: agent={agent_id}, accepted={proposal_accepted}")
        
        # Update agent performance
        self.performance_tracker.update_agent_performance(
            agent_id=agent_id,
            agent_name=agent_name,
            proposal_accepted=proposal_accepted,
            confidence_score=confidence_score,
            governance_overridden=governance_overridden,
        )
        
        # Recalibrate agent confidence
        new_confidence = self.confidence_calibrator.calibrate_agent(
            agent_id=agent_id,
            proposal_accepted=proposal_accepted,
            predicted_confidence=confidence_score,
        )
        
        # Store in memory
        self.strategic_memory.store(
            source_type=SourceType.AGENT,
            source_id=proposal_id,
            category=MemoryCategory.STRATEGY,
            summary=f"Agent {agent_name} proposal {proposal_id}: {'accepted' if proposal_accepted else 'rejected'}",
            metadata={
                "agent_id": agent_id,
                "agent_name": agent_name,
                "accepted": proposal_accepted,
                "confidence_score": confidence_score,
                "governance_overridden": governance_overridden,
            },
            tags=[agent_id],
        )
        
        # Check for agent degradation
        alerts = []
        if self.performance_tracker.get_agent_performance(agent_id):
            perf = self.performance_tracker.get_agent_performance(agent_id)
            alert = self.degradation_detector.check_agent_degradation(
                agent_id=agent_id,
                current_approval_rate=perf.approval_rate,
                previous_approval_rate=perf.approval_rate * 0.9,  # Assume 10% decline
                current_confidence_accuracy=new_confidence,
            )
            if alert:
                alerts.append(alert)
        
        return {
            "agent_id": agent_id,
            "proposal_accepted": proposal_accepted,
            "new_confidence": new_confidence,
            "alerts": [a.dict() for a in alerts] if alerts else [],
        }
    
    async def _check_degradation(
        self,
        strategy_id: str,
        evaluation: Any,
    ) -> List[DegradationAlert]:
        """Check for performance degradation."""
        alerts = []
        
        # Get current performance
        perf = self.performance_tracker.get_strategy_performance(strategy_id)
        
        if perf and perf.total_executions > 1:
            # Compare with previous performance (simplified - use current as proxy)
            alert = self.degradation_detector.check_strategy_degradation(
                strategy_id=strategy_id,
                current_win_rate=perf.win_rate,
                previous_win_rate=perf.win_rate * 1.1,  # Assume 10% decline
                current_drawdown=perf.average_drawdown,
                previous_drawdown=perf.average_drawdown * 0.9,
            )
            if alert:
                alerts.append(alert)
        
        return alerts
    
    async def _generate_insights(self, evaluation: Any) -> List[LearningInsight]:
        """Generate learning insights from evaluation."""
        insights = []
        
        # Generate insight based on overall score
        if evaluation.overall_score is not None:
            if evaluation.overall_score > 0.8:
                insight = LearningInsight(
                    insight_type="improvement",
                    title="High Strategy Accuracy",
                    description=f"Strategy is performing with {evaluation.overall_score:.0%} accuracy",
                    confidence=evaluation.overall_score,
                    actionable=True,
                    recommendations=[
                        "Consider increasing position sizes",
                        "Document success factors for replication",
                    ],
                )
                insights.append(insight)
            elif evaluation.overall_score < 0.4:
                insight = LearningInsight(
                    insight_type="degradation",
                    title="Low Strategy Accuracy",
                    description=f"Strategy accuracy has dropped to {evaluation.overall_score:.0%}",
                    confidence=1 - evaluation.overall_score,
                    actionable=True,
                    recommendations=[
                        "Review recent market conditions",
                        "Consider pausing strategy",
                        "Analyze failure patterns",
                    ],
                )
                insights.append(insight)
        
        return insights
    
    def get_statistics(self) -> LearningStatistics:
        """Get learning engine statistics."""
        perf_summary = self.performance_tracker.get_performance_summary()
        memory_stats = self.strategic_memory.get_statistics()
        degradation_summary = self.degradation_detector.get_degradation_summary()
        confidence_summary = self.confidence_calibrator.get_confidence_summary()
        
        return LearningStatistics(
            total_memory_records=memory_stats.get("total_records", 0),
            total_outcome_records=len(self.outcome_evaluator._evaluation_history),
            total_degradation_alerts=len(self.degradation_detector._alerts),
            active_alerts=degradation_summary.get("total_active", 0),
            strategies_tracked=perf_summary.get("strategies", {}).get("total", 0),
            agents_tracked=perf_summary.get("agents", {}).get("total", 0),
            average_return_accuracy=self.outcome_evaluator.get_return_accuracy_stats().get("mean", 0),
            average_risk_accuracy=self.outcome_evaluator.get_risk_accuracy_stats().get("mean", 0),
            overall_win_rate=perf_summary.get("strategies", {}).get("overall_win_rate", 0),
            overall_expectancy=0.0,  # Could calculate from performance
            confidence_adjustments_count=confidence_summary.get("total_adjustments", 0),
            learning_cycle_count=self._learning_cycles,
        )


# Singleton instance
_learning_engine: Optional[LearningEngine] = None


def get_learning_engine() -> LearningEngine:
    """Get the global learning engine instance."""
    global _learning_engine
    if _learning_engine is None:
        _learning_engine = LearningEngine()
    return _learning_engine


def reset_learning_engine() -> None:
    """Reset the learning engine (for testing)."""
    global _learning_engine
    _learning_engine = None
