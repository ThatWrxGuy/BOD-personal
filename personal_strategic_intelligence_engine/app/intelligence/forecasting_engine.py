"""Forecasting Engine for predictive analytics."""
import uuid
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strategic_signal import StrategicSignal, SignalCategory
from app.models.goal_progress import GoalProgress
from app.models.strategic_goal import StrategicGoal
from app.models.forecast_model import ForecastModel, ForecastType
from app.core.logging import get_logger

logger = get_logger(__name__)


class ForecastingEngine:
    """Generates forecasts from historical data."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def generate_financial_forecast(
        self,
        days_ahead: int = 30,
    ) -> ForecastModel:
        """Generate financial forecast based on historical signals."""
        cutoff = datetime.utcnow() - timedelta(days=30)
        
        result = await self.session.execute(
            select(StrategicSignal).where(
                StrategicSignal.category == SignalCategory.PERSONAL_FINANCE,
                StrategicSignal.timestamp >= cutoff,
            )
        )
        finance_signals = list(result.scalars().all())
        
        # Calculate simple moving average of financial signals
        if finance_signals:
            avg_strength = sum(s.signal_strength for s in finance_signals) / len(finance_signals)
            avg_urgency = sum(s.urgency for s in finance_signals) / len(finance_signals)
            
            # Project based on trend
            recent_signals = sorted(finance_signals, key=lambda x: x.timestamp)[-10:]
            if len(recent_signals) >= 2:
                first_half = recent_signals[:len(recent_signals)//2]
                second_half = recent_signals[len(recent_signals)//2:]
                
                avg_first = sum(s.signal_strength for s in first_half) / len(first_half)
                avg_second = sum(s.signal_strength for s in second_half) / len(second_half)
                trend = (avg_second - avg_first) / len(recent_signals)
                
                forecast_value = avg_strength + (trend * days_ahead)
            else:
                forecast_value = avg_strength
        else:
            forecast_value = 5.0
        
        # Estimate confidence based on data quantity
        confidence = min(0.7, len(finance_signals) / 30) if finance_signals else 0.3
        
        forecast = ForecastModel(
            forecast_type=ForecastType.FINANCIAL,
            forecast_target="financial_health",
            forecast_value=forecast_value,
            confidence=confidence,
            prediction_horizon=f"{days_ahead}_days",
            source_data_range="30_days",
            methodology="trend_extrapolation",
        )
        
        self.session.add(forecast)
        await self.session.commit()
        await self.session.refresh(forecast)
        
        return forecast

    async def generate_goal_forecast(
        self,
        goal_id: uuid.UUID,
        days_ahead: int = 30,
    ) -> ForecastModel:
        """Generate goal completion forecast."""
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
        
        if not progress_records or not goal.target_value:
            confidence = 0.3
            forecast_value = goal.current_value or 0
        else:
            # Calculate velocity
            first_record = progress_records[0]
            last_record = progress_records[-1]
            
            days_diff = (last_record.recorded_at - first_record.recorded_at).days
            if days_diff <= 0:
                velocity = 0
            else:
                velocity = (last_record.recorded_value - first_record.recorded_value) / days_diff
            
            # Project forward
            days_since_last = (datetime.utcnow() - last_record.recorded_at).days
            current_projected = last_record.recorded_value + (velocity * days_since_last)
            future_projected = current_projected + (velocity * days_ahead)
            
            forecast_value = min(goal.target_value, max(0, future_projected))
            
            # Confidence based on consistency
            if len(progress_records) >= 5:
                confidence = 0.7
            elif len(progress_records) >= 2:
                confidence = 0.5
            else:
                confidence = 0.3
        
        forecast = ForecastModel(
            forecast_type=ForecastType.GOAL_PROGRESS,
            forecast_target=str(goal_id),
            forecast_value=forecast_value,
            confidence=confidence,
            prediction_horizon=f"{days_ahead}_days",
            source_data_range=f"{len(progress_records)}_records",
            methodology="linear_projection",
        )
        
        self.session.add(forecast)
        await self.session.commit()
        await self.session.refresh(forecast)
        
        return forecast

    async def generate_workload_forecast(
        self,
        days_ahead: int = 7,
    ) -> ForecastModel:
        """Generate workload forecast from calendar signals."""
        cutoff = datetime.utcnow() - timedelta(days=30)
        
        result = await self.session.execute(
            select(StrategicSignal).where(
                StrategicSignal.category == SignalCategory.CALENDAR,
                StrategicSignal.timestamp >= cutoff,
            )
        )
        calendar_signals = list(result.scalars().all())
        
        if calendar_signals:
            # Calculate average workload
            avg_strength = sum(s.signal_strength for s in calendar_signals) / len(calendar_signals)
            
            # Look for trend
            recent = sorted(calendar_signals, key=lambda x: x.timestamp)[-10:]
            if len(recent) >= 2:
                first_avg = sum(s.signal_strength for s in recent[:len(recent)//2]) / (len(recent)//2)
                second_avg = sum(s.signal_strength for s in recent[len(recent)//2:]) / (len(recent) - len(recent)//2)
                trend = second_avg - first_avg
                
                forecast_value = avg_strength + (trend * (days_ahead / 7))
            else:
                forecast_value = avg_strength
        else:
            forecast_value = 5.0
        
        confidence = min(0.7, len(calendar_signals) / 30) if calendar_signals else 0.3
        
        forecast = ForecastModel(
            forecast_type=ForecastType.WORKLOAD,
            forecast_target="workload_level",
            forecast_value=forecast_value,
            confidence=confidence,
            prediction_horizon=f"{days_ahead}_days",
            source_data_range="30_days",
            methodology="trend_extrapolation",
        )
        
        self.session.add(forecast)
        await self.session.commit()
        await self.session.refresh(forecast)
        
        return forecast

    async def generate_health_forecast(
        self,
        days_ahead: int = 30,
    ) -> ForecastModel:
        """Generate health trend forecast."""
        cutoff = datetime.utcnow() - timedelta(days=30)
        
        result = await self.session.execute(
            select(StrategicSignal).where(
                StrategicSignal.category == SignalCategory.HEALTH,
                StrategicSignal.timestamp >= cutoff,
            )
        )
        health_signals = list(result.scalars().all())
        
        if health_signals:
            # Calculate average health signal strength (lower is better for health)
            avg_urgency = sum(s.urgency for s in health_signals) / len(health_signals)
            
            # Look for improving or degrading trend
            recent = sorted(health_signals, key=lambda x: x.timestamp)[-10:]
            if len(recent) >= 2:
                first_avg = sum(s.urgency for s in recent[:len(recent)//2]) / (len(recent)//2)
                second_avg = sum(s.urgency for s in recent[len(recent)//2:]) / (len(recent) - len(recent)//2)
                trend = second_avg - first_avg
                
                forecast_value = avg_urgency + (trend * (days_ahead / 30))
            else:
                forecast_value = avg_urgency
        else:
            forecast_value = 5.0
        
        confidence = min(0.7, len(health_signals) / 30) if health_signals else 0.3
        
        forecast = ForecastModel(
            forecast_type=ForecastType.HEALTH,
            forecast_target="health_status",
            forecast_value=forecast_value,
            confidence=confidence,
            prediction_horizon=f"{days_ahead}_days",
            source_data_range="30_days",
            methodology="trend_extrapolation",
        )
        
        self.session.add(forecast)
        await self.session.commit()
        await self.session.refresh(forecast)
        
        return forecast

    async def generate_all_forecasts(
        self,
        days_ahead: int = 30,
    ) -> list[ForecastModel]:
        """Generate all forecast types."""
        forecasts = []
        
        try:
            financial = await self.generate_financial_forecast(days_ahead)
            forecasts.append(financial)
        except Exception as e:
            logger.error(f"Error generating financial forecast: {e}")
        
        try:
            workload = await self.generate_workload_forecast(days_ahead=7)
            forecasts.append(workload)
        except Exception as e:
            logger.error(f"Error generating workload forecast: {e}")
        
        try:
            health = await self.generate_health_forecast(days_ahead)
            forecasts.append(health)
        except Exception as e:
            logger.error(f"Error generating health forecast: {e}")
        
        # Get active goals and forecast each
        result = await self.session.execute(
            select(StrategicGoal).where(StrategicGoal.status == "ACTIVE")
        )
        goals = list(result.scalars().all())
        
        for goal in goals:
            try:
                goal_forecast = await self.generate_goal_forecast(goal.id, days_ahead)
                forecasts.append(goal_forecast)
            except Exception as e:
                logger.error(f"Error generating goal forecast for {goal.id}: {e}")
        
        return forecasts


async def get_forecasting_engine(session: AsyncSession) -> ForecastingEngine:
    """Get a forecasting engine instance."""
    return ForecastingEngine(session)
