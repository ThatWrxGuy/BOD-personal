"""Goal Decomposer - Converts high-level goals into actionable components."""
import uuid
from typing import Dict, List, Optional

from app.intelligence.planning.planning_models import (
    StrategicGoal,
    GoalDecomposition,
    TimeHorizon,
)


class GoalDecomposer:
    """Decomposes strategic goals into actionable components."""
    
    # Goal decomposition templates
    DECOMPOSITION_TEMPLATES = {
        "wealth": {
            "milestones": [
                "Reduce high-interest debt",
                "Build emergency fund",
                "Maximize retirement contributions",
                "Diversify investments",
                "Build passive income streams",
            ],
            "dependencies": {
                "Build emergency fund": [],
                "Reduce high-interest debt": ["Build emergency fund"],
                "Maximize retirement contributions": ["Reduce high-interest debt"],
                "Diversify investments": ["Maximize retirement contributions"],
                "Build passive income streams": ["Diversify investments"],
            },
            "resources": {"time": "weekly", "capital": "moderate"},
        },
        "health": {
            "milestones": [
                "Establish daily exercise routine",
                "Improve sleep quality",
                "Optimize nutrition",
                "Build mental resilience",
                "Regular health monitoring",
            ],
            "dependencies": {
                "Establish daily exercise routine": [],
                "Improve sleep quality": ["Establish daily exercise routine"],
                "Optimize nutrition": ["Improve sleep quality"],
                "Build mental resilience": ["Optimize nutrition"],
                "Regular health monitoring": ["Build mental resilience"],
            },
            "resources": {"time": "daily", "capital": "low"},
        },
        "career": {
            "milestones": [
                "Update professional skills",
                "Expand professional network",
                "Seek advancement opportunities",
                "Increase responsibilities",
                "Develop leadership capabilities",
            ],
            "dependencies": {
                "Update professional skills": [],
                "Expand professional network": ["Update professional skills"],
                "Seek advancement opportunities": ["Expand professional network"],
                "Increase responsibilities": ["Seek advancement opportunities"],
                "Develop leadership capabilities": ["Increase responsibilities"],
            },
            "resources": {"time": "weekly", "capital": "medium"},
        },
    }
    
    def __init__(self):
        self.custom_decompositions: Dict[str, GoalDecomposition] = {}
    
    def decompose_goal(self, goal: StrategicGoal) -> GoalDecomposition:
        """Decompose a strategic goal into components."""
        
        domain = self._extract_domain(goal.title)
        
        if domain in self.DECOMPOSITION_TEMPLATES:
            template = self.DECOMPOSITION_TEMPLATES[domain]
            decomposition = GoalDecomposition(
                goal_id=goal.id,
                milestones=template["milestones"],
                dependencies=template["dependencies"],
                estimated_duration_days=self._estimate_duration(goal.time_horizon),
                required_resources=template.get("resources", {}),
            )
        else:
            decomposition = self._default_decomposition(goal)
        
        self.custom_decompositions[goal.id] = decomposition
        return decomposition
    
    def _extract_domain(self, title: str) -> str:
        """Extract domain from goal title."""
        title_lower = title.lower()
        
        if any(w in title_lower for w in ["wealth", "financial", "money", "income", "invest"]):
            return "wealth"
        elif any(w in title_lower for w in ["health", "fitness", "exercise", "wellness"]):
            return "health"
        elif any(w in title_lower for w in ["career", "job", "profession", "work"]):
            return "career"
        elif any(w in title_lower for w in ["relationship", "friend", "family", "social"]):
            return "relationships"
        elif any(w in title_lower for w in ["operation", "efficiency", "productivity", "routine"]):
            return "operations"
        
        return "default"
    
    def _estimate_duration(self, horizon: TimeHorizon) -> int:
        """Estimate duration based on time horizon."""
        duration_map = {
            TimeHorizon.IMMEDIATE: 7,
            TimeHorizon.SHORT_TERM: 30,
            TimeHorizon.MEDIUM_TERM: 90,
            TimeHorizon.LONG_TERM: 180,
            TimeHorizon.STRATEGIC: 365,
        }
        return duration_map.get(horizon, 90)
    
    def _default_decomposition(self, goal: StrategicGoal) -> GoalDecomposition:
        """Create a default decomposition for unknown goals."""
        
        return GoalDecomposition(
            goal_id=goal.id,
            milestones=[
                "Assess current state",
                "Define specific objectives",
                "Create action plan",
                "Execute and monitor",
                "Review and adjust",
            ],
            dependencies={
                "Assess current state": [],
                "Define specific objectives": ["Assess current state"],
                "Create action plan": ["Define specific objectives"],
                "Execute and monitor": ["Create action plan"],
                "Review and adjust": ["Execute and monitor"],
            },
            estimated_duration_days=self._estimate_duration(goal.time_horizon),
            required_resources={"time": "weekly", "capital": "variable"},
        )
    
    def get_decomposition(self, goal_id: str) -> Optional[GoalDecomposition]:
        """Get a stored decomposition."""
        return self.custom_decompositions.get(goal_id)
    
    def create_goal(
        self,
        title: str,
        description: str,
        priority: str = "medium",
        horizon: str = "medium_term",
        target_metrics: Optional[Dict[str, float]] = None,
    ) -> StrategicGoal:
        """Create a new strategic goal."""
        
        from app.intelligence.planning.planning_models import PriorityLevel, TimeHorizon
        
        goal = StrategicGoal(
            id=str(uuid.uuid4())[:8],
            title=title,
            description=description,
            priority=PriorityLevel(priority),
            time_horizon=TimeHorizon(horizon),
            target_metrics=target_metrics or {},
        )
        
        return goal


_decomposer: Optional[GoalDecomposer] = None


def get_goal_decomposer() -> GoalDecomposer:
    """Get the global goal decomposer."""
    global _decomposer
    if _decomposer is None:
        _decomposer = GoalDecomposer()
    return _decomposer
