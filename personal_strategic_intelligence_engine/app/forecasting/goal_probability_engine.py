"""Goal Probability Engine - Calculates probability of achieving goals."""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date

from app.forecasting.forecast_types import GoalProbability


class GoalProbabilityEngine:
    """Calculates probability of achieving strategic goals."""
    
    def __init__(self):
        self.goals: Dict[str, Dict] = {}
    
    def register_goal(
        self,
        goal_id: str,
        goal_name: str,
        target_date: date,
        current_progress: float = 0.0,
        target_value: float = 1.0,
        priority: float = 0.5,
    ) -> None:
        """Register a goal for tracking."""
        
        self.goals[goal_id] = {
            "goal_id": goal_id,
            "goal_name": goal_name,
            "target_date": target_date,
            "current_progress": current_progress,
            "target_value": target_value,
            "priority": priority,
            "progress_rate": 0.0,  # Will be calculated
        }
    
    def calculate_probability(self, goal_id: str) -> GoalProbability:
        """Calculate probability of achieving a goal."""
        
        if goal_id not in self.goals:
            return GoalProbability(
                goal_id=goal_id,
                goal_name="Unknown",
                probability_of_success=0.0,
                confidence=0.0,
            )
        
        goal = self.goals[goal_id]
        
        # Calculate progress rate
        progress_rate = self._calculate_progress_rate(goal)
        goal["progress_rate"] = progress_rate
        
        # Calculate probability based on multiple factors
        progress_prob = self._calculate_progress_probability(goal)
        time_prob = self._calculate_time_probability(goal)
        risk_prob = self._calculate_risk_probability(goal)
        
        # Combined probability
        probability = (
            progress_prob * 0.4 +
            time_prob * 0.35 +
            risk_prob * 0.25
        )
        
        # Calculate expected completion
        expected_months = self._estimate_completion_months(goal, progress_rate)
        
        # Determine risk factors
        risk_factors = self._identify_risk_factors(goal)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(progress_prob, time_prob, risk_prob)
        
        # Confidence based on data quality
        confidence = min(0.9, 0.3 + progress_rate * 0.6)
        
        return GoalProbability(
            goal_id=goal_id,
            goal_name=goal["goal_name"],
            current_progress=goal["current_progress"] / goal["target_value"],
            probability_of_success=probability,
            expected_months_to_completion=expected_months,
            confidence=confidence,
            risk_factors=risk_factors,
            recommendation=recommendation,
        )
    
    def _calculate_progress_rate(self, goal: Dict) -> float:
        """Calculate rate of progress."""
        
        # Simple rate based on time
        target = goal.get("target_date")
        if not target:
            return 0.1
        
        days_remaining = (target - date.today()).days
        
        if days_remaining <= 0:
            return 1.0 if goal.get("current_progress", 0) >= goal.get("target_value", 1) else 0.0
        
        remaining = goal.get("target_value", 1) - goal.get("current_progress", 0)
        
        if remaining <= 0:
            return 0.0
        
        rate = remaining / days_remaining
        
        return max(0, min(1, rate))
    
    def _calculate_progress_probability(self, goal: Dict) -> float:
        """Calculate probability based on progress rate."""
        
        progress_rate = goal.get("progress_rate", 0.1)
        target_date = goal.get("target_date")
        
        if not target_date:
            return 0.5
        
        days_remaining = (target_date - date.today()).days
        
        # If already past due
        if days_remaining < 0:
            return 0.1
        
        # Base on progress rate
        if progress_rate > 0.1:
            return 0.8
        elif progress_rate > 0.05:
            return 0.6
        else:
            return 0.3
    
    def _calculate_time_probability(self, goal: Dict) -> float:
        """Calculate probability based on time remaining."""
        
        target_date = goal.get("target_date")
        
        if not target_date:
            return 0.5
        
        days_remaining = (target_date - date.today()).days
        
        if days_remaining < 0:
            return 0.0
        elif days_remaining > 365:
            return 0.9
        elif days_remaining > 180:
            return 0.75
        elif days_remaining > 90:
            return 0.6
        else:
            return 0.4
    
    def _calculate_risk_probability(self, goal: Dict) -> float:
        """Calculate probability factoring in risk."""
        
        # Simplified risk assessment
        priority = goal.get("priority", 0.5)
        
        return 0.5 + (priority * 0.3)
    
    def _estimate_completion_months(
        self,
        goal: Dict,
        progress_rate: float,
    ) -> Optional[float]:
        """Estimate months to completion."""
        
        if progress_rate <= 0:
            return None
        
        remaining = goal.get("target_value", 1) - goal.get("current_progress", 0)
        
        if remaining <= 0:
            return 0.0
        
        # Rate per day
        rate_per_day = progress_rate / 30  # Approximate
        
        days_to_complete = remaining / rate_per_day if rate_per_day > 0 else None
        
        if days_to_complete and days_to_complete < 1000:
            return days_to_complete / 30
        
        return None
    
    def _identify_risk_factors(self, goal: Dict) -> List[str]:
        """Identify risk factors for goal."""
        
        factors = []
        
        target_date = goal.get("target_date")
        if target_date:
            days_remaining = (target_date - date.today()).days
            if days_remaining < 30:
                factors.append("Deadline approaching soon")
            if days_remaining < 0:
                factors.append("Goal deadline passed")
        
        progress_rate = goal.get("progress_rate", 0)
        if progress_rate < 0.05:
            factors.append("Low progress rate")
        
        priority = goal.get("priority", 0.5)
        if priority < 0.3:
            factors.append("Low priority")
        
        return factors
    
    def _generate_recommendation(
        self,
        progress_prob: float,
        time_prob: float,
        risk_prob: float,
    ) -> str:
        """Generate recommendation based on probabilities."""
        
        avg = (progress_prob + time_prob + risk_prob) / 3
        
        if avg >= 0.7:
            return "Goal on track - continue current approach"
        elif avg >= 0.5:
            return "Increase focus on this goal to improve success probability"
        else:
            return "Consider adjusting goal timeline or increasing resources"
    
    def calculate_all_probabilities(self) -> List[GoalProbability]:
        """Calculate probabilities for all goals."""
        
        return [self.calculate_probability(gid) for gid in self.goals.keys()]


# Global engine
_goal_engine: Optional[GoalProbabilityEngine] = None


def get_goal_probability_engine() -> GoalProbabilityEngine:
    """Get the global goal probability engine."""
    global _goal_engine
    if _goal_engine is None:
        _goal_engine = GoalProbabilityEngine()
    return _goal_engine
