"""Decision Tracker - Tracks strategic decisions made by the system."""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from app.intelligence.learning.learning_models import (
    DecisionRecord,
    DecisionStatus,
    StrategyType,
)


class DecisionTracker:
    """Tracks strategic decisions issued by the synthesizer."""
    
    def __init__(self):
        self.decisions: List[DecisionRecord] = []
    
    def track_decision(
        self,
        recommendation_id: str,
        strategy_type: StrategyType,
        action: str,
        expected_outcome: str,
        confidence: float,
        priority_score: float,
        domain_state: Dict[str, float],
        risk_state: Optional[Dict[str, float]] = None,
        insight_id: Optional[str] = None,
        source_engine: str = "synthesizer",
    ) -> DecisionRecord:
        """Track a new strategic decision."""
        
        decision = DecisionRecord(
            decision_id=str(uuid.uuid4())[:8],
            timestamp=datetime.utcnow(),
            insight_id=insight_id,
            recommendation_id=recommendation_id,
            strategy_type=strategy_type,
            action=action,
            expected_outcome=expected_outcome,
            confidence=confidence,
            priority_score=priority_score,
            domain_state=domain_state,
            risk_state=risk_state or {},
            status=DecisionStatus.PENDING,
            source_engine=source_engine,
        )
        
        self.decisions.append(decision)
        
        return decision
    
    def get_decision(self, decision_id: str) -> Optional[DecisionRecord]:
        """Get a specific decision."""
        
        for decision in self.decisions:
            if decision.decision_id == decision_id:
                return decision
        
        return None
    
    def get_pending_decisions(self) -> List[DecisionRecord]:
        """Get all pending decisions."""
        
        return [
            d for d in self.decisions
            if d.status == DecisionStatus.PENDING
        ]
    
    def get_decisions_for_evaluation(
        self,
        evaluation_delay_days: int = 7,
    ) -> List[DecisionRecord]:
        """Get decisions ready for outcome evaluation."""
        
        cutoff = datetime.utcnow() - timedelta(days=evaluation_delay_days)
        
        return [
            d for d in self.decisions
            if d.status == DecisionStatus.PENDING
            and d.timestamp < cutoff
        ]
    
    def mark_evaluated(
        self,
        decision_id: str,
        evaluation_id: str,
    ) -> bool:
        """Mark a decision as evaluated."""
        
        decision = self.get_decision(decision_id)
        
        if decision:
            decision.status = DecisionStatus.EVALUATED
            decision.evaluation_id = evaluation_id
            return True
        
        return False
    
    def get_decisions_by_strategy(
        self,
        strategy_type: StrategyType,
    ) -> List[DecisionRecord]:
        """Get all decisions of a specific strategy type."""
        
        return [
            d for d in self.decisions
            if d.strategy_type == strategy_type
        ]
    
    def get_recent_decisions(
        self,
        days: int = 30,
    ) -> List[DecisionRecord]:
        """Get recent decisions."""
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        return [
            d for d in self.decisions
            if d.timestamp > cutoff
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get tracking statistics."""
        
        total = len(self.decisions)
        
        if total == 0:
            return {"total_decisions": 0}
        
        by_status = {
            "pending": 0,
            "in_progress": 0,
            "evaluated": 0,
            "expired": 0,
        }
        
        by_strategy = {}
        
        for decision in self.decisions:
            by_status[decision.status.value] = by_status.get(decision.status.value, 0) + 1
            
            strategy = decision.strategy_type.value
            by_strategy[strategy] = by_strategy.get(strategy, 0) + 1
        
        return {
            "total_decisions": total,
            "by_status": by_status,
            "by_strategy": by_strategy,
        }
    
    def clear_old_decisions(self, days: int = 90) -> int:
        """Clear decisions older than specified days."""
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        original_count = len(self.decisions)
        
        self.decisions = [
            d for d in self.decisions
            if d.timestamp > cutoff or d.status == DecisionStatus.PENDING
        ]
        
        return original_count - len(self.decisions)


_tracker: Optional[DecisionTracker] = None


def get_decision_tracker() -> DecisionTracker:
    """Get the global decision tracker."""
    global _tracker
    if _tracker is None:
        _tracker = DecisionTracker()
    return _tracker
