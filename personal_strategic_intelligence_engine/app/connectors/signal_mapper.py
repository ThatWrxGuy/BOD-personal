"""Signal Mapper.

Normalizes external data into internal signal schema.
"""
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from app.connectors.connector_models import (
    ConnectorSignal,
    SignalPriority,
)


class SignalMapper:
    """Maps external data to internal signal format."""
    
    # Signal type mappings for different connectors
    CALENDAR_SIGNAL_TYPES = {
        "meeting_density": "workload_intensity",
        "deep_work_block": "focus_time_availability",
        "schedule_overload": "capacity_strain",
        "recovery_window": "rest_availability",
        "back_to_back": "cognitive_load",
        "travel_time": "time_drain",
    }
    
    FINANCE_SIGNAL_TYPES = {
        "liquidity_change": "cash_flow",
        "spending_spike": "expense_anomaly",
        "savings_trend": "savings_rate",
        "income_stability": "income_reliability",
        "bill_due": "obligation_upcoming",
        "investment_change": "asset_allocation",
    }
    
    TASKS_SIGNAL_TYPES = {
        "backlog_growth": "task_backlog",
        "overdue_task": "completion_delay",
        "priority_shift": "priority_change",
        "project_progress": "milestone_progress",
        "completion_rate": "productivity_rate",
        "blocker_identified": "impediment_detected",
    }
    
    HEALTH_SIGNAL_TYPES = {
        "sleep_quality": "rest_quality",
        "energy_level": "energy_status",
        "activity_level": "physical_activity",
        "stress_indicator": "stress_level",
        "mood_change": "emotional_state",
        "exercise_session": "fitness_activity",
    }
    
    def __init__(self):
        self._mappings = {
            "calendar": self.CALENDAR_SIGNAL_TYPES,
            "finance": self.FINANCE_SIGNAL_TYPES,
            "tasks": self.TASKS_SIGNAL_TYPES,
            "health": self.HEALTH_SIGNAL_TYPES,
        }
    
    def map_signal(
        self,
        connector_name: str,
        external_data: Dict[str, Any],
    ) -> Optional[ConnectorSignal]:
        """Map external data to internal signal format."""
        
        # Determine connector type from name
        connector_type = self._get_connector_type(connector_name)
        signal_type = external_data.get("type", external_data.get("signal_type", "unknown"))
        
        # Map to internal signal type - keep original if not found in mapping
        type_mapping = self._mappings.get(connector_type, {})
        internal_type = type_mapping.get(signal_type, signal_type)
        
        # Calculate priority based on magnitude
        magnitude = external_data.get("magnitude", external_data.get("value", 0.5))
        priority = self._calculate_priority(magnitude)
        
        # Calculate confidence
        confidence = external_data.get("confidence", 0.8)
        
        # Build the signal
        signal = ConnectorSignal(
            connector_name=connector_name,
            signal_type=internal_type,
            category=connector_type,
            priority=priority,
            title=external_data.get("title", signal_type),
            description=external_data.get("description"),
            value=magnitude,
            unit=external_data.get("unit"),
            source_id=external_data.get("id"),
            source_url=external_data.get("url"),
            external_timestamp=external_data.get("timestamp"),
            confidence=confidence,
            tags=external_data.get("tags", []),
            metadata=external_data.get("metadata", {}),
        )
        
        return signal
    
    def map_batch(
        self,
        connector_name: str,
        external_data_list: List[Dict[str, Any]],
    ) -> List[ConnectorSignal]:
        """Map multiple external data items to signals."""
        
        signals = []
        for data in external_data_list:
            signal = self.map_signal(connector_name, data)
            if signal:
                signals.append(signal)
        
        return signals
    
    def _get_connector_type(self, connector_name: str) -> str:
        """Determine connector type from name."""
        name_lower = connector_name.lower()
        
        if "calendar" in name_lower:
            return "calendar"
        elif "finance" in name_lower or "bank" in name_lower:
            return "finance"
        elif "task" in name_lower or "todo" in name_lower:
            return "tasks"
        elif "health" in name_lower or "fitbit" in name_lower or "sleep" in name_lower:
            return "health"
        else:
            return "custom"
    
    def _calculate_priority(self, magnitude: float) -> SignalPriority:
        """Calculate priority based on magnitude."""
        if magnitude >= 0.7:
            return SignalPriority.HIGH
        elif magnitude >= 0.4:
            return SignalPriority.MEDIUM
        else:
            return SignalPriority.LOW
    
    def validate_signal(self, signal: ConnectorSignal) -> bool:
        """Validate a mapped signal meets requirements."""
        
        # Check required fields
        if not signal.title:
            return False
        if not signal.signal_type:
            return False
        if not signal.category:
            return False
        
        # Validate value range
        if not -1.0 <= signal.value <= 1.0:
            return False
        
        # Validate confidence
        if not 0.0 <= signal.confidence <= 1.0:
            return False
        
        return True


# Global mapper instance
_signal_mapper: Optional[SignalMapper] = None


def get_signal_mapper() -> SignalMapper:
    """Get the global signal mapper instance."""
    global _signal_mapper
    if _signal_mapper is None:
        _signal_mapper = SignalMapper()
    return _signal_mapper
