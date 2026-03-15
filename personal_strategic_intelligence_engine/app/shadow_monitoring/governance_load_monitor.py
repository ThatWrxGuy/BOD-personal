"""Governance load monitor for measuring governance burden over time.

Tracks review queue volume, flag frequency, and operator burden.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.shadow_monitoring.monitoring_models import (
    GovernanceLoadSnapshot,
    MonitoringWindow,
    ShadowCycleRecord,
)


class GovernanceLoadMonitor:
    """Monitor for tracking governance load over time."""
    
    def __init__(
        self,
        load_threshold_high: float = 0.7,
        load_threshold_critical: float = 0.9,
    ):
        """Initialize governance load monitor.
        
        Args:
            load_threshold_high: Threshold for high load
            load_threshold_critical: Threshold for critical load
        """
        self.load_threshold_high = load_threshold_high
        self.load_threshold_critical = load_threshold_critical
        
        self.load_history: List[float] = []
        self.flag_counts: List[Dict[str, int]] = []
    
    def record_cycle(self, cycle: ShadowCycleRecord) -> None:
        """Record governance metrics from a cycle."""
        self.load_history.append(cycle.governance_load_score)
        self.flag_counts.append({
            "doctrine_flags": len(cycle.doctrine_flags),
            "risk_flags": len(cycle.risk_flags),
        })
        
        # Keep bounded
        if len(self.load_history) > 1000:
            self.load_history = self.load_history[-500:]
            self.flag_counts = self.flag_counts[-500:]
    
    def get_snapshot(self, window: MonitoringWindow) -> GovernanceLoadSnapshot:
        """Get governance load snapshot for a window."""
        window_sizes = {
            MonitoringWindow.ONE_DAY: 24,
            MonitoringWindow.SEVEN_DAYS: 24 * 7,
            MonitoringWindow.THIRTY_DAYS: 24 * 30,
        }
        
        size = window_sizes.get(window, 24)
        loads = self.load_history[-size:]
        flags = self.flag_counts[-size:]
        
        if not loads:
            return GovernanceLoadSnapshot(
                window=window,
                avg_governance_load=0.0,
                max_governance_load=0.0,
            )
        
        avg_load = sum(loads) / len(loads)
        max_load = max(loads)
        
        # Calculate trend
        if len(loads) >= 10:
            first_half = sum(loads[:len(loads)//2]) / (len(loads) // 2)
            second_half = sum(loads[len(loads)//2:]) / (len(loads) - len(loads) // 2)
            
            if second_half > first_half * 1.2:
                trend = "increasing"
            elif second_half < first_half * 0.8:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        # Aggregate flags
        total_doctrine_flags = sum(f.get("doctrine_flags", 0) for f in flags)
        total_risk_flags = sum(f.get("risk_flags", 0) for f in flags)
        
        # Estimate burden (rough: 5 min per load unit per day)
        estimated_hours = avg_load * 8  # 8 hours of potential load
        
        if estimated_hours > 6:
            burden_level = "critical"
        elif estimated_hours > 4:
            burden_level = "high"
        elif estimated_hours > 2:
            burden_level = "moderate"
        elif estimated_hours > 0.5:
            burden_level = "low"
        else:
            burden_level = "minimal"
        
        return GovernanceLoadSnapshot(
            timestamp=datetime.utcnow(),
            window=window,
            avg_governance_load=avg_load,
            max_governance_load=max_load,
            governance_load_trend=trend,
            total_doctrine_flags=total_doctrine_flags,
            total_risk_flags=total_risk_flags,
            estimated_hours_per_day=estimated_hours,
            burden_level=burden_level,
        )
    
    def detect_overload(self) -> Optional[Dict[str, Any]]:
        """Detect governance overload conditions."""
        if not self.load_history:
            return None
        
        recent = self.load_history[-10:]
        overload_count = sum(1 for l in recent if l >= self.load_threshold_critical)
        
        if overload_count >= 5:  # 5 out of 10 cycles at critical
            return {
                "detected": True,
                "severity": "critical",
                "overload_cycles": overload_count,
                "avg_load": sum(recent) / len(recent),
            }
        
        high_count = sum(1 for l in recent if l >= self.load_threshold_high)
        
        if high_count >= 7:
            return {
                "detected": True,
                "severity": "high",
                "high_load_cycles": high_count,
                "avg_load": sum(recent) / len(recent),
            }
        
        return {"detected": False}
    
    def get_flag_trend(self, window: MonitoringWindow) -> str:
        """Get flag trend for a window."""
        window_sizes = {
            MonitoringWindow.ONE_DAY: 24,
            MonitoringWindow.SEVEN_DAYS: 24 * 7,
            MonitoringWindow.THIRTY_DAYS: 24 * 30,
        }
        
        size = window_sizes.get(window, 24)
        flags = self.flag_counts[-size:]
        
        if len(flags) < 10:
            return "stable"
        
        first_half = sum(f.get("doctrine_flags", 0) + f.get("risk_flags", 0) for f in flags[:len(flags)//2])
        second_half = sum(f.get("doctrine_flags", 0) + f.get("risk_flags", 0) for f in flags[len(flags)//2:])
        
        if second_half > first_half * 1.3:
            return "increasing"
        elif second_half < first_half * 0.7:
            return "decreasing"
        
        return "stable"
    
    def reset(self) -> None:
        """Reset monitor state."""
        self.load_history = []
        self.flag_counts = []


def create_governance_load_monitor() -> GovernanceLoadMonitor:
    """Factory function to create a governance load monitor."""
    return GovernanceLoadMonitor()
