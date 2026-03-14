"""Evolution Logger.

Persists intelligence evolution outputs.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

from app.intelligence.evolution.evolution_models import EvolutionSnapshot


class EvolutionLogger:
    """Logs intelligence evolution outputs."""
    
    def __init__(self, storage_path: Optional[str] = None):
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path(__file__).parent / "data"
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.patterns_file = self.storage_path / "discovered_patterns.jsonl"
        self.features_file = self.storage_path / "feature_importance.jsonl"
        self.optimizations_file = self.storage_path / "optimization_proposals.jsonl"
        self.snapshots_file = self.storage_path / "evolution_snapshots.jsonl"
    
    def log_pattern(self, pattern: Dict) -> None:
        """Log a discovered pattern."""
        with open(self.patterns_file, "a") as f:
            f.write(json.dumps(pattern) + "\n")
    
    def log_feature_importance(self, features: List[Dict]) -> None:
        """Log feature importance snapshot."""
        with open(self.features_file, "a") as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "features": features,
            }) + "\n")
    
    def log_optimization(self, proposal: Dict) -> None:
        """Log an optimization proposal."""
        with open(self.optimizations_file, "a") as f:
            f.write(json.dumps(proposal) + "\n")
    
    def log_snapshot(self, snapshot: EvolutionSnapshot) -> None:
        """Log an evolution snapshot."""
        with open(self.snapshots_file, "a") as f:
            f.write(json.dumps(snapshot.to_dict()) + "\n")
    
    def get_patterns(self, limit: int = 50) -> List[Dict]:
        """Get discovered patterns."""
        if not self.patterns_file.exists():
            return []
        
        patterns = []
        with open(self.patterns_file, "r") as f:
            for line in f:
                try:
                    patterns.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        return patterns[-limit:]
    
    def get_feature_history(self, limit: int = 10) -> List[Dict]:
        """Get feature importance history."""
        if not self.features_file.exists():
            return []
        
        history = []
        with open(self.features_file, "r") as f:
            for line in f:
                try:
                    history.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        return history[-limit:]
    
    def get_optimizations(self, status: Optional[str] = None) -> List[Dict]:
        """Get optimization proposals."""
        if not self.optimizations_file.exists():
            return []
        
        optimizations = []
        with open(self.optimizations_file, "r") as f:
            for line in f:
                try:
                    optimizations.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        if status:
            optimizations = [o for o in optimizations if o.get("status") == status]
        
        return optimizations
    
    def get_summary(self) -> Dict:
        """Get evolution system summary."""
        patterns = self.get_patterns(limit=100)
        optimizations = self.get_optimizations()
        pending = self.get_optimizations(status="pending")
        
        return {
            "total_patterns": len(patterns),
            "total_optimizations": len(optimizations),
            "pending_proposals": len(pending),
        }


def create_logger() -> EvolutionLogger:
    """Create a new evolution logger."""
    return EvolutionLogger()
