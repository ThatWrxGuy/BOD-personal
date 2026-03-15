"""Doctrine store for persisting doctrine evaluations."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.doctrine.doctrine_models import DoctrineAssessment, DoctrineEvent

logger = logging.getLogger(__name__)


class DoctrineStore:
    """Store and retrieve doctrine evaluations."""

    def __init__(self):
        self._assessments: Dict[str, DoctrineAssessment] = {}
        self._cycle_assessments: Dict[str, List[str]] = {}
        self._events: List[DoctrineEvent] = []

    def store_assessment(self, assessment: DoctrineAssessment) -> bool:
        """Store a doctrine assessment."""
        try:
            self._assessments[assessment.cycle_id] = assessment
            
            # Index by cycle
            if assessment.cycle_id not in self._cycle_assessments:
                self._cycle_assessments[assessment.cycle_id] = []
            self._cycle_assessments[assessment.cycle_id].append(assessment.cycle_id)
            
            # Log event
            event = DoctrineEvent(
                event_type="assessment_stored",
                cycle_id=assessment.cycle_id,
                alignment_level=assessment.alignment_score.level.value,
                rules_evaluated=len(assessment.policy_rules_applied),
            )
            self._events.append(event)
            
            logger.info(f"Stored doctrine assessment for cycle: {assessment.cycle_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store assessment: {e}")
            return False

    def get_assessment(self, cycle_id: str) -> Optional[DoctrineAssessment]:
        """Get a doctrine assessment by cycle ID."""
        return self._assessments.get(cycle_id)

    def get_assessments_for_cycles(self, cycle_ids: List[str]) -> List[DoctrineAssessment]:
        """Get assessments for multiple cycles."""
        return [self._assessments[cid] for cid in cycle_ids if cid in self._assessments]

    def get_recent_assessments(self, limit: int = 10) -> List[DoctrineAssessment]:
        """Get recent doctrine assessments."""
        assessments = sorted(
            self._assessments.values(),
            key=lambda a: a.timestamp,
            reverse=True
        )
        return assessments[:limit]

    def get_assessments_by_alignment(
        self,
        alignment_level: str,
        limit: int = 10
    ) -> List[DoctrineAssessment]:
        """Get assessments by alignment level."""
        assessments = [
            a for a in self._assessments.values()
            if a.alignment_score.level.value == alignment_level
        ]
        assessments.sort(key=lambda a: a.timestamp, reverse=True)
        return assessments[:limit]

    def get_conflicts(self, min_severity: float = 0.5) -> List[Dict[str, Any]]:
        """Get all conflicts above a severity threshold."""
        conflicts = []
        
        for assessment in self._assessments.values():
            for conflict in assessment.doctrine_conflicts:
                if conflict.severity >= min_severity:
                    conflicts.append({
                        "cycle_id": assessment.cycle_id,
                        "timestamp": assessment.timestamp,
                        "conflict": conflict.model_dump(),
                    })
        
        conflicts.sort(key=lambda c: c["conflict"]["severity"], reverse=True)
        return conflicts

    def get_statistics(self) -> Dict[str, Any]:
        """Get doctrine store statistics."""
        
        if not self._assessments:
            return {
                "total_assessments": 0,
                "alignment_distribution": {},
                "total_conflicts": 0,
            }
        
        # Count by alignment level
        distribution = {}
        for a in self._assessments.values():
            level = a.alignment_score.level.value
            distribution[level] = distribution.get(level, 0) + 1
        
        # Count conflicts
        total_conflicts = sum(
            len(a.doctrine_conflicts) for a in self._assessments.values()
        )
        
        return {
            "total_assessments": len(self._assessments),
            "alignment_distribution": distribution,
            "total_conflicts": total_conflicts,
        }

    def clear(self):
        """Clear all stored data."""
        self._assessments.clear()
        self._cycle_assessments.clear()
        self._events.clear()


# Global store instance
_store: Optional[DoctrineStore] = None


def get_doctrine_store() -> DoctrineStore:
    """Get the global doctrine store instance."""
    global _store
    if _store is None:
        _store = DoctrineStore()
    return _store
