"""Context Clusterer.

Groups similar decision contexts.
"""
from typing import Any, Dict, List, Optional
from collections import defaultdict

from app.pattern_learning.pattern_models import (
    ContextCluster,
    DecisionContextProfile,
    DecisionPattern,
)


class ContextClusterer:
    """Groups similar decision contexts into clusters."""
    
    # Threshold for similarity
    SIMILARITY_THRESHOLD = 0.7
    
    # Known cluster definitions
    KNOWN_CLUSTERS = {
        "workload_overload": {
            "signals": ["schedule_overload", "meeting_density", "task_backlog"],
            "domain": "calendar",
        },
        "financial_stress": {
            "signals": ["liquidity_change", "spending_spike", "bill_due"],
            "domain": "finance",
        },
        "burnout_risk": {
            "signals": ["sleep_quality", "energy_level", "stress_indicator"],
            "domain": "health",
        },
        "productivity_stagnation": {
            "signals": ["completion_rate", "project_progress", "backlog_growth"],
            "domain": "tasks",
        },
    }
    
    def __init__(self):
        self._clusters: Dict[str, ContextCluster] = {}
        self._cluster_assignments: Dict[str, str] = {}
    
    def cluster_contexts(
        self,
        patterns: List[DecisionPattern],
    ) -> List[ContextCluster]:
        """Cluster decision contexts."""
        
        # Group patterns by known clusters first
        for name, definition in self.KNOWN_CLUSTERS.items():
            cluster = ContextCluster(
                cluster_id=f"cluster_{name}",
                cluster_name=name.replace("_", " ").title(),
                typical_signals={s: 0.5 for s in definition["signals"]},
                primary_domain=definition["domain"],
            )
            self._clusters[name] = cluster
        
        # Assign patterns to clusters
        for pattern in patterns:
            cluster_id = self._assign_to_cluster(pattern.context)
            if cluster_id:
                self._clusters[cluster_id].pattern_ids.append(pattern.pattern_id)
                self._clusters[cluster_id].member_count += 1
                self._cluster_assignments[pattern.pattern_id] = cluster_id
        
        return list(self._clusters.values())
    
    def _assign_to_cluster(
        self,
        context: DecisionContextProfile,
    ) -> Optional[str]:
        """Assign a context to the best matching cluster."""
        
        best_match = None
        best_score = 0.0
        
        for cluster_id, cluster in self.KNOWN_CLUSTERS.items():
            score = self._calculate_similarity(context, cluster)
            
            if score > best_score and score >= self.SIMILARITY_THRESHOLD:
                best_score = score
                best_match = cluster_id
        
        return best_match
    
    def _calculate_similarity(
        self,
        context: DecisionContextProfile,
        cluster_def: Dict[str, Any],
    ) -> float:
        """Calculate similarity between context and cluster definition."""
        
        # Check domain match
        if context.domains and cluster_def["domain"] in context.domains:
            domain_bonus = 0.3
        else:
            domain_bonus = 0.0
        
        # Check signal overlap
        cluster_signals = set(cluster_def["signals"])
        context_signals = set(context.signal_signatures.keys())
        
        if cluster_signals:
            overlap = len(cluster_signals & context_signals) / len(cluster_signals)
        else:
            overlap = 0.0
        
        return overlap + domain_bonus
    
    def get_cluster(self, cluster_id: str) -> Optional[ContextCluster]:
        """Get a cluster by ID."""
        return self._clusters.get(cluster_id)
    
    def get_all_clusters(self) -> List[ContextCluster]:
        """Get all clusters."""
        return list(self._clusters.values())
    
    def get_cluster_for_pattern(self, pattern_id: str) -> Optional[str]:
        """Get the cluster ID for a pattern."""
        return self._cluster_assignments.get(pattern_id)
    
    def get_patterns_in_cluster(
        self,
        cluster_id: str,
        all_patterns: List[DecisionPattern],
    ) -> List[DecisionPattern]:
        """Get all patterns in a cluster."""
        return [
            p for p in all_patterns
            if self._cluster_assignments.get(p.pattern_id) == cluster_id
        ]
    
    def create_new_cluster(
        self,
        context: DecisionContextProfile,
        patterns: List[DecisionPattern],
    ) -> ContextCluster:
        """Create a new cluster for unmatched contexts."""
        
        cluster_id = f"cluster_custom_{len(self._clusters)}"
        
        # Use context signals as typical
        typical_signals = context.signal_signatures if context.signal_signatures else {}
        
        primary_domain = context.domains[0] if context.domains else "general"
        
        cluster = ContextCluster(
            cluster_id=cluster_id,
            cluster_name=f"Custom Cluster {len(self._clusters)}",
            typical_signals=typical_signals,
            primary_domain=primary_domain,
            pattern_ids=[p.pattern_id for p in patterns],
            member_count=len(patterns),
        )
        
        self._clusters[cluster_id] = cluster
        
        return cluster


# Global clusterer instance
_context_clusterer: Optional[ContextClusterer] = None


def get_context_clusterer() -> ContextClusterer:
    """Get the global context clusterer instance."""
    global _context_clusterer
    if _context_clusterer is None:
        _context_clusterer = ContextClusterer()
    return _context_clusterer
