"""Memory Reporter.

Generates memory insight reports.
"""
from typing import Any, Dict, List, Optional
from collections import defaultdict

from app.strategic_memory.memory_graph import StrategicMemoryGraph
from app.strategic_memory.memory_models import (
    MemorySummary,
    StrategicPattern,
    RecurringChain,
    ChainStrength,
)


class MemoryReporter:
    """Generates memory insight reports."""
    
    def __init__(self, graph: StrategicMemoryGraph):
        self.graph = graph
    
    def generate_summary(self) -> MemorySummary:
        """Generate a summary of the memory graph."""
        nodes = self.graph.get_all_nodes()
        edges = self.graph.get_all_edges()
        
        # Count by category
        nodes_by_category = defaultdict(int)
        nodes_by_domain = defaultdict(int)
        
        for node in nodes:
            nodes_by_category[node.node_type.value] += 1
            nodes_by_domain[node.domain] += 1
        
        # Count by relationship
        edges_by_relationship = defaultdict(int)
        for edge in edges:
            edges_by_relationship[edge.relationship.value] += 1
        
        # Count chains by strength
        established = 0
        recurring = 0
        emerging = 0
        
        # Estimate based on edge evidence
        for edge in edges:
            if edge.evidence_count >= 5:
                established += 1
            elif edge.evidence_count >= 3:
                recurring += 1
            else:
                emerging += 1
        
        return MemorySummary(
            total_nodes=len(nodes),
            total_edges=len(edges),
            nodes_by_category=dict(nodes_by_category),
            nodes_by_domain=dict(nodes_by_domain),
            edges_by_relationship=dict(edges_by_relationship),
            established_chains=established,
            recurring_chains=recurring,
            emerging_chains=emerging,
        )
    
    def generate_pattern_report(self) -> Dict[str, Any]:
        """Generate a report on identified patterns."""
        # Find strong relationship groups
        nodes = self.graph.get_all_nodes()
        edges = self.graph.get_all_edges()
        
        # Group edges by relationship type
        relationship_groups = defaultdict(list)
        for edge in edges:
            relationship_groups[edge.relationship.value].append(edge)
        
        patterns = []
        
        for rel_type, rel_edges in relationship_groups.items():
            if len(rel_edges) >= 2:
                patterns.append({
                    "relationship": rel_type,
                    "count": len(rel_edges),
                    "avg_confidence": sum(e.confidence for e in rel_edges) / len(rel_edges),
                })
        
        return {
            "total_patterns": len(patterns),
            "patterns": sorted(patterns, key=lambda p: p["count"], reverse=True),
        }
    
    def generate_chain_report(self) -> Dict[str, Any]:
        """Generate a report on recurring chains."""
        edges = self.graph.get_all_edges()
        
        # Find potential chains (consecutive relationships)
        chains = []
        
        # Group by source
        by_source = defaultdict(list)
        for edge in edges:
            by_source[edge.source_node_id].append(edge)
        
        # Find chains
        for source, out_edges in by_source.items():
            if len(out_edges) >= 2:
                chain = {
                    "start": source,
                    "steps": len(out_edges),
                    "relationships": [e.relationship.value for e in out_edges],
                    "evidence": sum(e.evidence_count for e in out_edges),
                }
                chains.append(chain)
        
        return {
            "total_chains": len(chains),
            "chains": sorted(chains, key=lambda c: c["evidence"], reverse=True)[:10],
        }
    
    def generate_domain_report(self) -> Dict[str, Any]:
        """Generate a report on domain coverage."""
        nodes = self.graph.get_all_nodes()
        edges = self.graph.get_all_edges()
        
        # Domain stats
        domain_stats = defaultdict(lambda: {"nodes": 0, "incoming": 0, "outgoing": 0})
        
        for node in nodes:
            domain_stats[node.domain]["nodes"] += 1
        
        for edge in edges:
            source = self.graph.get_node(edge.source_node_id)
            target = self.graph.get_node(edge.target_node_id)
            
            if source:
                domain_stats[source.domain]["outgoing"] += 1
            if target:
                domain_stats[target.domain]["incoming"] += 1
        
        return {
            "domains": dict(domain_stats),
            "total_domains": len(domain_stats),
        }
    
    def generate_risk_report(self) -> Dict[str, Any]:
        """Generate a report on identified risks."""
        edges = self.graph.get_all_edges()
        
        # Find risk-related relationships
        risk_relationships = [
            "contributes_to",
            "escalates",
            "precedes",
        ]
        
        risk_edges = [
            e for e in edges
            if e.relationship.value in risk_relationships
        ]
        
        risk_chains = []
        
        for edge in risk_edges:
            # Find chains starting from this risk
            paths = self.graph.find_path(edge.source_node_id, edge.target_node_id, max_depth=3)
            
            for path in paths:
                risk_chains.append({
                    "start": edge.source_node_id,
                    "end": edge.target_node_id,
                    "path": path,
                    "confidence": edge.confidence,
                })
        
        return {
            "risk_relationship_count": len(risk_edges),
            "risk_chains": risk_chains[:10],
        }
    
    def generate_full_report(self) -> Dict[str, Any]:
        """Generate a comprehensive memory report."""
        return {
            "summary": self.generate_summary().model_dump(),
            "patterns": self.generate_pattern_report(),
            "chains": self.generate_chain_report(),
            "domains": self.generate_domain_report(),
            "risks": self.generate_risk_report(),
        }
    
    def get_top_interventions(self) -> List[Dict[str, Any]]:
        """Get historically effective interventions."""
        edges = self.graph.get_all_edges()
        
        # Find led_to and stabilized relationships
        effective_edges = [
            e for e in edges
            if e.relationship.value in ["led_to", "stabilizes"]
        ]
        
        # Sort by evidence count
        sorted_edges = sorted(
            effective_edges,
            key=lambda e: e.evidence_count,
            reverse=True,
        )
        
        interventions = []
        
        for edge in sorted_edges[:10]:
            source = self.graph.get_node(edge.source_node_id)
            target = self.graph.get_node(edge.target_node_id)
            
            if source:
                interventions.append({
                    "intervention": source.label,
                    "outcome": target.label if target else "unknown",
                    "evidence_count": edge.evidence_count,
                    "confidence": edge.confidence,
                })
        
        return interventions


# Factory function
def create_memory_reporter(graph: StrategicMemoryGraph) -> MemoryReporter:
    """Create a memory reporter with the given graph."""
    return MemoryReporter(graph)
