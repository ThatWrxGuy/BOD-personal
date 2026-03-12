"""Optimization Types - Core models and enums for the optimization system."""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class LifeDomain(str, Enum):
    """Core life domains that the system optimizes across."""
    HEALTH = "health"
    WEALTH = "wealth"
    CAREER = "career"
    LEARNING = "learning"
    RELATIONSHIPS = "relationships"
    PERSONAL_DEVELOPMENT = "personal_development"
    OPERATIONS = "operations"
    STRATEGIC_PROJECTS = "strategic_projects"

    @classmethod
    def get_all(cls) -> list[str]:
        """Get all domain names."""
        return [d.value for d in cls]


class DomainCondition(str, Enum):
    """Detected conditions in a domain."""
    HEALTHY = "healthy"
    NEGLECTED = "neglected"
    OVERINVESTED = "overinvested"
    UNSTABLE = "unstable"
    OPPORTUNITY_WINDOW = "opportunity_window"
    RISK_ESCALATION = "risk_escalation"
    STRATEGIC_IMBALANCE = "strategic_imbalance"


class OptimizationAction(str, Enum):
    """Possible optimization actions."""
    INCREASE_PRIORITY = "increase_priority"
    DECREASE_PRIORITY = "decrease_priority"
    SHIFT_FOCUS_BLOCKS = "shift_focus_blocks"
    ADJUST_WEEKLY_THEMES = "adjust_weekly_themes"
    INTRODUCE_RECOVERY = "introduce_recovery"
    TRIGGER_HABIT_INTERVENTION = "trigger_habit_intervention"
    ESCALATE_TO_STRATEGIC = "escalate_to_strategic"
    MAINTAIN_STATUS_QUO = "maintain_status_quo"


class TradeoffType(str, Enum):
    """Types of tradeoffs between domains."""
    CAREER_VS_HEALTH = "career_vs_health"
    INCOME_VS_LEARNING = "income_vs_learning"
    STRATEGIC_VS_OPERATIONAL = "strategic_vs_operational"
    RELATIONSHIPS_VS_WORKLOAD = "relationships_vs_workload"
    WEALTH_VS_TIME = "wealth_vs_time"
    DEVELOPMENT_VS_EXECUTION = "development_vs_execution"


class OptimizationPolicy(BaseModel):
    """Policy constraints and rules for optimization."""
    min_domain_score: float = Field(default=3.0, ge=0, le=10)
    max_domain_score: float = Field(default=9.0, ge=0, le=10)
    neglect_threshold: float = Field(default=3.5, ge=0, le=10)
    overinvest_threshold: float = Field(default=8.0, ge=0, le=10)
    risk_tolerance: str = Field(default="moderate")
    sustainability_weight: float = Field(default=0.3, ge=0, le=1)
    long_term_weight: float = Field(default=0.4, ge=0, le=1)
    energy_constraint_factor: float = Field(default=0.2, ge=0, le=1)
    enable_automatic_rebalancing: bool = True
    max_daily_domain_shifts: int = 2
    recovery_period_hours: int = 24


class DomainMetrics(BaseModel):
    """Metrics for a single domain."""
    domain: LifeDomain
    performance_score: float = Field(ge=0, le=10)
    risk_score: float = Field(ge=0, le=10)
    opportunity_score: float = Field(ge=0, le=10)
    momentum_score: float = Field(ge=-10, le=10)
    alignment_score: float = Field(ge=0, le=10)
    resource_allocation: float = Field(ge=0, le=100, description="Percentage of resources allocated")
    strategic_priority: int = Field(ge=1, le=10, description="Priority rank (1 is highest)")
    
    @property
    def composite_score(self) -> float:
        """Calculate composite domain score."""
        return (
            self.performance_score * 0.30 +
            self.opportunity_score * 0.20 +
            self.momentum_score * 0.15 +
            self.alignment_score * 0.25 +
            (10 - self.risk_score) * 0.10
        )
    
    @property
    def health_status(self) -> str:
        """Determine health status based on scores."""
        if self.composite_score >= 7.0:
            return "thriving"
        elif self.composite_score >= 5.0:
            return "stable"
        elif self.composite_score >= 3.0:
            return "struggling"
        else:
            return "critical"


class DomainConditionResult(BaseModel):
    """Result of domain condition detection."""
    domain: LifeDomain
    condition: DomainCondition
    severity: float = Field(ge=0, le=1)
    evidence: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TradeoffDecision(BaseModel):
    """A tradeoff decision between domains."""
    tradeoff_type: TradeoffType
    domains_involved: list[LifeDomain]
    winner: Optional[LifeDomain] = None
    loser: Optional[LifeDomain] = None
    reasoning: str
    long_term_value_impact: float = Field(ge=-1, le=1)
    risk_mitigation_score: float = Field(ge=0, le=1)
    sustainability_score: float = Field(ge=0, le=1)
    energy_impact: float = Field(ge=-1, le=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OptimizationActionRecommendation(BaseModel):
    """A recommended optimization action."""
    action: OptimizationAction
    target_domain: LifeDomain
    priority: int = Field(ge=1, le=10)
    reasoning: str
    expected_impact: float = Field(ge=-1, le=1)
    confidence: float = Field(ge=0, le=1)
    policy_constraints_respected: bool = True
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OptimizationCycle(BaseModel):
    """Complete optimization cycle results."""
    cycle_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    domain_metrics: list[DomainMetrics]
    detected_conditions: list[DomainConditionResult]
    tradeoff_decisions: list[TradeoffDecision]
    recommendations: list[OptimizationActionRecommendation]
    overall_balance_score: float = Field(ge=0, le=10)
    optimization_applied: bool = False
    execution_status: str = "pending"
    error_message: Optional[str] = None


class OptimizationSummary(BaseModel):
    """High-level optimization summary."""
    overall_health: float = Field(ge=0, le=10)
    balance_score: float = Field(ge=0, le=10)
    domains_needing_attention: list[LifeDomain]
    top_opportunities: list[LifeDomain]
    active_tradeoffs: list[TradeoffType]
    pending_recommendations: int
    last_cycle_timestamp: Optional[datetime] = None
    cycles_run_today: int = 0


class DomainDataInput(BaseModel):
    """Input data for domain modeling."""
    domain: LifeDomain
    # Performance indicators
    goal_progress: float = Field(default=0.5, ge=0, le=1, description="Progress toward domain goals")
    task_completion_rate: float = Field(default=0.5, ge=0, le=1)
    quality_indicators: list[float] = Field(default_factory=list)
    
    # Risk indicators
    threat_indicators: list[float] = Field(default_factory=list)
    vulnerability_score: float = Field(default=0.2, ge=0, le=1)
    
    # Opportunity indicators
    opportunity_indicators: list[float] = Field(default_factory=list)
    market_timing: float = Field(default=0.5, ge=0, le=1)
    
    # Momentum indicators
    recent_progress: float = Field(default=0.0, ge=-1, le=1)
    trend_direction: float = Field(default=0.0, ge=-1, le=1)
    
    # Resource indicators
    time_invested_hours: float = Field(default=10.0, ge=0)
    energy_invested: float = Field(default=0.5, ge=0, le=1)
    financial_investment: float = Field(default=100.0, ge=0)
    
    # Alignment
    strategic_alignment: float = Field(default=0.5, ge=0, le=1)
    goal_alignment: float = Field(default=0.5, ge=0, le=1)
