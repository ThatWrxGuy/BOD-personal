"""PSIE Output Report Models - standardized report schemas per V47-007.

This module defines the canonical schemas for all PSIE intelligence reports.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ReportType(str, Enum):
    """Types of PSIE reports."""
    EXECUTIVE_BRIEF = "executive_brief"
    STRATEGY_PROPOSAL = "strategy_proposal"
    GOVERNANCE_QUEUE = "governance_queue"
    EXECUTION_STATUS = "execution_status"
    FINANCIAL_INTELLIGENCE = "financial_intelligence"
    OPTIONS_INTELLIGENCE = "options_intelligence"
    LEARNING_REPORT = "learning_report"
    EOD_REPORT = "eod_report"


class ReportClassification(str, Enum):
    """Report classification per V47-007."""
    ADVISORY = "advisory"
    REVIEW_REQUIRED = "review_required"
    DECISION_REQUIRED = "decision_required"


# ============ Executive Brief ============

class SignalSummary(BaseModel):
    """Summary of signals detected."""
    total_signals: int = 0
    by_category: Dict[str, int] = Field(default_factory=dict)
    high_priority: int = 0
    critical: int = 0


class RiskSummary(BaseModel):
    """Summary of risks detected."""
    risks_detected: int = 0
    active_risks: List[Dict[str, Any]] = Field(default_factory=list)
    critical_risks: int = 0


class OpportunitySummary(BaseModel):
    """Summary of opportunities detected."""
    opportunities_detected: int = 0
    high_confidence: int = 0
    top_opportunities: List[Dict[str, Any]] = Field(default_factory=list)


class ExecutiveBrief(BaseModel):
    """Daily Executive Intelligence Brief."""
    report_type: str = "executive_brief"
    report_id: str
    generated_at: datetime
    
    # Signal summary
    signals_summary: SignalSummary = Field(default_factory=SignalSummary)
    
    # Risks
    risks_detected: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Opportunities
    opportunities_detected: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Financial snapshot
    financial_snapshot: Dict[str, Any] = Field(default_factory=dict)
    
    # Strategies
    strategies_proposed: int = 0
    strategies_approved: int = 0
    
    # Execution
    execution_summary: Dict[str, Any] = Field(default_factory=dict)
    
    # Alerts
    system_alerts: List[str] = Field(default_factory=list)
    
    # Classification
    classification: str = "advisory"


# ============ Strategy Proposal Report ============

class StrategyProposalReport(BaseModel):
    """Strategy Proposal Report."""
    report_type: str = "strategy_proposal"
    report_id: str
    generated_at: datetime
    
    proposals: List[Dict[str, Any]] = Field(default_factory=list)
    total_proposals: int = 0
    
    classification: str = "decision_required"


# ============ Governance Queue ============

class PendingDecision(BaseModel):
    """A decision pending approval."""
    decision_id: str
    decision_type: str
    risk_level: str
    proposal: Dict[str, Any] = Field(default_factory=dict)
    recommended_action: str
    submitted_at: datetime


class GovernanceQueueReport(BaseModel):
    """Governance Approval Queue."""
    report_type: str = "governance_queue"
    report_id: str
    generated_at: datetime
    
    pending_decisions: List[PendingDecision] = Field(default_factory=list)
    total_pending: int = 0
    
    classification: str = "decision_required"


# ============ Execution Status Report ============

class ActiveExecution(BaseModel):
    """An active execution task."""
    execution_id: str
    task_name: str
    status: str
    progress: float = 0.0
    started_at: datetime


class ExecutionStatusReport(BaseModel):
    """Execution Status Report."""
    report_type: str = "execution_status"
    report_id: str
    generated_at: datetime
    
    active_executions: List[ActiveExecution] = Field(default_factory=list)
    completed_today: int = 0
    failed_today: int = 0
    automation_status: str = "active"
    
    classification: str = "advisory"


# ============ Financial Intelligence Report ============

class FinancialIntelligenceReport(BaseModel):
    """Financial Risk & Opportunity Report."""
    report_type: str = "financial_intelligence"
    report_id: str
    generated_at: datetime
    
    # Liquidity
    liquidity_position: Dict[str, Any] = Field(default_factory=dict)
    
    # Debt
    debt_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    # Cashflow
    cashflow_forecast: Dict[str, Any] = Field(default_factory=dict)
    
    # Opportunities
    investment_opportunities: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Alerts
    risk_alerts: List[str] = Field(default_factory=list)
    
    classification: str = "review_required"


# ============ Options Intelligence Report ============

class OptionsIntelligenceReport(BaseModel):
    """SPY 0DTE Options Intelligence Brief."""
    report_type: str = "options_intelligence"
    report_id: str
    generated_at: datetime
    
    # Market conditions
    market_conditions: Dict[str, Any] = Field(default_factory=dict)
    
    # Greeks
    gamma_exposure: float = 0.0
    delta_velocity: float = 0.0
    
    # Liquidity
    liquidity_level: str = "normal"
    volume_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    # Volatility
    volatility_conditions: Dict[str, Any] = Field(default_factory=dict)
    
    # Strike candidates
    optimal_strikes: List[Dict[str, Any]] = Field(default_factory=list)
    
    classification: str = "review_required"


# ============ Learning Report ============

class LearningReport(BaseModel):
    """Learning & System Evolution Report."""
    report_type: str = "learning_report"
    report_id: str
    generated_at: datetime
    
    # Performance
    strategy_performance: Dict[str, Any] = Field(default_factory=dict)
    
    # Patterns
    detected_patterns: List[str] = Field(default_factory=list)
    
    # Degradation
    degradation_alerts: int = 0
    degraded_strategies: List[str] = Field(default_factory=list)
    
    # Feature importance
    feature_changes: Dict[str, float] = Field(default_factory=dict)
    
    classification: str = "advisory"


# ============ EOD Report ============

class EODReport(BaseModel):
    """End-of-Day System Report."""
    report_type: str = "eod_report"
    report_id: str
    generated_at: datetime
    
    # Daily stats
    signals_processed: int = 0
    strategies_evaluated: int = 0
    decisions_made: int = 0
    executions_performed: int = 0
    
    # Performance
    system_metrics: Dict[str, Any] = Field(default_factory=dict)
    
    # Summary
    daily_summary: str = ""
    
    classification: str = "advisory"


# ============ Output Generation Request ============

class OutputGenerateRequest(BaseModel):
    """Request to generate a specific output."""
    report_type: ReportType
    include_history: bool = False


class OutputListResponse(BaseModel):
    """List of available outputs."""
    reports: List[Dict[str, Any]] = Field(default_factory=list)
    total: int = 0
