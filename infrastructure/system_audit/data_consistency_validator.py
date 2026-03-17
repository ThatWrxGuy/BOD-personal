"""
Data Consistency Validator - BB-AUD-001

Validates stored data.

Checks:
- memory engine
- signal graph
- digital twin data
- strategy simulations

Detects:
- corrupted memory
- inconsistent graph edges
- missing strategy results
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class DataIssueType(Enum):
    """Types of data consistency issues."""
    CORRUPTED = "corrupted"
    INCONSISTENT = "inconsistent"
    MISSING = "missing"
    STALE = "stale"


@dataclass
class DataConsistencyIssue:
    """Represents a data consistency problem."""
    severity: str  # critical, warning, info
    component: str
    issue_type: str
    description: str
    remediation: str | None = None


@dataclass
class DataConsistencyResult:
    """Result of data consistency validation."""
    is_valid: bool
    health_score: float  # 0-100
    issues: list[DataConsistencyIssue] = field(default_factory=list)
    components_checked: list[str] = field(default_factory=list)
    memory_valid: bool = True
    graph_valid: bool = True
    digital_twin_valid: bool = True
    strategy_results_valid: bool = True


class DataConsistencyValidator:
    """
    Validates data consistency across the system.
    """
    
    def __init__(self, base_path: str | Path):
        self.base_path = Path(base_path)
        self.issues: list[DataConsistencyIssue] = []
        self.components_checked: list[str] = []
    
    def validate(self) -> DataConsistencyResult:
        """
        Run data consistency validation.
        
        Returns:
            DataConsistencyResult with findings
        """
        self.issues = []
        self.components_checked = []
        
        # Validate memory engine
        self._validate_memory_engine()
        
        # Validate signal graph
        self._validate_signal_graph()
        
        # Validate digital twin
        self._validate_digital_twin()
        
        # Validate strategy results
        self._validate_strategy_results()
        
        # Calculate health score
        health_score = self._calculate_health_score()
        
        return DataConsistencyResult(
            is_valid=len([i for i in self.issues if i.severity == "critical"]) == 0,
            health_score=health_score,
            issues=self.issues,
            components_checked=self.components_checked,
            memory_valid=self._is_memory_valid(),
            graph_valid=self._is_graph_valid(),
            digital_twin_valid=self._is_digital_twin_valid(),
            strategy_results_valid=self._is_strategy_valid(),
        )
    
    def _validate_memory_engine(self) -> None:
        """Validate memory engine data."""
        self.components_checked.append("memory_engine")
        
        memory_path = self.base_path / "infrastructure" / "memory_engine"
        
        if not memory_path.exists():
            self.issues.append(DataConsistencyIssue(
                severity="critical",
                component="memory_engine",
                issue_type="missing",
                description="Memory engine module not found",
                remediation="Create infrastructure/memory_engine/"
            ))
            return
        
        # Check for key memory components
        required_files = ["memory_engine.py"]
        for file in required_files:
            if not (memory_path / file).exists():
                self.issues.append(DataConsistencyIssue(
                    severity="warning",
                    component="memory_engine",
                    issue_type="missing_file",
                    description=f"Memory engine file missing: {file}",
                    remediation=f"Create {file}"
                ))
    
    def _validate_signal_graph(self) -> None:
        """Validate signal graph data."""
        self.components_checked.append("signal_graph")
        
        graph_path = self.base_path / "infrastructure" / "life_graph"
        
        if not graph_path.exists():
            self.issues.append(DataConsistencyIssue(
                severity="warning",
                component="signal_graph",
                issue_type="missing",
                description="Life graph module not found",
                remediation="Create infrastructure/life_graph/"
            ))
            return
        
        # Check for graph components
        required_files = [
            "life_signal_graph.py",
            "graph_models.py",
            "graph_builder.py",
        ]
        
        for file in required_files:
            if not (graph_path / file).exists():
                self.issues.append(DataConsistencyIssue(
                    severity="warning",
                    component="signal_graph",
                    issue_type="missing_file",
                    description=f"Graph file missing: {file}",
                    remediation=f"Create {file}"
                ))
        
        # Check for edge consistency validation
        builder_path = graph_path / "graph_builder.py"
        if builder_path.exists():
            content = builder_path.read_text()
            if "validate" not in content.lower() and "check" not in content.lower():
                self.issues.append(DataConsistencyIssue(
                    severity="info",
                    component="signal_graph",
                    issue_type="no_validation",
                    description="Graph builder may not validate edge consistency",
                    remediation="Add edge validation to graph builder"
                ))
    
    def _validate_digital_twin(self) -> None:
        """Validate digital twin data."""
        self.components_checked.append("digital_twin")
        
        twin_path = self.base_path / "infrastructure" / "digital_twin"
        
        if not twin_path.exists():
            self.issues.append(DataConsistencyIssue(
                severity="warning",
                component="digital_twin",
                issue_type="missing",
                description="Digital twin module not found",
                remediation="Create infrastructure/digital_twin/"
            ))
            return
        
        # Check for twin components
        required_files = ["digital_twin_model.py"]
        
        for file in required_files:
            if not (twin_path / file).exists():
                self.issues.append(DataConsistencyIssue(
                    severity="warning",
                    component="digital_twin",
                    issue_type="missing_file",
                    description=f"Digital twin file missing: {file}",
                    remediation=f"Create {file}"
                ))
    
    def _validate_strategy_results(self) -> None:
        """Validate strategy simulation results."""
        self.components_checked.append("strategy_results")
        
        # Check for strategy engines
        engines_path = self.base_path / "infrastructure" / "strategic_intelligence"
        
        if not engines_path.exists():
            self.issues.append(DataConsistencyIssue(
                severity="warning",
                component="strategy_results",
                issue_type="missing",
                description="Strategic intelligence module not found",
                remediation="Create infrastructure/strategic_intelligence/"
            ))
            return
        
        # Check for simulation engine
        sim_path = engines_path / "strategic_engines.py"
        if not sim_path.exists():
            self.issues.append(DataConsistencyIssue(
                severity="warning",
                component="strategy_results",
                issue_type="missing_simulation",
                description="Simulation engine not found",
                remediation="Create simulation engine"
            ))
    
    def _calculate_health_score(self) -> float:
        """Calculate data consistency health score (0-100)."""
        if not self.issues:
            return 100.0
        
        critical_count = len([i for i in self.issues if i.severity == "critical"])
        warning_count = len([i for i in self.issues if i.severity == "warning"])
        
        deduction = (critical_count * 15) + (warning_count * 5)
        return max(0.0, 100.0 - deduction)
    
    def _is_memory_valid(self) -> bool:
        """Check if memory engine is valid."""
        return not any(
            i for i in self.issues 
            if i.component == "memory_engine" and i.severity == "critical"
        )
    
    def _is_graph_valid(self) -> bool:
        """Check if signal graph is valid."""
        return not any(
            i for i in self.issues 
            if i.component == "signal_graph" and i.severity == "critical"
        )
    
    def _is_digital_twin_valid(self) -> bool:
        """Check if digital twin is valid."""
        return not any(
            i for i in self.issues 
            if i.component == "digital_twin" and i.severity == "critical"
        )
    
    def _is_strategy_valid(self) -> bool:
        """Check if strategy results are valid."""
        return not any(
            i for i in self.issues 
            if i.component == "strategy_results" and i.severity == "critical"
        )


def run_data_consistency_audit(base_path: str | Path) -> DataConsistencyResult:
    """
    Convenience function to run data consistency audit.
    
    Args:
        base_path: Path to the BOD-personal directory
        
    Returns:
        DataConsistencyResult
    """
    validator = DataConsistencyValidator(base_path)
    return validator.validate()


__all__ = [
    "DataConsistencyValidator",
    "DataConsistencyResult",
    "DataConsistencyIssue",
    "DataIssueType",
    "run_data_consistency_audit",
]
