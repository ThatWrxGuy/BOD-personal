"""Structure Logger for Market Structure Intelligence.

Logs all market structure intelligence for review and learning.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from app.agents.finance.tactical.market_structure.structure_models import (
    MarketStructureSignal,
    DayTypeClassification,
)


class StructureLogger:
    """
    Logs market structure intelligence.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize logger."""
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path(__file__).parent / "data"
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.snapshots_file = self.storage_path / "structure_snapshots.jsonl"
        self.day_types_file = self.storage_path / "day_types.jsonl"
        self.sweeps_file = self.storage_path / "sweeps.jsonl"
        self.suppressions_file = self.storage_path / "structure_suppressions.jsonl"
    
    def log_snapshot(self, signal: MarketStructureSignal) -> dict:
        """Log a structure snapshot."""
        entry = {
            "timestamp": signal.timestamp.isoformat(),
            "price": signal.price,
            "session_open": signal.session_open,
            "session_high": signal.session_high,
            "session_low": signal.session_low,
            "vwap_state": signal.vwap_context.state.value,
            "vwap_distance_pct": signal.vwap_context.distance_pct,
            "day_type": signal.day_type.day_type.value,
            "day_type_confidence": signal.day_type.confidence,
            "volatility_state": signal.volatility_state.state.value,
            "directional_bias": signal.directional_bias,
            "continuation_probability": signal.continuation_probability,
            "reversal_probability": signal.reversal_probability,
            "chop_probability": signal.chop_probability,
            "structure_quality_score": signal.structure_quality_score,
            "tactical_suitability_score": signal.tactical_suitability_score,
            "suppression_flags": signal.suppression_flags,
        }
        
        with open(self.snapshots_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return entry
    
    def log_day_type_change(
        self,
        old_type: str,
        new_type: str,
        confidence: float,
    ) -> dict:
        """Log a day type change."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "old_type": old_type,
            "new_type": new_type,
            "confidence": confidence,
        }
        
        with open(self.day_types_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return entry
    
    def log_sweep(self, sweep) -> dict:
        """Log a liquidity sweep event."""
        entry = sweep.to_dict()
        
        with open(self.sweeps_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return entry
    
    def log_suppression(
        self,
        signal_id: str,
        reason: str,
        structure_snapshot: dict,
    ) -> dict:
        """Log a structure-based suppression."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "signal_id": signal_id,
            "reason": reason,
            "structure_snapshot": structure_snapshot,
        }
        
        with open(self.suppressions_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return entry
    
    def get_recent_snapshots(self, limit: int = 100) -> List[dict]:
        """Get recent structure snapshots."""
        if not self.snapshots_file.exists():
            return []
        
        snapshots = []
        with open(self.snapshots_file, "r") as f:
            for line in f:
                try:
                    snapshots.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        return snapshots[-limit:]
    
    def get_day_type_history(self, limit: int = 100) -> List[dict]:
        """Get day type change history."""
        if not self.day_types_file.exists():
            return []
        
        history = []
        with open(self.day_types_file, "r") as f:
            for line in f:
                try:
                    history.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        return history[-limit:]
    
    def get_suppression_summary(self) -> dict:
        """Get summary of structure-based suppressions."""
        if not self.suppressions_file.exists():
            return {"total": 0, "by_reason": {}}
        
        suppressions = []
        with open(self.suppressions_file, "r") as f:
            for line in f:
                try:
                    suppressions.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        by_reason = {}
        for s in suppressions:
            reason = s.get("reason", "unknown")
            by_reason[reason] = by_reason.get(reason, 0) + 1
        
        return {
            "total": len(suppressions),
            "by_reason": by_reason,
        }


def create_logger() -> StructureLogger:
    """Factory function to create logger."""
    return StructureLogger()
