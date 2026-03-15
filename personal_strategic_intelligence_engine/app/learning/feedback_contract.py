"""Learning-to-Planning Feedback Contract.

This module defines the canonical feedback interface between learning outputs
and planning inputs, enabling execution outcomes to influence future strategy.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class FeedbackCategory(str, Enum):
    """Category of learning feedback."""
    ADVISORY = "advisory"           # Informational, planning can ignore
    WEIGHTING = "weighting"         # Adjusts weights in planning
    DOCTRINE = "doctrine"           # Affects doctrine/policy
    BLOCKING = "blocking"           # Prevents certain plans
    RISK_ESCALATION = "risk"       # Escalates risk concerns


class FeedbackPriority(str, Enum):
    """Priority of feedback."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FeedbackSource(str, Enum):
    """Source of feedback."""
    OPERATIONAL_LEARNING = "operational_learning"
    STRATEGIC_LEARNING = "strategic_learning"
    DOCTRINE_UPDATE = "doctrine_update"
    RECOMMENDATION_SCORING = "recommendation_scoring"
    OUTCOME_EVALUATION = "outcome_evaluation"
    STRATEGY_EFFECTIVENESS = "strategy_effectiveness"
    CONFIDENCE_CALIBRATION = "confidence_calibration"


# =============================================================================
# Learning Output Models
# =============================================================================

class EffectivenessMetrics(BaseModel):
    """Strategy effectiveness metrics."""
    strategy_id: str = Field(..., description="Strategy identifier")
    effectiveness_score: float = Field(..., description="Effectiveness score 0-1")
    success_rate: float = Field(..., description="Success rate 0-1")
    outcome_category: str = Field(..., description="Outcome category")
    sample_size: int = Field(..., description="Number of samples")
    confidence: float = Field(..., description="Confidence in metrics")


class DoctrineUpdate(BaseModel):
    """Doctrine update feedback."""
    update_id: UUID = Field(default_factory=uuid4)
    doctrine_type: str = Field(..., description="Type of doctrine")
    previous_value: Any = Field(..., description="Previous value")
    new_value: Any = Field(..., description="New value")
    reason: str = Field(..., description="Reason for update")
    source: FeedbackSource = Field(..., description="Feedback source")
    impact_scope: str = Field(..., description="Scope of impact")
    applied_at: Optional[datetime] = None


class RecommendationPerformance(BaseModel):
    """Recommendation performance feedback."""
    recommendation_id: str = Field(..., description="Recommendation identifier")
    predicted_outcome: str = Field(..., description="Predicted outcome")
    actual_outcome: str = Field(..., description="Actual outcome")
    accuracy_score: float = Field(..., description="Accuracy 0-1")
    failure_pattern: Optional[str] = Field(None, description="Failure pattern if any")
    sample_size: int = Field(..., description="Number of samples")


class ExecutionOutcomeSummary(BaseModel):
    """Execution outcome summary."""
    execution_id: str = Field(..., description="Execution identifier")
    plan_id: Optional[str] = Field(None, description="Plan identifier")
    status: str = Field(..., description="Execution status")
    outcome_summary: str = Field(..., description="Human-readable summary")
    success_indicators: List[str] = Field(default_factory=list)
    failure_indicators: List[str] = Field(default_factory=list)
    lessons_learned: List[str] = Field(default_factory=list)


class ConfidenceAdjustment(BaseModel):
    """Confidence calibration feedback."""
    agent_type: str = Field(..., description="Agent or component type")
    previous_confidence: float = Field(..., description="Previous confidence")
    adjusted_confidence: float = Field(..., description="Adjusted confidence")
    calibration_reason: str = Field(..., description="Reason for adjustment")
    evidence_count: int = Field(..., description="Evidence supporting adjustment")


class FailurePattern(BaseModel):
    """Failure pattern feedback."""
    pattern_id: UUID = Field(default_factory=uuid4)
    pattern_type: str = Field(..., description="Type of failure pattern")
    frequency: int = Field(..., description="Frequency of occurrence")
    severity: str = Field(..., description="Severity level")
    affected_domains: List[str] = Field(default_factory=list)
    recommended_action: str = Field(..., description="Recommended action")


# =============================================================================
# Unified Feedback Model
# =============================================================================

class LearningFeedback(BaseModel):
    """Unified learning feedback model for planning."""
    feedback_id: UUID = Field(default_factory=uuid4)
    
    # Source identification
    source: FeedbackSource = Field(..., description="Source of feedback")
    source_module: str = Field(..., description="Module that produced feedback")
    
    # Category and priority
    category: FeedbackCategory = Field(..., description="Feedback category")
    priority: FeedbackPriority = Field(FeedbackPriority.MEDIUM, description="Feedback priority")
    
    # Content (one of these will be populated)
    effectiveness: Optional[EffectivenessMetrics] = None
    doctrine_update: Optional[DoctrineUpdate] = None
    recommendation_performance: Optional[RecommendationPerformance] = None
    execution_outcome: Optional[ExecutionOutcomeSummary] = None
    confidence_adjustment: Optional[ConfidenceAdjustment] = None
    failure_pattern: Optional[FailurePattern] = None
    
    # Metadata
    produced_at: datetime = Field(default_factory=datetime.utcnow)
    applicable_period_start: datetime = Field(..., description="Feedback applicable from")
    applicable_period_end: Optional[datetime] = Field(None, description="Feedback applicable until")
    tags: List[str] = Field(default_factory=list, description="Tags for filtering")
    
    def get_impact_description(self) -> str:
        """Get human-readable impact description."""
        if self.effectiveness:
            return f"Strategy {self.effectiveness.strategy_id}: effectiveness={self.effectiveness.effectiveness_score:.2f}"
        elif self.doctrine_update:
            return f"Doctrine {self.doctrine_update.doctrine_type}: {self.doctrine_update.previous_value} → {self.doctrine_update.new_value}"
        elif self.recommendation_performance:
            return f"Recommendation {self.recommendation_performance.recommendation_id}: accuracy={self.recommendation_performance.accuracy_score:.2f}"
        elif self.failure_pattern:
            return f"Pattern {self.failure_pattern.pattern_type}: {self.failure_pattern.frequency} occurrences"
        else:
            return "Learning feedback"


