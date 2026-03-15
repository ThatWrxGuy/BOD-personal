"""Decision Pattern Extractor.

Extracts decision events from historical data.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.pattern_learning.pattern_models import (
    DecisionContextProfile,
    DecisionPattern,
    OutcomeType,
)


class DecisionPatternExtractor:
    """Extracts decision patterns from historical data."""
    
    def __init__(self):
        self._extracted_patterns: List[DecisionPattern] = []
    
    def extract_from_journal(
        self,
        journal_entries: List[Dict[str, Any]],
        signals_at_time: Optional[List[Dict[str, Any]]] = None,
    ) -> List[DecisionPattern]:
        """Extract patterns from decision journal entries."""
        patterns = []
        
        for entry in journal_entries:
            # Get decision context
            context = self._extract_context(entry, signals_at_time)
            
            # Get outcome
            outcome = entry.get("outcome", {})
            
            # Build pattern
            pattern = DecisionPattern(
                pattern_id=f"pattern_{entry.get('decision_id', '')}",
                context=context,
                recommendation_family=self._classify_recommendation(
                    entry.get("action_type", "")
                ),
                observed_outcomes=[outcome.get("type", "unknown")],
                success_count=1 if outcome.get("type") in ["improvement", "stabilization"] else 0,
                failure_count=1 if outcome.get("type") == "deterioration" else 0,
                total_count=1,
                success_rate=1.0 if outcome.get("type") in ["improvement", "stabilization"] else 0.0,
                evidence_record_ids=[entry.get("decision_id", "")],
                first_observed=entry.get("timestamp", datetime.utcnow()),
                last_observed=entry.get("timestamp", datetime.utcnow()),
            )
            
            patterns.append(pattern)
        
        return patterns
    
    def extract_from_audit(
        self,
        audit_entries: List[Dict[str, Any]],
    ) -> List[DecisionPattern]:
        """Extract patterns from execution audit data."""
        patterns = []
        
        for entry in audit_entries:
            # Extract from audit
            pattern = DecisionPattern(
                pattern_id=f"pattern_audit_{entry.get('audit_id', '')}",
                context=self._create_context_from_audit(entry),
                recommendation_family=self._classify_recommendation(
                    entry.get("action_type", "")
                ),
                observed_outcomes=[entry.get("outcome_type", "unknown")],
                success_count=1 if entry.get("outcome_type") == "success" else 0,
                failure_count=1 if entry.get("outcome_type") == "failure" else 0,
                total_count=1,
                evidence_record_ids=[entry.get("audit_id", "")],
            )
            
            patterns.append(pattern)
        
        return patterns
    
    def extract_from_memory_graph(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
    ) -> List[DecisionPattern]:
        """Extract patterns from memory graph."""
        patterns = []
        
        # Find recommendation -> outcome relationships
        for edge in edges:
            if edge.get("relationship") in ["led_to", "associated_with"]:
                # Extract pattern from relationship
                pattern = DecisionPattern(
                    pattern_id=f"pattern_mem_{edge.get('edge_id', '')}",
                    context=DecisionContextProfile(
                        context_id=f"context_{edge.get('source_node_id', '')}",
                    ),
                    recommendation_family=self._classify_recommendation(
                        edge.get("source_node_id", "")
                    ),
                    observed_outcomes=[edge.get("target_node_id", "")],
                    evidence_record_ids=[edge.get("edge_id", "")],
                )
                patterns.append(pattern)
        
        return patterns
    
    def _extract_context(
        self,
        entry: Dict[str, Any],
        signals: Optional[List[Dict[str, Any]]] = None,
    ) -> DecisionContextProfile:
        """Extract decision context from entry and signals."""
        
        # Build signal signatures
        signatures = {}
        domains = set()
        
        if signals:
            for signal in signals:
                sig_type = signal.get("signal_type", "unknown")
                value = signal.get("value", 0.0)
                signatures[sig_type] = value
                
                domain = signal.get("domain", "unknown")
                domains.add(domain)
        
        # Determine severity
        severity = self._calculate_severity(signatures)
        
        # Check persistence
        has_persistent = self._check_persistence(signatures)
        
        return DecisionContextProfile(
            context_id=f"context_{entry.get('decision_id', '')}",
            signal_signatures=signatures,
            domains=list(domains),
            overall_severity=severity,
            has_persistent_signals=has_persistent,
            sample_size=1,
        )
    
    def _create_context_from_audit(
        self,
        entry: Dict[str, Any],
    ) -> DecisionContextProfile:
        """Create context from audit entry."""
        
        context_data = entry.get("context", {})
        
        return DecisionContextProfile(
            context_id=f"context_{entry.get('audit_id', '')}",
            signal_signatures=context_data.get("signatures", {}),
            domains=context_data.get("domains", []),
            overall_severity=context_data.get("severity", 0.5),
            has_persistent_signals=context_data.get("has_persistent", False),
            sample_size=1,
        )
    
    def _calculate_severity(self, signatures: Dict[str, float]) -> float:
        """Calculate overall severity from signal signatures."""
        if not signatures:
            return 0.5
        
        # Average absolute values
        values = [abs(v) for v in signatures.values()]
        return sum(values) / len(values) if values else 0.5
    
    def _check_persistence(self, signatures: Dict[str, float]) -> bool:
        """Check if any signals indicate persistence."""
        # Simple check - if any signal has high magnitude
        for value in signatures.values():
            if abs(value) > 0.7:
                return True
        return False
    
    def _classify_recommendation(self, action_type: str) -> 'StrategyFamily':
        """Classify recommendation into strategy family."""
        
        action_lower = action_type.lower()
        
        if "reduce" in action_lower or "decrease" in action_lower:
            return StrategyFamily.DEFENSIVE_STABILIZATION
        elif "increase" in action_lower or "boost" in action_lower:
            if "productivity" in action_lower or "output" in action_lower:
                return StrategyFamily.PRODUCTIVITY_FOCUS
            elif "savings" in action_lower or "save" in action_lower:
                return StrategyFamily.FINANCIAL_STABILIZATION
            else:
                return StrategyFamily.RISK_MITIGATION
        elif "recover" in action_lower or "rest" in action_lower:
            return StrategyFamily.HEALTH_RECOVERY
        elif "focus" in action_lower or "prioritize" in action_lower:
            return StrategyFamily.FOCUS_PRIORITIZATION
        elif "schedule" in action_lower or "time" in action_lower:
            return StrategyFamily.RESOURCE_OPTIMIZATION
        else:
            return StrategyFamily.EXPLORATION


# Global extractor instance
_decision_pattern_extractor: Optional[DecisionPatternExtractor] = None


def get_decision_pattern_extractor() -> DecisionPatternExtractor:
    """Get the global decision pattern extractor instance."""
    global _decision_pattern_extractor
    if _decision_pattern_extractor is None:
        _decision_pattern_extractor = DecisionPatternExtractor()
    return _decision_pattern_extractor
