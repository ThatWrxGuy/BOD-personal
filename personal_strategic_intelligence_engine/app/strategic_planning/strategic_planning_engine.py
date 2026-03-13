"""Strategic Planning Engine.

Maintains coherent strategy across time horizons.
"""
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.strategic_planning.planning_models import (
    AlignmentScore,
    PlanEvaluation,
    PlanGenerationContext,
    PlanStatus,
    StrategicPlan,
    StrategicPriority,
    TimeHorizon,
    LIVE_EXECUTION_ENABLED,
    PLANNING_MODE,
)


class StrategicPlanningEngine:
    """Maintains coherent strategic plans across time horizons."""
    
    def __init__(self):
        self._current_plan: Optional[StrategicPlan] = None
        self._plan_history: List[StrategicPlan] = []
    
    def generate_plan(
        self,
        context: PlanGenerationContext,
    ) -> StrategicPlan:
        """Generate a strategic plan based on context.
        
        Uses deterministic hashing to ensure identical inputs
        produce identical outputs.
        """
        
        # Create deterministic plan from context
        plan = self._create_deterministic_plan(context)
        
        # Set as current plan
        self._current_plan = plan
        
        return plan
    
    def _create_deterministic_plan(
        self,
        context: PlanGenerationContext,
    ) -> StrategicPlan:
        """Create a deterministic plan from context."""
        
        # Generate deterministic IDs using context hash
        context_hash = self._hash_context(context)
        
        # Create yearly priority (top level)
        yearly_priority = self._create_yearly_priority(context, context_hash)
        
        # Create quarterly priorities (derived from yearly)
        quarterly_priorities = self._create_quarterly_priorities(
            yearly_priority, context, context_hash
        )
        
        # Create monthly priorities (derived from quarterly)
        monthly_priorities = self._create_monthly_priorities(
            quarterly_priorities, context, context_hash
        )
        
        # Create weekly priorities (derived from monthly)
        weekly_priorities = self._create_weekly_priorities(
            monthly_priorities, context, context_hash
        )
        
        # Create daily focus (derived from weekly)
        daily_focus = self._create_daily_focus(
            weekly_priorities, context, context_hash
        )
        
        # Calculate alignment scores
        overall_alignment = self._calculate_plan_alignment(
            yearly_priority,
            quarterly_priorities,
            monthly_priorities,
            weekly_priorities,
            daily_focus,
        )
        
        return StrategicPlan(
            plan_id=f"plan_{context_hash[:8]}",
            name=self._generate_plan_name(context, context_hash),
            description=self._generate_plan_description(context),
            yearly_priority=yearly_priority,
            quarterly_priorities=quarterly_priorities,
            monthly_priorities=monthly_priorities,
            weekly_priorities=weekly_priorities,
            daily_focus=daily_focus,
            overall_alignment_score=overall_alignment,
        )
    
    def _hash_context(self, context: PlanGenerationContext) -> str:
        """Create deterministic hash from context."""
        
        # Create deterministic string representation
        parts = []
        
        # Add signals (sorted)
        for key in sorted(context.active_signals.keys()):
            parts.append(f"{key}:{context.active_signals[key]:.2f}")
        
        # Add concerns (sorted)
        for concern in sorted(context.current_concerns):
            parts.append(f"concern:{concern}")
        
        # Add goals (sorted)
        for goal in sorted(context.current_goals):
            parts.append(f"goal:{goal}")
        
        # Add pattern context
        if context.pattern_context:
            parts.append(f"pattern:{context.pattern_context}")
        
        context_str = "|".join(parts)
        
        # Create hash
        return hashlib.sha256(context_str.encode()).hexdigest()
    
    def _create_yearly_priority(
        self,
        context: PlanGenerationContext,
        context_hash: str,
    ) -> StrategicPriority:
        """Create yearly priority from context."""
        
        # Determine focus based on signals
        focus = self._determine_yearly_focus(context)
        
        return StrategicPriority(
            priority_id=f"yearly_{context_hash[:8]}",
            title=f"Yearly Focus: {focus.replace('_', ' ').title()}",
            description=f"Strategic goal for the year: {focus}",
            time_horizon=TimeHorizon.YEARLY,
            focus_area=focus,
            target_outcome=f"Achieve meaningful progress in {focus}",
            success_metrics=[f"Quarterly milestones for {focus}"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            alignment_score=1.0,
        )
    
    def _determine_yearly_focus(self, context: PlanGenerationContext) -> str:
        """Determine yearly focus from signals."""
        
        # Map signals to focus areas
        signal_to_focus = {
            "health": "health_resilience",
            "energy": "health_resilience",
            "sleep_quality": "health_resilience",
            "finance": "financial_stability",
            "liquidity": "financial_stability",
            "tasks": "productivity",
            "backlog": "productivity",
            "calendar": "work_life_balance",
            "schedule_overload": "work_life_balance",
        }
        
        # Find dominant signal
        if context.active_signals:
            max_signal = max(
                context.active_signals.items(),
                key=lambda x: abs(x[1])
            )
            
            for signal_key, focus in signal_to_focus.items():
                if signal_key in max_signal[0].lower():
                    return focus
        
        # Default focus
        return "balanced_growth"
    
    def _create_quarterly_priorities(
        self,
        yearly: StrategicPriority,
        context: PlanGenerationContext,
        context_hash: str,
    ) -> List[StrategicPriority]:
        """Create quarterly priorities from yearly."""
        
        priorities = []
        focus = yearly.focus_area
        
        # Map yearly focus to quarterly priorities
        quarterly_mapping = {
            "health_resilience": [
                ("Q1", "Establish health routines"),
                ("Q2", "Build health habits"),
                ("Q3", "Maintain health momentum"),
                ("Q4", "Review and adjust health strategy"),
            ],
            "financial_stability": [
                ("Q1", "Financial assessment and planning"),
                ("Q2", "Implement savings strategy"),
                ("Q3", "Optimize financial decisions"),
                ("Q4", "Year-end financial review"),
            ],
            "productivity": [
                ("Q1", "Productivity system setup"),
                ("Q2", "Workflow optimization"),
                ("Q3", "Efficiency improvements"),
                ("Q4", "Productivity review"),
            ],
            "work_life_balance": [
                ("Q1", "Balance assessment"),
                ("Q2", "Boundary establishment"),
                ("Q3", "Balance maintenance"),
                ("Q4", "Balance review"),
            ],
            "balanced_growth": [
                ("Q1", "Foundation building"),
                ("Q2", "Growth momentum"),
                ("Q3", "Growth refinement"),
                ("Q4", "Growth consolidation"),
            ],
        }
        
        quarters = quarterly_mapping.get(focus, quarterly_mapping["balanced_growth"])
        
        for i, (quarter, title) in enumerate(quarters):
            priority = StrategicPriority(
                priority_id=f"quarterly_{context_hash[:6]}_{i}",
                title=f"{quarter}: {title}",
                description=f"Quarter {i+1} objective aligned with {focus}",
                time_horizon=TimeHorizon.QUARTERLY,
                parent_priority_id=yearly.priority_id,
                focus_area=focus,
                target_outcome=f"Achieve {quarter} milestones for {focus}",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            priorities.append(priority)
        
        return priorities
    
    def _create_monthly_priorities(
        self,
        quarterly: List[StrategicPriority],
        context: PlanGenerationContext,
        context_hash: str,
    ) -> List[StrategicPriority]:
        """Create monthly priorities from quarterly."""
        
        priorities = []
        
        for q in quarterly:
            # Create 3 monthly priorities per quarter
            months = ["Month 1", "Month 2", "Month 3"]
            
            for i, month in enumerate(months):
                priority = StrategicPriority(
                    priority_id=f"monthly_{context_hash[:4]}_{q.priority_id[-2:]}_{i}",
                    title=f"{month} of {q.title}",
                    description=f"Monthly focus aligned with {q.focus_area}",
                    time_horizon=TimeHorizon.MONTHLY,
                    parent_priority_id=q.priority_id,
                    focus_area=q.focus_area,
                    target_outcome=f"Progress toward {q.target_outcome}",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                priorities.append(priority)
        
        return priorities
    
    def _create_weekly_priorities(
        self,
        monthly: List[StrategicPriority],
        context: PlanGenerationContext,
        context_hash: str,
    ) -> List[StrategicPriority]:
        """Create weekly priorities from monthly."""
        
        priorities = []
        
        # Take first few monthly priorities
        for m in monthly[:4]:
            priority = StrategicPriority(
                priority_id=f"weekly_{context_hash[:4]}_{m.priority_id[-4:]}",
                title=f"Weekly: {m.focus_area.replace('_', ' ').title()}",
                description=f"Weekly focus on {m.focus_area}",
                time_horizon=TimeHorizon.WEEKLY,
                parent_priority_id=m.priority_id,
                focus_area=m.focus_area,
                target_outcome=f"Make progress on {m.target_outcome}",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            priorities.append(priority)
        
        return priorities
    
    def _create_daily_focus(
        self,
        weekly: List[StrategicPriority],
        context: PlanGenerationContext,
        context_hash: str,
    ) -> List[StrategicPriority]:
        """Create daily focus from weekly."""
        
        focus = []
        
        # Create daily focus from top weekly priority
        if weekly:
            top_weekly = weekly[0]
            
            daily_actions = [
                ("Morning priority", "Start with most important task"),
                ("Mid-day focus", "Maintain momentum on key work"),
                ("Evening review", "Review progress and plan tomorrow"),
            ]
            
            for i, (title, desc) in enumerate(daily_actions):
                priority = StrategicPriority(
                    priority_id=f"daily_{context_hash[:2]}_{i}",
                    title=title,
                    description=desc,
                    time_horizon=TimeHorizon.DAILY,
                    parent_priority_id=top_weekly.priority_id,
                    focus_area=top_weekly.focus_area,
                    target_outcome=top_weekly.target_outcome,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                focus.append(priority)
        
        return focus
    
    def _generate_plan_name(self, context: PlanGenerationContext, context_hash: str) -> str:
        """Generate plan name deterministically."""
        
        # Use first part of hash for deterministic name
        return f"Strategic Plan {context_hash[:8].upper()}"
    
    def _generate_plan_description(self, context: PlanGenerationContext) -> str:
        """Generate plan description from context."""
        
        if context.current_concerns:
            concerns = ", ".join(context.current_concerns[:2])
            return f"Plan addressing: {concerns}"
        elif context.current_goals:
            goals = ", ".join(context.current_goals[:2])
            return f"Plan supporting: {goals}"
        else:
            return "Strategic plan for balanced growth"
    
    def _calculate_plan_alignment(
        self,
        yearly: StrategicPriority,
        quarterly: List[StrategicPriority],
        monthly: List[StrategicPriority],
        weekly: List[StrategicPriority],
        daily: List[StrategicPriority],
    ) -> float:
        """Calculate overall alignment score for the plan."""
        
        # Check hierarchical alignment
        scores = []
        
        # Yearly -> Quarterly alignment
        if quarterly:
            q_focus = quarterly[0].focus_area
            scores.append(1.0 if q_focus == yearly.focus_area else 0.5)
        
        # Quarterly -> Monthly alignment
        if monthly:
            m_focus = monthly[0].focus_area
            if quarterly:
                q_focus = quarterly[0].focus_area
                scores.append(1.0 if m_focus == q_focus else 0.5)
        
        # Monthly -> Weekly alignment
        if weekly and monthly:
            w_focus = weekly[0].focus_area
            m_focus = monthly[0].focus_area
            scores.append(1.0 if w_focus == m_focus else 0.5)
        
        # Weekly -> Daily alignment
        if daily and weekly:
            d_focus = daily[0].focus_area
            w_focus = weekly[0].focus_area
            scores.append(1.0 if d_focus == w_focus else 0.5)
        
        return sum(scores) / len(scores) if scores else 1.0
    
    def get_current_plan(self) -> Optional[StrategicPlan]:
        """Get the current strategic plan."""
        return self._current_plan
    
    def evaluate_recommendation(
        self,
        recommendation_id: str,
        recommendation_type: str,
    ) -> PlanEvaluation:
        """Evaluate a recommendation against current plan."""
        
        plan = self._current_plan
        if not plan:
            return PlanEvaluation(
                recommendation_id=recommendation_id,
                recommendation_type=recommendation_type,
                alignment_verdict="neutral",
                adjusted_score=0.5,
            )
        
        # Determine recommendation alignment
        rec_type_lower = recommendation_type.lower()
        
        # Check each horizon
        alignment_scores = {}
        
        # Yearly alignment
        if plan.yearly_priority:
            yearly = plan.yearly_priority
            alignment_scores["yearly"] = self._calculate_recommendation_alignment(
                rec_type_lower, yearly
            )
        
        # Quarterly alignment
        if plan.quarterly_priorities:
            q_scores = [
                self._calculate_recommendation_alignment(rec_type_lower, q)
                for q in plan.quarterly_priorities
            ]
            alignment_scores["quarterly"] = sum(q_scores) / len(q_scores)
        
        # Monthly alignment
        if plan.monthly_priorities:
            m_scores = [
                self._calculate_recommendation_alignment(rec_type_lower, m)
                for m in plan.monthly_priorities
            ]
            alignment_scores["monthly"] = sum(m_scores) / len(m_scores)
        
        # Weekly alignment
        if plan.weekly_priorities:
            w_scores = [
                self._calculate_recommendation_alignment(rec_type_lower, w)
                for w in plan.weekly_priorities
            ]
            alignment_scores["weekly"] = sum(w_scores) / len(w_scores)
        
        # Daily alignment
        if plan.daily_focus:
            d_scores = [
                self._calculate_recommendation_alignment(rec_type_lower, d)
                for d in plan.daily_focus
            ]
            alignment_scores["daily"] = sum(d_scores) / len(d_scores)
        
        # Calculate overall
        overall = sum(alignment_scores.values()) / len(alignment_scores) if alignment_scores else 0.5
        
        # Determine verdict
        if overall > 0.7:
            verdict = "supports"
        elif overall < 0.3:
            verdict = "conflicts"
        else:
            verdict = "neutral"
        
        return PlanEvaluation(
            recommendation_id=recommendation_id,
            recommendation_type=recommendation_type,
            yearly_alignment=alignment_scores.get("yearly", 0.5),
            quarterly_alignment=alignment_scores.get("quarterly", 0.5),
            monthly_alignment=alignment_scores.get("monthly", 0.5),
            weekly_alignment=alignment_scores.get("weekly", 0.5),
            daily_alignment=alignment_scores.get("daily", 0.5),
            overall_alignment_score=overall,
            alignment_verdict=verdict,
            adjusted_score=overall,
        )
    
    def _calculate_recommendation_alignment(
        self,
        recommendation_type: str,
        priority: StrategicPriority,
    ) -> float:
        """Calculate alignment between recommendation and priority."""
        
        # Map recommendation types to focus areas
        rec_to_focus = {
            "reduce": ["health_resilience", "work_life_balance"],
            "increase_savings": ["financial_stability"],
            "schedule_recovery": ["health_resilience", "work_life_balance"],
            "prioritize": ["productivity"],
            "focus": ["productivity"],
        }
        
        # Check if recommendation supports priority focus
        for rec_key, focuses in rec_to_focus.items():
            if rec_key in recommendation_type:
                if priority.focus_area in focuses:
                    return 1.0
                else:
                    return 0.3
        
        return 0.5  # Neutral
    
    def get_alignment_scores(self) -> Dict[str, AlignmentScore]:
        """Get alignment scores for each time horizon."""
        
        plan = self._current_plan
        if not plan:
            return {}
        
        scores = {}
        
        # Yearly
        if plan.yearly_priority:
            scores["yearly"] = AlignmentScore(
                horizon=TimeHorizon.YEARLY,
                parent_alignment=1.0,  # Top level
                child_alignment=self._calculate_child_alignment(plan.yearly_priority, plan.quarterly_priorities),
                overall_score=1.0,
            )
        
        # Quarterly
        if plan.quarterly_priorities:
            avg_child = sum(
                self._calculate_child_alignment(q, plan.monthly_priorities)
                for q in plan.quarterly_priorities
            ) / len(plan.quarterly_priorities)
            
            scores["quarterly"] = AlignmentScore(
                horizon=TimeHorizon.QUARTERLY,
                parent_alignment=self._calculate_parent_alignment(
                    plan.quarterly_priorities[0],
                    plan.yearly_priority
                ),
                child_alignment=avg_child,
                overall_score=(self._calculate_parent_alignment(
                    plan.quarterly_priorities[0],
                    plan.yearly_priority
                ) + avg_child) / 2,
            )
        
        return scores
    
    def _calculate_parent_alignment(
        self,
        child: StrategicPriority,
        parent: Optional[StrategicPriority],
    ) -> float:
        """Calculate alignment with parent priority."""
        
        if not parent:
            return 0.5
        
        return 1.0 if child.focus_area == parent.focus_area else 0.3
    
    def _calculate_child_alignment(
        self,
        parent: StrategicPriority,
        children: List[StrategicPriority],
    ) -> float:
        """Calculate alignment with child priorities."""
        
        if not children:
            return 0.5
        
        aligned = sum(
            1 for c in children
            if c.focus_area == parent.focus_area and c.parent_priority_id == parent.priority_id
        )
        
        return aligned / len(children)


# Global engine instance
_strategic_planning_engine: Optional[StrategicPlanningEngine] = None


def get_strategic_planning_engine() -> StrategicPlanningEngine:
    """Get the global strategic planning engine instance."""
    global _strategic_planning_engine
    if _strategic_planning_engine is None:
        _strategic_planning_engine = StrategicPlanningEngine()
    return _strategic_planning_engine
