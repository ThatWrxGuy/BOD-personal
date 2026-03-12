"""DEPRECATED: Forecasting Engine - Now in app.forecasting.

This module is DEPRECATED. Use app.forecasting instead.
"""
from app.forecasting import ForecastEngine as ForecastingEngine, get_forecast_engine

# Alias for backward compatibility
__all__ = ["ForecastingEngine", "get_forecast_engine", "ForecastEngine"]
