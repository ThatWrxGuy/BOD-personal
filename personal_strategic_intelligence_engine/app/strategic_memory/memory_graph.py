"""Memory Graph.

Maintains the strategic memory graph structure.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from app.strategic_memory.memory_models import (
    MemoryEdge,
    MemoryGraphSnapshot,
    MemoryNode,
    NodeCategory,
    EdgeCategory,
)


class StrategicMemoryGraph:
    """Maintains the strategic memory graph."""
    
    def __init__(self):
        self._nodes: Dict[str, MemoryNode] = {}
        self._edges: Dict[str, MemoryEdge] = {}
        
        # Indexes for fast lookup
        self._nodes_by_type: Dict[NodeCategory, Set[str]] = {}
        self._nodes_by_domain: Dict[str, Set[str]] = {}
        self._edges_by_type: Dict[EdgeCategory, Set[str]] = {}
        self._edges_by_source: Dict[str, Set[str]] = {}
        self._edges_by_target: Dict[str, Set[str]] = {}
    
    # Node Operations
    
    def add_node(self, node: MemoryNode) -> None:
        """Add or update a node in the graph."""
        existing = self._nodes.get(node.node_id)
        
        if existing:
            # Update existing node
            existing.occurrence_count += 1
            existing.last_seen = datetime.utcnow()
            existing.source_record_ids = list(set(existing.source_record_ids + node.source_record_ids))
        else:
            # Add new node
            self._nodes[node.node_id] = node
            self._index_node(node)
    
    def get_node(self, node_id: str) -> Optional[MemoryNode]:
        """Get a node by ID."""
        return self._nodes.get(node_id)
    
    def get_nodes_by_type(self, node_type: NodeCategory) -> List[MemoryNode]:
        """Get all nodes of a given type."""
        node_ids = self._nodes_by_type.get(node_type, set())
        return [self._nodes[nid] for nid in node_ids if nid in self._nodes]
    
    def get_nodes_by_domain(self, domain: str) -> List[MemoryNode]:
        """Get all nodes in a given domain."""
        node_ids = self._nodes_by_domain.get(domain, set())
        return [self._nodes[nid] for nid in node_ids if nid in self._nodes]
    
    def get_all_nodes(self) -> List[MemoryNode]:
        """Get all nodes."""
        return list(self._nodes.values())
    
    # Edge Operations
    
    def add_edge(self, edge: MemoryEdge) -> None:
        """Add or update an edge in the graph."""
        existing = self._edges.get(edge.edge_id)
        
        if existing:
            # Update existing edge
            existing.evidence_count += 1
            existing.last_seen = datetime.utcnow()
            existing.supporting_record_ids = list(set(existing.supporting_record_ids + edge.supporting_record_ids))
            
            # Recalculate average time gap
            if edge.avg_time_gap_hours > 0:
                old_total = existing.avg_time_gap_hours * (existing.evidence_count - 1)
                existing.avg_time_gap_hours = (old_total + edge.avg_time_gap_hours) / existing.evidence_count
        else:
            # Add new edge
            self._edges[edge.edge_id] = edge
            self._index_edge(edge)
    
    def get_edge(self, edge_id: str) -> Optional[MemoryEdge]:
        """Get an edge by ID."""
        return self._edges.get(edge_id)
    
    def get_edges_by_type(self, edge_type: EdgeCategory) -> List[MemoryEdge]:
        """Get all edges of a given type."""
        edge_ids = self._edges_by_type.get(edge_type, set())
        return [self._edges[eid] for eid in edge_ids if eid in self._edges]
    
    def get_outgoing_edges(self, node_id: str) -> List[MemoryEdge]:
        """Get all edges leaving a node."""
        edge_ids = self._edges_by_source.get(node_id, set())
        return [self._edges[eid] for eid in edge_ids if eid in self._edges]
    
    def get_incoming_edges(self, node_id: str) -> List[MemoryEdge]:
        """Get all edges entering a node."""
        edge_ids = self._edges_by_target.get(node_id, set())
        return [self._edges[eid] for eid in edge_ids if eid in self._edges]
    
    def get_all_edges(self) -> List[MemoryEdge]:
        """Get all edges."""
        return list(self._edges.values())
    
    # Graph Operations
    
    def get_neighbors(self, node_id: str) -> List[MemoryNode]:
        """Get all neighboring nodes (both directions)."""
        neighbors = []
        
        # Outgoing
        for edge in self.get_outgoing_edges(node_id):
            neighbor = self._nodes.get(edge.target_node_id)
            if neighbor:
                neighbors.append(neighbor)
        
        # Incoming
        for edge in self.get_incoming_edges(node_id):
            neighbor = self._nodes.get(edge.source_node_id)
            if neighbor:
                neighbors.append(neighbor)
        
        return neighbors
    
    def find_path(self, start_id: str, end_id: str, max_depth: int = 3) -> List[List[str]]:
        """Find paths between two nodes."""
        paths = []
        
        def dfs(current: str, path: List[str], depth: int):
            if depth > max_depth:
                return
            if current == end_id:
                paths.append(path + [current])
                return
            
            for edge in self.get_outgoing_edges(current):
                if edge.target_node_id not in path:
                    dfs(edge.target_node_id, path + [current], depth + 1)
        
        dfs(start_id, [], 0)
        return paths
    
    def get_subgraph(self, node_ids: List[str]) -> 'StrategicMemoryGraph':
        """Extract a subgraph containing specified nodes."""
        subgraph = StrategicMemoryGraph()
        
        for node_id in node_ids:
            node = self._nodes.get(node_id)
            if node:
                subgraph.add_node(node)
        
        for edge in self._edges.values():
            if edge.source_node_id in node_ids and edge.target_node_id in node_ids:
                subgraph.add_edge(edge)
        
        return subgraph
    
    def get_snapshot(self) -> MemoryGraphSnapshot:
        """Get a snapshot of the current graph state."""
        domains = set()
        for node in self._nodes.values():
            domains.add(node.domain)
        
        return MemoryGraphSnapshot(
            snapshot_id=f"snap_{datetime.utcnow().timestamp()}",
            node_count=len(self._nodes),
            edge_count=len(self._edges),
            domains_covered=list(domains),
            created_at=datetime.utcnow(),
        )
    
    # Indexing
    
    def _index_node(self, node: MemoryNode) -> None:
        """Index a node for fast lookup."""
        # By type
        if node.node_type not in self._nodes_by_type:
            self._nodes_by_type[node.node_type] = set()
        self._nodes_by_type[node.node_type].add(node.node_id)
        
        # By domain
        if node.domain not in self._nodes_by_domain:
            self._nodes_by_domain[node.domain] = set()
        self._nodes_by_domain[node.domain].add(node.node_id)
    
    def _index_edge(self, edge: MemoryEdge) -> None:
        """Index an edge for fast lookup."""
        # By type
        if edge.relationship not in self._edges_by_type:
            self._edges_by_type[edge.relationship] = set()
        self._edges_by_type[edge.relationship].add(edge.edge_id)
        
        # By source
        if edge.source_node_id not in self._edges_by_source:
            self._edges_by_source[edge.source_node_id] = set()
        self._edges_by_source[edge.source_node_id].add(edge.edge_id)
        
        # By target
        if edge.target_node_id not in self._edges_by_target:
            self._edges_by_target[edge.target_node_id] = set()
        self._edges_by_target[edge.target_node_id].add(edge.edge_id)
    
    # Statistics
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        return {
            "total_nodes": len(self._nodes),
            "total_edges": len(self._edges),
            "nodes_by_type": {
                k.value: len(v) for k, v in self._nodes_by_type.items()
            },
            "nodes_by_domain": {
                k: len(v) for k, v in self._nodes_by_domain.items()
            },
            "edges_by_relationship": {
                k.value: len(v) for k, v in self._edges_by_type.items()
            },
        }


# Global graph instance
_strategic_memory_graph: Optional[StrategicMemoryGraph] = None


def get_strategic_memory_graph() -> StrategicMemoryGraph:
    """Get the global strategic memory graph instance."""
    global _strategic_memory_graph
    if _strategic_memory_graph is None:
        _strategic_memory_graph = StrategicMemoryGraph()
    return _strategic_memory_graph
