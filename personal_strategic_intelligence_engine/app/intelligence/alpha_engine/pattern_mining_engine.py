"""Pattern Mining Engine.

Identifies recurring signal patterns associated with outcomes.
"""

from typing import List, Dict, Optional
from collections import Counter
import random

from app.intelligence.alpha_engine.alpha_models import PatternCandidate


class PatternMiningEngine:
    """Identifies recurring signal patterns."""
    
    def __init__(self):
        self.min_frequency = 3
        self.patterns_discovered = []
    
    def mine_patterns(
        self,
        signal_history: List[Dict],
        outcome_history: List[Dict],
        sequence_length: int = 3,
    ) -> List[PatternCandidate]:
        """Mine patterns from signal and outcome history."""
        
        patterns = []
        
        # Extract signal sequences
        for i in range(len(signal_history) - sequence_length):
            sequence = [s.get("type") for s in signal_history[i:i+sequence_length]]
            
            # Get outcome after sequence
            if i + sequence_length < len(outcome_history):
                outcome = outcome_history[i + sequence_length].get("result", "unknown")
            else:
                continue
            
            # Store sequence with outcome
            key = tuple(sequence)
            if not hasattr(self, '_sequence_db'):
                self._sequence_db = {}
            
            if key not in self._sequence_db:
                self._sequence_db[key] = {"frequency": 0, "outcomes": {}}
            
            self._sequence_db[key]["frequency"] += 1
            self._sequence_db[key]["outcomes"][outcome] = \
                self._sequence_db[key]["outcomes"].get(outcome, 0) + 1
        
        # Convert to pattern candidates
        if hasattr(self, '_sequence_db'):
            for sequence, data in self._sequence_db.items():
                if data["frequency"] >= self.min_frequency:
                    # Calculate outcome distribution
                    total = sum(data["outcomes"].values())
                    outcome_dist = {
                        k: v / total * 100 
                        for k, v in data["outcomes"].items()
                    }
                    
                    # Calculate confidence based on frequency and consistency
                    max_outcome_pct = max(outcome_dist.values()) if outcome_dist else 0
                    confidence = (data["frequency"] / 20) * (max_outcome_pct / 100)
                    
                    pattern = PatternCandidate(
                        id=f"pattern-{len(patterns)+1}",
                        signal_sequence=list(sequence),
                        frequency=data["frequency"],
                        outcome_distribution=outcome_dist,
                        confidence=min(0.95, confidence),
                    )
                    patterns.append(pattern)
        
        self.patterns_discovered = patterns
        return patterns
    
    def find_vwap_gamma_patterns(
        self,
        signals: List[Dict],
    ) -> List[PatternCandidate]:
        """Find VWAP + gamma expansion patterns."""
        
        patterns = []
        
        # Look for VWAP reclaim followed by gamma signals
        for i in range(len(signals) - 2):
            if signals[i].get("type") == "vwap_reclaim_signal":
                if signals[i+1].get("type") == "gamma_acceleration_event":
                    # Check what happens next
                    outcome = signals[i+2].get("type", "unknown")
                    
                    patterns.append(PatternCandidate(
                        id=f"vwap-gamma-{i}",
                        signal_sequence=["vwap_reclaim_signal", "gamma_acceleration_event", outcome],
                        frequency=1,
                        outcome_distribution={outcome: 100},
                        confidence=0.6,
                    ))
        
        return patterns
    
    def find_opening_range_patterns(
        self,
        signals: List[Dict],
    ) -> List[PatternCandidate]:
        """Find opening range breakout patterns."""
        
        patterns = []
        
        for i in range(len(signals) - 2):
            if "opening_range" in signals[i].get("type", ""):
                if signals[i+1].get("payload", {}).get("direction") == "bullish":
                    outcome = signals[i+2].get("type", "unknown")
                    
                    patterns.append(PatternCandidate(
                        id=f"orb-{i}",
                        signal_sequence=["opening_range_breakout", "bullish_momentum", outcome],
                        frequency=1,
                        outcome_distribution={outcome: 100},
                        confidence=0.5,
                    ))
        
        return patterns
    
    def get_top_patterns(self, limit: int = 10) -> List[PatternCandidate]:
        """Get top patterns by confidence."""
        
        sorted_patterns = sorted(
            self.patterns_discovered,
            key=lambda p: p.confidence,
            reverse=True,
        )
        
        return sorted_patterns[:limit]


def create_engine() -> PatternMiningEngine:
    """Create pattern mining engine."""
    return PatternMiningEngine()
