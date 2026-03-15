"""Argument Generator for creating agent arguments in debates."""
from typing import Optional
from app.models.debate import Position
from app.core.logging import get_logger

logger = get_logger(__name__)


class ArgumentGenerator:
    """Generates structured arguments for debate agents."""
    
    AGENT_EXPERTISE = {
        "strategy": ["long-term planning", "market positioning", "competitive advantage"],
        "finance": ["budget", "investment", "ROI", "cash flow", "valuation"],
        "risk": ["risk mitigation", "contingency", "worst-case scenarios", "compliance"],
        "health": ["wellness", "work-life balance", "physical health", "mental health"],
        "operations": ["efficiency", "processes", "workflow", "automation"],
        "legacy": ["reputation", "values", "brand", "long-term impact"],
    }
    
    async def generate_argument(
        self,
        agent_id: str,
        debate_topic: str,
        context: dict,
        round_number: int = 1,
        parent_argument_id: Optional[str] = None,
    ) -> dict:
        """Generate an argument for an agent."""
        expertise = self.AGENT_EXPERTISE.get(agent_id.lower().replace("_agent", ""), [])
        position = self._determine_position(agent_id, context)
        
        argument_text = self._generate_argument_text(agent_id, debate_topic, expertise, position, context)
        reasoning = self._generate_reasoning(agent_id, debate_topic, expertise, context)
        risk_assessment = self._generate_risk_assessment(agent_id, context, expertise)
        supporting_data = self._generate_supporting_data(agent_id, context, expertise)
        
        return {
            "agent_id": agent_id,
            "position": position,
            "argument_text": argument_text,
            "reasoning": reasoning,
            "risk_assessment": risk_assessment,
            "supporting_data": supporting_data,
            "confidence_score": self._calculate_confidence(context),
            "parent_argument_id": parent_argument_id,
        }
    
    def _determine_position(self, agent_id: str, context: dict) -> str:
        """Determine agent's position."""
        agent_key = agent_id.lower()
        
        if "risk" in agent_key:
            return Position.OPPOSE if context.get("risk_level", 0.5) > 0.6 else Position.SUPPORT
        elif "finance" in agent_key:
            return Position.SUPPORT if context.get("expected_return", 0) > 0.1 else Position.OPPOSE
        elif "health" in agent_key:
            return Position.SUPPORT if context.get("health_impact", 0) > 0 else Position.OPPOSE
        
        return Position.NEUTRAL
    
    def _generate_argument_text(self, agent_id: str, topic: str, expertise: list, position: str, context: dict) -> str:
        """Generate argument text."""
        agent_name = agent_id.replace("_", " ").title()
        
        if position == Position.SUPPORT:
            template = f"As the {agent_name}, I support this initiative because "
        elif position == Position.OPPOSE:
            template = f"As the {agent_name}, I have concerns about this initiative because "
        else:
            template = f"As the {agent_name}, I offer a balanced perspective: "
        
        if expertise:
            template += f"from a {expertise[0]} perspective, "
        
        template += f"the proposal addresses key aspects of {topic}. "
        
        if context.get("expected_return"):
            template += f"The expected return of {context['expected_return']:.1%} is {'attractive' if context['expected_return'] > 0.1 else 'concerning'}."
        
        return template
    
    def _generate_reasoning(self, agent_id: str, topic: str, expertise: list, context: dict) -> str:
        """Generate reasoning."""
        reasoning = f"My analysis of {topic} considers multiple factors. "
        
        if expertise:
            reasoning += f"Our expertise in {', '.join(expertise[:2])} provides unique insights. "
        
        reasoning += "After careful evaluation, I believe this proposal "
        reasoning += "offers favorable outcomes " if context.get("expected_return", 0) > 0.1 else "requires further consideration "
        reasoning += "given the current strategic landscape."
        
        return reasoning
    
    def _generate_risk_assessment(self, agent_id: str, context: dict, expertise: list) -> dict:
        """Generate risk assessment."""
        base_risk = context.get("risk_level", 0.5)
        risk_multiplier = 1.2 if "risk" in agent_id.lower() else 1.0
        
        identified_risks = []
        if base_risk > 0.5:
            identified_risks.append("Moderate to high inherent risk in proposal")
        if context.get("complexity", 0) > 0.7:
            identified_risks.append("High complexity may introduce execution challenges")
        if not context.get("has_contingency"):
            identified_risks.append("No clear contingency plan identified")
        
        return {
            "overall_risk": min(1.0, base_risk * risk_multiplier),
            "identified_risks": identified_risks,
            "mitigation_suggestions": self._get_mitigation_suggestions(identified_risks),
        }
    
    def _generate_supporting_data(self, agent_id: str, context: dict, expertise: list) -> dict:
        """Generate supporting data."""
        data = {"metrics": [], "references": []}
        
        if context.get("historical_performance"):
            data["metrics"].append({"name": "Historical Performance", "value": context["historical_performance"]})
        
        for exp in expertise[:2]:
            data["metrics"].append({"name": f"{exp.title()} Index", "value": "Neutral"})
        
        return data
    
    def _calculate_confidence(self, context: dict) -> float:
        """Calculate confidence score."""
        confidence = 0.5
        if context.get("has_data"):
            confidence += 0.2
        if context.get("has_precedent"):
            confidence += 0.15
        if context.get("expert_consensus"):
            confidence += 0.15
        return min(1.0, confidence)
    
    def _get_mitigation_suggestions(self, risks: list) -> list:
        """Get mitigation suggestions."""
        suggestions = []
        for risk in risks:
            if "inherent risk" in risk.lower():
                suggestions.append("Implement phased rollout with clear milestones")
            if "complexity" in risk.lower():
                suggestions.append("Break down into smaller, manageable components")
            if "contingency" in risk.lower():
                suggestions.append("Develop comprehensive contingency plan")
        return suggestions
    
    async def generate_counter_argument(self, agent_id: str, target_argument: dict, context: dict) -> dict:
        """Generate counter-argument."""
        target_agent = target_argument.get("agent_id", "unknown")
        
        argument_text = f"While I respect the {target_agent}'s perspective, I would like to highlight additional considerations. "
        
        if target_argument.get("position") == Position.SUPPORT:
            argument_text += "The proposed approach may not fully account for potential drawbacks and alternative scenarios."
        else:
            argument_text += "We should also consider the strategic benefits that could be realized."
        
        return {
            "agent_id": agent_id,
            "position": Position.OPPOSE if target_argument.get("position") == Position.SUPPORT else Position.SUPPORT,
            "argument_text": argument_text,
            "reasoning": f"Counter-point to {target_agent}'s argument",
            "parent_argument_id": target_argument.get("id"),
            "confidence_score": target_argument.get("confidence_score", 0.5) * 0.8,
        }


def get_argument_generator() -> ArgumentGenerator:
    """Get argument generator instance."""
    return ArgumentGenerator()
