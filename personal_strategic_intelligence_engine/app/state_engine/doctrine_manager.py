"""Doctrine manager for evolving strategic doctrine."""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.state_engine.state_models import DoctrineEntry
from app.state_engine.state_repository import StateRepository


class DoctrineManager:
    """Manages evolving strategic doctrine.
    
    Responsible for:
    - Maintaining strategic doctrine based on system outcomes
    - Tracking doctrine confidence levels
    - Evolving doctrine as the system learns
    """
    
    def __init__(self, repository: Optional[StateRepository] = None):
        self.repository = repository or StateRepository()
        self._doctrine_cache: Dict[str, DoctrineEntry] = {}
        
        # Load active doctrine into cache
        self._load_active_doctrine()
    
    def _load_active_doctrine(self):
        """Load active doctrine entries into cache."""
        active = self.repository.get_active_doctrine()
        for entry in active:
            self._doctrine_cache[entry.doctrine_id] = entry
    
    # ============= Doctrine CRUD =============
    
    def add_doctrine_entry(
        self,
        strategic_rule: str,
        supporting_evidence: List[Dict[str, Any]],
        origin_cycle: str,
        confidence_level: float = 0.5,
    ) -> str:
        """Add a new doctrine entry.
        
        Args:
            strategic_rule: The strategic rule or principle
            supporting_evidence: Evidence supporting this doctrine
            origin_cycle: The cycle where this doctrine originated
            confidence_level: Initial confidence level (0-1)
            
        Returns:
            The doctrine ID
        """
        doctrine_id = f"doc_{uuid.uuid4().hex[:12]}"
        
        entry = DoctrineEntry(
            doctrine_id=doctrine_id,
            strategic_rule=strategic_rule,
            supporting_evidence=supporting_evidence,
            confidence_level=confidence_level,
            origin_cycle=origin_cycle,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True,
        )
        
        # Store in repository
        self.repository.store_doctrine(entry)
        
        # Add to cache
        self._doctrine_cache[doctrine_id] = entry
        
        return doctrine_id
    
    def get_doctrine(self, doctrine_id: str) -> Optional[DoctrineEntry]:
        """Retrieve a specific doctrine entry.
        
        Args:
            doctrine_id: The doctrine ID to retrieve
            
        Returns:
            The doctrine entry, or None if not found
        """
        # Check cache first
        if doctrine_id in self._doctrine_cache:
            return self._doctrine_cache[doctrine_id]
        
        # Check repository
        return self.repository.get_doctrine(doctrine_id)
    
    def get_active_doctrine(self) -> List[DoctrineEntry]:
        """Get all active doctrine entries.
        
        Returns:
            List of active doctrine entries
        """
        return list(self._doctrine_cache.values())
    
    def get_all_doctrine(self) -> List[DoctrineEntry]:
        """Get all doctrine entries (active and inactive).
        
        Returns:
            List of all doctrine entries
        """
        return self.repository.get_all_doctrine()
    
    def get_doctrine_by_confidence(self, min_confidence: float = 0.0) -> List[DoctrineEntry]:
        """Get doctrine entries above a confidence threshold.
        
        Args:
            min_confidence: Minimum confidence level
            
        Returns:
            Filtered list of doctrine entries
        """
        active = self.get_active_doctrine()
        return [d for d in active if d.confidence_level >= min_confidence]
    
    # ============= Doctrine Evolution =============
    
    def update_doctrine_confidence(
        self,
        doctrine_id: str,
        new_confidence: float,
        evidence: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Update the confidence level of a doctrine entry.
        
        Args:
            doctrine_id: The doctrine to update
            new_confidence: New confidence level (0-1)
            evidence: Optional new evidence to add
            
        Returns:
            True if updated, False if not found
        """
        entry = self.get_doctrine(doctrine_id)
        if not entry:
            return False
        
        # Update confidence
        entry.confidence_level = max(0.0, min(1.0, new_confidence))
        entry.updated_at = datetime.utcnow()
        
        # Add new evidence if provided
        if evidence:
            entry.supporting_evidence.append({
                **evidence,
                "timestamp": datetime.utcnow().isoformat(),
            })
        
        # Update in repository and cache
        self.repository.update_doctrine(entry)
        self._doctrine_cache[doctrine_id] = entry
        
        return True
    
    def add_evidence(
        self,
        doctrine_id: str,
        evidence: Dict[str, Any],
    ) -> bool:
        """Add supporting evidence to a doctrine entry.
        
        Args:
            doctrine_id: The doctrine to add evidence to
            evidence: The evidence to add
            
        Returns:
            True if added, False if not found
        """
        entry = self.get_doctrine(doctrine_id)
        if not entry:
            return False
        
        evidence_entry = {
            **evidence,
            "timestamp": datetime.utcnow().isoformat(),
        }
        entry.supporting_evidence.append(evidence_entry)
        entry.updated_at = datetime.utcnow()
        
        self.repository.update_doctrine(entry)
        self._doctrine_cache[doctrine_id] = entry
        
        return True
    
    def evolve_doctrine(
        self,
        doctrine_id: str,
        outcome: Dict[str, Any],
    ) -> bool:
        """Evolve a doctrine entry based on system outcome.
        
        Args:
            doctrine_id: The doctrine to evolve
            outcome: The outcome to learn from
            
        Returns:
            True if evolved, False if not found
        """
        entry = self.get_doctrine(doctrine_id)
        if not entry:
            return False
        
        # Calculate confidence adjustment based on outcome
        success = outcome.get("success", 0.5)
        
        # If successful, increase confidence; if failed, decrease
        if success >= 0.7:
            adjustment = 0.1
        elif success >= 0.4:
            adjustment = 0.0  # No change
        else:
            adjustment = -0.1
        
        new_confidence = max(0.0, min(1.0, entry.confidence_level + adjustment))
        
        # Add outcome as evidence
        evidence = {
            "type": "outcome",
            "outcome": outcome,
            "confidence_adjustment": adjustment,
        }
        
        return self.update_doctrine_confidence(doctrine_id, new_confidence, evidence)
    
    # ============= Doctrine Deactivation =============
    
    def deactivate_doctrine(self, doctrine_id: str) -> bool:
        """Deactivate a doctrine entry.
        
        Args:
            doctrine_id: The doctrine to deactivate
            
        Returns:
            True if deactivated, False if not found
        """
        entry = self.get_doctrine(doctrine_id)
        if not entry:
            return False
        
        entry.is_active = False
        entry.updated_at = datetime.utcnow()
        
        self.repository.update_doctrine(entry)
        
        # Remove from cache
        if doctrine_id in self._doctrine_cache:
            del self._doctrine_cache[doctrine_id]
        
        return True
    
    def reactivate_doctrine(self, doctrine_id: str) -> bool:
        """Reactivate a previously deactivated doctrine.
        
        Args:
            doctrine_id: The doctrine to reactivate
            
        Returns:
            True if reactivated, False if not found
        """
        entry = self.get_doctrine(doctrine_id)
        if not entry:
            return False
        
        entry.is_active = True
        entry.updated_at = datetime.utcnow()
        
        self.repository.update_doctrine(entry)
        self._doctrine_cache[doctrine_id] = entry
        
        return True
    
    # ============= Search and Filter =============
    
    def search_doctrine(self, query: str) -> List[DoctrineEntry]:
        """Search doctrine entries.
        
        Args:
            query: Search query
            
        Returns:
            Matching doctrine entries
        """
        active = self.get_active_doctrine()
        results = []
        
        query_lower = query.lower()
        for entry in active:
            if query_lower in entry.strategic_rule.lower():
                results.append(entry)
            for evidence in entry.supporting_evidence:
                if query_lower in str(evidence).lower():
                    results.append(entry)
                    break
        
        return results
    
    def get_doctrine_by_origin(self, origin_cycle: str) -> List[DoctrineEntry]:
        """Get doctrine entries from a specific origin cycle.
        
        Args:
            origin_cycle: The cycle ID
            
        Returns:
            Doctrine entries from that cycle
        """
        active = self.get_active_doctrine()
        return [d for d in active if d.origin_cycle == origin_cycle]
    
    def get_high_confidence_doctrine(self, threshold: float = 0.8) -> List[DoctrineEntry]:
        """Get high-confidence doctrine entries.
        
        Args:
            threshold: Minimum confidence level
            
        Returns:
            High confidence doctrine entries
        """
        return self.get_doctrine_by_confidence(threshold)
    
    # ============= Statistics =============
    
    def get_doctrine_stats(self) -> Dict[str, Any]:
        """Get doctrine statistics.
        
        Returns:
            Statistics about doctrine entries
        """
        all_entries = self.repository.get_all_doctrine()
        active = self.get_active_doctrine()
        
        if not all_entries:
            return {
                "total": 0,
                "active": 0,
                "inactive": 0,
                "avg_confidence": 0.0,
            }
        
        confidences = [e.confidence_level for e in all_entries]
        
        return {
            "total": len(all_entries),
            "active": len(active),
            "inactive": len(all_entries) - len(active),
            "avg_confidence": sum(confidences) / len(confidences),
            "high_confidence": len([c for c in confidences if c >= 0.8]),
            "low_confidence": len([c for c in confidences if c < 0.3]),
        }
    
    def consolidate_doctrine(self) -> int:
        """Consolidate similar doctrine entries.
        
        Returns:
            Number of entries consolidated
        """
        # This is a placeholder for more sophisticated consolidation
        # For now, just return 0
        return 0
