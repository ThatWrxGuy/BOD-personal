"""Trend Analyzer - Analyzes historical data to detect trends."""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.forecasting.forecast_types import (
    DomainTrend,
    TrendDirection,
    ForecastHorizon,
)


class TrendAnalyzer:
    """Analyzes historical domain data to detect trends."""
    
    def __init__(self):
        self.history: Dict[str, List[Dict]] = {}
    
    def add_data_point(
        self,
        domain: str,
        performance: float,
        risk: float,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Add a historical data point."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        if domain not in self.history:
            self.history[domain] = []
        
        self.history[domain].append({
            "timestamp": timestamp,
            "performance": performance,
            "risk": risk,
        })
    
    def analyze_trend(self, domain: str, horizons: List[str] = ["30d", "90d", "365d"]) -> DomainTrend:
        """Analyze trend for a specific domain."""
        
        if domain not in self.history or not self.history[domain]:
            # Return default if no data
            return DomainTrend(
                domain=domain,
                current_performance=5.0,
                projected_performance_30d=5.0,
                projected_performance_90d=5.0,
                projected_performance_365d=5.0,
                trend_direction=TrendDirection.STABLE,
                trend_confidence=0.0,
            )
        
        data = self.history[domain]
        current = data[-1]["performance"]
        
        # Get historical data for different periods
        now = datetime.utcnow()
        
        # Calculate trends
        trends = self._calculate_trends(data)
        
        # Project future performance
        proj_30 = self._project_performance(data, 30)
        proj_90 = self._project_performance(data, 90)
        proj_365 = self._project_performance(data, 365)
        
        # Determine direction
        direction = self._determine_direction(trends)
        
        # Calculate confidence
        confidence = self._calculate_confidence(data)
        
        # Calculate acceleration
        acceleration = self._calculate_acceleration(trends)
        
        return DomainTrend(
            domain=domain,
            current_performance=current,
            projected_performance_30d=proj_30,
            projected_performance_90d=proj_90,
            projected_performance_365d=proj_365,
            trend_direction=direction,
            trend_confidence=confidence,
            acceleration=acceleration,
        )
    
    def _calculate_trends(self, data: List[Dict]) -> Dict[str, float]:
        """Calculate various trend metrics."""
        
        if len(data) < 2:
            return {"slope": 0, "momentum": 0, "volatility": 0}
        
        # Calculate slope (linear regression)
        n = len(data)
        x = list(range(n))
        y = [d["performance"] for d in data]
        
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Momentum (recent change)
        momentum = y[-1] - y[0] if n > 1 else 0
        
        # Volatility (standard deviation)
        variance = sum((yi - y_mean) ** 2 for yi in y) / n
        volatility = variance ** 0.5
        
        return {
            "slope": slope,
            "momentum": momentum,
            "volatility": volatility,
            "recent_5": y[-5] - y[-6] if n > 5 else 0,
            "recent_10": y[-10] - y[-11] if n > 10 else 0,
        }
    
    def _project_performance(self, data: List[Dict], days: int) -> float:
        """Project performance for given days ahead."""
        
        if not data:
            return 5.0
        
        trends = self._calculate_trends(data)
        
        # Base projection on slope
        slope = trends["slope"]
        
        # Apply slope with decay for longer horizons
        decay = 0.8 ** (days / 30)  # Decay factor
        current = data[-1]["performance"]
        
        projected = current + (slope * days * decay)
        
        # Clamp to valid range
        return max(0, min(10, projected))
    
    def _determine_direction(self, trends: Dict[str, float]) -> TrendDirection:
        """Determine trend direction from metrics."""
        
        slope = trends.get("slope", 0)
        momentum = trends.get("momentum", 0)
        
        if abs(slope) < 0.01 and abs(momentum) < 0.5:
            return TrendDirection.STABLE
        elif slope > 0.01 or momentum > 1:
            return TrendDirection.IMPROVING
        elif slope < -0.01 or momentum < -1:
            return TrendDirection.DECLINING
        else:
            return TrendDirection.UNCERTAIN
    
    def _calculate_confidence(self, data: List[Dict]) -> float:
        """Calculate confidence in trend prediction."""
        
        if len(data) < 3:
            return 0.2
        elif len(data) < 7:
            return 0.4
        elif len(data) < 14:
            return 0.6
        elif len(data) < 30:
            return 0.75
        else:
            return 0.85
    
    def _calculate_acceleration(self, trends: Dict[str, float]) -> float:
        """Calculate acceleration (change in slope)."""
        
        recent = trends.get("recent_5", 0)
        overall = trends.get("slope", 0)
        
        return recent - overall
    
    def analyze_all_domains(self, domains: List[str]) -> List[DomainTrend]:
        """Analyze trends for all domains."""
        
        return [self.analyze_trend(domain) for domain in domains]


# Global analyzer
_trend_analyzer: Optional[TrendAnalyzer] = None


def get_trend_analyzer() -> TrendAnalyzer:
    """Get the global trend analyzer."""
    global _trend_analyzer
    if _trend_analyzer is None:
        _trend_analyzer = TrendAnalyzer()
    return _trend_analyzer
