"""Meta-Cognition Engine - Orchestrator of the Meta-Cognitive Layer."""
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from app.meta_cognition.meta_types import (
    ValidationStatus,
    OriginEngine,
    PolicyComplianceStatus,
)
from app.meta_cognition.meta_models import (
    StrategicDecision,
    MetaEvaluationResult,
)
from app.meta_cognition.confidence_scorer import ConfidenceScorer, calculate_contradiction_penalty
from app.meta_cognition.contradiction_detector import ContradictionDetector
from app.meta_cognition.policy_validator import PolicyValidator
from app.meta_cognition.reasoning_validator import ReasoningValidator
from app.meta_cognition.decision_auditor import DecisionAuditor
from app.state_engine import StateEngine


class MetaEngine:
    """Orchestrator of the meta-cognitive layer.
    
    Core workflow:
    1. detect contradictions
    2. calculate confidence score
    3. validate policy compliance
    4. validate reasoning completeness
    5. generate audit record
    6. determine validation status
    """
    
    def __init__(
        self,
        state_engine: Optional[StateEngine] = None,
    ):
        self.state_engine = state_engine
        self.confidence_scorer = ConfidenceScorer()
        self.contradiction_detector = ContradictionDetector()
        self.policy_validator = PolicyValidator()
        self.reasoning_validator = ReasoningValidator()
        self.decision_auditor = DecisionAuditor(state_engine)
    
    def evaluate_decision(
        self,
        decision: StrategicDecision,
        engine_outputs: Optional[Dict[OriginEngine, Dict[str, Any]]] = None,
    ) -> MetaEvaluationResult:
        """Evaluate a strategic decision through the meta-cognitive layer.
        
        Args:
            decision: The decision to evaluate
            engine_outputs: Optional outputs from different engines for comparison
            
        Returns:
            Complete evaluation result
        """
        # Step 1: Detect contradictions
        contradictions = self._detect_contradictions(decision, engine_outputs)
        
        # Calculate contradiction penalty
        contradiction_penalty = self._calculate_penalty(contradictions)
        
        # Step 2: Calculate confidence score
        confidence_score, confidence_tier = self._calculate_confidence(
            decision, contradiction_penalty
        )
        
        # Step 3: Validate policy compliance
        policy_status = self._validate_policy(decision, engine_outputs)
        
        # Step 4: Validate reasoning completeness
        reasoning_validation = self._validate_reasoning(decision)
        
        # Step 5: Determine validation status
        validation_status = self._determine_validation_status(
            confidence_tier,
            policy_status,
            reasoning_validation,
            contradictions,
        )
        
        # Update decision with results
        decision.confidence_score = confidence_score
        decision.validation_status = validation_status
        decision.contradictions_detected = [c.contradiction_id for c in contradictions]
        
        # Step 6: Generate audit record
        audit_record = self.decision_auditor.create_audit_record(decision, MetaEvaluationResult(
            decision=decision,
            confidence_score=confidence_score,
            confidence_tier=confidence_tier,
            contradictions=contradictions,
            policy_compliance=policy_status,
            reasoning_validation=reasoning_validation,
            validation_status=validation_status,
        ))
        
        return MetaEvaluationResult(
            decision=decision,
            confidence_score=confidence_score,
            confidence_tier=confidence_tier,
            contradictions=contradictions,
            policy_compliance=policy_status,
            reasoning_validation=reasoning_validation,
            validation_status=validation_status,
            audit_record=audit_record,
        )
    
    def _detect_contradictions(
        self,
        decision: StrategicDecision,
        engine_outputs: Optional[Dict[OriginEngine, Dict[str, Any]]],
    ) -> List:
        """Detect contradictions in the decision."""
        if not engine_outputs:
            # Try to extract from supporting signals
            return self._extract_contradictions_from_signals(decision.supporting_signals)
        
        # Detect contradictions between engines
        return self.contradiction_detector.detect_all_contradictions(engine_outputs)
    
    def _extract_contradictions_from_signals(self, signals: List[Dict]) -> List:
        """Extract contradictions from supporting signals."""
        # Simple check for contradictory signals
        contradictions = []
        
        if len(signals) >= 2:
            directions = {}
            for signal in signals:
                source = signal.get("source", "unknown")
                direction = signal.get("direction", "neutral")
                directions[source] = direction
            
            # Check for conflicting directions
            if len(set(directions.values())) > 1:
                # Has contradictions - but we need more sophisticated detection
                pass
        
        return contradictions
    
    def _calculate_penalty(self, contradictions: List) -> float:
        """Calculate penalty from contradictions."""
        if not contradictions:
            return 0.0
        
        return calculate_contradiction_penalty([
            {"severity": c.severity.value}
            for c in contradictions
        ])
    
    def _calculate_confidence(
        self,
        decision: StrategicDecision,
        contradiction_penalty: float,
    ) -> tuple:
        """Calculate confidence score for the decision."""
        # Extract data from decision context
        forecast_data = decision.context.get("forecast_data")
        simulation_data = decision.context.get("simulation_data")
        monte_carlo_data = decision.context.get("monte_carlo_data")
        
        # Default doctrine alignment
        doctrine_alignment = decision.context.get("doctrine_alignment", 0.5)
        
        return self.confidence_scorer.calculate_confidence(
            forecast_data=forecast_data,
            simulation_data=simulation_data,
            monte_carlo_data=monte_carlo_data,
            doctrine_alignment=doctrine_alignment,
            signals=decision.supporting_signals,
            contradiction_penalty=contradiction_penalty,
        )
    
    def _validate_policy(
        self,
        decision: StrategicDecision,
        engine_outputs: Optional[Dict[OriginEngine, Dict[str, Any]]],
    ) -> PolicyComplianceStatus:
        """Validate policy compliance."""
        # Build decision dict for validation
        decision_dict = {
            "expected_drawdown": decision.context.get("expected_drawdown", 0.0),
            "concentration": decision.context.get("concentration", 0.0),
            "leverage": decision.context.get("leverage", 1.0),
            "planned_trades": decision.context.get("planned_trades", 0),
        }
        
        # Get doctrine alignment
        doctrine_alignment = decision.context.get("doctrine_alignment", 0.5)
        
        status, _ = self.policy_validator.validate_decision(
            decision_dict, 
            doctrine_alignment
        )
        
        return status
    
    def _validate_reasoning(
        self,
        decision: StrategicDecision,
    ) -> Any:
        """Validate reasoning completeness."""
        # Extract engines consulted from signals
        engines_consulted = []
        for signal in decision.supporting_signals:
            engine = signal.get("engine")
            if engine:
                try:
                    engines_consulted.append(OriginEngine(engine))
                except:
                    pass
        
        return self.reasoning_validator.validate_reasoning(
            supporting_signals=decision.supporting_signals,
            engines_consulted=engines_consulted,
            context=decision.context,
        )
    
    def _determine_validation_status(
        self,
        confidence_tier,
        policy_status: PolicyComplianceStatus,
        reasoning_validation,
        contradictions: List,
    ) -> ValidationStatus:
        """Determine final validation status."""
        
        # Check for critical violations
        if policy_status == PolicyComplianceStatus.VIOLATION:
            return ValidationStatus.REJECTED
        
        # Check for critical contradictions
        if self.contradiction_detector.has_critical_contradictions(contradictions):
            return ValidationStatus.REJECTED
        
        # Check confidence
        if confidence_tier.value == "low":
            return ValidationStatus.REQUIRES_REVIEW
        
        # Check reasoning quality
        if not reasoning_validation.is_valid:
            return ValidationStatus.REQUIRES_REVIEW
        
        # Check policy warnings
        if policy_status == PolicyComplianceStatus.WARNING:
            return ValidationStatus.REQUIRES_REVIEW
        
        # All checks passed
        return ValidationStatus.APPROVED
    
    def create_decision(
        self,
        origin_engine: OriginEngine,
        recommendation_type: str,
        recommendation_summary: str,
        supporting_signals: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> StrategicDecision:
        """Create a new strategic decision for evaluation.
        
        Args:
            origin_engine: The engine that generated this recommendation
            recommendation_type: Type of recommendation
            recommendation_summary: Summary of the recommendation
            supporting_signals: List of supporting signals
            context: Additional context
            
        Returns:
            Created decision
        """
        decision = StrategicDecision(
            decision_id=f"dec_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            origin_engine=origin_engine,
            recommendation_type=recommendation_type,
            recommendation_summary=recommendation_summary,
            supporting_signals=supporting_signals,
            context=context or {},
        )
        
        return decision
    
    def get_audit_statistics(self) -> Dict[str, Any]:
        """Get audit statistics."""
        return self.decision_auditor.get_audit_statistics()
    
    def get_recent_violations(self) -> List:
        """Get recent policy violations."""
        return self.decision_auditor.get_recent_violations()


# ============= Singleton Access =============

_meta_engine_instance: Optional[MetaEngine] = None


def get_meta_engine() -> MetaEngine:
    """Get the singleton Meta Engine instance."""
    global _meta_engine_instance
    if _meta_engine_instance is None:
        _meta_engine_instance = MetaEngine()
    return _meta_engine_instance


def reset_meta_engine():
    """Reset the meta engine singleton (for testing)."""
    global _meta_engine_instance
    _meta_engine_instance = None
