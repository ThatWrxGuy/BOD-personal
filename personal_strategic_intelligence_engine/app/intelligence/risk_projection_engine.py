"""DEPRECATED: Risk Projection Engine - Now in app.forecasting.

This module is DEPRECATED. Use app.forecasting instead.
"""
from app.forecasting import RiskProjector as RiskProjectorModel, get_risk_projector

__all__ = ["RiskProjector", "get_risk_projector", "RiskProjectorModel"]

# Alias for backward compatibility
RiskProjector = RiskProjectorModel
