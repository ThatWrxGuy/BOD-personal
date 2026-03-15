"""Cycle monitor for tracking cycle-level activity over time.

Records each monitoring cycle and computes rolling summaries.
"""
import asyncio
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.shadow_monitoring.monitoring_models import (
    MonitoringStatus,
    MonitoringWindow,
    ShadowCycleRecord,
)


class CycleMonitor:
    """Monitor for tracking cycle-level activity."""
    
    def __init__(self):
        """Initialize cycle monitor."""
        self.cycles: List[ShadowCycleRecord] = []
        self.current_status = MonitoringStatus.STOPPED
        self.cycle_counter = 0
        self.start_time: Optional[datetime] = None
        self.last_cycle_time: Optional[datetime] = None
        
        # Rolling window settings
        self.max_cycles_in_memory = 10000
    
    async def start_monitoring(self) -> None:
        """Start cycle monitoring."""
        self.current_status = MonitoringStatus.RUNNING
        self.start_time = datetime.utcnow()
        self.cycle_counter = 0
    
    async def stop_monitoring(self) -> None:
        """Stop cycle monitoring."""
        self.current_status = MonitoringStatus.STOPPED
    
    async def pause_monitoring(self) -> None:
        """Pause cycle monitoring."""
        self.current_status = MonitoringStatus.PAUSED
    
    async def resume_monitoring(self) -> None:
        """Resume cycle monitoring."""
        self.current_status = MonitoringStatus.RUNNING
    
    async def record_cycle(
        self,
        cycle_data: Dict[str, Any],
    ) -> ShadowCycleRecord:
        """Record a cycle."""
        self.cycle_counter += 1
        
        # Create cycle record
        record = ShadowCycleRecord(
            cycle_id=cycle_data.get("cycle_id", f"shadow_cycle_{self.cycle_counter}"),
            cycle_number=self.cycle_counter,
            timestamp=datetime.utcnow(),
            cycle_duration_ms=cycle_data.get("duration_ms", 0.0),
            signals_processed=cycle_data.get("signals_processed", 0),
            signals_by_domain=cycle_data.get("signals_by_domain", {}),
            stale_signals=cycle_data.get("stale_signals", 0),
            malformed_signals=cycle_data.get("malformed_signals", 0),
            recommendations_generated=cycle_data.get("recommendations_generated", 0),
            recommendations_by_domain=cycle_data.get("recommendations_by_domain", {}),
            recommendations_by_urgency=cycle_data.get("recommendations_by_urgency", {}),
            repeated_recommendations=cycle_data.get("repeated_recommendations", 0),
            execution_intents_generated=cycle_data.get("execution_intents_generated", 0),
            approval_required_count=cycle_data.get("approval_required_count", 0),
            doctrine_blocked_count=cycle_data.get("doctrine_blocked_count", 0),
            risk_rejected_count=cycle_data.get("risk_rejected_count", 0),
            doctrine_flags=cycle_data.get("doctrine_flags", []),
            doctrine_conflicts=cycle_data.get("doctrine_conflicts", 0),
            alignment_score=cycle_data.get("alignment_score", 0.0),
            alignment_level=cycle_data.get("alignment_level", "neutral"),
            risk_flags=cycle_data.get("risk_flags", []),
            risk_level=cycle_data.get("risk_level", "low"),
            confidence_score=cycle_data.get("confidence_score", 0.5),
            confidence_delta=cycle_data.get("confidence_delta", 0.0),
            tier_distribution=cycle_data.get("tier_distribution", {}),
            current_tier=cycle_data.get("current_tier", "tier_0_manual_only"),
            learning_updates=cycle_data.get("learning_updates", 0),
            calibration_adjustments=cycle_data.get("calibration_adjustments", 0.0),
            governance_load_score=cycle_data.get("governance_load_score", 0.0),
            pending_approvals=cycle_data.get("pending_approvals", 0),
            state_snapshot=cycle_data.get("state_snapshot", {}),
        )
        
        self.cycles.append(record)
        self.last_cycle_time = datetime.utcnow()
        
        # Trim if needed
        if len(self.cycles) > self.max_cycles_in_memory:
            self.cycles = self.cycles[-self.max_cycles_in_memory:]
        
        return record
    
    def get_recent_cycles(self, count: int = 10) -> List[ShadowCycleRecord]:
        """Get the most recent cycles."""
        return self.cycles[-count:] if self.cycles else []
    
    def get_cycles_in_window(self, window: MonitoringWindow) -> List[ShadowCycleRecord]:
        """Get cycles within a time window."""
        now = datetime.utcnow()
        
        window_hours = {
            MonitoringWindow.ONE_DAY: 24,
            MonitoringWindow.SEVEN_DAYS: 24 * 7,
            MonitoringWindow.THIRTY_DAYS: 24 * 30,
        }
        
        hours = window_hours.get(window, 24)
        cutoff = now - timedelta(hours=hours)
        
        return [c for c in self.cycles if c.timestamp >= cutoff]
    
    def compute_rolling_summary(self, window: MonitoringWindow) -> Dict[str, Any]:
        """Compute rolling summary for a window."""
        cycles = self.get_cycles_in_window(window)
        
        if not cycles:
            return {
                "total_cycles": 0,
                "avg_duration_ms": 0.0,
                "avg_signals": 0.0,
                "avg_recommendations": 0.0,
            }
        
        return {
            "total_cycles": len(cycles),
            "avg_duration_ms": sum(c.cycle_duration_ms for c in cycles) / len(cycles),
            "avg_signals": sum(c.signals_processed for c in cycles) / len(cycles),
            "avg_recommendations": sum(c.recommendations_generated for c in cycles) / len(cycles),
            "avg_execution_intents": sum(c.execution_intents_generated for c in cycles) / len(cycles),
            "avg_confidence": sum(c.confidence_score for c in cycles) / len(cycles),
            "avg_governance_load": sum(c.governance_load_score for c in cycles) / len(cycles),
            "first_cycle_time": cycles[0].timestamp if cycles else None,
            "last_cycle_time": cycles[-1].timestamp if cycles else None,
        }
    
    def detect_missing_cycles(self, expected_frequency_minutes: int = 60) -> bool:
        """Detect if cycles are missing."""
        if not self.last_cycle_time:
            return False
        
        now = datetime.utcnow()
        elapsed = (now - self.last_cycle_time).total_seconds() / 60
        
        return elapsed > expected_frequency_minutes
    
    def get_cycle_count(self) -> int:
        """Get total cycle count."""
        return self.cycle_counter
    
    def get_status(self) -> MonitoringStatus:
        """Get current monitoring status."""
        return self.current_status
    
    def reset(self) -> None:
        """Reset monitor state."""
        self.cycles = []
        self.cycle_counter = 0
        self.start_time = None
        self.last_cycle_time = None
        self.current_status = MonitoringStatus.STOPPED


def create_cycle_monitor() -> CycleMonitor:
    """Factory function to create a cycle monitor."""
    return CycleMonitor()
