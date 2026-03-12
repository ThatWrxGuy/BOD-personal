"""State repository for persistence."""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from app.state_engine.state_models import (
    SystemStateSnapshot,
    SnapshotRecord,
    MemoryEntry,
    DoctrineEntry,
)
from app.state_engine.state_types import MemoryTier


class StateRepository:
    """Repository for persisting state data."""
    
    def __init__(self, base_path: str = "data/state"):
        self.base_path = Path(base_path)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure storage directories exist."""
        dirs = ["snapshots", "memory", "doctrine"]
        for d in dirs:
            (self.base_path / d).mkdir(parents=True, exist_ok=True)
    
    # ============= Snapshot Operations =============
    
    def store_snapshot(self, snapshot: SystemStateSnapshot) -> str:
        """Store a state snapshot."""
        timestamp = snapshot.timestamp.strftime("%Y%m%d_%H%M%S")
        cycle_suffix = f"_{snapshot.cycle_id}" if snapshot.cycle_id else ""
        filename = f"snapshot_{timestamp}{cycle_suffix}.json"
        filepath = self.base_path / "snapshots" / filename
        
        with open(filepath, "w") as f:
            json.dump(snapshot.to_dict(), f, indent=2, default=str)
        
        return filename
    
    def get_snapshot(self, snapshot_id: str) -> Optional[SystemStateSnapshot]:
        """Retrieve a specific snapshot."""
        filepath = self.base_path / "snapshots" / snapshot_id
        if not filepath.exists():
            return None
        
        with open(filepath, "r") as f:
            data = json.load(f)
        
        return SystemStateSnapshot(**data)
    
    def get_recent_snapshots(self, limit: int = 10) -> List[SystemStateSnapshot]:
        """Get most recent snapshots."""
        snapshots_dir = self.base_path / "snapshots"
        if not snapshots_dir.exists():
            return []
        
        files = sorted(snapshots_dir.glob("snapshot_*.json"), reverse=True)
        results = []
        
        for f in files[:limit]:
            with open(f, "r") as fp:
                data = json.load(fp)
                results.append(SystemStateSnapshot(**data))
        
        return results
    
    def get_snapshots_by_cycle(self, cycle_id: str) -> List[SystemStateSnapshot]:
        """Get snapshots for a specific cycle."""
        snapshots_dir = self.base_path / "snapshots"
        if not snapshots_dir.exists():
            return []
        
        files = snapshots_dir.glob(f"snapshot_*_{cycle_id}.json")
        results = []
        
        for f in files:
            with open(f, "r") as fp:
                data = json.load(fp)
                results.append(SystemStateSnapshot(**data))
        
        return results
    
    # ============= Memory Operations =============
    
    def store_memory(self, entry: MemoryEntry) -> str:
        """Store a memory entry."""
        tier_dir = self.base_path / "memory" / entry.memory_type
        tier_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{entry.entry_id}.json"
        filepath = tier_dir / filename
        
        with open(filepath, "w") as f:
            json.dump(entry.model_dump(), f, indent=2, default=str)
        
        return filename
    
    def get_memory(self, entry_id: str, memory_type: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry."""
        filepath = self.base_path / "memory" / memory_type / f"{entry_id}.json"
        if not filepath.exists():
            return None
        
        with open(filepath, "r") as f:
            data = json.load(f)
        
        return MemoryEntry(**data)
    
    def get_memory_by_tier(self, tier: MemoryTier, limit: int = 100) -> List[MemoryEntry]:
        """Get memory entries by tier."""
        tier_dir = self.base_path / "memory" / tier.value
        if not tier_dir.exists():
            return []
        
        files = sorted(tier_dir.glob("*.json"), reverse=True)
        results = []
        
        for f in files[:limit]:
            with open(f, "r") as fp:
                data = json.load(fp)
                results.append(MemoryEntry(**data))
        
        return results
    
    def get_all_memory(self, limit: int = 100) -> List[MemoryEntry]:
        """Get all memory entries across tiers."""
        results = []
        
        for tier in MemoryTier:
            tier_entries = self.get_memory_by_tier(tier, limit)
            results.extend(tier_entries)
        
        # Sort by timestamp, most recent first
        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results[:limit]
    
    def delete_memory(self, entry_id: str, memory_type: str) -> bool:
        """Delete a memory entry."""
        filepath = self.base_path / "memory" / memory_type / f"{entry_id}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False
    
    # ============= Doctrine Operations =============
    
    def store_doctrine(self, doctrine: DoctrineEntry) -> str:
        """Store a doctrine entry."""
        filepath = self.base_path / "doctrine" / f"{doctrine.doctrine_id}.json"
        
        with open(filepath, "w") as f:
            json.dump(doctrine.model_dump(), f, indent=2, default=str)
        
        return doctrine.doctrine_id
    
    def get_doctrine(self, doctrine_id: str) -> Optional[DoctrineEntry]:
        """Retrieve a doctrine entry."""
        filepath = self.base_path / "doctrine" / f"{doctrine_id}.json"
        if not filepath.exists():
            return None
        
        with open(filepath, "r") as f:
            data = json.load(f)
        
        return DoctrineEntry(**data)
    
    def get_active_doctrine(self) -> List[DoctrineEntry]:
        """Get all active doctrine entries."""
        doctrine_dir = self.base_path / "doctrine"
        if not doctrine_dir.exists():
            return []
        
        results = []
        for f in doctrine_dir.glob("*.json"):
            with open(f, "r") as fp:
                data = json.load(fp)
                doctrine = DoctrineEntry(**data)
                if doctrine.is_active:
                    results.append(doctrine)
        
        return results
    
    def get_all_doctrine(self) -> List[DoctrineEntry]:
        """Get all doctrine entries."""
        doctrine_dir = self.base_path / "doctrine"
        if not doctrine_dir.exists():
            return []
        
        results = []
        for f in doctrine_dir.glob("*.json"):
            with open(f, "r") as fp:
                data = json.load(fp)
                results.append(DoctrineEntry(**data))
        
        return results
    
    def update_doctrine(self, doctrine: DoctrineEntry) -> bool:
        """Update a doctrine entry."""
        filepath = self.base_path / "doctrine" / f"{doctrine.doctrine_id}.json"
        if not filepath.exists():
            return False
        
        with open(filepath, "w") as f:
            json.dump(doctrine.model_dump(), f, indent=2, default=str)
        
        return True
    
    def delete_doctrine(self, doctrine_id: str) -> bool:
        """Delete a doctrine entry."""
        filepath = self.base_path / "doctrine" / f"{doctrine_id}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False
