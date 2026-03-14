"""Strategy generator for creating strategic plans."""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.planning import StrategicPlan, PlanAction
from app.planning.plan_types import (
    PlanType,
    TimeHorizon,
    PlanStatus,
    ActionStatus,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class StrategyGenerator:
    """Generates strategic plans based on analysis."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def generate_plan(
        self,
        scope: str,
        domains: List[str],
        insights: Optional[List[Dict[str, Any]]] = None,
    ) -> StrategicPlan:
        """Generate a strategic plan."""
        
        # Determine plan type based on scope
        plan_type = self._determine_plan_type(scope, domains)
        
        # Determine time horizon
        time_horizon = self._determine_time_horizon(scope)
        
        # Create plan
        plan = StrategicPlan(
            plan_type=plan_type.value,
            time_horizon=time_horizon.value,
            status=PlanStatus.DRAFT,
            title=self._generate_title(plan_type, time_horizon),
            description=self._generate_description(domains, insights),
            domains_involved=domains,
            start_date=datetime.utcnow(),
            end_date=self._calculate_end_date(time_horizon),
        )
        
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)
        
        # Generate actions
        actions = await self._generate_actions(plan.id, domains, plan_type)
        
        # Generate insights summary
        plan.insights_summary = self._generate_insights_summary(insights or [], domains)
        
        # Generate tradeoff analysis
        plan.tradeoff_analysis = await self._generate_tradeoff_analysis(domains)
        
        # Generate risk assessment
        plan.risk_assessment = await self._generate_risk_assessment(domains)
        
        # Set confidence score
        plan.confidence_score = self._calculate_confidence(insights or [], len(actions))
        
        await self.session.commit()
        await self.session.refresh(plan)
        
        logger.info(f"Generated strategic plan {plan.id} of type {plan_type.value}")
        
        return plan
    
    def _determine_plan_type(self, scope: str, domains: List[str]) -> PlanType:
        """Determine the plan type."""
        
        if len(domains) > 1:
            return PlanType.CROSS_DOMAIN
        
        if scope in ["weekly"]:
            return PlanType.PRODUCTIVITY
        elif scope in ["monthly", "quarterly"]:
            if "financial" in domains:
                return PlanType.FINANCIAL
            elif "health" in domains:
                return PlanType.HEALTH
        
        return PlanType.PRODUCTIVITY
    
    def _determine_time_horizon(self, scope: str) -> TimeHorizon:
        """Determine time horizon from scope."""
        
        if scope == "weekly":
            return TimeHorizon.WEEKLY
        elif scope == "monthly":
            return TimeHorizon.MONTHLY
        elif scope == "quarterly":
            return TimeHorizon.QUARTERLY
        elif scope == "yearly":
            return TimeHorizon.YEARLY
        
        return TimeHorizon.MONTHLY
    
    def _generate_title(self, plan_type: PlanType, time_horizon: TimeHorizon) -> str:
        """Generate a title for the plan."""
        
        type_names = {
            PlanType.FINANCIAL: "Financial",
            PlanType.HEALTH: "Health",
            PlanType.PRODUCTIVITY: "Productivity",
            PlanType.CROSS_DOMAIN: "Integrated",
            PlanType.QUARTERLY: "Quarterly",
        }
        
        horizon_names = {
            TimeHorizon.WEEKLY: "Weekly",
            TimeHorizon.MONTHLY: "Monthly",
            TimeHorizon.QUARTERLY: "Quarterly",
            TimeHorizon.YEARLY: "Yearly",
        }
        
        return f"{horizon_names.get(time_horizon, '')} {type_names.get(plan_type, 'Strategic')} Strategy"
    
    def _generate_description(
        self,
        domains: List[str],
        insights: Optional[List[Dict[str, Any]]],
    ) -> str:
        """Generate a description for the plan."""
        
        domain_names = {
            "financial": "financial position",
            "health": "health and wellness",
            "productivity": "productivity and work",
            "projects": "projects and initiatives",
            "risk": "risk management",
        }
        
        description = f"This plan addresses "
        description += ", ".join([domain_names.get(d, d) for d in domains])
        description += "."
        
        if insights:
            key_insights = [i.get("title", "") for i in insights[:3]]
            if key_insights:
                description += f" Key insights include: {', '.join(key_insights)}."
        
        return description
    
    async def _generate_actions(
        self,
        plan_id: Any,
        domains: List[str],
        plan_type: PlanType,
    ) -> List[PlanAction]:
        """Generate actions for the plan."""
        
        actions = []
        
        # Financial actions
        if "financial" in domains:
            actions.extend([
                PlanAction(
                    plan_id=plan_id,
                    action_type="financial_review",
                    description="Review financial position and cash flow",
                    priority="high",
                    domain="financial",
                    expected_outcome="Clear understanding of financial status",
                ),
                PlanAction(
                    plan_id=plan_id,
                    action_type="budget_assessment",
                    description="Assess budget and spending patterns",
                    priority="medium",
                    domain="financial",
                    expected_outcome="Identified areas for optimization",
                ),
            ])
        
        # Health actions
        if "health" in domains:
            actions.extend([
                PlanAction(
                    plan_id=plan_id,
                    action_type="health_check",
                    description="Review health metrics and trends",
                    priority="high",
                    domain="health",
                    expected_outcome="Health status assessment",
                ),
                PlanAction(
                    plan_id=plan_id,
                    action_type="wellness_planning",
                    description="Plan wellness activities",
                    priority="medium",
                    domain="health",
                    expected_outcome="Scheduled wellness activities",
                ),
            ])
        
        # Productivity actions
        if "productivity" in domains:
            actions.extend([
                PlanAction(
                    plan_id=plan_id,
                    action_type="priority_review",
                    description="Review and prioritize tasks",
                    priority="high",
                    domain="productivity",
                    expected_outcome="Prioritized task list",
                ),
                PlanAction(
                    plan_id=plan_id,
                    action_type="schedule_optimization",
                    description="Optimize calendar and schedule",
                    priority="medium",
                    domain="productivity",
                    expected_outcome="Improved time allocation",
                ),
            ])
        
        # Cross-domain actions
        if len(domains) > 1:
            actions.append(
                PlanAction(
                    plan_id=plan_id,
                    action_type="integration_planning",
                    description="Coordinate actions across domains",
                    priority="high",
                    domain="cross_domain",
                    expected_outcome="Integrated action plan",
                )
            )
        
        for action in actions:
            self.session.add(action)
        
        await self.session.commit()
        
        return actions
    
    def _generate_insights_summary(
        self,
        insights: List[Dict[str, Any]],
        domains: List[str],
    ) -> str:
        """Generate an insights summary."""
        
        if not insights:
            return f"Analysis of {', '.join(domains)} domains suggests focusing on core priorities."
        
        summary = "Key insights from analysis:\n"
        
        for insight in insights[:5]:
            title = insight.get("title", "Insight")
            domain = insight.get("domain", "")
            summary += f"- {title} ({domain})\n"
        
        return summary
    
    async def _generate_tradeoff_analysis(
        self,
        domains: List[str],
    ) -> Dict[str, Any]:
        """Generate tradeoff analysis."""
        
        tradeoffs = []
        
        if "productivity" in domains and "health" in domains:
            tradeoffs.append({
                "type": "time_allocation",
                "description": "More time on productivity may reduce health focus",
                "mitigation": "Schedule dedicated health time",
            })
        
        if "financial" in domains and "productivity" in domains:
            tradeoffs.append({
                "type": "resource_allocation",
                "description": "Financial optimization may require productivity tradeoffs",
                "mitigation": "Prioritize high-impact financial actions",
            })
        
        return {
            "identified_tradeoffs": tradeoffs,
            "complexity": "high" if len(domains) > 2 else "medium",
        }
    
    async def _generate_risk_assessment(
        self,
        domains: List[str],
    ) -> Dict[str, Any]:
        """Generate risk assessment."""
        
        risks = []
        
        if "financial" in domains:
            risks.append({
                "domain": "financial",
                "risk": "market volatility",
                "severity": "medium",
                "mitigation": "Diversify investments",
            })
        
        if "health" in domains:
            risks.append({
                "domain": "health",
                "risk": "burnout",
                "severity": "high",
                "mitigation": "Maintain work-life balance",
            })
        
        if "productivity" in domains:
            risks.append({
                "domain": "productivity",
                "risk": "scope creep",
                "severity": "medium",
                "mitigation": "Clear prioritization",
            })
        
        return {
            "identified_risks": risks,
            "overall_risk_level": "high" if any(r.get("severity") == "high" for r in risks) else "medium",
        }
    
    def _calculate_confidence(
        self,
        insights: List[Dict[str, Any]],
        action_count: int,
    ) -> float:
        """Calculate confidence score for the plan."""
        
        base_confidence = 0.5
        
        # More insights = higher confidence
        if len(insights) > 5:
            base_confidence += 0.2
        elif len(insights) > 0:
            base_confidence += 0.1
        
        # More actions can reduce confidence
        if action_count > 10:
            base_confidence -= 0.1
        elif action_count < 3:
            base_confidence -= 0.1
        
        return max(0.3, min(0.9, base_confidence))
    
    def _calculate_end_date(self, time_horizon: TimeHorizon) -> datetime:
        """Calculate the end date based on time horizon."""
        
        if time_horizon == TimeHorizon.WEEKLY:
            return datetime.utcnow() + timedelta(days=7)
        elif time_horizon == TimeHorizon.MONTHLY:
            return datetime.utcnow() + timedelta(days=30)
        elif time_horizon == TimeHorizon.QUARTERLY:
            return datetime.utcnow() + timedelta(days=90)
        elif time_horizon == TimeHorizon.YEARLY:
            return datetime.utcnow() + timedelta(days=365)
        
        return datetime.utcnow() + timedelta(days=30)


async def get_strategy_generator(session: AsyncSession) -> StrategyGenerator:
    """Get strategy generator instance."""
    return StrategyGenerator(session)
