"""Memory Store.

Persists memory graph data and snapshots.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.strategic_memory.memory_models import (
    MemoryNode,
    MemoryEdge,
    StrategicPattern,
    RecurringChain,
    MemoryGraphSnapshot,
    MemorySummary,
)


class MemoryStore:
    """Store for memory graph data persistence."""
    
    def __init__(self, storage_path: Optional[str] = None):
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            # Default to data directory
            base_path = Path(__file__).parent.parent.parent / "data" / "memory"
            self.storage_path = base_path
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self._nodes_file = self.storage_path / "nodes.json"
        self._edges_file = self.storage_path / "edges.json"
        self._patterns_file = self.storage_path / "patterns.json"
        self._chains_file = self.storage_path / "chains.json"
        self._snapshots_file = self.storage_path / "snapshots.json"
        
        # Initialize files if they don't exist
        for filepath in [self._nodes_file, self._edges_file, self._patterns_file, 
                        self._chains_file, self._snapshots_file]:
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
    
    # Nodes
    
    def save_nodes(self, nodes: List[MemoryNode]) -> None:
        """Save nodes to storage."""
        data = [n.model_dump() for n in nodes]
        self._write_json(self._nodes_file, data)
    
    def load_nodes(self) -> List[MemoryNode]:
        """Load nodes from storage."""
        data = self._read_json(self._nodes_file) or []
        return [MemoryNode(**n) for n in data]
    
    # Edges
    
    def save_edges(self, edges: List[MemoryEdge]) -> None:
        """Save edges to storage."""
        data = [e.model_dump() for e in edges]
        self._write_json(self._edges_file, data)
    
    def load_edges(self) -> List[MemoryEdge]:
        """Load edges from storage."""
        data = self._read_json(self._edges_file) or []
        return [MemoryEdge(**e) for e in data]
    
    # Patterns
    
    def save_patterns(self, patterns: List[StrategicPattern]) -> None:
        """Save patterns to storage."""
        data = [p.model_dump() for p in patterns]
        self._write_json(self._patterns_file, data)
    
    def load_patterns(self) -> List[StrategicPattern]:
        """Load patterns from storage."""
        data = self._read_json(self._patterns_file) or []
        return [StrategicPattern(**p) for p in data]
    
    # Chains
    
    def save_chains(self, chains: List[RecurringChain]) -> None:
        """Save chains to storage."""
        data = [c.model_dump() for c in chains]
        self._write_json(self._chains_file, data)
    
    def load_chains(self) -> List[RecurringChain]:
        """Load chains from storage."""
        data = self._read_json(self._chains_file) or []
        return [RecurringChain(**c) for c in data]
    
    # Snapshots
    
    def save_snapshot(self, snapshot: MemoryGraphSnapshot) -> None:
        """Save a graph snapshot."""
        snapshots = self._read_json(self._snapshots_file) or []
        snapshots.append(snapshot.model_dump())
        
        # Keep only last 50
        if len(snapshots) > 50:
            snapshots = snapshots[-50:]
        
        self._write_json(self._snapshots_file, snapshots)
    
    def load_snapshots(self, limit: int = 10) -> List[MemoryGraphSnapshot]:
        """Load recent snapshots."""
        data = self._read_json(self._snapshots_file) or []
        return [MemoryGraphSnapshot(**s) for s in data[-limit:]]
    
    # Summary
    
    def generate_summary(self, nodes: List[MemoryNode], edges: List[MemoryEdge]) -> MemorySummary:
        """Generate a memory summary."""
        
        # Count by category
        nodes_by_category = {}
        nodes_by_domain = {}
        
        for node in nodes:
            cat = node.node_type.value
            nodes_by_category[cat] = nodes_by_category.get(cat, 0) + 1
            
            domain = node.domain
            nodes_by_domain[domain] = nodes_by_domain.get(domain, 0) + 1
        
        # Count by relationship
        edges_by_relationship = {}
        for edge in edges:
            rel = edge.relationship.value
            edges_by_relationship[rel] = edges_by_relationship.get(rel, 0) + 1
        
        return MemorySummary(
            total_nodes=len(nodes),
            total_edges=len(edges),
            nodes_by_category=nodes_by_category,
            nodes_by_domain=nodes_by_domain,
            edges_by_relationship=edges_by_relationship,
            generated_at=datetime.utcnow(),
        )


# Global store instance
_memory_store: Optional[MemoryStore] = None


def get_memory_store() -> MemoryStore:
    """Get the global memory store instance."""
    global _memory_store
    if _memory_store is None:
        _memory_store = MemoryStore()
    return _memory_store
