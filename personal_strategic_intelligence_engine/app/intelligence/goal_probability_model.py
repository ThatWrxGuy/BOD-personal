"""DEPRECATED: Goal Probability Model - Now in app.forecasting.

This module is DEPRECATED. Use app.forecasting instead.
"""
from app.forecasting import GoalProbabilityEngine as GoalProbabilityModel, get_goal_probability_engine

__all__ = ["GoalProbabilityEngine", "get_goal_probability_engine", "GoalProbabilityModel"]

# Alias for backward compatibility
GoalProbabilityEngine = GoalProbabilityModel
