"""Output Collector - collects raw outputs from PSIE subsystems.

The Output Collector gathers intelligence outputs from all PSIE subsystems
for aggregation and report generation.
"""
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.system_outputs.output_models import (
    StrategyOutput,
    ExecutionOutput,
    FinancialOutput,
    LearningOutput,
    SystemOutput,
    KnowledgeOutput,
    DecisionStatus,
    RiskLevel,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class OutputCollector:
    """
    Collects raw outputs from all PSIE subsystems.
    
    Sources:
    - Strategy Pipeline: proposal decisions
    - Execution Engine: executed actions
    - Learning Engine: learning insights
    - Knowledge Graph: contextual patterns
    - Signal Bus: signal statistics
    - Scheduler: cycle metrics
    """
    
    def __init__(self):
        self._strategy_outputs: List[StrategyOutput] = []
        self._execution_outputs: List[ExecutionOutput] = []
        self._financial_outputs: List[FinancialOutput] = []
        self._learning_outputs: List[LearningOutput] = []
        self._system_outputs: List[SystemOutput] = []
        self._knowledge_outputs: List[KnowledgeOutput] = []
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample data for demonstration."""
        # Sample strategy outputs
        for i in range(5):
            self._strategy_outputs.append(StrategyOutput(
                proposal_id=f"prop_{uuid.uuid4().hex[:8]}",
                title=f"Strategy Alpha {i+1}",
                description=f"Proposed strategy for market condition {i+1}",
                decision=DecisionStatus.APPROVED if i < 3 else DecisionStatus.REJECTED,
                confidence=0.65 + (i * 0.05),
                risk_level=RiskLevel.MEDIUM,
                agent_id=f"agent_{i % 4}",
                category="momentum",
                timestamp=datetime.utcnow() - timedelta(hours=i),
            ))
        
        # Sample execution outputs
        for i in range(4):
            self._execution_outputs.append(ExecutionOutput(
                execution_id=f"exec_{uuid.uuid4().hex[:8]}",
                action_type="trade_execution" if i < 3 else "portfolio_adjustment",
                status="completed" if i < 3 else "failed",
                success=i < 3,
                parameters={"symbol": "SPY", "quantity": 100 * (i+1)},
                result={"price": 450.00 + i, "commission": 1.00},
                timestamp=datetime.utcnow() - timedelta(hours=i*2),
            ))
        
        # Sample learning outputs
        for i in range(3):
            self._learning_outputs.append(LearningOutput(
                insight_id=f"insight_{uuid.uuid4().hex[:8]}",
                insight_type="performance_improvement" if i < 2 else "confidence_adjustment",
                description=f"Detected improvement in strategy performance metrics",
                strategy_id=f"strategy_{i}",
                confidence_change=0.05 if i < 2 else -0.02,
                performance_impact=0.03,
                timestamp=datetime.utcnow() - timedelta(hours=i*3),
            ))
        
        # Sample system output
        self._system_outputs.append(SystemOutput(
            signals_processed=42,
            signals_by_category={"financial": 15, "market": 12, "risk": 8, "governance": 4, "system": 3},
            agents_active=4,
            agents_total=8,
            agent_cycles_completed=24,
            pipeline_latency_ms=450.0,
            execution_latency_ms=120.0,
            uptime_seconds=3600.0,
            timestamp=datetime.utcnow(),
        ))
    
    # ============ Strategy Outputs ============
    
    def add_strategy_output(self, output: StrategyOutput):
        """Add a strategy output."""
        self._strategy_outputs.append(output)
    
    def get_strategy_outputs(self, limit: int = 50) -> List[StrategyOutput]:
        """Get recent strategy outputs."""
        return self._strategy_outputs[-limit:]
    
    def get_strategy_outputs_by_decision(
        self,
        decision: DecisionStatus,
    ) -> List[StrategyOutput]:
        """Get strategy outputs by decision type."""
        return [o for o in self._strategy_outputs if o.decision == decision]
    
    # ============ Execution Outputs ============
    
    def add_execution_output(self, output: ExecutionOutput):
        """Add an execution output."""
        self._execution_outputs.append(output)
    
    def get_execution_outputs(self, limit: int = 50) -> List[ExecutionOutput]:
        """Get recent execution outputs."""
        return self._execution_outputs[-limit:]
    
    def get_execution_outputs_by_status(
        self,
        status: str,
    ) -> List[ExecutionOutput]:
        """Get execution outputs by status."""
        return [o for o in self._execution_outputs if o.status == status]
    
    # ============ Financial Outputs ============
    
    def add_financial_output(self, output: FinancialOutput):
        """Add a financial output."""
        self._financial_outputs.append(output)
    
    def get_financial_outputs(self, limit: int = 10) -> List[FinancialOutput]:
        """Get recent financial outputs."""
        return self._financial_outputs[-limit:]
    
    def get_latest_financial(self) -> Optional[FinancialOutput]:
        """Get the latest financial output."""
        if self._financial_outputs:
            return self._financial_outputs[-1]
        return None
    
    # ============ Learning Outputs ============
    
    def add_learning_output(self, output: LearningOutput):
        """Add a learning output."""
        self._learning_outputs.append(output)
    
    def get_learning_outputs(self, limit: int = 50) -> List[LearningOutput]:
        """Get recent learning outputs."""
        return self._learning_outputs[-limit:]
    
    # ============ System Outputs ============
    
    def add_system_output(self, output: SystemOutput):
        """Add a system output."""
        self._system_outputs.append(output)
    
    def get_system_outputs(self, limit: int = 10) -> List[SystemOutput]:
        """Get recent system outputs."""
        return self._system_outputs[-limit:]
    
    def get_latest_system(self) -> Optional[SystemOutput]:
        """Get the latest system output."""
        if self._system_outputs:
            return self._system_outputs[-1]
        return None
    
    # ============ Knowledge Outputs ============
    
    def add_knowledge_output(self, output: KnowledgeOutput):
        """Add a knowledge output."""
        self._knowledge_outputs.append(output)
    
    def get_knowledge_outputs(self, limit: int = 50) -> List[KnowledgeOutput]:
        """Get recent knowledge outputs."""
        return self._knowledge_outputs[-limit:]
    
    # ============ Statistics ============
    
    def get_output_counts(self) -> Dict[str, int]:
        """Get counts of outputs by category."""
        return {
            "strategy": len(self._strategy_outputs),
            "execution": len(self._execution_outputs),
            "financial": len(self._financial_outputs),
            "learning": len(self._learning_outputs),
            "system": len(self._system_outputs),
            "knowledge": len(self._knowledge_outputs),
        }
    
    def clear_outputs(self, category: Optional[str] = None):
        """Clear outputs, optionally by category."""
        if category is None:
            self._strategy_outputs.clear()
            self._execution_outputs.clear()
            self._financial_outputs.clear()
            self._learning_outputs.clear()
            self._system_outputs.clear()
            self._knowledge_outputs.clear()
        elif category == "strategy":
            self._strategy_outputs.clear()
        elif category == "execution":
            self._execution_outputs.clear()
        elif category == "financial":
            self._financial_outputs.clear()
        elif category == "learning":
            self._learning_outputs.clear()
        elif category == "system":
            self._system_outputs.clear()
        elif category == "knowledge":
            self._knowledge_outputs.clear()


# Singleton instance
_output_collector: Optional[OutputCollector] = None


def get_output_collector() -> OutputCollector:
    """Get the global output collector instance."""
    global _output_collector
    if _output_collector is None:
        _output_collector = OutputCollector()
    return _output_collector


def reset_output_collector() -> None:
    """Reset the output collector (for testing)."""
    global _output_collector
    _output_collector = None
