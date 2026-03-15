"""Memory Query Engine.

Exposes memory retrieval capabilities.
"""
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.strategic_memory.memory_graph import StrategicMemoryGraph
from app.strategic_memory.memory_models import (
    MemoryQuery,
    MemoryQueryResult,
    EdgeCategory,
    NodeCategory,
)


class MemoryQueryEngine:
    """Exposes memory retrieval capabilities."""
    
    def __init__(self, graph: StrategicMemoryGraph):
        self.graph = graph
    
    def query(self, query: MemoryQuery) -> MemoryQueryResult:
        """Execute a memory query."""
        start_time = time.time()
        
        results = []
        
        if query.query_type == "what_follows":
            results = self._query_what_follows(query)
        elif query.query_type == "what_precedes":
            results = self._query_what_precedes(query)
        elif query.query_type == "similar_context":
            results = self._query_similar_context(query)
        elif query.query_type == "chain":
            results = self._query_chain(query)
        elif query.query_type == "intervention":
            results = self._query_intervention(query)
        elif query.query_type == "domain":
            results = self._query_by_domain(query)
        else:
            results = self._query_general(query)
        
        execution_time = (time.time() - start_time) * 1000
        
        return MemoryQueryResult(
            query_id=query.query_id,
            results=results,
            total_results=len(results),
            execution_time_ms=execution_time,
            evidence_summary=self._build_evidence_summary(results),
        )
    
    def _query_what_follows(self, query: MemoryQuery) -> List[Dict[str, Any]]:
        """Find what typically follows a given signal or condition."""
        results = []
        
        for node_id in query.node_ids:
            # Get outgoing edges
            edges = self.graph.get_outgoing_edges(node_id)
            
            # Filter by relationship types if specified
            if query.relationship_types:
                edges = [e for e in edges if e.relationship.value in query.relationship_types]
            
            for edge in edges:
                target = self.graph.get_node(edge.target_node_id)
                if target:
                    results.append({
                        "source_node": self._node_summary(node_id),
                        "target_node": self._node_summary(edge.target_node_id),
                        "relationship": edge.relationship.value,
                        "confidence": edge.confidence,
                        "evidence_count": edge.evidence_count,
                        "avg_time_gap_hours": edge.avg_time_gap_hours,
                    })
        
        return results[:query.max_results]
    
    def _query_what_precedes(self, query: MemoryQuery) -> List[Dict[str, Any]]:
        """Find what typically precedes a given signal or condition."""
        results = []
        
        for node_id in query.node_ids:
            # Get incoming edges
            edges = self.graph.get_incoming_edges(node_id)
            
            for edge in edges:
                source = self.graph.get_node(edge.source_node_id)
                if source:
                    results.append({
                        "source_node": self._node_summary(edge.source_node_id),
                        "target_node": self._node_summary(node_id),
                        "relationship": edge.relationship.value,
                        "confidence": edge.confidence,
                        "evidence_count": edge.evidence_count,
                    })
        
        return results[:query.max_results]
    
    def _query_similar_context(self, query: MemoryQuery) -> List[Dict[str, Any]]:
        """Find similar historical contexts."""
        results = []
        
        for node_id in query.node_ids:
            # Get neighbors
            neighbors = self.graph.get_neighbors(node_id)
            
            for neighbor in neighbors:
                edge = self._find_edge(node_id, neighbor.node_id)
                
                if edge:
                    results.append({
                        "context_node": self._node_summary(node_id),
                        "related_node": self._node_summary(neighbor.node_id),
                        "relationship": edge.relationship.value,
                        "confidence": edge.confidence,
                    })
        
        return results[:query.max_results]
    
    def _query_chain(self, query: MemoryQuery) -> List[Dict[str, Any]]:
        """Find chains involving given nodes."""
        results = []
        
        for node_id in query.node_ids:
            # Find paths from this node
            for other_id in query.node_ids:
                if node_id != other_id:
                    paths = self.graph.find_path(node_id, other_id, max_depth=4)
                    
                    for path in paths:
                        results.append({
                            "chain": path,
                            "length": len(path),
                        })
        
        return results[:query.max_results]
    
    def _query_intervention(self, query: MemoryQuery) -> List[Dict[str, Any]]:
        """Find historically effective interventions."""
        results = []
        
        # Find intervention nodes
        all_nodes = self.graph.get_all_nodes()
        
        for node in all_nodes:
            if node.node_type == NodeCategory.INTERVENTION:
                # Find outcomes
                edges = self.graph.get_outgoing_edges(node.node_id)
                
                for edge in edges:
                    if edge.relationship in [EdgeCategory.LED_TO, EdgeCategory.STABILIZES]:
                        target = self.graph.get_node(edge.target_node_id)
                        if target:
                            results.append({
                                "intervention": self._node_summary(node.node_id),
                                "outcome": self._node_summary(edge.target_node_id),
                                "relationship": edge.relationship.value,
                                "confidence": edge.confidence,
                                "evidence_count": edge.evidence_count,
                            })
        
        return results[:query.max_results]
    
    def _query_by_domain(self, query: MemoryQuery) -> List[Dict[str, Any]]:
        """Query nodes by domain."""
        results = []
        
        for domain in query.domains:
            nodes = self.graph.get_nodes_by_domain(domain)
            
            for node in nodes:
                results.append(self._node_summary(node.node_id))
        
        return results[:query.max_results]
    
    def _query_general(self, query: MemoryQuery) -> List[Dict[str, Any]]:
        """General query across all nodes and edges."""
        results = []
        
        # Get all nodes
        all_nodes = self.graph.get_all_nodes()
        
        for node in all_nodes:
            if query.min_evidence_count and node.occurrence_count < query.min_evidence_count:
                continue
            
            results.append(self._node_summary(node.node_id))
        
        return results[:query.max_results]
    
    def _find_edge(self, source_id: str, target_id: str):
        """Find an edge between two nodes."""
        for edge in self.graph.get_outgoing_edges(source_id):
            if edge.target_node_id == target_id:
                return edge
        return None
    
    def _node_summary(self, node_id: str) -> Dict[str, Any]:
        """Get a summary of a node."""
        node = self.graph.get_node(node_id)
        
        if not node:
            return {"node_id": node_id, "label": "Unknown"}
        
        return {
            "node_id": node.node_id,
            "label": node.label,
            "type": node.node_type.value,
            "domain": node.domain,
            "occurrence_count": node.occurrence_count,
        }
    
    def _build_evidence_summary(self, results: List[Dict]) -> Dict[str, Any]:
        """Build an evidence summary for results."""
        if not results:
            return {"total_evidence": 0}
        
        total_evidence = sum(r.get("evidence_count", 1) for r in results)
        avg_confidence = sum(r.get("confidence", 0) for r in results) / len(results)
        
        return {
            "total_evidence": total_evidence,
            "avg_confidence": avg_confidence,
            "result_count": len(results),
        }


# Factory function
def create_memory_query_engine(graph: StrategicMemoryGraph) -> MemoryQueryEngine:
    """Create a memory query engine with the given graph."""
    return MemoryQueryEngine(graph)
