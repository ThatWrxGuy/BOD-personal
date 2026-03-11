"""Command interpreter for routing intents to system modules."""
from typing import Dict, Any, Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.chat_types import IntentType
from app.core.logging import get_logger

logger = get_logger(__name__)


class CommandInterpreter:
    """Interpret intents and execute commands."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def execute(self, intent: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command based on intent."""
        
        if intent == IntentType.QUERY_RISKS:
            return await self._query_risks(params)
        
        elif intent == IntentType.QUERY_OPPORTUNITIES:
            return await self._query_opportunities(params)
        
        elif intent == IntentType.RUN_SIMULATION:
            return await self._run_simulation(params)
        
        elif intent == IntentType.START_RESEARCH:
            return await self._start_research(params)
        
        elif intent == IntentType.GENERATE_PLAN:
            return await self._generate_plan(params)
        
        elif intent == IntentType.RUN_REVIEW:
            return await self._run_review(params)
        
        elif intent == IntentType.CHECK_FINANCES:
            return await self._check_finances(params)
        
        elif intent == IntentType.QUERY_GOALS:
            return await self._query_goals(params)
        
        elif intent == IntentType.SYSTEM_STATUS:
            return await self._system_status()
        
        elif intent == IntentType.LIST_BILLS:
            return await self._list_bills(params)
        
        elif intent == IntentType.CHECK_LIQUIDITY:
            return await self._check_liquidity(params)
        
        else:
            return await self._general_query(params)
    
    async def _query_risks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query detected risks."""
        
        from app.detection.detection_engine import get_detection_engine
        
        engine = await get_detection_engine(self.session)
        events = await engine.get_detection_events(domain=None, limit=10)
        
        risks = [e for e in events if e.severity in ["high", "critical"]]
        
        return {
            "type": "risks",
            "count": len(risks),
            "items": [
                {
                    "title": r.title,
                    "severity": r.severity,
                    "domain": r.domain,
                }
                for r in risks[:5]
            ],
        }
    
    async def _query_opportunities(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query detected opportunities."""
        
        from app.detection.detection_engine import get_detection_engine
        
        engine = await get_detection_engine(self.session)
        events = await engine.get_detection_events(domain=None, limit=10)
        
        opportunities = [e for e in events if e.event_type == "opportunity"]
        
        return {
            "type": "opportunities",
            "count": len(opportunities),
            "items": [
                {
                    "title": o.title,
                    "confidence": o.confidence_score,
                    "domain": o.domain,
                }
                for o in opportunities[:5]
            ],
        }
    
    async def _run_simulation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a simulation."""
        
        from app.simulation.simulation_engine import get_simulation_engine
        
        engine = await get_simulation_engine(self.session)
        
        # Determine decision type
        decision_type = params.get("decision_type", "investment")
        
        simulation = await engine.run_simulation(
            decision_type=decision_type,
            decision_params=params.get("decision_params", {}),
            time_horizon_days=params.get("time_horizon_days", 90),
        )
        
        return {
            "type": "simulation",
            "simulation_id": str(simulation.id),
            "status": simulation.status,
            "scenarios": simulation.scenarios_generated,
            "recommended": simulation.recommended_scenario,
        }
    
    async def _start_research(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start research."""
        
        from app.research.research_engine import get_research_engine
        
        engine = await get_research_engine(self.session)
        
        topic = params.get("topic", "general research")
        
        task = await engine.run_research(
            topic=topic,
            scope=params.get("scope", "standard"),
        )
        
        return {
            "type": "research",
            "task_id": str(task.id),
            "status": task.status,
            "topic": task.topic,
        }
    
    async def _generate_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a strategic plan."""
        
        from app.planning.strategic_planner import get_strategic_planner
        
        planner = await get_strategic_planner(self.session)
        
        plan = await planner.generate_plan(
            scope=params.get("scope", "monthly"),
            domains=params.get("domains"),
        )
        
        return {
            "type": "plan",
            "plan_id": str(plan.id),
            "title": plan.title,
            "status": plan.status,
            "domains": plan.domains_involved,
        }
    
    async def _run_review(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a strategic review."""
        
        from app.reviews.strategic_review_engine import get_strategic_review_engine
        
        engine = await get_strategic_review_engine(self.session)
        
        review = await engine.run_review(
            review_type=params.get("type", "monthly"),
            domains=params.get("domains"),
        )
        
        return {
            "type": "review",
            "review_id": str(review.id),
            "status": review.status,
            "type": review.review_type,
        }
    
    async def _check_finances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check financial status."""
        
        from app.finance_ops.bill_registry import get_bill_registry
        from app.finance_ops.cashflow_forecaster import get_cashflow_forecaster, get_liquidity_monitor
        
        bill_registry = await get_bill_registry(self.session)
        bills = await bill_registry.get_bills(limit=10)
        
        forecaster = await get_cashflow_forecaster(self.session)
        forecast = await forecaster.forecast_cashflow(30)
        
        monitor = await get_liquidity_monitor(self.session)
        liquidity = await monitor.check_liquidity()
        
        return {
            "type": "financial_status",
            "upcoming_bills": len(bills),
            "bills_total": sum(b.amount for b in bills),
            "forecast": {
                "ending_balance": forecast.get("ending_balance"),
                "lowest_date": forecast.get("lowest_balance_date"),
            },
            "liquidity": {
                "status": liquidity.get("status"),
                "days_coverage": liquidity.get("days_of_coverage"),
            },
        }
    
    async def _query_goals(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query goals from knowledge graph."""
        
        from app.knowledge.knowledge_graph import get_knowledge_graph
        
        graph = await get_knowledge_graph(self.session)
        
        entities = await graph.get_entities(entity_type="goal")
        
        return {
            "type": "goals",
            "count": len(entities),
            "items": [
                {
                    "name": e.name,
                    "domain": e.domain,
                    "status": e.status,
                }
                for e in entities[:10]
            ],
        }
    
    async def _system_status(self) -> Dict[str, Any]:
        """Get system status."""
        
        return {
            "type": "system_status",
            "status": "operational",
            "version": "3.0",
            "modules": [
                "strategic_reviews",
                "detection",
                "planning",
                "knowledge",
                "research",
                "finance_ops",
                "simulation",
            ],
        }
    
    async def _list_bills(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List upcoming bills."""
        
        from app.finance_ops.bill_registry import get_bill_registry
        
        registry = await get_bill_registry(self.session)
        
        days = params.get("days_ahead", 30)
        bills = await registry.get_upcoming_bills(days)
        
        return {
            "type": "bills",
            "count": len(bills),
            "total": sum(b.amount for b in bills),
            "items": [
                {
                    "name": b.name,
                    "amount": b.amount,
                    "due_date": str(b.due_date),
                    "category": b.category,
                }
                for b in bills[:10]
            ],
        }
    
    async def _check_liquidity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check liquidity."""
        
        from app.finance_ops.cashflow_forecaster import get_liquidity_monitor
        
        monitor = await get_liquidity_monitor(self.session)
        liquidity = await monitor.check_liquidity()
        
        return {
            "type": "liquidity",
            "status": liquidity.get("status"),
            "current_balance": liquidity.get("current_balance"),
            "days_of_coverage": liquidity.get("days_of_coverage"),
            "alerts": [
                {"message": a.message, "severity": a.severity}
                for a in liquidity.get("alerts", [])[:3]
            ],
        }
    
    async def _general_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general query."""
        
        return {
            "type": "general",
            "message": "I can help with risks, opportunities, simulations, research, plans, reviews, finances, and goals. What would you like to explore?",
        }


async def get_command_interpreter(session: AsyncSession) -> CommandInterpreter:
    """Get command interpreter instance."""
    return CommandInterpreter(session)
