"""Optimization Logger - Records optimization cycles and decisions."""
import json
import logging
from datetime import datetime, timedelta
from typing import Optional

from app.optimization.optimization_types import (
    OptimizationCycle,
    OptimizationSummary,
    TradeoffDecision,
    OptimizationActionRecommendation,
    DomainConditionResult,
)

# Use standard logging
logger = logging.getLogger(__name__)


class OptimizationLogger:
    """Records and retrieves optimization cycle data."""
    
    def __init__(self):
        self._cycles: list[OptimizationCycle] = []
        self._summaries: list[OptimizationSummary] = []
    
    def record_cycle(self, cycle: OptimizationCycle) -> None:
        """Record a completed optimization cycle."""
        self._cycles.append(cycle)
        logger.info(
            f"Optimization cycle {cycle.cycle_id} recorded: "
            f"{len(cycle.recommendations)} recommendations, "
            f"balance score: {cycle.overall_balance_score:.2f}"
        )
    
    def record_summary(self, summary: OptimizationSummary) -> None:
        """Record an optimization summary."""
        self._summaries.append(summary)
        logger.info(
            f"Optimization summary recorded: health={summary.overall_health:.2f}, "
            f"balance={summary.balance_score:.2f}, "
            f"recommendations={summary.pending_recommendations}"
        )
    
    def get_recent_cycles(self, count: int = 10) -> list[OptimizationCycle]:
        """Get the most recent optimization cycles."""
        return sorted(
            self._cycles,
            key=lambda c: c.timestamp,
            reverse=True
        )[:count]
    
    def get_latest_cycle(self) -> Optional[OptimizationCycle]:
        """Get the most recent optimization cycle."""
        cycles = self.get_recent_cycles(1)
        return cycles[0] if cycles else None
    
    def get_latest_summary(self) -> Optional[OptimizationSummary]:
        """Get the most recent optimization summary."""
        if self._summaries:
            return sorted(self._summaries, key=lambda s: s.last_cycle_timestamp or datetime.min, reverse=True)[0]
        return None
    
    def get_cycle_history(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> list[OptimizationCycle]:
        """Get cycle history within a time range."""
        cycles = self._cycles
        
        if start_time:
            cycles = [c for c in cycles if c.timestamp >= start_time]
        if end_time:
            cycles = [c for c in cycles if c.timestamp <= end_time]
        
        return sorted(cycles, key=lambda c: c.timestamp, reverse=True)
    
    def get_cycles_today(self) -> int:
        """Get the number of cycles run today."""
        today = datetime.utcnow().date()
        return sum(
            1 for c in self._cycles
            if c.timestamp.date() == today
        )
    
    def export_cycle_json(self, cycle: OptimizationCycle) -> str:
        """Export a cycle to JSON string."""
        return cycle.model_dump_json(indent=2)
    
    def export_summary_json(self, summary: OptimizationSummary) -> str:
        """Export a summary to JSON string."""
        return summary.model_dump_json(indent=2)
    
    def log_recommendation(self, rec: OptimizationActionRecommendation) -> None:
        """Log a recommendation decision."""
        logger.info(
            f"Recommendation: {rec.action.value} for {rec.target_domain.value} - "
            f"priority={rec.priority}, impact={rec.expected_impact:.2f}, "
            f"reasoning: {rec.reasoning}"
        )
    
    def log_tradeoff(self, decision: TradeoffDecision) -> None:
        """Log a tradeoff decision."""
        winner = decision.winner.value if decision.winner else "none"
        loser = decision.loser.value if decision.loser else "none"
        logger.info(
            f"Tradeoff {decision.tradeoff_type.value}: {winner} wins over {loser} - "
            f"reasoning: {decision.reasoning}"
        )
    
    def log_condition(self, condition: DomainConditionResult) -> None:
        """Log a detected domain condition."""
        logger.info(
            f"Domain {condition.domain.value}: {condition.condition.value} "
            f"(severity={condition.severity:.2f}) - evidence: {condition.evidence}"
        )
    
    def clear_old_cycles(self, days: int = 30) -> int:
        """Clear cycles older than specified days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        old_count = len(self._cycles)
        self._cycles = [
            c for c in self._cycles
            if c.timestamp >= cutoff
        ]
        cleared = old_count - len(self._cycles)
        logger.info(f"Cleared {cleared} optimization cycles older than {days} days")
        return cleared
    
    def get_statistics(self) -> dict:
        """Get optimization statistics."""
        if not self._cycles:
            return {
                "total_cycles": 0,
                "average_balance_score": 0.0,
                "average_health": 0.0,
                "total_recommendations": 0,
            }
        
        return {
            "total_cycles": len(self._cycles),
            "average_balance_score": sum(c.overall_balance_score for c in self._cycles) / len(self._cycles),
            "average_health": sum(
                sum(dm.composite_score for dm in c.domain_metrics) / len(c.domain_metrics)
                for c in self._cycles
            ) / len(self._cycles),
            "total_recommendations": sum(len(c.recommendations) for c in self._cycles),
            "cycles_today": self.get_cycles_today(),
        }


# Global logger instance
_optimization_logger: Optional[OptimizationLogger] = None


def get_optimization_logger() -> OptimizationLogger:
    """Get the global optimization logger."""
    global _optimization_logger
    if _optimization_logger is None:
        _optimization_logger = OptimizationLogger()
    return _optimization_logger
