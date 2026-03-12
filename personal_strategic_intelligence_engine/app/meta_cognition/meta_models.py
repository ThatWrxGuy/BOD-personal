"""Meta-cognition data models."""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.meta_cognition.meta_types import (
    ValidationStatus,
    ContradictionSeverity,
    ConfidenceTier,
    PolicyComplianceStatus,
    OriginEngine,
    ReasoningQuality,
)


class StrategicDecision(BaseModel):
    """A strategic decision to be evaluated."""
    decision_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    origin_engine: OriginEngine
    recommendation_type: str
    recommendation_summary: str
    supporting_signals: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: float = 0.0
    validation_status: ValidationStatus = ValidationStatus.PENDING
    contradictions_detected: List[str] = Field(default_factory=list)
    
    # Additional metadata
    context: Dict[str, Any] = Field(default_factory=dict)
    priority: float = 0.5


class ContradictionRecord(BaseModel):
    """Record of a detected contradiction."""
    contradiction_id: str
    engine_a: OriginEngine
    engine_b: OriginEngine
    conflicting_signal: str
    severity: ContradictionSeverity
    resolution_status: str = "unresolved"
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    description: str = ""
    evidence: Dict[str, Any] = Field(default_factory=dict)


class DecisionAuditRecord(BaseModel):
    """Audit record for a strategic decision."""
    audit_id: str
    decision_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    engines_consulted: List[OriginEngine] = Field(default_factory=list)
    reasoning_path: List[str] = Field(default_factory=list)
    confidence_score: float = 0.0
    confidence_tier: ConfidenceTier = ConfidenceTier.LOW
    policy_compliance: PolicyComplianceStatus = PolicyComplianceStatus.COMPLIANT
    validation_result: ValidationStatus = ValidationStatus.PENDING
    contradictions_found: int = 0
    reasoning_quality: ReasoningQuality = ReasoningQuality.INSUFFICIENT
    recommendations: List[str] = Field(default_factory=list)
    notes: str = ""


class PolicyRule(BaseModel):
    """A policy rule for validation."""
    rule_id: str
    name: str
    description: str
    rule_type: str  # risk_threshold, doctrine_contradiction, prohibited_pattern
    condition: Dict[str, Any]
    severity: ContradictionSeverity = ContradictionSeverity.MEDIUM
    is_active: bool = True


class ReasoningValidationResult(BaseModel):
    """Result of reasoning validation."""
    is_valid: bool
    quality: ReasoningQuality
    issues: List[str] = Field(default_factory=list)
    missing_signals: List[str] = Field(default_factory=list)
    score: float = 0.0


class ConfidenceScoreComponents(BaseModel):
    """Components that contribute to confidence scoring."""
    forecast_reliability: float = 0.0
    simulation_stability: float = 0.0
    monte_carlo_confidence: float = 0.0
    doctrine_alignment: float = 0.0
    signal_agreement: float = 0.0
    contradiction_penalty: float = 0.0
    
    def total_score(self) -> float:
        """Calculate total confidence score."""
        return (
            self.forecast_reliability +
            self.simulation_stability +
            self.monte_carlo_confidence +
            self.doctrine_alignment +
            self.signal_agreement -
            self.contradiction_penalty
        )


class MetaEvaluationResult(BaseModel):
    """Complete result of meta-cognitive evaluation."""
    decision: StrategicDecision
    confidence_score: float
    confidence_tier: ConfidenceTier
    contradictions: List[ContradictionRecord] = Field(default_factory=list)
    policy_compliance: PolicyComplianceStatus
    reasoning_validation: ReasoningValidationResult
    validation_status: ValidationStatus
    audit_record: Optional[DecisionAuditRecord] = None
    
    def is_approved(self) -> bool:
        """Check if decision is approved."""
        return self.validation_status == ValidationStatus.APPROVED
    
    def is_rejected(self) -> bool:
        """Check if decision is rejected."""
        return self.validation_status == ValidationStatus.REJECTED
    
    def needs_review(self) -> bool:
        """Check if decision requires review."""
        return self.validation_status == ValidationStatus.REQUIRES_REVIEW
