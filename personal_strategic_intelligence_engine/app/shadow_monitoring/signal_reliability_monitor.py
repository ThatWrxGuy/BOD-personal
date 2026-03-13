"""Signal reliability monitor for measuring signal source quality in real operation.

Tracks stale signals, missing data, source uptime, and malformed signals.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.shadow_monitoring.monitoring_models import (
    MonitoringWindow,
    ShadowCycleRecord,
    SignalReliabilitySnapshot,
)


class SignalReliabilityMonitor:
    """Monitor for tracking signal source reliability."""
    
    def __init__(self):
        """Initialize signal reliability monitor."""
        self.signal_history: List[Dict[str, Any]] = []
        self.source_uptime: Dict[str, List[bool]] = {}
        self.source_last_seen: Dict[str, datetime] = {}
    
    def record_signals(
        self,
        signals: List[Dict[str, Any]],
        cycle_number: int,
    ) -> None:
        """Record signal metrics from a cycle."""
        # Track signals
        for signal in signals:
            source = signal.get("source", "unknown")
            is_stale = signal.get("is_stale", False)
            is_malformed = signal.get("is_malformed", False)
            
            # Record signal
            self.signal_history.append({
                "source": source,
                "is_stale": is_stale,
                "is_malformed": is_malformed,
                "cycle_number": cycle_number,
                "timestamp": datetime.utcnow(),
            })
            
            # Track source uptime
            if source not in self.source_uptime:
                self.source_uptime[source] = []
                self.source_last_seen[source] = datetime.utcnow()
            
            self.source_uptime[source].append(not is_stale and not is_malformed)
            self.source_last_seen[source] = datetime.utcnow()
        
        # Trim history
        if len(self.signal_history) > 10000:
            self.signal_history = self.signal_history[-5000:]
        
        # Trim source uptime
        for source in self.source_uptime:
            if len(self.source_uptime[source]) > 1000:
                self.source_uptime[source] = self.source_uptime[source][-500:]
    
    def get_snapshot(self, window: MonitoringWindow) -> SignalReliabilitySnapshot:
        """Get signal reliability snapshot for a window."""
        window_hours = {
            MonitoringWindow.ONE_DAY: 24,
            MonitoringWindow.SEVEN_DAYS: 24 * 7,
            MonitoringWindow.THIRTY_DAYS: 24 * 30,
        }
        
        hours = window_hours.get(window, 24)
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        recent_signals = [
            s for s in self.signal_history
            if s["timestamp"] >= cutoff
        ]
        
        if not recent_signals:
            return SignalReliabilitySnapshot(
                window=window,
                overall_reliability=1.0,
            )
        
        # Calculate rates
        total = len(recent_signals)
        stale_count = sum(1 for s in recent_signals if s.get("is_stale", False))
        malformed_count = sum(1 for s in recent_signals if s.get("is_malformed", False))
        
        stale_rate = stale_count / total
        malformed_rate = malformed_count / total
        
        # Overall reliability
        overall = 1.0 - (stale_rate + malformed_rate) / 2
        
        # Source reliability
        source_reliability: Dict[str, float] = {}
        for source in self.source_uptime:
            uptime_list = self.source_uptime[source][-100:]  # Last 100
            if uptime_list:
                source_reliability[source] = sum(uptime_list) / len(uptime_list)
        
        # Source uptime
        source_uptime: Dict[str, float] = {}
        for source, last_seen in self.source_last_seen.items():
            if datetime.utcnow() - last_seen < timedelta(hours=hours):
                source_uptime[source] = 1.0
            else:
                source_uptime[source] = 0.0
        
        # Determine trend
        if len(recent_signals) >= 20:
            first_quarter = recent_signals[:len(recent_signals)//4]
            last_quarter = recent_signals[-len(recent_signals)//4:]
            
            first_reliability = 1.0 - (
                sum(1 for s in first_quarter if s.get("is_stale", False)) +
                sum(1 for s in first_quarter if s.get("is_malformed", False))
            ) / len(first_quarter)
            
            last_reliability = 1.0 - (
                sum(1 for s in last_quarter if s.get("is_stale", False)) +
                sum(1 for s in last_quarter if s.get("is_malformed", False))
            ) / len(last_quarter)
            
            if last_reliability > first_reliability * 1.1:
                trend = "improving"
            elif last_reliability < first_reliability * 0.9:
                trend = "degrading"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return SignalReliabilitySnapshot(
            timestamp=datetime.utcnow(),
            window=window,
            overall_reliability=overall,
            reliability_trend=trend,
            source_reliability=source_reliability,
            source_uptime=source_uptime,
            stale_signal_rate=stale_rate,
            malformed_signal_rate=malformed_rate,
            missing_data_rate=0.0,  # Would need domain-specific logic
            quality_trend=trend,
        )
    
    def detect_degradation(self) -> Optional[Dict[str, Any]]:
        """Detect signal source degradation."""
        recent = self.signal_history[-50:]
        
        if len(recent) < 20:
            return None
        
        first_half = recent[:len(recent)//2]
        second_half = recent[len(recent)//2:]
        
        first_issues = sum(
            1 for s in first_half
            if s.get("is_stale", False) or s.get("is_malformed", False)
        ) / len(first_half)
        
        second_issues = sum(
            1 for s in second_half
            if s.get("is_stale", False) or s.get("is_malformed", False)
        ) / len(second_half)
        
        if second_issues > first_issues * 2:  # Doubled issue rate
            return {
                "detected": True,
                "previous_issue_rate": first_issues,
                "current_issue_rate": second_issues,
                "severity": "high" if second_issues > 0.3 else "medium",
            }
        
        return None
    
    def get_sources(self) -> List[str]:
        """Get list of known signal sources."""
        return list(self.source_uptime.keys())
    
    def reset(self) -> None:
        """Reset monitor state."""
        self.signal_history = []
        self.source_uptime = {}
        self.source_last_seen = {}


def create_signal_reliability_monitor() -> SignalReliabilityMonitor:
    """Factory function to create a signal reliability monitor."""
    return SignalReliabilityMonitor()
