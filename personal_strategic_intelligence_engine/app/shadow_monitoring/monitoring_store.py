"""Monitoring store for persisting shadow monitoring records.

Provides in-memory storage for cycle records, anomalies, and summaries.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.shadow_monitoring.monitoring_models import (
    LongHorizonReadinessAssessment,
    MonitoringAnomaly,
    MonitoringWindow,
    ShadowCycleRecord,
    ShadowOperationReport,
)


class MonitoringStore:
    """Store for shadow monitoring data."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize monitoring store.
        
        Args:
            storage_path: Optional path for file-backed storage
        """
        self.storage_path = storage_path
        self.cycles: List[ShadowCycleRecord] = []
        self.anomalies: List[MonitoringAnomaly] = []
        self.reports: List[ShadowOperationReport] = []
        self.assessments: List[LongHorizonReadinessAssessment] = []
        
        # Load from file if exists
        if storage_path:
            self._load()
    
    def store_cycle(self, record: ShadowCycleRecord) -> None:
        """Store a cycle record."""
        self.cycles.append(record)
        
        # Keep bounded
        if len(self.cycles) > 10000:
            self.cycles = self.cycles[-5000:]
    
    def store_anomaly(self, anomaly: MonitoringAnomaly) -> None:
        """Store an anomaly."""
        self.anomalies.append(anomaly)
        
        if len(self.anomalies) > 1000:
            self.anomalies = self.anomalies[-500:]
    
    def store_report(self, report: ShadowOperationReport) -> None:
        """Store a monitoring report."""
        self.reports.append(report)
        
        if len(self.reports) > 100:
            self.reports = self.reports[-50:]
    
    def store_assessment(self, assessment: LongHorizonReadinessAssessment) -> None:
        """Store a readiness assessment."""
        self.assessments.append(assessment)
        
        if len(self.assessments) > 100:
            self.assessments = self.assessments[-50:]
    
    def get_recent_cycles(self, count: int = 10) -> List[ShadowCycleRecord]:
        """Get recent cycles."""
        return self.cycles[-count:] if self.cycles else []
    
    def get_cycles_in_window(self, window: MonitoringWindow) -> List[ShadowCycleRecord]:
        """Get cycles within a time window."""
        now = datetime.utcnow()
        
        window_hours = {
            MonitoringWindow.ONE_DAY: 24,
            MonitoringWindow.SEVEN_DAYS: 24 * 7,
            MonitoringWindow.THIRTY_DAYS: 24 * 30,
        }
        
        hours = window_hours.get(window, 24)
        cutoff = now - timedelta(hours=hours)
        
        return [c for c in self.cycles if c.timestamp >= cutoff]
    
    def get_recent_anomalies(self, count: int = 10) -> List[MonitoringAnomaly]:
        """Get recent anomalies."""
        return self.anomalies[-count:] if self.anomalies else []
    
    def get_reports(self, count: int = 10) -> List[ShadowOperationReport]:
        """Get recent reports."""
        return self.reports[-count:] if self.reports else []
    
    def get_latest_assessment(self) -> Optional[LongHorizonReadinessAssessment]:
        """Get latest readiness assessment."""
        return self.assessments[-1] if self.assessments else None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get store statistics."""
        return {
            "total_cycles": len(self.cycles),
            "total_anomalies": len(self.anomalies),
            "total_reports": len(self.reports),
            "total_assessments": len(self.assessments),
            "oldest_cycle": self.cycles[0].timestamp.isoformat() if self.cycles else None,
            "newest_cycle": self.cycles[-1].timestamp.isoformat() if self.cycles else None,
        }
    
    def clear(self) -> None:
        """Clear all stored data."""
        self.cycles = []
        self.anomalies = []
        self.reports = []
        self.assessments = []
    
    def _load(self) -> None:
        """Load data from file."""
        if not self.storage_path:
            return
        
        path = Path(self.storage_path)
        if not path.exists():
            return
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                
                # Load cycles
                self.cycles = [
                    ShadowCycleRecord(**c) for c in data.get('cycles', [])
                ]
                
                # Load anomalies
                self.anomalies = [
                    MonitoringAnomaly(**a) for a in data.get('anomalies', [])
                ]
                
        except Exception:
            pass  # Start fresh if load fails
    
    def _save(self) -> None:
        """Save data to file."""
        if not self.storage_path:
            return
        
        try:
            path = Path(self.storage_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'cycles': [c.model_dump() for c in self.cycles[-100:]],
                'anomalies': [a.model_dump() for a in self.anomalies[-50:]],
            }
            
            with open(path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception:
            pass  # Silently fail if save fails
    
    def persist(self) -> None:
        """Persist data to storage."""
        self._save()


def create_monitoring_store(storage_path: Optional[str] = None) -> MonitoringStore:
    """Factory function to create a monitoring store."""
    return MonitoringStore(storage_path=storage_path)
