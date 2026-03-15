"""Audit Models - schemas for system audit and validation.

Defines data models for system validation, metrics, and reports.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AuditStatus(str, Enum):
    """Status of an audit run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SubsystemStatus(str, Enum):
    """Status of a subsystem."""
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    PENDING = "pending"


class SignalCategory(str, Enum):
    """Categories of signals for testing."""
    FINANCIAL = "financial"
    MARKET = "market"
    RISK = "risk"
    GOVERNANCE = "governance"
    SYSTEM = "system"


class ValidationStep(BaseModel):
    """A single validation step."""
    step_name: str
    status: SubsystemStatus
    duration_ms: float = 0.0
    message: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class AuditResult(BaseModel):
    """Result of a full system audit."""
    audit_id: str
    status: AuditStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0
    
    # Subsystem results
    subsystems: Dict[str, SubsystemStatus] = Field(default_factory=dict)
    
    # Validation steps
    validation_steps: List[ValidationStep] = Field(default_factory=list)
    
    # Metrics
    metrics: Dict[str, Any] = Field(default_factory=dict)
    
    # Errors
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class SystemMetrics(BaseModel):
    """System performance metrics."""
    # Signal metrics
    signals_processed: int = 0
    signals_by_category: Dict[str, int] = Field(default_factory=dict)
    
    # Agent metrics
    agents_active: int = 0
    agents_total: int = 0
    agent_cycles_completed: int = 0
    
    # Strategy pipeline metrics
    proposals_generated: int = 0
    proposals_approved: int = 0
    proposals_rejected: int = 0
    debates_completed: int = 0
    simulations_run: int = 0
    
    # Execution metrics
    executions_triggered: int = 0
    executions_completed: int = 0
    executions_failed: int = 0
    success_rate: float = 0.0
    
    # Learning metrics
    learning_events: int = 0
    degradation_alerts: int = 0
    confidence_adjustments: int = 0
    
    # Graph metrics
    entities_created: int = 0
    relationships_created: int = 0
    
    # Latency metrics (in ms)
    avg_signal_latency: float = 0.0
    avg_agent_latency: float = 0.0
    avg_pipeline_latency: float = 0.0
    avg_execution_latency: float = 0.0


class EODIntelligenceReport(BaseModel):
    """End-of-Day Intelligence Report."""
    report_id: str
    generated_at: datetime
    
    # Summary metrics
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


class FinancialIntelligenceReport(BaseModel):
    """Financial Intelligence Report."""
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


class SystemAuditReport(BaseModel):
    """Full System Audit Report."""
    report_id: str
    generated_at: datetime
    
    # Subsystem status
    subsystem_status: Dict[str, SubsystemStatus] = Field(default_factory=dict)
    
    # Overall health
    overall_health_score: float
    system_status: str
    
    # Detailed metrics
    metrics: SystemMetrics
    
    # Performance
    uptime_seconds: float
    
    # Error summary
    total_errors: int
    error_summary: Dict[str, int] = Field(default_factory=dict)
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list)


class AuditRequest(BaseModel):
    """Request to run an audit."""
    test_signals: bool = True
    test_agents: bool = True
    test_pipeline: bool = True
    test_execution: bool = True
    test_learning: bool = True
    test_graph: bool = True


class AuditSummary(BaseModel):
    """Summary of audit status."""
    last_audit_id: Optional[str] = None
    last_audit_status: Optional[AuditStatus] = None
    last_audit_time: Optional[datetime] = None
    next_scheduled: Optional[datetime] = None
