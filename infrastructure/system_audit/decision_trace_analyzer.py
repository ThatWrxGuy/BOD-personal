"""
Decision Trace Analyzer - BB-AUD-001

Tracks decision lineage.

For every decision:
1. Decision
2. Signals Used
3. Agents Involved
4. Debate Outcomes
5. Council Resolution
6. Final Recommendation

Ensures:
- transparency
- reproducibility
- reasoning validity
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class DecisionStatus(Enum):
    """Decision status in the trace."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"


@dataclass
class DecisionNode:
    """Represents a node in the decision trace."""
    node_id: str
    node_type: str  # decision, signal, agent, debate, council, recommendation
    timestamp: datetime
    data: dict[str, Any]
    parent_id: str | None = None


@dataclass
class DecisionTrace:
    """Complete trace of a decision."""
    trace_id: str
    decision: DecisionNode
    signals_used: list[DecisionNode] = field(default_factory=list)
    agents_involved: list[DecisionNode] = field(default_factory=list)
    debate_outcomes: list[DecisionNode] = field(default_factory=list)
    council_resolution: DecisionNode | None = None
    final_recommendation: DecisionNode | None = None
    status: DecisionStatus = DecisionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None


@dataclass
class DecisionTraceIssue:
    """Represents an issue in decision tracing."""
    severity: str  # critical, warning, info
    trace_id: str | None
    issue_type: str
    description: str
    remediation: str | None = None


@dataclass
class DecisionTraceResult:
    """Result of decision trace validation."""
    is_valid: bool
    health_score: float  # 0-100
    issues: list[DecisionTraceIssue] = field(default_factory=list)
    traces_found: int = 0
    complete_traces: int = 0
    incomplete_traces: int = 0
    missing_lineage: list[str] = field(default_factory=list)


