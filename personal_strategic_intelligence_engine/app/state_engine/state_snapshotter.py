"""State snapshotter for capturing historical state."""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from app.state_engine.state_models import SystemStateSnapshot, SnapshotRecord
from app.state_engine.state_repository import StateRepository


class StateSnapshotter:
    """Captures and manages historical state snapshots.
    
    Responsible for:
    - Capturing full system state at the end of each strategy loop cycle
    - Storing historical snapshots
    - Enabling historical comparison
    """
    
    def __init__(self, repository: Optional[StateRepository] = None):
        self.repository = repository or StateRepository()
        self._snapshot_history: List[SnapshotRecord] = []
    
    def capture_snapshot(
        self,
        state: SystemStateSnapshot,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SnapshotRecord:
        """Capture a snapshot of the current system state.
        
        Args:
            state: The system state to capture
            metadata: Optional metadata about this snapshot
            
        Returns:
            The created snapshot record
        """
        snapshot_id = f"snap_{uuid.uuid4().hex[:12]}"
        
        record = SnapshotRecord(
            snapshot_id=snapshot_id,
            cycle_id=state.cycle_id or "unknown",
            timestamp=datetime.utcnow(),
            state=state,
            metadata=metadata or {},
        )
        
        # Store in memory and persistence
        self._snapshot_history.append(record)
        self.repository.store_snapshot(state)
        
        return record
    
    def capture_cycle_snapshot(self, state: SystemStateSnapshot) -> str:
        """Capture a snapshot for a completed cycle.
        
        Args:
            state: The system state at cycle completion
            
        Returns:
            The snapshot ID
        """
        record = self.capture_snapshot(
            state,
            metadata={"event": "cycle_complete", "cycle_id": state.cycle_id}
        )
        return record.snapshot_id
    
    def get_snapshot(self, snapshot_id: str) -> Optional[SnapshotRecord]:
        """Retrieve a specific snapshot by ID.
        
        Args:
            snapshot_id: The ID of the snapshot to retrieve
            
        Returns:
            The snapshot record, or None if not found
        """
        # Check memory first
        for record in self._snapshot_history:
            if record.snapshot_id == snapshot_id:
                return record
        
        # Check persistence
        snapshots = self.repository.get_recent_snapshots(limit=1000)
        for snap in snapshots:
            if f"snap_{snap.cycle_id}" == snapshot_id or snap.cycle_id == snapshot_id:
                return SnapshotRecord(
                    snapshot_id=snapshot_id,
                    cycle_id=snap.cycle_id,
                    timestamp=snap.timestamp,
                    state=snap,
                    metadata={},
                )
        
        return None
    
    def get_recent_snapshots(self, limit: int = 10) -> List[SnapshotRecord]:
        """Get the most recent snapshots.
        
        Args:
            limit: Maximum number of snapshots to retrieve
            
        Returns:
            List of recent snapshot records
        """
        # Combine memory and persistence
        all_snapshots = list(self._snapshot_history)
        
        # Add from persistence if needed
        if len(all_snapshots) < limit:
            persistant = self.repository.get_recent_snapshots(limit)
            for snap in persistant:
                exists = any(s.snapshot_id == snap.cycle_id for s in all_snapshots)
                if not exists:
                    all_snapshots.append(SnapshotRecord(
                        snapshot_id=snap.cycle_id or "unknown",
                        cycle_id=snap.cycle_id,
                        timestamp=snap.timestamp,
                        state=snap,
                        metadata={},
                    ))
        
        # Sort by timestamp, most recent first
        all_snapshots.sort(key=lambda x: x.timestamp, reverse=True)
        return all_snapshots[:limit]
    
    def get_snapshots_by_time_range(
        self,
        start: datetime,
        end: datetime,
    ) -> List[SnapshotRecord]:
        """Get snapshots within a time range.
        
        Args:
            start: Start of time range
            end: End of time range
            
        Returns:
            List of snapshots in the time range
        """
        results = []
        
        for record in self._snapshot_history:
            if start <= record.timestamp <= end:
                results.append(record)
        
        # Also check persistence
        all_snapshots = self.repository.get_recent_snapshots(limit=1000)
        for snap in all_snapshots:
            if start <= snap.timestamp <= end:
                exists = any(s.state.cycle_id == snap.cycle_id for s in results)
                if not exists:
                    results.append(SnapshotRecord(
                        snapshot_id=snap.cycle_id or "unknown",
                        cycle_id=snap.cycle_id,
                        timestamp=snap.timestamp,
                        state=snap,
                        metadata={},
                    ))
        
        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results
    
    def get_snapshots_by_cycle(self, cycle_id: str) -> List[SnapshotRecord]:
        """Get all snapshots for a specific cycle.
        
        Args:
            cycle_id: The cycle ID to search for
            
        Returns:
            List of snapshots for the cycle
        """
        results = []
        
        for record in self._snapshot_history:
            if record.cycle_id == cycle_id:
                results.append(record)
        
        # Check persistence
        persisted = self.repository.get_snapshots_by_cycle(cycle_id)
        for snap in persisted:
            results.append(SnapshotRecord(
                snapshot_id=snap.cycle_id or "unknown",
                cycle_id=snap.cycle_id,
                timestamp=snap.timestamp,
                state=snap,
                metadata={},
            ))
        
        return results
    
    def compare_snapshots(
        self,
        snapshot_id1: str,
        snapshot_id2: str,
    ) -> Dict[str, Any]:
        """Compare two snapshots.
        
        Args:
            snapshot_id1: First snapshot ID
            snapshot_id2: Second snapshot ID
            
        Returns:
            Dictionary of differences between snapshots
        """
        snap1 = self.get_snapshot(snapshot_id1)
        snap2 = self.get_snapshot(snapshot_id2)
        
        if not snap1 or not snap2:
            return {"error": "One or both snapshots not found"}
        
        # Compare key metrics
        return {
            "snapshot1": {
                "cycle_id": snap1.cycle_id,
                "timestamp": snap1.timestamp.isoformat(),
            },
            "snapshot2": {
                "cycle_id": snap2.cycle_id,
                "timestamp": snap2.timestamp.isoformat(),
            },
            "differences": {
                "tasks": {
                    "before": len(snap1.state.operational_state.current_tasks),
                    "after": len(snap2.state.operational_state.current_tasks),
                },
                "goals": {
                    "before": len(snap1.state.goal_state.active_goals),
                    "after": len(snap2.state.goal_state.active_goals),
                },
                "risks": {
                    "before": len(snap1.state.risk_state.identified_risks),
                    "after": len(snap2.state.risk_state.identified_risks),
                },
                "confidence": {
                    "before": snap1.state.strategic_state.confidence_score,
                    "after": snap2.state.strategic_state.confidence_score,
                },
            },
        }
    
    def get_trend_data(self, metric: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get trend data for a specific metric over time.
        
        Args:
            metric: The metric to track (e.g., 'confidence', 'tasks', 'goals')
            days: Number of days to look back
            
        Returns:
            List of metric values over time
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        snapshots = self.get_snapshots_by_time_range(start_date, datetime.utcnow())
        
        results = []
        for snap in snapshots:
            value = None
            
            if metric == "confidence":
                value = snap.state.strategic_state.confidence_score
            elif metric == "tasks":
                value = len(snap.state.operational_state.current_tasks)
            elif metric == "goals":
                value = len(snap.state.goal_state.active_goals)
            elif metric == "risks":
                value = len(snap.state.risk_state.identified_risks)
            elif metric == "high_priority_risks":
                value = len(snap.state.risk_state.high_priority_risks)
            
            if value is not None:
                results.append({
                    "timestamp": snap.timestamp.isoformat(),
                    "cycle_id": snap.cycle_id,
                    "value": value,
                })
        
        return results
    
    def get_snapshot_count(self) -> int:
        """Get total number of snapshots."""
        return len(self._snapshot_history)
    
    def clear_history(self):
        """Clear in-memory snapshot history."""
        self._snapshot_history.clear()
