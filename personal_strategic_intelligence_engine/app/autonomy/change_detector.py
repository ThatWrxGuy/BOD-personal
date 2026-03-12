"""Change detector - identifies significant changes between observations."""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.autonomy.loop_types import (
    ChangeEvent, 
    ChangeCategory, 
    ChangeSeverity,
    StateObservation,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class ChangeDetector:
    """Detects significant changes between state observations."""
    
    def __init__(self):
        self.last_observation: Optional[StateObservation] = None
        self.change_history: List[ChangeEvent] = []
    
    async def detect_changes(
        self,
        current: StateObservation,
    ) -> List[ChangeEvent]:
        """Detect changes from last observation to current."""
        
        changes = []
        
        if not self.last_observation:
            # First observation - no changes to detect
            self.last_observation = current
            return changes
        
        # Compare domains
        current_domains = {d.domain: d for d in current.domains}
        last_domains = {d.domain: d for d in self.last_observation.domains}
        
        # Check each domain
        for domain, current_state in current_domains.items():
            last_state = last_domains.get(domain)
            
            if not last_state:
                continue
            
            # Detect domain-specific changes
            domain_changes = await self._detect_domain_changes(
                domain,
                last_state.state,
                current_state.state,
            )
            changes.extend(domain_changes)
        
        # Update history
        self.change_history.extend(changes)
        self.last_observation = current
        
        return changes
    
    async def _detect_domain_changes(
        self,
        domain: str,
        prior: Dict[str, Any],
        current: Dict[str, Any],
    ) -> List[ChangeEvent]:
        """Detect changes within a specific domain."""
        
        changes = []
        
        if domain == "risks":
            changes.extend(await self._detect_risk_changes(prior, current))
        elif domain == "opportunities":
            changes.extend(await self._detect_opportunity_changes(prior, current))
        elif domain == "habits":
            changes.extend(await self._detect_habit_changes(prior, current))
        elif domain == "goals":
            changes.extend(await self._detect_goal_changes(prior, current))
        elif domain == "daily_plan":
            changes.extend(await self._detect_daily_plan_changes(prior, current))
        
        return changes
    
    async def _detect_risk_changes(
        self,
        prior: Dict[str, Any],
        current: Dict[str, Any],
    ) -> List[ChangeEvent]:
        """Detect risk-related changes."""
        
        changes = []
        
        prior_count = prior.get("count", 0)
        current_count = current.get("count", 0)
        
        if current_count > prior_count:
            # New risks detected
            change = ChangeEvent(
                change_id=str(uuid.uuid4()),
                category=ChangeCategory.RISK_INCREASE,
                domain="risks",
                prior_value=prior_count,
                current_value=current_count,
                severity=ChangeSeverity.HIGH if current_count > 3 else ChangeSeverity.MEDIUM,
                confidence=0.8,
                explanation=f"Risk count increased from {prior_count} to {current_count}",
                recommended_response=None,
            )
            changes.append(change)
        
        elif current_count < prior_count:
            # Risks reduced
            change = ChangeEvent(
                change_id=str(uuid.uuid4()),
                category=ChangeCategory.RISK_DECREASE,
                domain="risks",
                prior_value=prior_count,
                current_value=current_count,
                severity=ChangeSeverity.LOW,
                confidence=0.8,
                explanation=f"Risk count decreased from {prior_count} to {current_count}",
                recommended_response=None,
            )
            changes.append(change)
        
        return changes
    
    async def _detect_opportunity_changes(
        self,
        prior: Dict[str, Any],
        current: Dict[str, Any],
    ) -> List[ChangeEvent]:
        """Detect opportunity-related changes."""
        
        changes = []
        
        prior_count = prior.get("count", 0)
        current_count = current.get("count", 0)
        
        if current_count > prior_count:
            # New opportunities
            change = ChangeEvent(
                change_id=str(uuid.uuid4()),
                category=ChangeCategory.OPPORTUNITY_EMERGE,
                domain="opportunities",
                prior_value=prior_count,
                current_value=current_count,
                severity=ChangeSeverity.MEDIUM,
                confidence=0.7,
                explanation=f"New opportunities detected: {current_count - prior_count} new",
                recommended_response=None,
            )
            changes.append(change)
        
        elif current_count < prior_count:
            # Opportunities expired
            change = ChangeEvent(
                change_id=str(uuid.uuid4()),
                category=ChangeCategory.OPPORTUNITY_DECAY,
                domain="opportunities",
                prior_value=prior_count,
                current_value=current_count,
                severity=ChangeSeverity.LOW,
                confidence=0.7,
                explanation=f"Opportunities reduced from {prior_count} to {current_count}",
                recommended_response=None,
            )
            changes.append(change)
        
        return changes
    
    async def _detect_habit_changes(
        self,
        prior: Dict[str, Any],
        current: Dict[str, Any],
    ) -> List[ChangeEvent]:
        """Detect habit-related changes."""
        
        changes = []
        
        prior_habits = {h["id"]: h for h in prior.get("active_habits", [])}
        current_habits = {h["id"]: h for h in current.get("active_habits", [])}
        
        # Check for declining streaks
        for habit_id, current_habit in current_habits.items():
            prior_habit = prior_habits.get(habit_id)
            
            if prior_habit:
                prior_streak = prior_habit.get("streak", 0)
                current_streak = current_habit.get("streak", 0)
                
                if current_streak < prior_streak:
                    change = ChangeEvent(
                        change_id=str(uuid.uuid4()),
                        category=ChangeCategory.HABIT_DECLINE,
                        domain="habits",
                        prior_value=prior_streak,
                        current_value=current_streak,
                        severity=ChangeSeverity.MEDIUM if current_streak < 7 else ChangeSeverity.LOW,
                        confidence=0.9,
                        explanation=f"Habit streak dropped from {prior_streak} to {current_streak}",
                        recommended_response=None,
                    )
                    changes.append(change)
        
        return changes
    
    async def _detect_goal_changes(
        self,
        prior: Dict[str, Any],
        current: Dict[str, Any],
    ) -> List[ChangeEvent]:
        """Detect goal-related changes."""
        
        changes = []
        
        prior_goals = {g["id"]: g for g in prior.get("active_goals", [])}
        current_goals = {g["id"]: g for g in current.get("active_goals", [])}
        
        for goal_id, current_goal in current_goals.items():
            prior_goal = prior_goals.get(goal_id)
            
            if prior_goal:
                prior_progress = prior_goal.get("progress", 0)
                current_progress = current_goal.get("progress", 0)
                
                if current_progress > prior_progress + 10:
                    change = ChangeEvent(
                        change_id=str(uuid.uuid4()),
                        category=ChangeCategory.GOAL_PROGRESS_ACCELERATE,
                        domain="goals",
                        prior_value=prior_progress,
                        current_value=current_progress,
                        severity=ChangeSeverity.LOW,
                        confidence=0.8,
                        explanation=f"Goal progress accelerated from {prior_progress}% to {current_progress}%",
                        recommended_response=None,
                    )
                    changes.append(change)
        
        return changes
    
    async def _detect_daily_plan_changes(
        self,
        prior: Dict[str, Any],
        current: Dict[str, Any],
    ) -> List[ChangeEvent]:
        """Detect daily plan changes."""
        
        changes = []
        
        prior_completion = prior.get("completion_rate", 0)
        current_completion = current.get("completion_rate", 0)
        
        if current_completion < prior_completion - 0.2:
            change = ChangeEvent(
                change_id=str(uuid.uuid4()),
                category=ChangeCategory.EXECUTION_OVERLOAD,
                domain="daily_plan",
                prior_value=prior_completion,
                current_value=current_completion,
                severity=ChangeSeverity.MEDIUM,
                confidence=0.9,
                explanation=f"Daily completion dropped significantly from {prior_completion} to {current_completion}",
                recommended_response=None,
            )
            changes.append(change)
        
        return changes
    
    def get_change_history(self) -> List[ChangeEvent]:
        """Get change history."""
        return self.change_history[-50:]  # Last 50 changes
    
    def clear_history(self):
        """Clear change history."""
        self.change_history = []


async def get_change_detector() -> ChangeDetector:
    """Get change detector instance."""
    return ChangeDetector()
