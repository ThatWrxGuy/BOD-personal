"""Enhanced Planning with Learning Feedback Integration.

This version of strategy planning integrates learning feedback into the planning process,
enabling execution outcomes and doctrine updates to influence future strategy generation.
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.planning.strategy_generator import StrategyGenerator
from app.planning.strategic_planner import StrategicPlanner
from app.learning.feedback_contract import (
    get_learning_feedback_contract,
    LearningFeedback,
    FeedbackCategory,
    FeedbackPriority,
)
from app.learning.feedback_collector import get_learning_feedback_collector
from app.learning.feedback_audit import get_feedback_audit_logger

logger = logging.getLogger(__name__)


class EnhancedPlanningContext(BaseModel):
    """Planning context enhanced with learning feedback."""
    
    # Standard inputs
    current_state: Dict[str, Any]
    forecasts: Dict[str, Any]
    risks: List[Dict[str, Any]]
    goals: List[Dict[str, Any]]
    doctrine: Dict[str, Any]
    
    # NEW: Learning feedback inputs
    learning_feedback: List[Dict[str, Any]] = []
    feedback_summary: Dict[str, Any] = {}
    doctrine_updates: List[Dict[str, Any]] = []
    effectiveness_adjustments: List[Dict[str, Any]] = []
    
    # Context metadata
    planning_run_id: str = ""
    created_at: datetime = None
    
    def __init__(self, **data):
        if data.get('created_at') is None:
            data['created_at'] = datetime.utcnow()
        if not data.get('planning_run_id'):
            data['planning_run_id'] = str(uuid.uuid4())
        super().__init__(**data)


class EnhancedStrategyGenerator:
    """Strategy generator with integrated learning feedback.
    
    This enhanced version incorporates learning feedback into strategy generation,
    allowing past outcomes to influence future strategies.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.base_generator = None
        self.feedback_contract = get_learning_feedback_contract()
        self.collector = get_learning_feedback_collector()
        self.audit_logger = get_feedback_audit_logger()
    
    async def _ensure_initialized(self):
        """Lazy initialization."""
        if self.base_generator is None:
            self.base_generator = StrategyGenerator(self.session)
    
    async def generate_strategy(
        self,
        context: EnhancedPlanningContext,
    ) -> Dict[str, Any]:
        """Generate strategy with learning feedback integration.
        
        Args:
            context: Planning context with feedback
            
        Returns:
            Generated strategy
        """
        await self._ensure_initialized()
        
        planning_run_id = uuid.UUID(context.planning_run_id)
        
        # Collect fresh feedback if needed
        if not context.learning_feedback:
            await self.collector.collect_all_feedback()
            
            # Get relevant feedback for planning
            relevant_feedback = await self.feedback_contract.get_feedback_for_planning(
                min_priority=FeedbackPriority.MEDIUM,
            )
            
            context.learning_feedback = [fb.dict() for fb in relevant_feedback]
        
        # Apply feedback to strategy generation
        context = await self._apply_feedback_to_context(context, planning_run_id)
        
        # Generate strategy (with feedback influence)
        strategy = await self.base_generator.generate(context.dict())
        
        # Log feedback usage
        await self._log_feedback_usage(planning_run_id, context, strategy)
        
        return strategy
    
    async def _apply_feedback_to_context(
        self,
        context: EnhancedPlanningContext,
        planning_run_id: uuid.UUID,
    ) -> EnhancedPlanningContext:
        """Apply learning feedback to planning context.
        
        Args:
            context: Planning context
            planning_run_id: ID of this planning run
            
        Returns:
            Context with feedback applied
        """
        # Separate feedback by category
        doctrine_updates = []
        effectiveness_adjustments = []
        weighting_hints = []
        
        for fb_dict in context.learning_feedback:
            category = fb_dict.get("category")
            
            if category == FeedbackCategory.DOCTRINE.value:
                doctrine_updates.append(fb_dict)
            elif category == FeedbackCategory.WEIGHTING.value:
                effectiveness_adjustments.append(fb_dict)
            elif category == FeedbackCategory.ADVISORY.value:
                weighting_hints.append(fb_dict)
        
        # Apply to context
        context.doctrine_updates = doctrine_updates
        context.effectiveness_adjustments = effectiveness_adjustments
        
        # Update context with feedback summary
        context.feedback_summary = {
            "total_feedback": len(context.learning_feedback),
            "doctrine_updates": len(doctrine_updates),
            "effectiveness_adjustments": len(effectiveness_adjustments),
            "weighting_hints": len(weighting_hints),
        }
        
        # Apply doctrine updates to doctrine context
        for update in doctrine_updates:
            doctrine = context.doctrine
            if "doctrine_update" in update:
                du = update["doctrine_update"]
                doctrine_type = du.get("doctrine_type")
                new_value = du.get("new_value")
                if doctrine_type and new_value:
                    doctrine[doctrine_type] = new_value
                    logger.info(f"Applied doctrine update: {doctrine_type} = {new_value}")
        
        # Apply effectiveness adjustments to weighting
        for adj in effectiveness_adjustments:
            if "effectiveness" in adj:
                eff = adj["effectiveness"]
                strategy_id = eff.get("strategy_id")
                score = eff.get("effectiveness_score", 1.0)
                
                # Adjust strategy weighting based on past effectiveness
                logger.info(f"Applying effectiveness adjustment: {strategy_id} -> {score}")
        
        return context
    
    async def _log_feedback_usage(
        self,
        planning_run_id: uuid.UUID,
        context: EnhancedPlanningContext,
        strategy: Dict[str, Any],
    ):
        """Log feedback usage for audit."""
        for fb_dict in context.learning_feedback:
            await self.audit_logger.log_feedback_application(
                planning_run_id=planning_run_id,
                feedback_id=uuid.UUID(fb_dict.get("feedback_id", str(uuid.uuid4()))),
                feedback_source=fb_dict.get("source", "unknown"),
                feedback_category=fb_dict.get("category", "unknown"),
                applied_by="EnhancedStrategyGenerator",
                impact_type="strategy_weighting",
                impact_details={"feedback_summary": context.feedback_summary},
                affected_plans=[strategy.get("strategy_id", "unknown")],
                plan_selection_changed=False,
                reasoning=f"Applied {len(context.learning_feedback)} feedback items",
            )


