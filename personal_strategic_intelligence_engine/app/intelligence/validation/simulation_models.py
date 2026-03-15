"""Validation Models - Data structures for system validation."""
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class ScenarioDomain(str, Enum):
    """Domains for validation scenarios."""
    FINANCIAL = "financial"
    CAREER = "career"
    HEALTH = "health"
    OPERATIONS = "operations"
    RELATIONSHIPS = "relationships"
    MIXED = "mixed"


class SimulationStatus(str, Enum):
    """Status of simulation."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationScenario(BaseModel):
    """A scenario for system validation."""
    id: str
    name: str
    description: str
    
    domain: ScenarioDomain
    
    # Initial state
    initial_state: Dict[str, Any] = Field(default_factory=dict)
    
    # Goal
    goal: str
    goal_metrics: Dict[str, float] = Field(default_factory=dict)
    
    # Constraints
    constraints: Dict[str, Any] = Field(default_factory=dict)
    
    # Challenges
    expected_challenges: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SimulationResult(BaseModel):
    """Result of a simulation run."""
    id: str
    scenario_id: str
    
    system_used: bool
    
    # Outcome metrics
    outcome_score: float = Field(ge=0, le=100)
    risk_exposure: float = Field(ge=0, le=100)
    goal_completion: float = Field(ge=0, le=100)
    execution_efficiency: float = Field(ge=0, le=100)
    resource_utilization: float = Field(ge=0, le=100)
    decision_quality: float = Field(ge=0, le=100)
    
    # Additional
    duration_days: int = 0
    decisions_made: int = 0
    adjustments_made: int = 0
    
    # Details
    steps_taken: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class PerformanceComparison(BaseModel):
    """Comparison between baseline and system results."""
    scenario_id: str
    scenario_name: str
    
    # Scores
    baseline_score: float
    system_score: float
    improvement_delta: float
    
    # Metrics
    goal_improvement: float
    risk_reduction: float
    efficiency_gain: float
    decision_quality_improvement: float
    
    # Summary
    system_wins: bool
    margin: float


class AuditCategory(str, Enum):
    """Categories for system audit."""
    ARCHITECTURE = "architecture"
    CODE_ORGANIZATION = "code_organization"
    DATA_MODELS = "data_models"
    PIPELINE_INTEGRATION = "pipeline_integration"
    EXECUTION_SAFETY = "execution_safety"
    LEARNING_LOOP = "learning_loop"


class AuditIssue(BaseModel):
    """An issue found during audit."""
    category: AuditCategory
    severity: str  # low, medium, high, critical
    description: str
    location: str
    recommendation: str


class SystemAuditReport(BaseModel):
    """System audit report."""
    id: str
    
    # Scores
    architecture_score: float
    integration_score: float
    reliability_score: float
    maintainability_score: float
    
    overall_score: float
    
    # Issues
    issues_found: List[AuditIssue] = Field(default_factory=list)
    critical_issues: int = 0
    high_issues: int = 0
    
    # Details
    modules_checked: int = 0
    modules_passed: int = 0
    
    recommendations: List[str] = Field(default_factory=list)
    
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class ValidationReport(BaseModel):
    """Complete validation report."""
    id: str
    
    # Scenario results
    scenarios_run: int = 0
    scenarios_succeeded: int = 0
    
    # Performance
    average_improvement: float = 0.0
    average_risk_reduction: float = 0.0
    
    # System
    system_wins: int = 0
    baseline_wins: int = 0
    
    # Comparison
    performance_comparisons: List[PerformanceComparison] = Field(default_factory=list)
    
    # Audit
    audit_report: Optional[SystemAuditReport] = None
    
    completed_at: datetime = Field(default_factory=datetime.utcnow)
