"""Relationship Extractor.

Extracts candidate relationships from existing data.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.strategic_memory.memory_models import (
    MemoryEdge,
    MemoryNode,
    NodeCategory,
    EdgeCategory,
)


class RelationshipExtractor:
    """Extracts relationships from historical data."""
    
    # Known relationship patterns
    SIGNAL_OUTCOME_PATTERNS = {
        ("sleep_quality", "low"): [
            ("energy_level", "decline", EdgeCategory.CONTRIBUTES_TO),
        ],
        ("energy_level", "low"): [
            ("task_backlog", "growth", EdgeCategory.CONTRIBUTES_TO),
        ],
        ("task_backlog", "growth"): [
            ("schedule_overload", "increase", EdgeCategory.CONTRIBUTES_TO),
        ],
        ("schedule_overload", "increase"): [
            ("stress_level", "rise", EdgeCategory.ESCALATES),
        ],
        ("liquidity_change", "negative"): [
            ("stress_level", "increase", EdgeCategory.CONTRIBUTES_TO),
        ],
    }
    
    # Known co-occurrence patterns
    CO_OCCURRENCE_PATTERNS = [
        ["energy_level", "task_backlog"],
        ["schedule_overload", "stress_level"],
        ["liquidity_change", "spending_spike"],
    ]
    
    def __init__(self):
        self._extracted_edges: List[MemoryEdge] = []
    
    def extract_from_signal_sequence(
        self,
        signals: List[Dict[str, Any]],
    ) -> List[MemoryEdge]:
        """Extract relationships from a sequence of signals."""
        edges = []
        
        # Sort by timestamp
        sorted_signals = sorted(
            signals,
            key=lambda s: s.get("timestamp", datetime.min),
        )
        
        # Look for temporal relationships
        for i in range(len(sorted_signals) - 1):
            current = sorted_signals[i]
            next_signal = sorted_signals[i + 1]
            
            # Check if time gap is reasonable (within 7 days)
            current_time = current.get("timestamp", datetime.min)
            next_time = next_signal.get("timestamp", datetime.min)
            
            if isinstance(current_time, datetime) and isinstance(next_time, datetime):
                gap_hours = (next_time - current_time).total_seconds() / 3600
                
                if 0 < gap_hours < 168:  # Within 7 days
                    edge = self._infer_relationship(
                        source_id=f"signal_{current.get('signal_type', 'unknown')}",
                        target_id=f"signal_{next_signal.get('signal_type', 'unknown')}",
                        source_domain=current.get("domain", "unknown"),
                        target_domain=next_signal.get("domain", "unknown"),
                        time_gap_hours=gap_hours,
                        record_id=current.get("signal_id", ""),
                    )
                    if edge:
                        edges.append(edge)
        
        return edges
    
    def extract_from_recommendation_outcome(
        self,
        recommendations: List[Dict[str, Any]],
        outcomes: List[Dict[str, Any]],
    ) -> List[MemoryEdge]:
        """Extract recommendation to outcome relationships."""
        edges = []
        
        for rec in recommendations:
            rec_id = rec.get("recommendation_id", "")
            rec_type = rec.get("action_type", "unknown")
            rec_domain = rec.get("domain", "unknown")
            
            # Look for matching outcomes
            for outcome in outcomes:
                if self._is_related(rec, outcome):
                    gap_hours = self._calculate_time_gap(rec, outcome)
                    
                    edge = MemoryEdge(
                        edge_id=f"edge_{rec_id}_{outcome.get('outcome_id', 'unknown')}",
                        source_node_id=f"rec_{rec_type}",
                        target_node_id=f"outcome_{outcome.get('outcome_type', 'unknown')}",
                        relationship=EdgeCategory.LED_TO if gap_hours < 720 else EdgeCategory.ASSOCIATED_WITH,
                        evidence_count=1,
                        confidence=0.7,
                        avg_time_gap_hours=gap_hours,
                        supporting_record_ids=[rec_id, outcome.get("outcome_id", "")],
                    )
                    edges.append(edge)
        
        return edges
    
    def extract_from_state_changes(
        self,
        state_changes: List[Dict[str, Any]],
    ) -> List[MemoryEdge]:
        """Extract relationships from state changes."""
        edges = []
        
        for i in range(len(state_changes) - 1):
            current = state_changes[i]
            next_change = state_changes[i + 1]
            
            current_domain = current.get("domain", "unknown")
            next_domain = next_change.get("domain", "unknown")
            
            # Different domains may indicate cross-domain relationships
            if current_domain != next_domain:
                current_value = current.get("value", 0.5)
                next_value = next_change.get("value", 0.5)
                
                # Check for causal direction
                if current_value < 0.5 and next_value < 0.5:
                    # Both declining - possible contribution
                    edge = MemoryEdge(
                        edge_id=f"edge_state_{current.get('id', '')}_{next_change.get('id', '')}",
                        source_node_id=f"state_{current_domain}",
                        target_node_id=f"state_{next_domain}",
                        relationship=EdgeCategory.CONTRIBUTES_TO,
                        evidence_count=1,
                        confidence=0.5,
                        supporting_record_ids=[current.get("id", ""), next_change.get("id", "")],
                    )
                    edges.append(edge)
        
        return edges
    
    def _infer_relationship(
        self,
        source_id: str,
        target_id: str,
        source_domain: str,
        target_domain: str,
        time_gap_hours: float,
        record_id: str,
    ) -> Optional[MemoryEdge]:
        """Infer relationship type based on known patterns."""
        
        # Check known patterns
        for (sig_type, direction), related in self.SIGNAL_OUTCOME_PATTERNS.items():
            if sig_type in source_id.lower():
                for target_type, edge_type in related:
                    if target_type in target_id.lower():
                        return MemoryEdge(
                            edge_id=f"edge_{source_id}_{target_id}_{datetime.utcnow().timestamp()}",
                            source_node_id=source_id,
                            target_node_id=target_id,
                            relationship=edge_type,
                            evidence_count=1,
                            confidence=0.6,
                            avg_time_gap_hours=time_gap_hours,
                            supporting_record_ids=[record_id],
                        )
        
        # Default to temporal association
        if time_gap_hours < 24:
            relationship = EdgeCategory.PRECEDES
            confidence = 0.5
        else:
            relationship = EdgeCategory.ASSOCIATED_WITH
            confidence = 0.3
        
        return MemoryEdge(
            edge_id=f"edge_{source_id}_{target_id}_{datetime.utcnow().timestamp()}",
            source_node_id=source_id,
            target_node_id=target_id,
            relationship=relationship,
            evidence_count=1,
            confidence=confidence,
            avg_time_gap_hours=time_gap_hours,
            supporting_record_ids=[record_id],
        )
    
    def _is_related(self, rec: Dict, outcome: Dict) -> bool:
        """Check if recommendation is related to outcome."""
        # Simple check - same domain and close in time
        if rec.get("domain") != outcome.get("domain"):
            return False
        
        rec_time = rec.get("timestamp", datetime.min)
        outcome_time = outcome.get("timestamp", datetime.min)
        
        if isinstance(rec_time, datetime) and isinstance(outcome_time, datetime):
            gap = abs((outcome_time - rec_time).total_seconds()) / 3600
            return gap < 720  # Within 30 days
        
        return False
    
    def _calculate_time_gap(self, rec: Dict, outcome: Dict) -> float:
        """Calculate time gap between recommendation and outcome."""
        rec_time = rec.get("timestamp", datetime.utcnow())
        outcome_time = outcome.get("timestamp", datetime.utcnow())
        
        if isinstance(rec_time, datetime) and isinstance(outcome_time, datetime):
            return abs((outcome_time - rec_time).total_seconds()) / 3600
        
        return 0.0
    
    def create_node_from_signal(self, signal: Dict[str, Any]) -> MemoryNode:
        """Create a memory node from a signal."""
        return MemoryNode(
            node_id=f"signal_{signal.get('signal_type', 'unknown')}_{signal.get('signal_id', '')}",
            node_type=NodeCategory.SIGNAL,
            domain=signal.get("domain", "unknown"),
            label=signal.get("title", signal.get("signal_type", "Unknown")),
            description=signal.get("description"),
            properties={"value": signal.get("value"), "confidence": signal.get("confidence")},
            source_record_ids=[signal.get("signal_id", "")],
        )
    
    def create_node_from_recommendation(self, rec: Dict[str, Any]) -> MemoryNode:
        """Create a memory node from a recommendation."""
        return MemoryNode(
            node_id=f"rec_{rec.get('action_type', 'unknown')}_{rec.get('recommendation_id', '')}",
            node_type=NodeCategory.RECOMMENDATION,
            domain=rec.get("domain", "unknown"),
            label=rec.get("action_type", "Unknown"),
            properties={"priority": rec.get("priority"), "confidence": rec.get("confidence")},
            source_record_ids=[rec.get("recommendation_id", "")],
        )
    
    def create_node_from_outcome(self, outcome: Dict[str, Any]) -> MemoryNode:
        """Create a memory node from an outcome."""
        return MemoryNode(
            node_id=f"outcome_{outcome.get('outcome_type', 'unknown')}_{outcome.get('outcome_id', '')}",
            node_type=NodeCategory.OUTCOME,
            domain=outcome.get("domain", "unknown"),
            label=outcome.get("outcome_type", "Unknown"),
            properties=outcome.get("properties", {}),
            source_record_ids=[outcome.get("outcome_id", "")],
        )


# Global extractor instance
_relationship_extractor: Optional[RelationshipExtractor] = None


def get_relationship_extractor() -> RelationshipExtractor:
    """Get the global relationship extractor instance."""
    global _relationship_extractor
    if _relationship_extractor is None:
        _relationship_extractor = RelationshipExtractor()
    return _relationship_extractor
