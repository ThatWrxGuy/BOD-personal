"""Plan Prioritizer - Ranks and selects optimal plans."""
from typing import List, Dict, Any, Optional

from app.intelligence.planning.planning_models import (
    StrategicPlan,
    PlanEvaluation,
)


class PlanPrioritizer:
    """Ranks and prioritizes strategic plans."""
    
    def __init__(self):
        self.prioritized_plans: List[str] = []  # Plan IDs
    
    def prioritize_plans(
        self,
        plans: List[StrategicPlan],
        evaluations: List[PlanEvaluation],
    ) -> List[StrategicPlan]:
        """Prioritize plans based on evaluations."""
        
        # Create evaluation lookup
        eval_lookup = {e.plan_id: e for e in evaluations}
        
        # Add scores to plans
        scored_plans = []
        
        for plan in plans:
            evaluation = eval_lookup.get(plan.id)
            
            if evaluation:
                scored_plans.append({
                    "plan": plan,
                    "evaluation": evaluation,
                })
        
        # Sort by overall score
        scored_plans.sort(
            key=lambda x: x["evaluation"].overall_score,
            reverse=True
        )
        
        # Update prioritized list
        self.prioritized_plans = [s["plan"].id for s in scored_plans]
        
        return [s["plan"] for s in scored_plans]
    
    def get_top_plan(
        self,
        plans: List[StrategicPlan],
        evaluations: List[PlanEvaluation],
    ) -> Optional[StrategicPlan]:
        """Get the highest-ranked plan."""
        
        prioritized = self.prioritize_plans(plans, evaluations)
        
        return prioritized[0] if prioritized else None
    
    def filter_by_risk(
        self,
        plans: List[StrategicPlan],
        evaluations: List[PlanEvaluation],
        max_risk: float = 5.0,
    ) -> List[StrategicPlan]:
        """Filter plans by maximum risk tolerance."""
        
        eval_lookup = {e.plan_id: e for e in evaluations}
        
        filtered = [
            plan for plan in plans
            if eval_lookup.get(plan.id) and eval_lookup[plan.id].risk_score <= max_risk
        ]
        
        return filtered
    
    def filter_by_timeframe(
        self,
        plans: List[StrategicPlan],
        max_duration_days: int,
    ) -> List[StrategicPlan]:
        """Filter plans by maximum duration."""
        
        return [
            plan for plan in plans
            if plan.estimated_duration_days <= max_duration_days
        ]
    
    def get_recommendations(
        self,
        plans: List[StrategicPlan],
        evaluations: List[PlanEvaluation],
    ) -> Dict[str, Any]:
        """Generate recommendations based on prioritization."""
        
        prioritized = self.prioritize_plans(plans, evaluations)
        eval_lookup = {e.plan_id: e for e in evaluations}
        
        recommendations = {
            "top_recommendation": None,
            "alternatives": [],
            "risky_plans": [],
            "reasoning": [],
        }
        
        if prioritized:
            top = prioritized[0]
            top_eval = eval_lookup.get(top.id)
            
            if top_eval:
                recommendations["top_recommendation"] = {
                    "plan_id": top.id,
                    "plan_type": top.plan_type.value,
                    "score": top_eval.overall_score,
                    "probability": top_eval.probability_of_success,
                    "risk": top_eval.risk_score,
                }
                
                recommendations["reasoning"].append(
                    f"Selected {top.plan_type.value} plan with "
                    f"overall score {top_eval.overall_score:.1f}/10"
                )
            
            # Alternatives
            for alt in prioritized[1:3]:
                alt_eval = eval_lookup.get(alt.id)
                if alt_eval:
                    recommendations["alternatives"].append({
                        "plan_id": alt.id,
                        "plan_type": alt.plan_type.value,
                        "score": alt_eval.overall_score,
                    })
        
        # Identify risky plans
        for plan in plans:
            eval = eval_lookup.get(plan.id)
            if eval and eval.risk_score >= 7.0:
                recommendations["risky_plans"].append({
                    "plan_id": plan.id,
                    "risk": eval.risk_score,
                    "reason": "High risk score",
                })
                recommendations["reasoning"].append(
                    f"Warning: {plan.plan_type.value} plan has elevated risk"
                )
        
        return recommendations


_prioritizer: Optional[PlanPrioritizer] = None


def get_plan_prioritizer() -> PlanPrioritizer:
    """Get the global plan prioritizer."""
    global _prioritizer
    if _prioritizer is None:
        _prioritizer = PlanPrioritizer()
    return _prioritizer
