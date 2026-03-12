"""Risk Projection - Projects future risk exposure."""
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.forecasting.forecast_types import (
    RiskProjection,
    RiskLevel,
)
from app.forecasting.trend_analyzer import TrendAnalyzer


class RiskProjector:
    """Projects future risk exposure."""
    
    def __init__(self, trend_analyzer: TrendAnalyzer):
        self.trend_analyzer = trend_analyzer
    
    def project_risk(
        self,
        domain: str,
        risk_type: str,
        current_risk: float,
        days_ahead: int = 30,
    ) -> RiskProjection:
        """Project risk for a domain."""
        
        # Get risk history
        risk_history = []
        if domain in self.trend_analyzer.history:
            for point in self.trend_analyzer.history[domain]:
                risk_history.append(point.get("risk", current_risk))
        
        # Calculate trend
        risk_trend = self._calculate_risk_trend(risk_history)
        
        # Project future risk
        projected = self._project_future_risk(current_risk, risk_trend, days_ahead)
        
        # Calculate probability of risk event
        prob_event = self._calculate_event_probability(projected, risk_trend)
        
        # Estimate time to event
        time_to_event = self._estimate_time_to_event(current_risk, risk_trend)
        
        # Determine severity
        severity = self._determine_severity(projected)
        
        return RiskProjection(
            domain=domain,
            risk_type=risk_type,
            current_risk=current_risk,
            projected_risk_30d=projected if days_ahead >= 30 else current_risk,
            projected_risk_90d=projected if days_ahead >= 90 else self._project_future_risk(current_risk, risk_trend, 90),
            probability_of_event=prob_event,
            estimated_time_to_event_days=time_to_event,
            severity=severity,
        )
    
    def _calculate_risk_trend(self, history: List[float]) -> Dict[str, float]:
        """Calculate risk trend from history."""
        
        if len(history) < 2:
            return {"slope": 0, "momentum": 0, "volatility": 0}
        
        # Simple linear trend
        n = len(history)
        x = list(range(n))
        
        x_mean = sum(x) / n
        y_mean = sum(history) / n
        
        numerator = sum((x[i] - x_mean) * (history[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Momentum
        momentum = history[-1] - history[0]
        
        return {
            "slope": slope,
            "momentum": momentum,
            "volatility": (sum((y - y_mean) ** 2 for y in history) / n) ** 0.5,
        }
    
    def _project_future_risk(
        self,
        current: float,
        trend: Dict[str, float],
        days: int,
    ) -> float:
        """Project future risk level."""
        
        slope = trend.get("slope", 0)
        
        # Project with decay
        decay = 0.7 ** (days / 30)
        projected = current + (slope * days * decay)
        
        return max(0, min(10, projected))
    
    def _calculate_event_probability(
        self,
        projected_risk: float,
        trend: Dict[str, float],
    ) -> float:
        """Calculate probability of risk event."""
        
        # Base probability from projected risk
        base_prob = projected_risk / 10
        
        # Increase if risk is accelerating
        if trend.get("slope", 0) > 0.05:
            base_prob *= 1.3
        
        # Decrease if volatile
        if trend.get("volatility", 0) > 2:
            base_prob *= 0.9
        
        return min(1.0, base_prob)
    
    def _estimate_time_to_event(
        self,
        current: float,
        trend: Dict[str, float],
    ) -> Optional[int]:
        """Estimate days until risk threshold is breached."""
        
        threshold = 7.0  # High risk threshold
        
        if current >= threshold:
            return 0
        
        slope = trend.get("slope", 0)
        
        if slope <= 0:
            return None  # Won't reach threshold
        
        days_to_threshold = (threshold - current) / slope
        
        if days_to_threshold > 365:
            return None  # Too far in future
        
        return int(days_to_threshold)
    
    def _determine_severity(self, risk: float) -> RiskLevel:
        """Determine risk severity level."""
        
        if risk < 3:
            return RiskLevel.LOW
        elif risk < 5:
            return RiskLevel.MEDIUM
        elif risk < 7:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def project_all_risks(
        self,
        domains: List[Dict[str, Any]],
    ) -> List[RiskProjection]:
        """Project risks for all domains."""
        
        projections = []
        
        for domain_data in domains:
            name = domain_data.get("name", "unknown")
            risk = domain_data.get("risk_score", 5.0)
            
            proj = self.project_risk(name, "general", risk)
            projections.append(proj)
        
        return projections


# Global projector
_risk_projector: Optional[RiskProjector] = None


def get_risk_projector() -> RiskProjector:
    """Get the global risk projector."""
    global _risk_projector
    if _risk_projector is None:
        from app.forecasting.trend_analyzer import get_trend_analyzer
        analyzer = get_trend_analyzer()
        _risk_projector = RiskProjector(analyzer)
    return _risk_projector
