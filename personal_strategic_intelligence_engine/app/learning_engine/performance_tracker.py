"""Performance Tracker - tracks long-term system performance.

The Performance Tracker maintains performance metrics for strategies, agents,
action types, and decision categories over time.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.learning_engine.memory_models import (
    AgentPerformanceSnapshot,
    StrategyPerformanceSnapshot,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class PerformanceTracker:
    """
    Tracks long-term system performance.
    
    Tracked entities:
    - strategies
    - agents
    - action types
    - decision categories
    
    Metrics include:
    - win rate
    - expectancy
    - drawdown statistics
    - confidence accuracy
    - execution success rate
    """
    
    def __init__(self):
        # Strategy performance: strategy_id -> StrategyPerformanceSnapshot
        self._strategy_performance: Dict[str, StrategyPerformanceSnapshot] = {}
        
        # Agent performance: agent_id -> AgentPerformanceSnapshot
        self._agent_performance: Dict[str, AgentPerformanceSnapshot] = {}
        
        # Action type performance
        self._action_type_stats: Dict[str, Dict[str, Any]] = {}
    
    def update_strategy_performance(
        self,
        strategy_id: str,
        category: str,
        success: bool,
        return_value: Optional[float] = None,
        drawdown: Optional[float] = None,
    ) -> StrategyPerformanceSnapshot:
        """
        Update performance for a strategy.
        
        Args:
            strategy_id: The strategy identifier
            category: Strategy category
            success: Whether execution was successful
            return_value: Return value from execution
            drawdown: Drawdown value
            
        Returns:
            Updated performance snapshot
        """
        if strategy_id not in self._strategy_performance:
            # Create new snapshot
            now = datetime.utcnow()
            self._strategy_performance[strategy_id] = StrategyPerformanceSnapshot(
                strategy_id=strategy_id,
                category=category,
                period_start=now,
                period_end=now,
            )
        
        snapshot = self._strategy_performance[strategy_id]
        snapshot.total_executions += 1
        
        if success:
            snapshot.successful_executions += 1
        else:
            snapshot.failed_executions += 1
        
        # Update return metrics
        if return_value is not None:
            snapshot.total_return += return_value
            
            if snapshot.best_return is None or return_value > snapshot.best_return:
                snapshot.best_return = return_value
            
            if snapshot.worst_return is None or return_value < snapshot.worst_return:
                snapshot.worst_return = return_value
            
            # Recalculate average
            if snapshot.total_executions > 0:
                snapshot.average_return = snapshot.total_return / snapshot.total_executions
        
        # Update drawdown metrics
        if drawdown is not None:
            if drawdown > snapshot.max_drawdown:
                snapshot.max_drawdown = drawdown
            
            # Recalculate average
            total_dd = snapshot.average_drawdown * (snapshot.total_executions - 1) + drawdown
            snapshot.average_drawdown = total_dd / snapshot.total_executions
        
        # Calculate win rate
        if snapshot.total_executions > 0:
            snapshot.win_rate = snapshot.successful_executions / snapshot.total_executions
        
        # Calculate expectancy (average return weighted by win/loss)
        if snapshot.total_executions > 0 and snapshot.average_return != 0:
            loss_rate = 1 - snapshot.win_rate
            avg_win = snapshot.average_return if snapshot.average_return > 0 else 0
            avg_loss = abs(snapshot.average_return) if snapshot.average_return < 0 else 0
            
            if loss_rate > 0:
                snapshot.expectancy = (snapshot.win_rate * avg_win) - (loss_rate * avg_loss)
        
        snapshot.last_updated = datetime.utcnow()
        
        logger.info(f"Updated strategy performance: {strategy_id}, win_rate={snapshot.win_rate:.2%}")
        
        return snapshot
    
    def update_agent_performance(
        self,
        agent_id: str,
        agent_name: str,
        proposal_accepted: bool,
        confidence_score: Optional[float] = None,
        governance_overridden: bool = False,
    ) -> AgentPerformanceSnapshot:
        """
        Update performance for an agent.
        
        Args:
            agent_id: The agent identifier
            agent_name: The agent name
            proposal_accepted: Whether proposal was accepted
            confidence_score: Confidence score of proposal
            governance_overridden: Whether governance overrode agent decision
            
        Returns:
            Updated performance snapshot
        """
        if agent_id not in self._agent_performance:
            now = datetime.utcnow()
            self._agent_performance[agent_id] = AgentPerformanceSnapshot(
                agent_id=agent_id,
                agent_name=agent_name,
                period_start=now,
                period_end=now,
            )
        
        snapshot = self._agent_performance[agent_id]
        snapshot.total_proposals += 1
        
        if proposal_accepted:
            snapshot.accepted_proposals += 1
        else:
            snapshot.rejected_proposals += 1
        
        # Update confidence metrics
        if confidence_score is not None:
            # Weighted average update
            n = snapshot.total_proposals - 1  # before this proposal
            if n > 0:
                snapshot.average_confidence = (
                    (snapshot.average_confidence * n) + confidence_score
                ) / snapshot.total_proposals
            else:
                snapshot.average_confidence = confidence_score
        
        # Update approval rate
        if snapshot.total_proposals > 0:
            snapshot.approval_rate = snapshot.accepted_proposals / snapshot.total_proposals
        
        # Update governance override rate
        if governance_overridden:
            snapshot.governance_override_rate = (
                (snapshot.governance_override_rate * (snapshot.total_proposals - 1)) + 1
            ) / snapshot.total_proposals
        
        snapshot.last_updated = datetime.utcnow()
        
        logger.info(f"Updated agent performance: {agent_id}, approval_rate={snapshot.approval_rate:.2%}")
        
        return snapshot
    
    def update_action_type_performance(
        self,
        action_type: str,
        success: bool,
        execution_time_ms: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Update performance for an action type.
        
        Args:
            action_type: The type of action
            success: Whether execution succeeded
            execution_time_ms: Time taken to execute
            
        Returns:
            Updated stats
        """
        if action_type not in self._action_type_stats:
            self._action_type_stats[action_type] = {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "total_time_ms": 0.0,
                "avg_time_ms": 0.0,
            }
        
        stats = self._action_type_stats[action_type]
        stats["total"] += 1
        
        if success:
            stats["successful"] += 1
        else:
            stats["failed"] += 1
        
        if execution_time_ms is not None:
            stats["total_time_ms"] += execution_time_ms
            stats["avg_time_ms"] = stats["total_time_ms"] / stats["total"]
        
        return stats
    
    def get_strategy_performance(
        self,
        strategy_id: str,
    ) -> Optional[StrategyPerformanceSnapshot]:
        """Get performance snapshot for a strategy."""
        return self._strategy_performance.get(strategy_id)
    
    def get_agent_performance(
        self,
        agent_id: str,
    ) -> Optional[AgentPerformanceSnapshot]:
        """Get performance snapshot for an agent."""
        return self._agent_performance.get(agent_id)
    
    def get_action_type_stats(
        self,
        action_type: str,
    ) -> Optional[Dict[str, Any]]:
        """Get stats for an action type."""
        return self._action_type_stats.get(action_type)
    
    def get_all_strategy_performance(self) -> List[StrategyPerformanceSnapshot]:
        """Get all strategy performance snapshots."""
        return list(self._strategy_performance.values())
    
    def get_all_agent_performance(self) -> List[AgentPerformanceSnapshot]:
        """Get all agent performance snapshots."""
        return list(self._agent_performance.values())
    
    def get_top_performing_strategies(self, limit: int = 10) -> List[StrategyPerformanceSnapshot]:
        """Get top performing strategies by win rate."""
        strategies = sorted(
            self._strategy_performance.values(),
            key=lambda s: s.win_rate,
            reverse=True,
        )
        return strategies[:limit]
    
    def get_underperforming_strategies(
        self,
        min_executions: int = 5,
        threshold: float = 0.4,
    ) -> List[StrategyPerformanceSnapshot]:
        """Get strategies that are underperforming."""
        return [
            s for s in self._strategy_performance.values()
            if s.total_executions >= min_executions and s.win_rate < threshold
        ]
    
    def get_top_agents(self, limit: int = 10) -> List[AgentPerformanceSnapshot]:
        """Get top performing agents by approval rate."""
        agents = sorted(
            self._agent_performance.values(),
            key=lambda a: a.approval_rate,
            reverse=True,
        )
        return agents[:limit]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary."""
        strategies = list(self._strategy_performance.values())
        agents = list(self._agent_performance.values())
        
        # Calculate aggregate metrics
        total_strat_executions = sum(s.total_executions for s in strategies)
        total_successful = sum(s.successful_executions for s in strategies)
        
        overall_win_rate = (
            total_successful / total_strat_executions
            if total_strat_executions > 0 else 0.0
        )
        
        avg_return = (
            sum(s.average_return for s in strategies) / len(strategies)
            if strategies else 0.0
        )
        
        avg_approval_rate = (
            sum(a.approval_rate for a in agents) / len(agents)
            if agents else 0.0
        )
        
        return {
            "strategies": {
                "total": len(strategies),
                "total_executions": total_strat_executions,
                "overall_win_rate": overall_win_rate,
                "average_return": avg_return,
            },
            "agents": {
                "total": len(agents),
                "average_approval_rate": avg_approval_rate,
            },
            "action_types": {
                "total": len(self._action_type_stats),
                "types": {
                    k: {
                        "total": v["total"],
                        "success_rate": v["successful"] / v["total"] if v["total"] > 0 else 0,
                        "avg_time_ms": v["avg_time_ms"],
                    }
                    for k, v in self._action_type_stats.items()
                },
            },
        }


# Singleton instance
_performance_tracker: Optional[PerformanceTracker] = None


def get_performance_tracker() -> PerformanceTracker:
    """Get the global performance tracker instance."""
    global _performance_tracker
    if _performance_tracker is None:
        _performance_tracker = PerformanceTracker()
    return _performance_tracker


def reset_performance_tracker() -> None:
    """Reset the performance tracker (for testing)."""
    global _performance_tracker
    _performance_tracker = None