# =============================================================================
# Feedback Contract Interface
# =============================================================================

class BaseFeedbackContract(ABC):
    """Abstract base class for feedback contracts."""
    
    @property
    @abstractmethod
    def contract_id(self) -> str:
        """Unique contract identifier."""
        pass
    
    @abstractmethod
    async def collect_feedback(self) -> List[LearningFeedback]:
        """Collect feedback from learning outputs."""
        pass
    
    @abstractmethod
    async def apply_to_planning(self, feedback: List[LearningFeedback], planning_context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply feedback to planning context."""
        pass


class LearningToPlanningFeedbackContract(BaseFeedbackContract):
    """Contract for learning-to-planning feedback.
    
    This contract defines how learning outputs are collected and applied
    to planning inputs.
    """
    
    def __init__(self):
        self._feedback_store: List[LearningFeedback] = []
    
    @property
    def contract_id(self) -> str:
        return "learning_to_planning_feedback"
    
    async def collect_feedback(self) -> List[LearningFeedback]:
        """Collect feedback from all learning sources."""
        feedback_list = []
        
        # In production, would collect from each learning service
        # For now, return stored feedback
        feedback_list.extend(self._feedback_store)
        
        return feedback_list
    
    async def add_feedback(self, feedback: LearningFeedback):
        """Add feedback to the store."""
        self._feedback_store.append(feedback)
        logger.info(f"Added feedback: {feedback.feedback_id} from {feedback.source.value}")
    
    async def get_feedback_for_planning(
        self,
        categories: Optional[List[FeedbackCategory]] = None,
        min_priority: FeedbackPriority = FeedbackPriority.LOW,
        domains: Optional[List[str]] = None,
    ) -> List[LearningFeedback]:
        """Get relevant feedback for planning.
        
        Args:
            categories: Filter by categories
            min_priority: Minimum priority level
            domains: Filter by affected domains
            
        Returns:
            Filtered list of feedback
        """
        priority_order = [FeedbackPriority.LOW, FeedbackPriority.MEDIUM, FeedbackPriority.HIGH, FeedbackPriority.CRITICAL]
        min_idx = priority_order.index(min_priority)
        
        filtered = []
        for fb in self._feedback_store:
            # Check priority
            fb_idx = priority_order.index(fb.priority)
            if fb_idx < min_idx:
                continue
            
            # Check category
            if categories and fb.category not in categories:
                continue
            
            # Check domains (for failure patterns)
            if domains and fb.failure_pattern:
                if not any(d in fb.failure_pattern.affected_domains for d in domains):
                    continue
            
            filtered.append(fb)
        
        return filtered
    
    async def apply_to_planning(
        self,
        feedback: List[LearningFeedback],
        planning_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apply feedback to planning context.
        
        Args:
            feedback: List of feedback to apply
            planning_context: Current planning context
            
        Returns:
            Updated planning context with feedback applied
        """
        context = planning_context.copy()
        
        # Initialize feedback sections
        context["feedback_applied"] = {
            "effectiveness_adjustments": [],
            "doctrine_updates": [],
            "weighting_adjustments": [],
            "blocking_rules": [],
            "risk_escalations": [],
        }
        
        for fb in feedback:
            if fb.category == FeedbackCategory.WEIGHTING or fb.effectiveness:
                context["feedback_applied"]["effectiveness_adjustments"].append(fb.dict())
            
            elif fb.category == FeedbackCategory.DOCTRINE or fb.doctrine_update:
                context["feedback_applied"]["doctrine_updates"].append(fb.dict())
            
            elif fb.category == FeedbackCategory.RISK_ESCALATION or fb.failure_pattern:
                context["feedback_applied"]["risk_escalations"].append(fb.dict())
            
            elif fb.category == FeedbackCategory.BLOCKING:
                context["feedback_applied"]["blocking_rules"].append(fb.dict())
            
            elif fb.category == FeedbackCategory.ADVISORY:
                context["feedback_applied"]["weighting_adjustments"].append(fb.dict())
        
        return context


# Singleton
_feedback_contract: Optional[LearningToPlanningFeedbackContract] = None


def get_learning_feedback_contract() -> LearningToPlanningFeedbackContract:
    """Get the learning-to-planning feedback contract singleton."""
    global _feedback_contract
    if _feedback_contract is None:
        _feedback_contract = LearningToPlanningFeedbackContract()
    return _feedback_contract
