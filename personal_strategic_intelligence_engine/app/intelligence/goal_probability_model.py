"""Goal Probability Model for estimating goal completion likelihood."""
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.goal_probability import GoalProbability
from app.models.strategic_goal import StrategicGoal
from app.models.goal_progress import GoalProgress
from app.core.logging import get_logger

logger = get_logger(__name__)


class GoalProbabilityModel:
    """Estimates probability of goal completion."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def calculate_goal_probability(
        self,
        goal_id: uuid.UUID,
    ) -> GoalProbability:
        """Calculate probability of achieving a goal."""
        goal = await self.session.get(StrategicGoal, goal_id)
        if not goal:
            raise ValueError(f"Goal {goal_id} not found")
        
        # Get progress history
        result = await self.session.execute(
            select(GoalProgress).where(
                GoalProgress.goal_id == goal_id,
            ).order_by(GoalProgress.recorded_at)
        )
        progress_records = list(result.scalars().all())
        
        if not goal.target_value or not goal.current_value or not goal.target_date:
            # Insufficient data
            probability = 0.5
            method = "insufficient_data"
            estimated_date = None
            confidence = 0.3
            factors = {"reason": "missing_data"}
        else:
            # Calculate key metrics
            remaining_value = goal.target_value - goal.current_value
            days_remaining = (goal.target_date - datetime.utcnow()).days
            
            if days_remaining <= 0:
                probability = 0.1
                method = "past_deadline"
                estimated_date = goal.target_date
                confidence = 0.9
                factors = {"days_overdue": abs(days_remaining)}
            else:
                # Calculate velocity
                if len(progress_records) >= 2:
                    first = progress_records[0]
                    last = progress_records[-1]
                    days_span = (last.recorded_at - first.recorded_at).days
                    
                    if days_span > 0:
                        velocity = (last.recorded_value - first.recorded_value) / days_span
                    else:
                        velocity = 0
                else:
                    velocity = 0
                
                # Calculate required daily progress
                required_daily = remaining_value / days_remaining
                
                # Calculate probability based on velocity comparison
                if velocity <= 0:
                    probability = 0.2
                    method = "no_progress"
                elif velocity < required_daily * 0.5:
                    probability = 0.3
                    method = "slow_velocity"
                elif velocity < required_daily:
                    probability = 0.5
                    method = "below_required"
                elif velocity < required_daily * 1.5:
                    probability = 0.75
                    method = "good_velocity"
                else:
                    probability = 0.9
                    method = "excellent_velocity"
                
                # Estimate completion date
                if velocity > 0:
                    days_to_complete = remaining_value / velocity
                    estimated_date = datetime.utcnow() + timedelta(days=days_to_complete)
                else:
                    estimated_date = None
                
                # Confidence based on data quality
                if len(progress_records) >= 5:
                    confidence = 0.8
                elif len(progress_records) >= 2:
                    confidence = 0.6
                else:
                    confidence = 0.4
                
                factors = {
                    "remaining_value": remaining_value,
                    "days_remaining": days_remaining,
                    "velocity": velocity,
                    "required_daily": required_daily,
                    "progress_records": len(progress_records),
                }
        
        # Create and save probability record
        prob = GoalProbability(
            goal_id=goal_id,
            probability_of_success=probability,
            estimated_completion_date=estimated_date,
            confidence=confidence,
            calculation_method=method,
            factors=factors,
        )
        
        self.session.add(prob)
        await self.session.commit()
        await self.session.refresh(prob)
        
        return prob

    async def calculate_all_goal_probabilities(self) -> list[GoalProbability]:
        """Calculate probabilities for all active goals."""
        result = await self.session.execute(
            select(StrategicGoal).where(StrategicGoal.status == "ACTIVE")
        )
        goals = list(result.scalars().all())
        
        probabilities = []
        
        for goal in goals:
            try:
                prob = await self.calculate_goal_probability(goal.id)
                probabilities.append(prob)
            except Exception as e:
                logger.error(f"Error calculating probability for goal {goal.id}: {e}")
        
        return probabilities


async def get_goal_probability_model(session: AsyncSession) -> GoalProbabilityModel:
    """Get a goal probability model instance."""
    return GoalProbabilityModel(session)
