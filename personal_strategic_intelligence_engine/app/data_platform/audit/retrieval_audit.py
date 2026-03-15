"""Retrieval Logging and Audit - Log retrieval activity for audit purposes.

Records retrieval activity including:
- Requesting agent
- Sources accessed
- Timestamp
- Policy decisions
- Retrieval latency
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class RetrievalLogEntry(BaseModel):
    """Log entry for a retrieval request."""
    entry_id: UUID = Field(default_factory=uuid4)
    request_id: UUID = Field(..., description="Original request ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Agent info
    agent_id: Optional[str] = Field(None, description="Agent ID")
    agent_type: str = Field(..., description="Agent type")
    agent_domain: Optional[str] = Field(None, description="Agent domain")
    
    # Request details
    query: str = Field(..., description="Search query")
    domains_requested: List[str] = Field(default_factory=list, description="Domains requested")
    
    # Sources accessed
    sources_accessed: List[str] = Field(default_factory=list, description="Source IDs accessed")
    sources_blocked: List[str] = Field(default_factory=list, description="Blocked sources")
    
    # Policy decisions
    policy_applied: str = Field(..., description="Policy applied")
    policy_decisions: Dict[str, Any] = Field(default_factory=dict, description="Policy decision details")
    access_granted: bool = Field(..., description="Whether access was granted")
    denial_reason: Optional[str] = Field(None, description="Reason for denial if any")
    
    # Results
    results_count: int = Field(0, description="Number of results returned")
    
    # Performance
    latency_ms: float = Field(..., description="Retrieval latency in milliseconds")
    
    # Error handling
    error: Optional[str] = Field(None, description="Error message if any")


class RetrievalAuditLogger:
    """Logs retrieval activity for audit purposes."""
    
    def __init__(self):
        self._logs: List[RetrievalLogEntry] = []
        self._max_logs = 10000  # Keep last 10k logs
    
    async def log_request(
        self,
        entry: RetrievalLogEntry,
    ) -> None:
        """Log a retrieval request.
        
        Args:
            entry: Retrieval log entry
        """
        # Store in memory (in production, would write to database)
        self._logs.append(entry)
        
        # Trim old logs
        if len(self._logs) > self._max_logs:
            self._logs = self._logs[-self._max_logs:]
        
        # Log to standard logger
        logger.info(
            f"Retrieval: agent={entry.agent_type}, query='{entry.query[:50]}', "
            f"sources={len(entry.sources_accessed)}, results={entry.results_count}, "
            f"latency={entry.latency_ms:.2f}ms"
        )
    
    async def get_logs(
        self,
        agent_type: Optional[str] = None,
        domain: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[RetrievalLogEntry]:
        """Get retrieval logs with filters.
        
        Args:
            agent_type: Filter by agent type
            domain: Filter by domain
            since: Filter by timestamp
            limit: Maximum logs to return
            
        Returns:
            List of matching log entries
        """
        results = []
        
        for entry in reversed(self._logs):
            # Apply filters
            if agent_type and entry.agent_type != agent_type:
                continue
            if domain and domain not in entry.domains_requested:
                continue
            if since and entry.timestamp < since:
                continue
            
            results.append(entry)
            
            if len(results) >= limit:
                break
        
        return results
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get retrieval statistics.
        
        Returns:
            Statistics dictionary
        """
        total_requests = len(self._logs)
        
        if total_requests == 0:
            return {
                "total_requests": 0,
                "avg_latency_ms": 0,
                "denied_requests": 0,
            }
        
        total_latency = sum(e.latency_ms for e in self._logs)
        denied_count = sum(1 for e in self._logs if not e.access_granted)
        
        # Count by agent type
        by_agent_type: Dict[str, int] = {}
        for entry in self._logs:
            by_agent_type[entry.agent_type] = by_agent_type.get(entry.agent_type, 0) + 1
        
        return {
            "total_requests": total_requests,
            "avg_latency_ms": total_latency / total_requests,
            "denied_requests": denied_count,
            "denial_rate": denied_count / total_requests,
            "by_agent_type": by_agent_type,
        }


# Singleton
_audit_logger: Optional[RetrievalAuditLogger] = None


def get_retrieval_audit_logger() -> RetrievalAuditLogger:
    """Get the retrieval audit logger singleton."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = RetrievalAuditLogger()
    return _audit_logger