class DecisionTraceAnalyzer:
    """
    Validates decision traceability and lineage.
    """
    
    # Required components for complete decision trace
    REQUIRED_TRACE_COMPONENTS = [
        "decision",
        "signals_used",
        "agents_involved",
        "debate_outcomes",
        "council_resolution",
        "final_recommendation",
    ]
    
    def __init__(self, base_path: str | Path):
        self.base_path = Path(base_path)
        self.issues: list[DecisionTraceIssue] = []
        self.traces: list[DecisionTrace] = []
    
    def validate(self) -> DecisionTraceResult:
        """
        Run decision trace validation.
        
        Returns:
            DecisionTraceResult with findings
        """
        self.issues = []
        self.traces = []
        
        # Check decision tracking infrastructure
        self._validate_decision_infrastructure()
        
        # Check strategic intelligence for decision support
        self._validate_strategic_intelligence()
        
        # Check for executive council decision logging
        self._validate_council_decisions()
        
        # Validate trace completeness
        self._validate_trace_completeness()
        
        # Calculate health score
        health_score = self._calculate_health_score()
        
        return DecisionTraceResult(
            is_valid=len([i for i in self.issues if i.severity == "critical"]) == 0,
            health_score=health_score,
            issues=self.issues,
            traces_found=len(self.traces),
            complete_traces=len([t for t in self.traces if self._is_trace_complete(t)]),
            incomplete_traces=len([t for t in self.traces if not self._is_trace_complete(t)]),
            missing_lineage=self._get_missing_lineage(),
        )
    
    def _validate_decision_infrastructure(self) -> None:
        """Check that decision tracking infrastructure exists."""
        # Check for strategic intelligence module
        strategic_path = self.base_path / "infrastructure" / "strategic_intelligence"
        
        if not strategic_path.exists():
            self.issues.append(DecisionTraceIssue(
                severity="warning",
                trace_id=None,
                issue_type="missing_strategic_intelligence",
                description="strategic_intelligence module not found",
                remediation="Create infrastructure/strategic_intelligence/"
            ))
            return
        
        # Check for strategy models
        models_path = strategic_path / "strategy_models.py"
        if not models_path.exists():
            self.issues.append(DecisionTraceIssue(
                severity="warning",
                trace_id=None,
                issue_type="missing_strategy_models",
                description="strategy_models.py not found",
                remediation="Create strategy_models.py"
            ))
    
    def _validate_strategic_intelligence(self) -> None:
        """Validate strategic intelligence decision support."""
        engines_path = self.base_path / "infrastructure" / "strategic_intelligence" / "strategic_engines.py"
        
        if not engines_path.exists():
            self.issues.append(DecisionTraceIssue(
                severity="warning",
                trace_id=None,
                issue_type="missing_strategic_engines",
                description="strategic_engines.py not found",
                remediation="Create strategic_engines.py"
            ))
            return
        
        content = engines_path.read_text()
        
        # Check for key decision-making components
        required_components = [
            "StrategyGenerationEngine",
            "ScenarioSimulationEngine", 
            "StrategicDebateEngine",
            "AlignmentEngine",
        ]
        
        for component in required_components:
            if component not in content:
                self.issues.append(DecisionTraceIssue(
                    severity="warning",
                    trace_id=None,
                    issue_type="missing_component",
                    description=f"Strategic engine missing: {component}",
                    remediation=f"Implement {component}"
                ))
    
    def _validate_council_decisions(self) -> None:
        """Validate Executive Council decision logging."""
        council_path = self.base_path / "layer2_governance_layer" / "executive_council" / "executive_council.py"
        
        if not council_path.exists():
            self.issues.append(DecisionTraceIssue(
                severity="warning",
                trace_id=None,
                issue_type="missing_council",
                description="Executive Council implementation not found",
                remediation="Create executive_council.py"
            ))
            return
        
        content = council_path.read_text()
        
        # Check for decision logging
        required_logging = ["decision", "vote", "resolution"]
        for item in required_logging:
            if item not in content.lower():
                self.issues.append(DecisionTraceIssue(
                    severity="warning",
                    trace_id=None,
                    issue_type="missing_council_tracking",
                    description=f"Executive Council may not track: {item}",
                    decision_tracking=f"Implement {item} tracking"
                ))
    
    def _validate_trace_completeness(self) -> None:
        """Validate that decision traces are complete."""
        # Check if there's a mechanism to store complete traces
        # In a real system, this would query the memory engine
        
        # For now, check if memory engine can store decisions
        memory_path = self.base_path / "infrastructure" / "memory_engine" / "memory_engine.py"
        
        if not memory_path.exists():
            self.issues.append(DecisionTraceIssue(
                severity="warning",
                trace_id=None,
                issue_type="missing_memory_engine",
                description="Memory engine not found for decision storage",
                remediation="Create memory_engine.py"
            ))
    
    def _is_trace_complete(self, trace: DecisionTrace) -> bool:
        """Check if a decision trace is complete."""
        return (
            trace.decision is not None and
            len(trace.signals_used) > 0 and
            len(trace.agents_involved) > 0 and
            trace.council_resolution is not None and
            trace.final_recommendation is not None
        )
    
    def _get_missing_lineage(self) -> list[str]:
        """Get list of missing lineage components."""
        missing = []
        
        # Check if each component type is tracked
        strategic = self.base_path / "infrastructure" / "strategic_intelligence"
        if not strategic.exists():
            missing.append("strategic_intelligence")
        
        council = self.base_path / "layer2_governance_layer" / "executive_council"
        if not council.exists():
            missing.append("executive_council_decisions")
        
        return missing
    
    def _calculate_health_score(self) -> float:
        """Calculate decision trace health score (0-100)."""
        if not self.issues:
            return 100.0
        
        critical_count = len([i for i in self.issues if i.severity == "critical"])
        warning_count = len([i for i in self.issues if i.severity == "warning"])
        
        deduction = (critical_count * 15) + (warning_count * 5)
        return max(0.0, 100.0 - deduction)
    
    def create_trace(
        self,
        decision_id: str,
        decision_data: dict[str, Any]
    ) -> DecisionTrace:
        """
        Create a new decision trace.
        
        Args:
            decision_id: Unique identifier for the decision
            decision_data: Decision metadata
            
        Returns:
            New DecisionTrace
        """
        trace = DecisionTrace(
            trace_id=decision_id,
            decision=DecisionNode(
                node_id=f"{decision_id}_decision",
                node_type="decision",
                timestamp=datetime.now(),
                data=decision_data
            )
        )
        
        self.traces.append(trace)
        return trace
    
    def add_signal_to_trace(
        self,
        trace: DecisionTrace,
        signal_id: str,
        signal_data: dict[str, Any]
    ) -> None:
        """Add a signal to a decision trace."""
        node = DecisionNode(
            node_id=signal_id,
            node_type="signal",
            timestamp=datetime.now(),
            data=signal_data,
            parent_id=trace.decision.node_id
        )
        trace.signals_used.append(node)
    
    def add_agent_to_trace(
        self,
        trace: DecisionTrace,
        agent_id: str,
        agent_data: dict[str, Any]
    ) -> None:
        """Add an agent to a decision trace."""
        node = DecisionNode(
            node_id=agent_id,
            node_type="agent",
            timestamp=datetime.now(),
            data=agent_data,
            parent_id=trace.decision.node_id
        )
        trace.agents_involved.append(node)
    
    def add_debate_outcome(
        self,
        trace: DecisionTrace,
        debate_id: str,
        outcome_data: dict[str, Any]
    ) -> None:
        """Add a debate outcome to a decision trace."""
        node = DecisionNode(
            node_id=debate_id,
            node_type="debate",
            timestamp=datetime.now(),
            data=outcome_data,
            parent_id=trace.decision.node_id
        )
        trace.debate_outcomes.append(node)
    
    def set_council_resolution(
        self,
        trace: DecisionTrace,
        resolution_data: dict[str, Any]
    ) -> None:
        """Set the council resolution for a decision trace."""
        trace.council_resolution = DecisionNode(
            node_id=f"{trace.trace_id}_resolution",
            node_type="council_resolution",
            timestamp=datetime.now(),
            data=resolution_data,
            parent_id=trace.decision.node_id
        )
    
    def set_recommendation(
        self,
        trace: DecisionTrace,
        recommendation_data: dict[str, Any]
    ) -> None:
        """Set the final recommendation for a decision trace."""
        trace.final_recommendation = DecisionNode(
            node_id=f"{trace.trace_id}_recommendation",
            node_type="recommendation",
            timestamp=datetime.now(),
            data=recommendation_data,
            parent_id=trace.council_resolution.node_id if trace.council_resolution else None
        )


def run_decision_trace_audit(base_path: str | Path) -> DecisionTraceResult:
    """
    Convenience function to run decision trace audit.
    
    Args:
        base_path: Path to the BOD-personal directory
        
    Returns:
        DecisionTraceResult
    """
    analyzer = DecisionTraceAnalyzer(base_path)
    return analyzer.validate()


__all__ = [
    "DecisionTraceAnalyzer",
    "DecisionTraceResult",
    "DecisionTraceIssue",
    "DecisionTrace",
    "DecisionNode",
    "DecisionStatus",
    "run_decision_trace_audit",
]
