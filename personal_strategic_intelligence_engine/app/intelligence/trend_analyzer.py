"""DEPRECATED: Trend Analyzer - Now in app.forecasting.

This module is DEPRECATED. Use app.forecasting instead.
"""
from app.forecasting import TrendAnalyzer as TrendAnalyzerModel, get_trend_analyzer

__all__ = ["TrendAnalyzer", "get_trend_analyzer", "TrendAnalyzerModel"]

# Alias for backward compatibility
TrendAnalyzer = TrendAnalyzerModel
