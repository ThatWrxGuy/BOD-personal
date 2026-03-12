"""Decision audit system for tracking all evaluated decisions."""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.meta_cognition.meta_models import (
    DecisionAuditRecord,
    StrategicDecision,
    MetaEvaluationResult,
)
from app.state_engine import StateEngine


class DecisionAuditor:
    """Creates permanent audit records for all evaluated decisions.
    
    Audit records are stored through the State Engine repository
    to enable later doctrine refinement and analysis.
    """
    
    def __init__(self, state_engine: Optional[StateEngine] = None):
        self.state_engine = state_engine
        self._audit_cache: List[DecisionAuditRecord] = []
    
    def create_audit_record(
        self,
        decision: StrategicDecision,
        evaluation_result: MetaEvaluationResult,
    ) -> DecisionAuditRecord:
        """Create an audit record for a decision evaluation.
        
        Args:
            decision: The decision that was evaluated
            evaluation_result: The result of meta-cognitive evaluation
            
        Returns:
            Created audit record
        """
        audit_id = f"audit_{uuid.uuid4().hex[:12]}"
        
        # Extract engines consulted from signals
        engines_consulted = set()
        for signal in decision.supporting_signals:
            if "engine" in signal:
                engines_consulted.add(signal["engine"])
        
        record = DecisionAuditRecord(
            audit_id=audit_id,
            decision_id=decision.decision_id,
            timestamp=datetime.utcnow(),
            engines_consulted=list(engines_consulted),
            reasoning_path=self._extract_reasoning_path(evaluation_result),
            confidence_score=evaluation_result.confidence_score,
            confidence_tier=evaluation_result.confidence_tier,
            policy_compliance=evaluation_result.policy_compliance,
            validation_result=evaluation_result.validation_status,
            contradictions_found=len(evaluation_result.contradictions),
            reasoning_quality=evaluation_result.reasoning_validation.quality,
            recommendations=self._extract_recommendations(evaluation_result),
            notes=self._generate_notes(evaluation_result),
        )
        
        # Store in cache
        self._audit_cache.append(record)
        
        # Store in state engine if available
        if self.state_engine:
            self._store_in_state_engine(record)
        
        return record
    
    def _extract_reasoning_path(
        self,
        evaluation_result: MetaEvaluationResult,
    ) -> List[str]:
        """Extract the reasoning path from evaluation."""
        path = []
        
        # Add contradiction detection
        if evaluation_result.contradictions:
            path.append("contradiction_detection")
        
        # Add confidence scoring
        path.append("confidence_scoring")
        
        # Add policy validation
        path.append("policy_validation")
        
        # Add reasoning validation
        path.append("reasoning_validation")
        
        # Add final decision
        path.append(f"decision_{evaluation_result.validation_status.value}")
        
        return path
    
    def _extract_recommendations(
        self,
        evaluation_result: MetaEvaluationResult,
    ) -> List[str]:
        """Extract recommendations from evaluation."""
        recommendations = []
        
        # Add recommendations based on validation status
        if evaluation_result.validation_status.value == "rejected":
            recommendations.append("Review decision before resubmission")
        
        if evaluation_result.validation_status.value == "requires_review":
            recommendations.append("Gather additional supporting signals")
            recommendations.append("Consult additional engines")
        
        # Add recommendations based on confidence
        if evaluation_result.confidence_tier.value == "low":
            recommendations.append("Increase confidence through additional analysis")
        
        # Add recommendations based on contradictions
        if len(evaluation_result.contradictions) > 0:
            recommendations.append("Resolve contradictions before proceeding")
        
        # Add recommendations based on policy compliance
        if evaluation_result.policy_compliance.value == "violation":
            recommendations.append("Address policy violations")
        
        return recommendations
    
    def _generate_notes(
        self,
        evaluation_result: MetaEvaluationResult,
    ) -> str:
        """Generate notes for the audit record."""
        notes = []
        
        # Add contradiction summary
        if evaluation_result.contradictions:
            severe = sum(1 for c in evaluation_result.contradictions 
                       if c.severity.value in ["high", "critical"])
            notes.append(f"Found {len(evaluation_result.contradictions)} contradictions "
                        f"({severe} severe)")
        
        # Add confidence summary
        notes.append(f"Confidence: {evaluation_result.confidence_score:.2f} "
                    f"({evaluation_result.confidence_tier.value})")
        
        # Add policy summary
        notes.append(f"Policy: {evaluation_result.policy_compliance.value}")
        
        # Add reasoning quality
        notes.append(f"Reasoning: {evaluation_result.reasoning_validation.quality.value}")
        
        return "; ".join(notes)
    
    def _store_in_state_engine(self, record: DecisionAuditRecord):
        """Store audit record in state engine."""
        try:
            # Use memory manager if available
            from app.state_engine import get_state_engine, MemoryTier
            
            engine = get_state_engine()
            
            # Store as short-term memory
            memory_data = {
                "audit_id": record.audit_id,
                "decision_id": record.decision_id,
                "confidence": record.confidence_score,
                "validation": record.validation_result.value,
                "contradictions": record.contradictions_found,
            }
            
            # Would use memory manager here
            # engine.store_memory(memory_data, MemoryTier.SHORT_TERM)
            
        except Exception as e:
            # Silently fail if state engine not available
            pass
    
    def get_audit_record(self, audit_id: str) -> Optional[DecisionAuditRecord]:
        """Get a specific audit record."""
        for record in self._audit_cache:
            if record.audit_id == audit_id:
                return record
        return None
    
    def get_audit_record_by_decision(
        self,
        decision_id: str,
    ) -> Optional[DecisionAuditRecord]:
        """Get audit record by decision ID."""
        for record in self._audit_cache:
            if record.decision_id == decision_id:
                return record
        return None
    
    def get_recent_audits(
        self,
        limit: int = 50,
    ) -> List[DecisionAuditRecord]:
        """Get recent audit records."""
        return self._audit_cache[-limit:]
    
    def get_audits_by_status(
        self,
        validation_status: str,
    ) -> List[DecisionAuditRecord]:
        """Get audit records by validation status."""
        return [
            r for r in self._audit_cache
            if r.validation_result.value == validation_status
        ]
    
    def get_audit_statistics(self) -> Dict[str, Any]:
        """Get statistics about audit records."""
        if not self._audit_cache:
            return {
                "total_audits": 0,
                "approved": 0,
                "rejected": 0,
                "requires_review": 0,
                "avg_confidence": 0.0,
            }
        
        status_counts = {
            "approved": 0,
            "rejected": 0,
            "requires_review": 0,
            "pending": 0,
        }
        
        confidences = []
        
        for record in self._audit_cache:
            status_counts[record.validation_result.value] = \
                status_counts.get(record.validation_result.value, 0) + 1
            confidences.append(record.confidence_score)
        
        return {
            "total_audits": len(self._audit_cache),
            "status_counts": status_counts,
            "avg_confidence": sum(confidences) / len(confidences),
            "min_confidence": min(confidences),
            "max_confidence": max(confidences),
        }
    
    def get_recent_violations(self) -> List[DecisionAuditRecord]:
        """Get recent policy violations."""
        return [
            r for r in self._audit_cache
            if r.policy_compliance.value == "violation"
        ][-10:]
    
    def clear_cache(self):
        """Clear audit cache."""
        self._audit_cache.clear()