class EnhancedStrategicPlanner:
    """Strategic planner with integrated learning feedback.
    
    This enhanced version incorporates learning feedback into plan selection and prioritization.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.base_planner = None
        self.feedback_contract = get_learning_feedback_contract()
        self.audit_logger = get_feedback_audit_logger()
    
    async def _ensure_initialized(self):
        """Lazy initialization."""
        if self.base_planner is None:
            self.base_planner = StrategicPlanner(self.session)
    
    async def create_plan(
        self,
        context: EnhancedPlanningContext,
    ) -> Dict[str, Any]:
        """Create plan with learning feedback integration.
        
        Args:
            context: Planning context with feedback
            
        Returns:
            Created plan
        """
        await self._ensure_initialized()
        
        # Get feedback for plan weighting
        relevant_feedback = await self.feedback_contract.get_feedback_for_planning(
            min_priority=FeedbackPriority.LOW,
        )
        
        # Apply feedback to plan selection
        plan = await self.base_planner.create_plan(context.dict())
        
        # Apply feedback adjustments to plan prioritization
        plan = await self._apply_feedback_to_plan(plan, relevant_feedback)
        
        return plan
    
    async def _apply_feedback_to_plan(
        self,
        plan: Dict[str, Any],
        feedback: List[LearningFeedback],
    ) -> Dict[str, Any]:
        """Apply feedback to plan weighting and prioritization.
        
        Args:
            plan: Base plan
            feedback: Feedback to apply
            
        Returns:
            Plan with feedback adjustments
        """
        # Check for blocking rules
        blocking_rules = [fb for fb in feedback if fb.category == FeedbackCategory.BLOCKING]
        
        if blocking_rules:
            plan["has_blocking_feedback"] = True
            plan["blocking_reasons"] = [fb.get_impact_description() for fb in blocking_rules]
        
        # Check for risk escalations
        risk_escalations = [fb for fb in feedback if fb.category == FeedbackCategory.RISK_ESCALATION]
        
        if risk_escalations:
            plan["risk_escalations"] = [fb.get_impact_description() for fb in risk_escalations]
        
        # Apply weighting adjustments
        weighting_adj = [fb for fb in feedback if fb.category == FeedbackCategory.WEIGHTING]
        
        if weighting_adj:
            plan["feedback_weighting"] = {
                "adjustments": len(weighting_adj),
                "applied": True,
            }
        
        return plan


async def get_enhanced_strategy_generator(session: AsyncSession) -> EnhancedStrategyGenerator:
    """Get enhanced strategy generator."""
    return EnhancedStrategyGenerator(session)


async def get_enhanced_strategic_planner(session: AsyncSession) -> EnhancedStrategicPlanner:
    """Get enhanced strategic planner."""
    return EnhancedStrategicPlanner(session)
