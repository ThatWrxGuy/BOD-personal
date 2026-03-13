"""Pattern Linker.

Links related records into reusable strategic patterns.
"""
from typing import Any, Dict, List, Optional
from collections import defaultdict

from app.strategic_memory.memory_graph import StrategicMemoryGraph
from app.strategic_memory.memory_models import (
    StrategicPattern,
    EdgeCategory,
    NodeCategory,
)


class PatternLinker:
    """Links related records into reusable patterns."""
    
    # Known pattern templates
    PATTERN_TEMPLATES = {
        "overload_chain": {
            "name": "Overload Chain",
            "description": "Progressive workload leading to stress",
            "categories": ["workload", "stress"],
            "edge_types": [EdgeCategory.CONTRIBUTES_TO, EdgeCategory.ESCALATES],
        },
        "financial_stress_chain": {
            "name": "Financial Stress Chain",
            "description": "Financial issues leading to reduced performance",
            "categories": ["finance", "productivity"],
            "edge_types": [EdgeCategory.CONTRIBUTES_TO, EdgeCategory.LED_TO],
        },
        "burnout_precursor": {
            "name": "Burnout Precursor",
            "description": "Early warning signs of burnout",
            "categories": ["health", "workload"],
            "edge_types": [EdgeCategory.CONTRIBUTES_TO, EdgeCategory.PRECEDES],
        },
        "productivity_recovery": {
            "name": "Productivity Recovery",
            "description": "Successful intervention leading to recovery",
            "categories": ["productivity", "intervention"],
            "edge_types": [EdgeCategory.LED_TO, EdgeCategory.STABILIZES],
        },
    }
    
    def __init__(self, graph: StrategicMemoryGraph):
        self.graph = graph
        self._patterns: Dict[str, StrategicPattern] = {}
    
    def identify_patterns(self) -> List[StrategicPattern]:
        """Identify patterns from the current graph."""
        patterns = []
        
        # Use templates to find matching sequences
        for template_id, template in self.PATTERN_TEMPLATES.items():
            matching_edges = self._find_matching_edges(template["edge_types"])
            
            if len(matching_edges) >= 2:
                # Build pattern from matching edges
                pattern = self._build_pattern(
                    template_id=template_id,
                    template=template,
                    edges=matching_edges,
                )
                patterns.append(pattern)
                self._patterns[pattern.pattern_id] = pattern
        
        return patterns
    
    def link_by_co_occurrence(
        self,
        node_ids: List[str],
        time_window_hours: float = 168,
    ) -> List[StrategicPattern]:
        """Link nodes that co-occur within a time window."""
        # Group edges by their time gaps
        co_occurrence_groups = defaultdict(list)
        
        for edge in self.graph.get_all_edges():
            if edge.relationship == EdgeCategory.CO_OCCURS_WITH:
                continue  # Skip already linked
            
            if edge.avg_time_gap_hours < time_window_hours:
                key = tuple(sorted([edge.source_node_id, edge.target_node_id]))
                co_occurrence_groups[key].append(edge)
        
        patterns = []
        for (source, target), edges in co_occurrence_groups.items():
            if len(edges) >= 2:  # Require at least 2 co-occurrences
                pattern = StrategicPattern(
                    pattern_id=f"pattern_cooccur_{source}_{target}",
                    name=f"Co-occurrence: {source} ↔ {target}",
                    description=f"Nodes {source} and {target} frequently co-occur",
                    node_ids=[source, target],
                    edge_ids=[e.edge_id for e in edges],
                    occurrence_count=len(edges),
                    success_rate=0.5,  # Would need outcome data
                    domains=self._extract_domains([source, target]),
                    categories=["co-occurrence"],
                )
                patterns.append(pattern)
        
        return patterns
    
    def link_similar_chains(
        self,
        min_similarity: float = 0.7,
    ) -> List[StrategicPattern]:
        """Find and link similar chains of events."""
        # This would require more sophisticated sequence matching
        # For now, return empty
        return []
    
    def get_pattern(self, pattern_id: str) -> Optional[StrategicPattern]:
        """Get a pattern by ID."""
        return self._patterns.get(pattern_id)
    
    def get_all_patterns(self) -> List[StrategicPattern]:
        """Get all identified patterns."""
        return list(self._patterns.values())
    
    def _find_matching_edges(
        self,
        edge_types: List[EdgeCategory],
    ) -> List:
        """Find edges matching a template."""
        matching = []
        
        for edge in self.graph.get_all_edges():
            if edge.relationship in edge_types:
                matching.append(edge)
        
        return matching
    
    def _build_pattern(
        self,
        template_id: str,
        template: Dict[str, Any],
        edges: List,
    ) -> StrategicPattern:
        """Build a pattern from matching edges."""
        node_ids = set()
        for edge in edges:
            node_ids.add(edge.source_node_id)
            node_ids.add(edge.target_node_id)
        
        return StrategicPattern(
            pattern_id=f"pattern_{template_id}_{len(self._patterns)}",
            name=template["name"],
            description=template["description"],
            node_ids=list(node_ids),
            edge_ids=[e.edge_id for e in edges],
            occurrence_count=len(edges),
            success_rate=0.5,
            domains=template["categories"],
            categories=template["categories"],
        )
    
    def _extract_domains(self, node_ids: List[str]) -> List[str]:
        """Extract domains from node IDs."""
        domains = set()
        
        for node_id in node_ids:
            node = self.graph.get_node(node_id)
            if node:
                domains.add(node.domain)
        
        return list(domains)


# Factory function
def create_pattern_linker(graph: StrategicMemoryGraph) -> PatternLinker:
    """Create a pattern linker with the given graph."""
    return PatternLinker(graph)
