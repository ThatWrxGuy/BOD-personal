"""Degradation Monitor.

Detects when strategies lose effectiveness.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field

from app.intelligence.alpha_engine.alpha_models import DegradationAlert, AlphaCandidate


@dataclass
class PerformanceSnapshot:
    """Performance snapshot for comparison."""
    period: str
    expectancy: float
    win_rate: float
    sample_size: int


class DegradationMonitor:
    """Detects strategy degradation."""
    
    def __init__(self):
        self.alerts_history = []
        self.baseline_performance = {}
    
    def check_degradation(
        self,
        candidate: AlphaCandidate,
        recent_trades: List[Dict],
    ) -> Optional[DegradationAlert]:
        """Check if strategy is degrading."""
        
        if not recent_trades or len(recent_trades) < 10:
            return None
        
        # Calculate recent metrics
        recent_expectancy = sum(t.get("pnl", 0) for t in recent_trades) / len(recent_trades)
        recent_win_rate = len([t for t in recent_trades if t.get("pnl", 0) > 0]) / len(recent_trades) * 100
        
        # Get baseline
        baseline = self.baseline_performance.get(candidate.id)
        
        if not baseline:
            # Set baseline
            self.baseline_performance[candidate.id] = {
                "expectancy": recent_expectancy,
                "win_rate": recent_win_rate,
                "sample_size": len(recent_trades),
            }
            return None
        
        # Calculate changes
        expectancy_change = ((recent_expectancy - baseline["expectancy"]) / abs(baseline["expectancy"]) * 100) if baseline["expectancy"] != 0 else 0
        win_rate_change = recent_win_rate - baseline["win_rate"]
        
        # Check for degradation
        if expectancy_change < -25 or win_rate_change < -15:
            severity = "critical" if expectancy_change < -50 or win_rate_change < -25 else "high"
            
            alert = DegradationAlert(
                strategy_id=candidate.id,
                strategy_name=candidate.name,
                expectancy_change=expectancy_change,
                win_rate_change=win_rate_change,
                severity=severity,
                recommended_action=self._get_action(severity),
            )
            
            self.alerts_history.append(alert)
            
            # Update baseline if major change
            if abs(expectancy_change) > 30:
                self.baseline_performance[candidate.id] = {
                    "expectancy": recent_expectancy,
                    "win_rate": recent_win_rate,
                    "sample_size": len(recent_trades),
                }
            
            return alert
        
        return None
    
    def _get_action(self, severity: str) -> str:
        """Get recommended action based on severity."""
        
        if severity == "critical":
            return "Immediately limit or retire strategy"
        elif severity == "high":
            return "Reduce position size and monitor closely"
        else:
            return "Monitor - consider reducing confidence"
    
    def get_active_alerts(self) -> List[DegradationAlert]:
        """Get active degradation alerts."""
        
        return self.alerts_history[-10:]
    
    def reset_baseline(self, candidate_id: str) -> None:
        """Reset baseline for a strategy."""
        
        if candidate_id in self.baseline_performance:
            del self.baseline_performance[candidate_id]


def create_monitor() -> DegradationMonitor:
    """Create degradation monitor."""
    return DegradationMonitor()
