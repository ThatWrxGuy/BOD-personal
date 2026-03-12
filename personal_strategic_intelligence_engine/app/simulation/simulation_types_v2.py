"""Simulation Types V2 - Core models and enums for the seeded simulation framework."""
import uuid
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Optional, Any, List, Dict
from pydantic import BaseModel, Field


class ScenarioType(str, Enum):
    """Types of simulation scenarios."""
    BASELINE = "baseline"
    PRESSURE = "pressure"
    OPPORTUNITY = "opportunity"
    RECOVERY = "recovery"
    CONFLICT = "conflict"
    VOLATILITY = "volatility"


class EventType(str, Enum):
    """Types of simulated events."""
    UNEXPECTED_EXPENSE = "unexpected_expense"
    WORKLOAD_SURGE = "workload_surge"
    MISSED_HABIT_STREAK = "missed_habit_streak"
    MOTIVATION_SURGE = "motivation_surge"
    LEARNING_BREAKTHROUGH = "learning_breakthrough"
    SIDE_INCOME_OPPORTUNITY = "side_income_opportunity"
    DEBT_STRESS_SPIKE = "debt_stress_spike"
    RELATIONSHIP_NEGLECT = "relationship_neglect"
    HEALTH_SETBACK = "health_setback"
    GOAL_PROGRESS_SURGE = "goal_progress_surge"
    PRIORITY_CONFLICT = "priority_conflict"
    SCHEDULE_COLLAPSE = "schedule_collapse"


class SimulationStatus(str, Enum):
    """Status of a simulation run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# Pydantic models

class PersonalProfileSim(BaseModel):
    """Simulated personal profile."""
    age_range: str = "30-40"
    work_hours: float = 40.0
    available_time: float = 20.0
    energy_baseline: float = 0.6
    stress_baseline: float = 0.4
    focus_stability: float = 0.7
    life_complexity: float = 0.5


class FinancialStateSim(BaseModel):
    """Simulated financial state."""
    monthly_income: float = 5000.0
    fixed_expenses: float = 3000.0
    debt_balances: float = 10000.0
    investment_balances: float = 25000.0
    liquidity: float = 5000.0
    cash_flow_pressure: float = 0.3


class StrategicGoalSim(BaseModel):
    """Simulated strategic goal."""
    id: str
    title: str
    description: str
    domain: str
    target_date: date
    urgency_score: float = Field(ge=0, le=1)
    progress_percentage: float = Field(ge=0, le=1, default=0.0)


class HabitSim(BaseModel):
    """Simulated habit."""
    id: str
    name: str
    domain: str
    streak_count: int = 0
    completion_probability: float = Field(ge=0, le=1)
    focus_adherence: float = Field(ge=0, le=1)


class RiskSignalSim(BaseModel):
    """Simulated risk signal."""
    type: str
    domain: str
    severity: float = Field(ge=0, le=1)
    description: str


class OpportunitySignalSim(BaseModel):
    """Simulated opportunity signal."""
    type: str
    domain: str
    potential_impact: float = Field(ge=0, le=1)
    description: str


class DomainStateSim(BaseModel):
    """Simulated domain state."""
    domain: str
    performance_score: float = Field(ge=0, le=10, default=5.0)
    risk_score: float = Field(ge=0, le=10, default=3.0)
    opportunity_score: float = Field(ge=0, le=10, default=5.0)
    momentum_score: float = Field(ge=-10, le=10, default=0.0)
    alignment_score: float = Field(ge=0, le=10, default=5.0)
    resource_allocation: float = Field(ge=0, le=100, default=12.5)


class SimulatedEvent(BaseModel):
    """A simulated event."""
    id: str
    timestamp: datetime
    event_type: EventType
    affected_domain: str
    severity: float = Field(ge=0, le=1)
    description: str
    expected_effect: str
    observed_effect: Optional[str] = None


class DailySummary(BaseModel):
    """Daily simulation summary."""
    day: int
    date: date
    morning_state: Dict[str, Any]
    events_triggered: List[str]
    risks_detected: List[str]
    opportunities_detected: List[str]
    priority_shifts: List[Dict[str, Any]]
    domain_changes: Dict[str, float]
    habit_performance: Dict[str, float]
    summary: str


class WeeklySummary(BaseModel):
    """Weekly simulation summary."""
    week: int
    start_date: date
    end_date: date
    daily_summaries: List[DailySummary]
    average_performance: float
    risks_emerged: List[str]
    opportunities_captured: List[str]
    strategic_adjustments: List[str]
    summary: str


class SubsystemStatus(BaseModel):
    """Status of a subsystem during simulation."""
    name: str
    invoked: bool = False
    success: bool = False
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None


class SimulationMetadata(BaseModel):
    """Metadata for a simulation run."""
    simulation_id: str
    seed: str
    scenario_type: ScenarioType
    duration_days: int
    start_time: datetime
    end_time: Optional[datetime] = None
    status: SimulationStatus = SimulationStatus.PENDING
    subsystems_used: List[SubsystemStatus] = Field(default_factory=list)


class SimulationResults(BaseModel):
    """Results from a simulation run."""
    metadata: SimulationMetadata
    initial_profile: Optional[PersonalProfileSim] = None
    initial_financial: Optional[FinancialStateSim] = None
    initial_goals: List[StrategicGoalSim] = Field(default_factory=list)
    initial_habits: List[HabitSim] = Field(default_factory=list)
    initial_domains: List[DomainStateSim] = Field(default_factory=list)
    daily_summaries: List[DailySummary] = Field(default_factory=list)
    weekly_summaries: List[WeeklySummary] = Field(default_factory=list)
    all_events: List[SimulatedEvent] = Field(default_factory=list)
    final_domains: List[DomainStateSim] = Field(default_factory=list)
    analysis_scores: Dict[str, float] = Field(default_factory=dict)
    detected_issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class SimulationReport(BaseModel):
    """Final simulation report."""
    metadata: SimulationMetadata
    initial_conditions: Dict[str, Any]
    major_events: List[Dict[str, Any]]
    system_behavior: Dict[str, Any]
    scorecard: Dict[str, float]
    weaknesses: List[str]
    recommendations: List[str]
    final_state: Dict[str, Any]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
