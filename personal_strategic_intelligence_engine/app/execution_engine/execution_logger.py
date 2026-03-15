"""Execution Logger - maintains permanent execution history.

The execution logger provides an audit trail of all system actions.
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.execution_engine.execution_models import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionRecord,
    ExecutionStatistics,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class ExecutionLogger:
    """
    Maintains permanent execution history.
    
    Execution records include:
    - execution ID
    - associated proposal
    - action type
    - parameters
    - execution result
    - timestamp
    
    This ensures full auditability of system actions.
    """
    
    def __init__(self):
        self._records: Dict[str, ExecutionRecord] = {}
    
    async def log_execution(
        self,
        request: ExecutionRequest,
        result: ExecutionResult,
    ) -> ExecutionRecord:
        """
        Log a successful execution.
        
        Args:
            request: The execution request
            result: The execution result
            
        Returns:
            The created execution record
        """
        record = ExecutionRecord(
            execution_id=request.id,
            proposal_id=request.proposal_id,
            governance_decision_id=request.governance_decision_id,
            action_type=request.action_type,
            parameters=request.parameters,
            status="completed",
            result=result.result_data,
            risk_level=request.risk_level,
            approved_by=request.approved_by,
            execution_duration_ms=request.execution_duration_ms,
            created_at=request.created_at,
            executed_at=request.executed_at,
            completed_at=request.completed_at,
        )
        
        self._records[record.record_id] = record
        
        logger.info(f"Logged execution: {record.record_id}")
        
        return record
    
    async def log_failure(
        self,
        request: ExecutionRequest,
        error: str,
    ) -> ExecutionRecord:
        """
        Log a failed execution.
        
        Args:
            request: The execution request
            error: The error message
            
        Returns:
            The created execution record
        """
        record = ExecutionRecord(
            execution_id=request.id,
            proposal_id=request.proposal_id,
            governance_decision_id=request.governance_decision_id,
            action_type=request.action_type,
            parameters=request.parameters,
            status="failed",
            error_message=error,
            risk_level=request.risk_level,
            approved_by=request.approved_by,
            execution_duration_ms=request.execution_duration_ms,
            created_at=request.created_at,
            executed_at=request.executed_at,
            completed_at=request.completed_at,
        )
        
        self._records[record.record_id] = record
        
        logger.warning(f"Logged execution failure: {record.record_id} - {error}")
        
        return record
    
    def get_record(self, record_id: str) -> Optional[ExecutionRecord]:
        """Get an execution record by ID."""
        return self._records.get(record_id)
    
    def get_by_execution_id(self, execution_id: str) -> Optional[ExecutionRecord]:
        """Get an execution record by execution ID."""
        for record in self._records.values():
            if record.execution_id == execution_id:
                return record
        return None
    
    def get_by_proposal(self, proposal_id: str) -> List[ExecutionRecord]:
        """Get all execution records for a proposal."""
        return [
            r for r in self._records.values()
            if r.proposal_id == proposal_id
        ]
    
    def get_by_status(self, status: str) -> List[ExecutionRecord]:
        """Get all execution records with a specific status."""
        return [
            r for r in self._records.values()
            if r.status == status
        ]
    
    def get_by_action_type(self, action_type: str) -> List[ExecutionRecord]:
        """Get all execution records for a specific action type."""
        return [
            r for r in self._records.values()
            if r.action_type == action_type
        ]
    
    def get_history(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ExecutionRecord]:
        """Get execution history with pagination."""
        sorted_records = sorted(
            self._records.values(),
            key=lambda r: r.created_at,
            reverse=True,
        )
        return sorted_records[offset:offset + limit]
    
    def get_statistics(self) -> ExecutionStatistics:
        """Get execution statistics."""
        records = list(self._records.values())
        
        if not records:
            return ExecutionStatistics()
        
        total = len(records)
        completed = sum(1 for r in records if r.status == "completed")
        failed = sum(1 for r in records if r.status == "failed")
        pending = sum(1 for r in records if r.status == "pending")
        in_progress = sum(1 for r in records if r.status == "executing")
        
        # Count by action type
        by_action_type: Dict[str, int] = {}
        for r in records:
            by_action_type[r.action_type] = by_action_type.get(r.action_type, 0) + 1
        
        # Count by status
        by_status: Dict[str, int] = {}
        for r in records:
            by_status[r.status] = by_status.get(r.status, 0) + 1
        
        # Calculate average execution time
        execution_times = [
            r.execution_duration_ms for r in records
            if r.execution_duration_ms is not None
        ]
        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0.0
        
        # Calculate success rate
        success_rate = completed / total if total > 0 else 0.0
        
        return ExecutionStatistics(
            total_executions=total,
            completed=completed,
            failed=failed,
            pending=pending,
            in_progress=in_progress,
            by_action_type=by_action_type,
            by_status=by_status,
            average_execution_time_ms=avg_time,
            success_rate=success_rate,
        )
    
    def search(
        self,
        query: str,
        limit: int = 50,
    ) -> List[ExecutionRecord]:
        """Search execution records."""
        results = []
        query_lower = query.lower()
        
        for record in self._records.values():
            if query_lower in record.action_type.lower():
                results.append(record)
            elif record.result and query_lower in str(record.result).lower():
                results.append(record)
        
        return results[:limit]
    
    def clear_history(self) -> int:
        """Clear all execution history (use with caution)."""
        count = len(self._records)
        self._records.clear()
        logger.warning(f"Cleared {count} execution records")
        return count


# Singleton instance
_execution_logger: Optional[ExecutionLogger] = None


def get_execution_logger() -> ExecutionLogger:
    """Get the global execution logger instance."""
    global _execution_logger
    if _execution_logger is None:
        _execution_logger = ExecutionLogger()
    return _execution_logger


def reset_execution_logger() -> None:
    """Reset the execution logger (for testing)."""
    global _execution_logger
    _execution_logger = None
