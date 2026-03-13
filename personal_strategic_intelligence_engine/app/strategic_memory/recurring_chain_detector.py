"""Recurring Chain Detector.

Detects repeated strategic chains across time.
"""
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta

from app.strategic_memory.memory_graph import StrategicMemoryGraph
from app.strategic_memory.memory_models import (
    RecurringChain,
    ChainStrength,
    EdgeCategory,
)


class RecurringChainDetector:
    """Detects recurring chains in the memory graph."""
    
    # Thresholds for chain classification
    EMERGING_THRESHOLD = 2      # 2 occurrences
    RECURRING_THRESHOLD = 3     # 3 occurrences
    ESTABLISHED_THRESHOLD = 5   # 5 occurrences
    
    def __init__(self, graph: StrategicMemoryGraph):
        self.graph = graph
        self._chains: Dict[str, RecurringChain] = {}
    
    def detect_chains(self) -> List[RecurringChain]:
        """Detect recurring chains in the graph."""
        chains = []
        
        # Find paths in the graph
        all_nodes = self.graph.get_all_nodes()
        
        for node in all_nodes:
            # Find chains starting from this node
            starting_chains = self._find_chains_from(node.node_id, max_depth=4)
            
            for chain_nodes in starting_chains:
                if len(chain_nodes) >= 3:  # Minimum chain length
                    chain = self._build_chain(chain_nodes)
                    if chain:
                        chain_id = self._generate_chain_id(chain_nodes)
                        
                        if chain_id in self._chains:
                            # Update existing chain
                            existing = self._chains[chain_id]
                            existing.repetition_count += 1
                            self._update_chain_strength(existing)
                        else:
                            # Add new chain
                            self._chains[chain_id] = chain
                            chains.append(chain)
        
        return chains
    
    def get_chain(self, chain_id: str) -> Optional[RecurringChain]:
        """Get a chain by ID."""
        return self._chains.get(chain_id)
    
    def get_all_chains(self) -> List[RecurringChain]:
        """Get all detected chains."""
        return list(self._chains.values())
    
    def get_strongest_chains(self, limit: int = 10) -> List[RecurringChain]:
        """Get the strongest chains by repetition count."""
        chains = sorted(
            self._chains.values(),
            key=lambda c: c.repetition_count,
            reverse=True,
        )
        return chains[:limit]
    
    def get_chains_by_domain(self, domain: str) -> List[RecurringChain]:
        """Get chains involving a specific domain."""
        return [
            c for c in self._chains.values()
            if domain in c.domains
        ]
    
    def _find_chains_from(
        self,
        start_node_id: str,
        max_depth: int = 4,
    ) -> List[List[str]]:
        """Find chains starting from a given node."""
        chains = []
        
        def dfs(current: str, path: List[str], depth: int):
            if depth > max_depth:
                return
            
            path = path + [current]
            
            # If path is long enough, add as a chain
            if len(path) >= 3:
                chains.append(path)
            
            # Continue traversal
            for edge in self.graph.get_outgoing_edges(current):
                dfs(edge.target_node_id, path, depth + 1)
        
        dfs(start_node_id, [], 0)
        return chains
    
    def _build_chain(self, node_sequence: List[str]) -> Optional[RecurringChain]:
        """Build a chain from a node sequence."""
        if len(node_sequence) < 3:
            return None
        
        # Get edges between nodes
        edge_sequence = []
        domains = set()
        
        for i in range(len(node_sequence) - 1):
            source = node_sequence[i]
            target = node_sequence[i + 1]
            
            # Find edge between source and target
            edges = self.graph.get_outgoing_edges(source)
            matching = [e for e in edges if e.target_node_id == target]
            
            if matching:
                edge_sequence.append(matching[0].edge_id)
            else:
                edge_sequence.append("")
            
            # Extract domain
            node = self.graph.get_node(source)
            if node:
                domains.add(node.domain)
        
        # Calculate average duration
        avg_duration = self._estimate_chain_duration(node_sequence)
        
        # Determine strength
        repetition_count = 1  # Default
        chain_strength = ChainStrength.EMERGING
        
        chain = RecurringChain(
            chain_id=self._generate_chain_id(node_sequence),
            name=self._generate_chain_name(node_sequence),
            description=f"Chain: {' → '.join(node_sequence[:3])}...",
            node_sequence=node_sequence,
            edge_sequence=edge_sequence,
            repetition_count=repetition_count,
            chain_strength=chain_strength,
            avg_duration_hours=avg_duration,
            domains=list(domains),
        )
        
        self._update_chain_strength(chain)
        
        return chain
    
    def _update_chain_strength(self, chain: RecurringChain) -> None:
        """Update the strength classification of a chain."""
        if chain.repetition_count >= self.ESTABLISHED_THRESHOLD:
            chain.chain_strength = ChainStrength.ESTABLISHED
        elif chain.repetition_count >= self.RECURRING_THRESHOLD:
            chain.chain_strength = ChainStrength.RECURRING
        elif chain.repetition_count >= self.EMERGING_THRESHOLD:
            chain.chain_strength = ChainStrength.EMERGING
        else:
            chain.chain_strength = ChainStrength.EMERGING
    
    def _estimate_chain_duration(self, node_sequence: List[str]) -> float:
        """Estimate the average duration of a chain."""
        # Sum up average time gaps for each edge
        total_gap = 0.0
        count = 0
        
        for i in range(len(node_sequence) - 1):
            source = node_sequence[i]
            target = node_sequence[i + 1]
            
            edges = self.graph.get_outgoing_edges(source)
            for edge in edges:
                if edge.target_node_id == target:
                    total_gap += edge.avg_time_gap_hours
                    count += 1
                    break
        
        return total_gap / count if count > 0 else 0.0
    
    def _generate_chain_id(self, node_sequence: List[str]) -> str:
        """Generate a unique ID for a chain."""
        return "chain_" + "_".join(node_sequence[:3])
    
    def _generate_chain_name(self, node_sequence: List[str]) -> str:
        """Generate a human-readable name for a chain."""
        # Get node labels
        labels = []
        for node_id in node_sequence[:3]:
            node = self.graph.get_node(node_id)
            if node:
                labels.append(node.label)
            else:
                labels.append(node_id)
        
        return " → ".join(labels)


# Factory function
def create_recurring_chain_detector(graph: StrategicMemoryGraph) -> RecurringChainDetector:
    """Create a recurring chain detector with the given graph."""
    return RecurringChainDetector(graph)
