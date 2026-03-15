"""Output Models - schemas for PSIE operational outputs.

Defines canonical schemas for all PSIE intelligence outputs.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OutputCategory(str, Enum):
    """Categories of PSIE outputs."""
    STRATEGY = "strategy"
    EXECUTION = "execution"
    FINANCIAL = "financial"
    LEARNING = "learning"
    SYSTEM = "system"
    KNOWLEDGE = "knowledge"


class DecisionStatus(str, Enum):
    """Status of strategy decisions."""
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"
    EXPIRED = "expired"


class RiskLevel(str, Enum):
    """Risk level classifications."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============ Individual Output Models ============

class StrategyOutput(BaseModel):
    """Individual strategy output."""
    proposal_id: str
    title: str
    description: str
    decision: DecisionStatus
    confidence: float
    risk_level: RiskLevel
    agent_id: str
    category: str
    expected_outcome: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ExecutionOutput(BaseModel):
    """Individual execution output."""
    execution_id: str
    action_type: str
    status: str
    success: bool
    parameters: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FinancialOutput(BaseModel):
    """Financial intelligence output."""
    portfolio_value: float
    daily_return: float
    weekly_return: float
    monthly_return: float
    current_drawdown: float
    max_drawdown: float
    risk_exposure: str
    asset_allocation: Dict[str, float] = Field(default_factory=dict)
    liquidity_status: str
    cash_reserve: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class LearningOutput(BaseModel):
    """Learning insight output."""
    insight_id: str
    insight_type: str
    description: str
    strategy_id: Optional[str] = None
    confidence_change: Optional[float] = None
    performance_impact: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SystemOutput(BaseModel):
    """System metrics output."""
    signals_processed: int
    signals_by_category: Dict[str, int] = Field(default_factory=dict)
    agents_active: int
    agents_total: int
    agent_cycles_completed: int
    pipeline_latency_ms: float
    execution_latency_ms: float
    uptime_seconds: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class KnowledgeOutput(BaseModel):
    """Knowledge graph output."""
    entity_id: str
    entity_type: str
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    influence_score: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============ Report Models ============

class StrategyReport(BaseModel):
    """Strategy activity report."""
    report_id: str
    generated_at: datetime
    
    # Counts
    strategies_proposed: int
    strategies_approved: int
    strategies_rejected: int
    
    # Metrics
    average_confidence: float
    average_risk_score: float
    
    # Top items
    top_strategy: Optional[str] = None
    top_approved_strategy: Optional[str] = None
    
    # Recent outputs
    recent_outputs: List[StrategyOutput] = Field(default_factory=list)


class ExecutionReport(BaseModel):
    """Execution activity report."""
    report_id: str
    generated_at: datetime
    
    # Counts
    executions_today: int
    successful_executions: int
    failed_executions: int
    
    # Metrics
    execution_success_rate: float
    average_execution_time_ms: float
    
    # By type
    by_action_type: Dict[str, int] = Field(default_factory=dict)
    
    # Recent outputs
    recent_outputs: List[ExecutionOutput] = Field(default_factory=list)


class FinancialReport(BaseModel):
    """Financial intelligence report."""
    report_id: str
    generated_at: datetime
    
    # Portfolio metrics
    portfolio_value: float
    daily_return: float
    weekly_return: float
    monthly_return: float
    
    # Risk metrics
    current_drawdown: float
    max_drawdown: float
    risk_exposure: str
    
    # Allocation
    asset_allocation: Dict[str, float] = Field(default_factory=dict)
    
    # Liquidity
    liquidity_status: str
    cash_reserve: float


class LearningReport(BaseModel):
    """Learning insights report."""
    report_id: str
    generated_at: datetime
    
    # Activity
    learning_events: int
    strategy_improvements: int
    degradation_alerts: int
    confidence_adjustments: int
    
    # Insights
    recent_insights: List[LearningOutput] = Field(default_factory=list)
    
    # Performance
    overall_performance_change: Optional[float] = None


class SystemMetricsReport(BaseModel):
    """System metrics report."""
    report_id: str
    generated_at: datetime
    
    # Signal metrics
    signals_processed: int
    signals_by_category: Dict[str, int] = Field(default_factory=dict)
    
    # Agent metrics
    agents_active: int
    agents_total: int
    agent_cycles_completed: int
    
    # Pipeline metrics
    proposals_generated: int
    proposals_approved: int
    
    # Execution metrics
    executions_completed: int
    execution_success_rate: float
    
    # Latency metrics
    avg_signal_latency_ms: float
    avg_agent_latency_ms: float
    avg_pipeline_latency_ms: float
    avg_execution_latency_ms: float
    
    # System
    uptime_seconds: float


class EODReport(BaseModel):
    """End-of-Day Intelligence Report."""
    report_id: str
    generated_at: datetime
    
    # Summary counts
    signals_processed: int
    strategies_proposed: int
    proposals_approved: int
    proposals_rejected: int
    executions_completed: int
    executions_failed: int
    learning_events: int
    degradation_alerts: int
    
    # Performance
    overall_success_rate: float
    
    # Top insights
    top_insights: List[str] = Field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list)


# ============ Overview Model ============

class OutputsOverview(BaseModel):
    """Complete intelligence outputs overview."""
    generated_at: datetime
    
    # Strategy
    strategy: StrategyReport
    
    # Execution
    execution: ExecutionReport
    
    # Financial
    financial: FinancialReport
    
    # Learning
    learning: LearningReport
    
    # System
    system: SystemMetricsReport
    
    # Counts summary
    total_outputs: int
    output_categories: List[str] = Field(default_factory=list)
