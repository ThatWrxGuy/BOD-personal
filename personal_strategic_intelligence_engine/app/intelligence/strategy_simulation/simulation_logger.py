"""Simulation Logger.

Persists simulation results and research data.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

from app.intelligence.strategy_simulation.simulation_models import (
    SimulationResult,
    SimulationSnapshot,
)


class SimulationLogger:
    """Logs simulation results and research."""
    
    def __init__(self, storage_path: Optional[str] = None):
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path(__file__).parent / "data"
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.simulations_file = self.storage_path / "simulations.jsonl"
        self.comparisons_file = self.storage_path / "comparisons.jsonl"
        self.discoveries_file = self.storage_path / "discoveries.jsonl"
        self.proposals_file = self.storage_path / "proposals.jsonl"
    
    def log_simulation(self, result: SimulationResult) -> None:
        """Log a simulation result."""
        with open(self.simulations_file, "a") as f:
            f.write(json.dumps(result.to_dict()) + "\n")
    
    def log_comparison(self, comparison: Dict) -> None:
        """Log a strategy comparison."""
        with open(self.comparisons_file, "a") as f:
            f.write(json.dumps(comparison) + "\n")
    
    def log_discovery(self, discovery: Dict) -> None:
        """Log a strategy discovery."""
        with open(self.discoveries_file, "a") as f:
            f.write(json.dumps(discovery) + "\n")
    
    def log_proposal(self, proposal: Dict) -> None:
        """Log an optimization proposal."""
        with open(self.proposals_file, "a") as f:
            f.write(json.dumps(proposal) + "\n")
    
    def get_simulations(self, limit: int = 50) -> List[Dict]:
        """Get simulation results."""
        if not self.simulations_file.exists():
            return []
        
        results = []
        with open(self.simulations_file, "r") as f:
            for line in f:
                try:
                    results.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        return results[-limit:]
    
    def get_comparisons(self, limit: int = 20) -> List[Dict]:
        """Get strategy comparisons."""
        if not self.comparisons_file.exists():
            return []
        
        results = []
        with open(self.comparisons_file, "r") as f:
            for line in f:
                try:
                    results.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        return results[-limit:]
    
    def get_discoveries(self, limit: int = 20) -> List[Dict]:
        """Get strategy discoveries."""
        if not self.discoveries_file.exists():
            return []
        
        results = []
        with open(self.discoveries_file, "r") as f:
            for line in f:
                try:
                    results.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        return results[-limit:]
    
    def get_proposals(self, status: Optional[str] = None) -> List[Dict]:
        """Get optimization proposals."""
        if not self.proposals_file.exists():
            return []
        
        results = []
        with open(self.proposals_file, "r") as f:
            for line in f:
                try:
                    results.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        if status:
            results = [r for r in results if r.get("status") == status]
        
        return results
    
    def get_summary(self) -> Dict:
        """Get simulation summary."""
        simulations = self.get_simulations(limit=100)
        comparisons = self.get_comparisons()
        discoveries = self.get_discoveries()
        proposals = self.get_proposals()
        pending = self.get_proposals(status="pending")
        
        return {
            "total_simulations": len(simulations),
            "total_comparisons": len(comparisons),
            "total_discoveries": len(discoveries),
            "total_proposals": len(proposals),
            "pending_proposals": len(pending),
        }


def create_logger() -> SimulationLogger:
    """Create a new simulation logger."""
    return SimulationLogger()
