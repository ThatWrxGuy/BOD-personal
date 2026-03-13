"""Outcome linker for connecting recommendations with later signals."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.learning.outcome_models import ObservationWindow
from app.signal_ingestion.signal_models import NormalizedSignal

logger = logging.getLogger(__name__)


class OutcomeLinker:
    """Links recommendations with later observed signals."""

    def __init__(self):
        # Domain to signal type mapping
        self._domain_signal_map = {
            "health": ["health", "performance"],
            "wealth": ["wealth", "performance"],
            "career": ["career", "performance"],
            "relationships": ["relationships", "performance"],
            "learning": ["learning", "performance"],
        }

    def link_outcome(
        self,
        recommendation_id: str,
        domain: str,
        baseline_timestamp: datetime,
        window_hours: int = 168,
    ) -> Optional[ObservationWindow]:
        """Create observation window for outcome tracking."""
        
        start_time = baseline_timestamp
        end_time = baseline_timestamp + timedelta(hours=window_hours)

        window = ObservationWindow(
            window_type="standard",
            duration_hours=window_hours,
            start_time=start_time,
            end_time=end_time,
        )

        logger.info(
            f"Created observation window for {recommendation_id}: "
            f"{window_hours}h ending at {end_time}"
        )

        return window

    def find_followup_signals(
        self,
        domain: str,
        after_timestamp: datetime,
        signal_store=None,
    ) -> List[Dict[str, Any]]:
        """Find signals relevant to a domain after a timestamp."""
        
        # Get relevant signal types for the domain
        signal_types = self._domain_signal_map.get(domain, [domain])
        
        # In a real implementation, this would query the signal store
        # For now, return empty list (would be populated from signal_ingestion)
        followup_signals = []
        
        logger.debug(
            f"Looking for follow-up signals for domain {domain} "
            f"after {after_timestamp}"
        )

        return followup_signals

    def compare_states(
        self,
        baseline_state: Dict[str, Any],
        followup_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Compare baseline and follow-up states."""
        
        changes = {}
        
        # Compare each metric
        all_keys = set(baseline_state.keys()) | set(followup_state.keys())
        
        for key in all_keys:
            baseline = baseline_state.get(key, 0)
            followup = followup_state.get(key, 0)
            
            if isinstance(baseline, (int, float)) and isinstance(followup, (int, float)):
                change = followup - baseline
                changes[key] = {
                    "baseline": baseline,
                    "followup": followup,
                    "change": change,
                    "percent_change": (change / baseline * 100) if baseline != 0 else 0,
                }

        # Determine overall direction
        positive_count = sum(
            1 for c in changes.values() 
            if isinstance(c.get("change"), (int, float)) and c["change"] > 0
        )
        negative_count = sum(
            1 for c in changes.values() 
            if isinstance(c.get("change"), (int, float)) and c["change"] < 0
        )

        if positive_count > negative_count:
            direction = "positive"
        elif negative_count > positive_count:
            direction = "negative"
        else:
            direction = "neutral"

        return {
            "changes": changes,
            "direction": direction,
            "positive_metrics": positive_count,
            "negative_metrics": negative_count,
        }

    def build_evidence_bundle(
        self,
        baseline_state: Dict[str, Any],
        followup_signals: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Build evidence bundle for outcome evaluation."""
        
        # Extract follow-up state from signals
        followup_state = {}
        for signal in followup_signals:
            if "normalized_payload" in signal:
                followup_state.update(signal["normalized_payload"])

        # Compare states
        comparison = self.compare_states(baseline_state, followup_state)

        return {
            "baseline": baseline_state,
            "followup": followup_state,
            "comparison": comparison,
            "signal_count": len(followup_signals),
        }

    def register_domain_mapping(
        self,
        domain: str,
        signal_types: List[str],
    ):
        """Register a custom domain to signal type mapping."""
        self._domain_signal_map[domain] = signal_types
        logger.info(f"Registered domain mapping: {domain} -> {signal_types}")


# Global linker instance
_linker: Optional[OutcomeLinker] = None


def get_outcome_linker() -> OutcomeLinker:
    """Get the global outcome linker instance."""
    global _linker
    if _linker is None:
        _linker = OutcomeLinker()
    return _linker
