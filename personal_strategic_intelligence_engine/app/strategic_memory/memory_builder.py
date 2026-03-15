"""Memory Builder.

Builds memory graph from historical records.
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.strategic_memory.memory_graph import StrategicMemoryGraph
from app.strategic_memory.memory_models import (
    MemoryNode,
    MemoryEdge,
    NodeCategory,
    EdgeCategory,
)
from app.strategic_memory.relationship_extractor import get_relationship_extractor

logger = logging.getLogger(__name__)


class MemoryBuilder:
    """Builds memory graph from historical records."""
    
    def __init__(self, graph: StrategicMemoryGraph):
        self.graph = graph
        self.extractor = get_relationship_extractor()
    
    def build_from_records(
        self,
        signals: Optional[List[Dict[str, Any]]] = None,
        recommendations: Optional[List[Dict[str, Any]]] = None,
        outcomes: Optional[List[Dict[str, Any]]] = None,
        state_changes: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Build memory graph from historical records."""
        
        logger.info("Building memory graph from records...")
        
        # Add signal nodes
        if signals:
            self._add_signal_nodes(signals)
        
        # Add recommendation nodes
        if recommendations:
            self._add_recommendation_nodes(recommendations)
        
        # Add outcome nodes
        if outcomes:
            self._add_outcome_nodes(outcomes)
        
        # Extract relationships
        if signals:
            edges = self.extractor.extract_from_signal_sequence(signals)
            for edge in edges:
                self.graph.add_edge(edge)
        
        if recommendations and outcomes:
            edges = self.extractor.extract_from_recommendation_outcome(
                recommendations, outcomes
            )
            for edge in edges:
                self.graph.add_edge(edge)
        
        if state_changes:
            edges = self.extractor.extract_from_state_changes(state_changes)
            for edge in edges:
                self.graph.add_edge(edge)
        
        logger.info(f"Memory graph built: {len(self.graph.get_all_nodes())} nodes, {len(self.graph.get_all_edges())} edges")
    
    def _add_signal_nodes(self, signals: List[Dict[str, Any]]) -> None:
        """Add signal nodes to the graph."""
        for signal in signals:
            node = self.extractor.create_node_from_signal(signal)
            self.graph.add_node(node)
    
    def _add_recommendation_nodes(self, recommendations: List[Dict[str, Any]]) -> None:
        """Add recommendation nodes to the graph."""
        for rec in recommendations:
            node = self.extractor.create_node_from_recommendation(rec)
            self.graph.add_node(node)
    
    def _add_outcome_nodes(self, outcomes: List[Dict[str, Any]]) -> None:
        """Add outcome nodes to the graph."""
        for outcome in outcomes:
            node = self.extractor.create_node_from_outcome(outcome)
            self.graph.add_node(node)
    
    def add_signal(
        self,
        signal_id: str,
        signal_type: str,
        domain: str,
        value: float,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Add a signal to the graph."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        node = MemoryNode(
            node_id=f"signal_{signal_type}_{signal_id}",
            node_type=NodeCategory.SIGNAL,
            domain=domain,
            label=signal_type,
            properties={"value": value},
            first_seen=timestamp,
            last_seen=timestamp,
            source_record_ids=[signal_id],
        )
        self.graph.add_node(node)
    
    def add_recommendation(
        self,
        recommendation_id: str,
        action_type: str,
        domain: str,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Add a recommendation to the graph."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        node = MemoryNode(
            node_id=f"rec_{action_type}_{recommendation_id}",
            node_type=NodeCategory.RECOMMENDATION,
            domain=domain,
            label=action_type,
            first_seen=timestamp,
            last_seen=timestamp,
            source_record_ids=[recommendation_id],
        )
        self.graph.add_node(node)
    
    def add_outcome(
        self,
        outcome_id: str,
        outcome_type: str,
        domain: str,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Add an outcome to the graph."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        node = MemoryNode(
            node_id=f"outcome_{outcome_type}_{outcome_id}",
            node_type=NodeCategory.OUTCOME,
            domain=domain,
            label=outcome_type,
            first_seen=timestamp,
            last_seen=timestamp,
            source_record_ids=[outcome_id],
        )
        self.graph.add_node(node)
    
    def link_signal_to_outcome(
        self,
        signal_id: str,
        outcome_id: str,
        relationship: EdgeCategory = EdgeCategory.ASSOCIATED_WITH,
        confidence: float = 0.5,
    ) -> None:
        """Link a signal to an outcome."""
        edge = MemoryEdge(
            edge_id=f"edge_{signal_id}_{outcome_id}",
            source_node_id=signal_id,
            target_node_id=outcome_id,
            relationship=relationship,
            confidence=confidence,
            evidence_count=1,
        )
        self.graph.add_edge(edge)
    
    def link_recommendation_to_outcome(
        self,
        recommendation_id: str,
        outcome_id: str,
        relationship: EdgeCategory = EdgeCategory.LED_TO,
        confidence: float = 0.7,
    ) -> None:
        """Link a recommendation to an outcome."""
        edge = MemoryEdge(
            edge_id=f"edge_{recommendation_id}_{outcome_id}",
            source_node_id=recommendation_id,
            target_node_id=outcome_id,
            relationship=relationship,
            confidence=confidence,
            evidence_count=1,
        )
        self.graph.add_edge(edge)
    
    def rebuild(
        self,
        signals: Optional[List[Dict[str, Any]]] = None,
        recommendations: Optional[List[Dict[str, Any]]] = None,
        outcomes: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Rebuild the entire memory graph."""
        logger.info("Rebuilding memory graph...")
        
        # Clear existing graph
        self.graph._nodes.clear()
        self.graph._edges.clear()
        self.graph._nodes_by_type.clear()
        self.graph._nodes_by_domain.clear()
        self.graph._edges_by_type.clear()
        self.graph._edges_by_source.clear()
        self.graph._edges_by_target.clear()
        
        # Rebuild
        self.build_from_records(signals, recommendations, outcomes)


# Factory function
def create_memory_builder(graph: StrategicMemoryGraph) -> MemoryBuilder:
    """Create a memory builder with the given graph."""
    return MemoryBuilder(graph)
