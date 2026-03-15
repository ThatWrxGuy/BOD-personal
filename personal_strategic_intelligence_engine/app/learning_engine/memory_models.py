"""Memory Models - canonical schemas for PSIE historical knowledge.

This module provides data models for storing and retrieving strategic memory,
outcome records, performance snapshots, and learning metrics.
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MemoryCategory(str, Enum):
    """Categories of memory records."""
    SIGNAL = "signal"
    STRATEGY = "strategy"
    DECISION = "decision"
    EXECUTION = "execution"
    OUTCOME = "outcome"
    PERFORMANCE = "performance"
    AGENT = "agent"
    GOVERNANCE = "governance"


class SourceType(str, Enum):
    """Types of sources for memory records."""
    SIGNAL_BUS = "signal_bus"
    STRATEGY_PIPELINE = "strategy_pipeline"
    GOVERNANCE = "governance"
    EXECUTION_ENGINE = "execution_engine"
    AGENT = "agent"
    SIMULATION = "simulation"


class DegradationLevel(str, Enum):
    """Levels of performance degradation."""
    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class MemoryRecord(BaseModel):
    """A stored memory record in the strategic memory."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_type: SourceType
    source_id: str
    category: MemoryCategory
    summary: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "category": self.category,
            "summary": self.summary,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "tags": self.tags,
        }


class OutcomeRecord(BaseModel):
    """Record of an execution outcome with predictions vs actuals."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    execution_id: str
    proposal_id: str
    
    # Predicted outcomes (from simulations)
    predicted_return: Optional[float] = None
    predicted_drawdown: Optional[float] = None
    predicted_risk_level: Optional[str] = None
    confidence_score: Optional[float] = None
    
    # Actual outcomes (from execution)
    actual_return: Optional[float] = None
    actual_drawdown: Optional[float] = None
    actual_risk_level: Optional[str] = None
    success: bool = False
    
    # Evaluation
    return_accuracy: Optional[float] = None
    risk_accuracy: Optional[float] = None
    overall_score: Optional[float] = None
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def calculate_accuracy(self) -> None:
        """Calculate accuracy metrics."""
        if self.predicted_return is not None and self.actual_return is not None:
            if self.predicted_return != 0:
                self.return_accuracy = 1 - abs(self.actual_return - self.predicted_return) / abs(self.predicted_return)
            else:
                self.return_accuracy = 1.0 if self.actual_return == 0 else 0.0
        
        if self.predicted_risk_level and self.actual_risk_level:
            self.risk_accuracy = 1.0 if self.predicted_risk_level == self.actual_risk_level else 0.0
        
        # Overall score
        scores = [s for s in [self.return_accuracy, self.risk_accuracy] if s is not None]
        if scores:
            self.overall_score = sum(scores) / len(scores)


class StrategyPerformanceSnapshot(BaseModel):
    """Performance snapshot for a strategy."""
    strategy_id: str
    category: str
    
    # Performance metrics
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    
    # Return metrics
    average_return: float = 0.0
    total_return: float = 0.0
    best_return: Optional[float] = None
    worst_return: Optional[float] = None
    
    # Risk metrics
    average_drawdown: float = 0.0
    max_drawdown: float = 0.0
    
    # Accuracy metrics
    return_accuracy: float = 0.0
    risk_accuracy: float = 0.0
    
    # Calculated metrics
    win_rate: float = 0.0
    expectancy: float = 0.0
    
    # Time period
    period_start: datetime
    period_end: datetime
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class AgentPerformanceSnapshot(BaseModel):
    """Performance snapshot for an agent."""
    agent_id: str
    agent_name: str
    
    # Proposal metrics
    total_proposals: int = 0
    accepted_proposals: int = 0
    rejected_proposals: int = 0
    
    # Quality metrics
    average_confidence: float = 0.0
    confidence_accuracy: float = 0.0
    
    # Approval rates
    approval_rate: float = 0.0
    governance_override_rate: float = 0.0
    
    # Time period
    period_start: datetime
    period_end: datetime
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class DegradationAlert(BaseModel):
    """Alert for detected performance degradation."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: str  # strategy, agent, execution, confidence
    entity_id: str
    entity_type: str  # strategy, agent
    
    degradation_level: DegradationLevel
    metric_name: str
    previous_value: float
    current_value: float
    threshold: float
    
    description: str
    recommendations: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False


class ConfidenceAdjustment(BaseModel):
    """Record of confidence score adjustments."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_id: str
    entity_type: str  # strategy, agent
    
    previous_confidence: float
    new_confidence: float
    adjustment_reason: str
    
    based_on_samples: int = 0
    accuracy_delta: Optional[float] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LearningStatistics(BaseModel):
    """Statistics about learning and memory."""
    total_memory_records: int = 0
    total_outcome_records: int = 0
    total_degradation_alerts: int = 0
    active_alerts: int = 0
    
    strategies_tracked: int = 0
    agents_tracked: int = 0
    
    average_return_accuracy: float = 0.0
    average_risk_accuracy: float = 0.0
    
    overall_win_rate: float = 0.0
    overall_expectancy: float = 0.0
    
    confidence_adjustments_count: int = 0
    learning_cycle_count: int = 0


class LearningInsight(BaseModel):
    """Generated learning insight."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    insight_type: str  # improvement, degradation, pattern, recommendation
    title: str
    description: str
    
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    
    confidence: float = 0.5
    actionable: bool = False
    
    recommendations: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
