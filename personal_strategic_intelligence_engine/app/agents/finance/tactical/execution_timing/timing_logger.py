"""Timing Logger for Execution Timing Intelligence.

Logs timing decisions for review and learning.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from app.agents.finance.tactical.execution_timing.timing_models import ExecutionTimingDecision


class TimingLogger:
    """Logs execution timing decisions."""
    
    def __init__(self, storage_path: Optional[str] = None):
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path(__file__).parent / "data"
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.decisions_file = self.storage_path / "timing_decisions.jsonl"
        self.suppressions_file = self.storage_path / "timing_suppressions.jsonl"
    
    def log_decision(self, decision: ExecutionTimingDecision) -> dict:
        """Log a timing decision."""
        entry = decision.to_dict()
        
        with open(self.decisions_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return entry
    
    def log_suppression(self, signal_id: str, reason: str, timing_data: dict) -> dict:
        """Log a timing-based suppression."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "signal_id": signal_id,
            "reason": reason,
            "timing_data": timing_data,
        }
        
        with open(self.suppressions_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return entry
    
    def get_recent_decisions(self, limit: int = 100) -> List[dict]:
        """Get recent timing decisions."""
        if not self.decisions_file.exists():
            return []
        
        decisions = []
        with open(self.decisions_file, "r") as f:
            for line in f:
                try:
                    decisions.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        return decisions[-limit:]
    
    def get_suppression_summary(self) -> dict:
        """Get summary of timing suppressions."""
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
        
        return {"total": len(suppressions), "by_reason": by_reason}


def create_logger() -> TimingLogger:
    return TimingLogger()
