"""Learning Logger.

Persists learning outputs for replay analysis and dashboard display.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

from app.agents.finance.learning.learning_models import (
    SignalOutcomeRecord,
    FeaturePerformanceReport,
    ConfidenceCalibrationReport,
    SuppressionEffectivenessReport,
    RegimePerformanceReport,
    TimingPerformanceReport,
    ScoreOptimizationProposal,
    TacticalLearningSnapshot,
)


class LearningLogger:
    """Logs learning outputs for analysis."""
    
    def __init__(self, storage_path: Optional[str] = None):
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path(__file__).parent / "data"
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.outcomes_file = self.storage_path / "signal_outcomes.jsonl"
        self.snapshots_file = self.storage_path / "learning_snapshots.jsonl"
        self.proposals_file = self.storage_path / "optimization_proposals.jsonl"
    
    def log_signal_outcome(self, record: SignalOutcomeRecord) -> None:
        """Log a signal outcome record."""
        with open(self.outcomes_file, "a") as f:
            f.write(json.dumps(record.to_dict()) + "\n")
    
    def log_snapshot(self, snapshot: TacticalLearningSnapshot) -> None:
        """Log a learning snapshot."""
        with open(self.snapshots_file, "a") as f:
            f.write(json.dumps(snapshot.to_dict()) + "\n")
    
    def log_proposal(self, proposal: ScoreOptimizationProposal) -> None:
        """Log an optimization proposal."""
        with open(self.proposals_file, "a") as f:
            f.write(json.dumps(proposal.to_dict()) + "\n")
    
    def get_signal_outcomes(self, limit: int = 100) -> List[Dict]:
        """Get recent signal outcomes."""
        if not self.outcomes_file.exists():
            return []
        
        outcomes = []
        with open(self.outcomes_file, "r") as f:
            for line in f:
                try:
                    outcomes.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        return outcomes[-limit:]
    
    def get_snapshots(self, limit: int = 10) -> List[Dict]:
        """Get recent learning snapshots."""
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
    
    def get_proposals(self, status: Optional[str] = None) -> List[Dict]:
        """Get optimization proposals."""
        if not self.proposals_file.exists():
            return []
        
        proposals = []
        with open(self.proposals_file, "r") as f:
            for line in f:
                try:
                    proposals.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        if status:
            proposals = [p for p in proposals if p.get("status") == status]
        
        return proposals
    
    def get_summary(self) -> Dict:
        """Get learning system summary."""
        outcomes = self.get_signal_outcomes(limit=1000)
        snapshots = self.get_snapshots(limit=10)
        pending_proposals = self.get_proposals(status="pending")
        
        resolved = [o for o in outcomes if o.get("outcome") != "pending"]
        wins = [o for o in resolved if o.get("outcome") == "win"]
        
        return {
            "total_signals": len(outcomes),
            "resolved_signals": len(resolved),
            "win_count": len(wins),
            "win_rate": len(wins) / len(resolved) * 100 if resolved else 0,
            "snapshots_count": len(snapshots),
            "pending_proposals": len(pending_proposals),
        }


def create_logger() -> LearningLogger:
    """Create a new learning logger."""
    return LearningLogger()
