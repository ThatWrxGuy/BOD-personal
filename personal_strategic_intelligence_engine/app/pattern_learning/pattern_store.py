"""Pattern Store.

Persists learned patterns and statistics.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.pattern_learning.pattern_models import (
    ContextCluster,
    DecisionPattern,
    PatternLearningSummary,
    RecommendationFamily,
    StrategyEffectivenessScore,
)


class PatternStore:
    """Store for pattern learning data persistence."""
    
    def __init__(self, storage_path: Optional[str] = None):
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            # Default to data directory
            base_path = Path(__file__).parent.parent.parent / "data" / "patterns"
            self.storage_path = base_path
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self._patterns_file = self.storage_path / "patterns.json"
        self._clusters_file = self.storage_path / "clusters.json"
        self._rankings_file = self.storage_path / "rankings.json"
        self._families_file = self.storage_path / "families.json"
        
        # Initialize files if they don't exist
        for filepath in [self._patterns_file, self._clusters_file, 
                       self._rankings_file, self._families_file]:
            if not filepath.exists():
                self._write_json(filepath, [])
    
    def _read_json(self, filepath: Path) -> Any:
        """Read JSON from file."""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def _write_json(self, filepath: Path, data: Any) -> None:
        """Write JSON to file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    # Patterns
    
    def save_patterns(self, patterns: List[DecisionPattern]) -> None:
        """Save decision patterns."""
        data = [p.model_dump() for p in patterns]
        self._write_json(self._patterns_file, data)
    
    def load_patterns(self) -> List[DecisionPattern]:
        """Load decision patterns."""
        data = self._read_json(self._patterns_file) or []
        return [DecisionPattern(**p) for p in data]
    
    # Clusters
    
    def save_clusters(self, clusters: List[ContextCluster]) -> None:
        """Save context clusters."""
        data = [c.model_dump() for c in clusters]
        self._write_json(self._clusters_file, data)
    
    def load_clusters(self) -> List[ContextCluster]:
        """Load context clusters."""
        data = self._read_json(self._clusters_file) or []
        return [ContextCluster(**c) for c in data]
    
    # Rankings
    
    def save_rankings(self, rankings: Dict[str, List]) -> None:
        """Save strategy rankings."""
        data = {
            k: [r.model_dump() for r in v] 
            for k, v in rankings.items()
        }
        self._write_json(self._rankings_file, data)
    
    def load_rankings(self) -> Dict[str, List[StrategyEffectivenessScore]]:
        """Load strategy rankings."""
        data = self._read_json(self._rankings_file) or {}
        return {
            k: [StrategyEffectivenessScore(**r) for r in v]
            for k, v in data.items()
        }
    
    # Families
    
    def save_families(self, families: List[RecommendationFamily]) -> None:
        """Save recommendation families."""
        data = [f.model_dump() for f in families]
        self._write_json(self._families_file, data)
    
    def load_families(self) -> List[RecommendationFamily]:
        """Load recommendation families."""
        data = self._read_json(self._families_file) or []
        return [RecommendationFamily(**f) for f in data]
    
    # Summary
    
    def generate_summary(
        self,
        patterns: List[DecisionPattern],
        clusters: List[ContextCluster],
    ) -> PatternLearningSummary:
        """Generate pattern learning summary."""
        
        # Count patterns by family
        family_counts = {}
        for pattern in patterns:
            family = pattern.recommendation_family.value
            family_counts[family] = family_counts.get(family, 0) + 1
        
        # Calculate average success rate
        if patterns:
            avg_success = sum(p.success_rate for p in patterns) / len(patterns)
        else:
            avg_success = 0.0
        
        # Get domains
        domains = set()
        for pattern in patterns:
            domains.update(pattern.context.domains)
        
        return PatternLearningSummary(
            total_patterns=len(patterns),
            total_clusters=len(clusters),
            total_families=len(set(p.recommendation_family for p in patterns)),
            domains_covered=list(domains),
            avg_success_rate=avg_success,
            avg_confidence=0.5,  # Would calculate from patterns
        )


# Global store instance
_pattern_store: Optional[PatternStore] = None


def get_pattern_store() -> PatternStore:
    """Get the global pattern store instance."""
    global _pattern_store
    if _pattern_store is None:
        _pattern_store = PatternStore()
    return _pattern_store
