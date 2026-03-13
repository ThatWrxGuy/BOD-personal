"""Calibration Store.

Persists calibration outputs and summaries.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.signal_calibration.calibration_models import (
    CalibratedSignal,
    CalibrationSummary,
)


class CalibrationStore:
    """Store for calibration data persistence."""
    
    def __init__(self, storage_path: Optional[str] = None):
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            # Default to data directory
            base_path = Path(__file__).parent.parent.parent / "data" / "calibration"
            self.storage_path = base_path
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self._signals_file = self.storage_path / "calibrated_signals.json"
        self._summary_file = self.storage_path / "calibration_summaries.json"
        
        # Initialize files if they don't exist
        if not self._signals_file.exists():
            self._write_json(self._signals_file, [])
        if not self._summary_file.exists():
            self._write_json(self._summary_file, [])
    
    def _read_json(self, filepath: Path) -> Any:
        """Read JSON from file."""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def _write_json(self, filepath: Path, data: Any) -> None:
        """Write JSON to file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    # Calibrated Signals
    
    def save_calibrated_signal(self, signal: CalibratedSignal) -> None:
        """Save a calibrated signal."""
        signals = self._read_json(self._signals_file) or []
        signals.append(signal.model_dump())
        
        # Keep only last 1000 signals
        if len(signals) > 1000:
            signals = signals[-1000:]
        
        self._write_json(self._signals_file, signals)
    
    def save_calibrated_signals(self, signals: List[CalibratedSignal]) -> None:
        """Save multiple calibrated signals."""
        for signal in signals:
            self.save_calibrated_signal(signal)
    
    def get_calibrated_signals(
        self,
        signal_id: Optional[str] = None,
        domain: Optional[str] = None,
        limit: int = 100,
    ) -> List[CalibratedSignal]:
        """Get calibrated signals."""
        signals = self._read_json(self._signals_file) or []
        
        if signal_id:
            signals = [s for s in signals if s.get("signal_id") == signal_id]
        
        if domain:
            signals = [s for s in signals if s.get("domain") == domain]
        
        # Return most recent
        return [CalibratedSignal(**s) for s in signals[-limit:]]
    
    # Calibration Summaries
    
    def save_summary(self, summary: CalibrationSummary) -> None:
        """Save a calibration summary."""
        summaries = self._read_json(self._summary_file) or []
        summaries.append(summary.model_dump())
        
        # Keep only last 100 summaries
        if len(summaries) > 100:
            summaries = summaries[-100:]
        
        self._write_json(self._summary_file, summaries)
    
    def get_summaries(
        self,
        limit: int = 10,
    ) -> List[CalibrationSummary]:
        """Get calibration summaries."""
        summaries = self._read_json(self._summary_file) or []
        return [CalibrationSummary(**s) for s in summaries[-limit:]]
    
    # Cleanup
    
    def clear_signals(self, older_than_days: Optional[int] = None) -> int:
        """Clear old calibrated signals."""
        signals = self._read_json(self._signals_file) or []
        
        if older_than_days is None:
            # Clear all
            self._write_json(self._signals_file, [])
            return len(signals)
        
        # Clear signals older than specified days
        cutoff = datetime.utcnow().timestamp() - (older_than_days * 86400)
        original_count = len(signals)
        signals = [
            s for s in signals
            if s.get("calibrated_at", 0) > cutoff
        ]
        
        self._write_json(self._signals_file, signals)
        return original_count - len(signals)


# Global store instance
_calibration_store: Optional[CalibrationStore] = None


def get_calibration_store() -> CalibrationStore:
    """Get the global calibration store instance."""
    global _calibration_store
    if _calibration_store is None:
        _calibration_store = CalibrationStore()
    return _calibration_store
