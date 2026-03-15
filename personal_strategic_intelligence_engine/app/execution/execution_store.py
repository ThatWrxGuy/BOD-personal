"""Execution store - persistent storage of execution history."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.execution.execution_models import ExecutionRecord

logger = logging.getLogger(__name__)


class ExecutionStore:
    """Stores and retrieves execution history."""

    def __init__(self):
        self._records: Dict[str, ExecutionRecord] = {}

    def store(self, record: ExecutionRecord) -> bool:
        """Store an execution record."""
        try:
            self._records[record.intent.intent_id] = record
            logger.info(f"Stored execution record: {record.intent.intent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store record: {e}")
            return False

    def get(self, intent_id: str) -> Optional[ExecutionRecord]:
        """Get an execution record by intent ID."""
        return self._records.get(intent_id)

    def get_by_decision_id(self, decision_id: str) -> Optional[ExecutionRecord]:
        """Get an execution record by decision ID."""
        for record in self._records.values():
            if record.decision.decision_id == decision_id:
                return record
        return None

    def get_all(self, limit: int = 100) -> List[ExecutionRecord]:
        """Get all execution records."""
        records = sorted(
            self._records.values(),
            key=lambda r: r.updated_at,
            reverse=True,
        )
        return records[:limit]

    def get_by_status(self, status: str, limit: int = 100) -> List[ExecutionRecord]:
        """Get execution records by status."""
        records = [
            r for r in self._records.values()
            if r.decision.status.value == status
        ]
        records.sort(key=lambda r: r.updated_at, reverse=True)
        return records[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self._records:
            return {
                "total_records": 0,
                "by_status": {},
            }
        
        by_status = {}
        for record in self._records.values():
            status = record.decision.status.value
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            "total_records": len(self._records),
            "by_status": by_status,
        }

    def clear(self):
        """Clear all stored records."""
        self._records.clear()


# Global store instance
_store: Optional["ExecutionStore"] = None


def get_execution_store() -> ExecutionStore:
    """Get the global execution store instance."""
    global _store
    if _store is None:
        _store = ExecutionStore()
    return _store
