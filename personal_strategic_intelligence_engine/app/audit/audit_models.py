"""Audit data models for end-to-end operational audit.

Defines structures for the comprehensive audit system.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AuditStatus(str, Enum):
    """Status of audit run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AuditMode(str, Enum):
    """Mode of audit execution."""
    REALISTIC_SCENARIO = "realistic_scenario"
    MULTI_CYCLE_SIMULATION = "multi_cycle_simulation"


class ScenarioTypeAudit(str, Enum):
    """Types of realistic scenarios for audit."""
    PERSONAL_LIFE_OPTIMIZATION = "personal_life_optimization"
    FINANCIAL_STRESS_RECOVERY = "financial_stress_recovery"
    COMPETING_PRIORITIES = "competing_priorities"
    OPPORTUNITY_PRIORITIZATION = "opportunity_prioritization"
    MIXED_DOMAIN_STRATEGIC = "mixed_domain_strategic"
    GOVERNANCE_HEAVY = "governance_heavy"


class GateOutcome(str, Enum):
    """Outcome of governance gates."""
    PASSED = "passed"
    BLOCKED = "blocked"
    FLAGGED = "flagged"


class ApprovalStatus(str, Enum):
    """Approval status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MANUAL_REQUIRED = "manual_required"
    AUTO_APPROVED = "auto_approved"


class AuditCycleRecord(BaseModel):
    """Record of a single audit cycle."""
    cycle_id: str
    scenario_name: str
    audit_mode: AuditMode
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cycle_duration_ms: float = 0.0
    
    # Input signals
    signals_received: List[Dict[str, Any]] = Field(default_factory=list)
    signal_summary: str = ""
    
    # State
    state_summary: Dict[str, Any] = Field(default_factory=dict)
    
    # Forecasting
    forecast_highlights: List[str] = Field(default_factory=list)
    
    # Doctrine
    doctrine_assessment: Optional[Dict[str, Any]] = None
    alignment_score: float = 0.0
    alignment_level: str = "neutral"
    doctrine_flags: List[str] = Field(default_factory=list)
    doctrine_conflicts: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Recommendations
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    recommendation_count: int = 0
    
    # Execution intents
    execution_intents: List[Dict[str, Any]] = Field(default_factory=list)
    execution_intent_count: int = 0
    
    # Gate outcomes
    policy_gate_outcome: GateOutcome = GateOutcome.PASSED
    doctrine_gate_outcome: GateOutcome = GateOutcome.PASSED
    risk_gate_outcome: GateOutcome = GateOutcome.PASSED
    
    # Approval
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    approval_tier: str = "tier_0_manual_only"
    
    # Journal
    journal_entry_id: Optional[str] = None
    
    # Learning
    confidence_before: float = 0.5
    confidence_after: float = 0.5
    learning_updates: List[str] = Field(default_factory=list)
    
    # Anomalies
    conflicts_detected: List[str] = Field(default_factory=list)
    anomalies_detected: List[str] = Field(default_factory=list)


class DecisionInventory(BaseModel):
    """Inventory of all decisions from audit."""
    # By domain
    decisions_by_domain: Dict[str, int] = Field(default_factory=dict)
    
    # By urgency
    decisions_by_urgency: Dict[str, int] = Field(default_factory=dict)
    
    # Totals
    total_recommendations: int = 0
    
    # By alignment
    aligned_decisions: int = 0
    misaligned_decisions: int = 0
    neutral_decisions: int = 0
    
    # By execution eligibility
    eligible_for_execution: int = 0
    blocked_by_doctrine: int = 0
    blocked_by_policy: int = 0
    blocked_by_risk: int = 0
    requires_manual_approval: int = 0
    
    # Repeated recommendations
    repeated_recommendations: Dict[str, int] = Field(default_factory=dict)
    
    # Quality metrics
    high_value_decisions: int = 0
    low_value_decisions: int = 0
    noisy_decisions: int = 0


class GovernanceOutcomeReport(BaseModel):
    """Summary of governance outcomes."""
    total_recommendations: int = 0
    total_execution_intents: int = 0
    
    # Doctrine
    doctrine_passes: int = 0
    doctrine_blocks: int = 0
    doctrine_flags_raised: int = 0
    
    # Policy
    policy_passes: int = 0
    policy_blocks: int = 0
    
    # Risk
    risk_passes: int = 0
    risk_rejections: int = 0
    
    # Approval
    approval_required_count: int = 0
    manual_only_count: int = 0
    fast_path_count: int = 0
    auto_approved_count: int = 0
    
    # Blocked rationale
    blocked_rationale: Dict[str, int] = Field(default_factory=dict)


class LearningReport(BaseModel):
    """Summary of learning and confidence behavior."""
    # Confidence
    initial_confidence: float = 0.5
    final_confidence: float = 0.5
    confidence_drift: float = 0.0
    confidence_min: float = 1.0
    confidence_max: float = 0.0
    
    # Drift events
    confidence_collapse_events: int = 0
    confidence_inflation_events: int = 0
    oscillating_confidence_events: int = 0
    
    # Calibration
    calibration_updates: int = 0
    avg_calibration_change: float = 0.0
    
    # Overreaction/underreaction
    overreaction_events: int = 0
    underreaction_events: int = 0


class AuditFindings(BaseModel):
    """Findings from the audit."""
    # Strategic coherence
    strategic_coherence_assessment: str = ""
    coherent_recommendations: int = 0
    incoherent_recommendations: int = 0
    
    # Doctrine alignment
    doctrine_consistency_score: float = 1.0
    doctrine_consistency_assessment: str = ""
    inconsistent_assessments: int = 0
    
    # Governance quality
    governance_quality_assessment: str = ""
    correctly_blocked_actions: int = 0
    incorrectly_allowed_actions: int = 0
    
    # Decision quality
    decision_quality_assessment: str = ""
    specific_useful_decisions: int = 0
    repetitive_noisy_decisions: int = 0
    
    # Learning behavior
    learning_behavior_assessment: str = ""
    bounded_confidence_updates: bool = True
    proportional_learning: bool = True
    
    # End-to-end integrity
    flow_consistency_score: float = 1.0
    broken_flows: int = 0


class VisionAlignment(BaseModel):
    """Assessment of system alignment with intended vision."""
    # What's working well
    aligned_areas: List[str] = Field(default_factory=list)
    
    # What's questionable
    questionable_areas: List[str] = Field(default_factory=list)
    
    # Major issues
    major_issues: List[str] = Field(default_factory=list)
    
    # Overall verdict
    overall_verdict: str = ""
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list)


class MasterAuditReport(BaseModel):
    """Complete master audit report."""
    report_id: str = Field(default_factory=lambda: f"audit_report_{datetime.utcnow().timestamp()}")
    
    # Metadata
    audit_modes: List[AuditMode] = Field(default_factory=list)
    scenarios_executed: List[str] = Field(default_factory=list)
    total_cycles: int = 0
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    duration_ms: float = 0.0
    
    # Executive summary
    executive_summary: str = ""
    
    # Cycle records
    cycle_records: List[AuditCycleRecord] = Field(default_factory=list)
    
    # Decision inventory
    decision_inventory: DecisionInventory = Field(default_factory=DecisionInventory)
    
    # Governance outcomes
    governance_outcomes: GovernanceOutcomeReport = Field(default_factory=GovernanceOutcomeReport)
    
    # Learning report
    learning_report: LearningReport = Field(default_factory=LearningReport)
    
    # Findings
    findings: AuditFindings = Field(default_factory=AuditFindings)
    
    # Vision alignment
    vision_alignment: VisionAlignment = Field(default_factory=VisionAlignment)


# Safety constants
LIVE_EXECUTION_ENABLED = False
AUTO_EXECUTION_ENABLED = False
EXECUTION_MODE = "disabled"
APPROVAL_REQUIRED = True
REPLAY_MODE = True
SHADOW_MODE = True
