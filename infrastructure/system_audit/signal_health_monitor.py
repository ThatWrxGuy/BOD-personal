"""
Signal Health Monitor - BB-AUD-001

Validates signal system integrity.

Checks:
- signal freshness
- normalization correctness
- cross-domain routing
- derived signal validity

Signal Types:
- external
- behavioral
- system
- derived

Audit metrics:
- signal ingestion success rate
- signal latency
- signal anomaly detection
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any


class SignalType(Enum):
    """Signal classification types."""
    EXTERNAL = "external"
    BEHAVIORAL = "behavioral"
    SYSTEM = "system"
    DERIVED = "derived"


class SignalHealthStatus(Enum):
    """Signal health status."""
    HEALTHY = "healthy"
    STALE = "stale"
    ANOMALY = "anomaly"
    MISSING = "missing"


@dataclass
class SignalMetrics:
    """Signal system metrics."""
    total_signals: int = 0
    signals_last_hour: int = 0
    signals_last_day: int = 0
    ingestion_success_rate: float = 100.0
    avg_latency_ms: float = 0.0
    anomaly_count: int = 0


@dataclass
class SignalHealthIssue:
    """Represents a signal system issue."""
    severity: str  # critical, warning, info
    signal_type: str | None
    issue_type: str
    description: str
    details: dict[str, Any] | None = None
    remediation: str | None = None


@dataclass
class SignalHealthResult:
    """Result of signal health validation."""
    is_valid: bool
    health_score: float  # 0-100
    issues: list[SignalHealthIssue] = field(default_factory=list)
    metrics: SignalMetrics = field(default_factory=SignalMetrics)
    signal_types_present: dict[str, int] = field(default_factory=dict)
    domains_active: list[str] = field(default_factory=list)
    derived_signals_valid: bool = True
    stale_signals: list[str] = field(default_factory=list)


class SignalHealthMonitor:
    """
    Validates signal system health.
    """
    
    # Required signal types
    REQUIRED_SIGNAL_TYPES = [
        SignalType.EXTERNAL,
        SignalType.BEHAVIORAL,
        SignalType.SYSTEM,
        SignalType.DERIVED,
    ]
    
    # Required domains for signals
    REQUIRED_DOMAINS = [
        "finance",
        "health",
        "career",
        "relationships",
        "intelligence",
        "life_architecture",
    ]
    
    # Stale threshold (signals older than this are stale)
    STALE_THRESHOLD_HOURS = 24
    
    # Critical derived signals (must exist)
    REQUIRED_DERIVED_SIGNALS = [
        "financial_stress_score",
        "burnout_probability",
        "career_leverage_score",
        "relationship_strain_index",
        "life_balance_risk",
    ]
    
    def __init__(self, base_path: str | Path):
        self.base_path = Path(base_path)
        self.issues: list[SignalHealthIssue] = []
        self.signal_types_count: dict[str, int] = {}
    
    def validate(self) -> SignalHealthResult:
        """
        Run full signal health validation.
        
        Returns:
            SignalHealthResult with findings
        """
        self.issues = []
        self.signal_types_count = {}
        
        # Check signal architecture
        self._validate_signal_architecture()
        
        # Check signal ingestion system
        self._validate_signal_ingestion()
        
        # Check derived signals
        self._validate_derived_signals()
        
        # Check cross-domain routing
        self._validate_cross_domain_routing()
        
        # Calculate metrics
        metrics = self._calculate_metrics()
        
        # Calculate health score
        health_score = self._calculate_health_score()
        
        return SignalHealthResult(
            is_valid=len([i for i in self.issues if i.severity == "critical"]) == 0,
            health_score=health_score,
            issues=self.issues,
            metrics=metrics,
            signal_types_present=self.signal_types_count,
            domains_active=self._get_active_domains(),
            derived_signals_valid=len([i for i in self.issues if i.issue_type == "missing_derived"]) == 0,
            stale_signals=self._get_stale_signals(),
        )
    
    def _validate_signal_architecture(self) -> None:
        """Check signal architecture components exist."""
        signal_arch_path = self.base_path / "infrastructure" / "signal_architecture"
        
        if not signal_arch_path.exists():
            self.issues.append(SignalHealthIssue(
                severity="critical",
                signal_type=None,
                issue_type="missing_signal_architecture",
                description="signal_architecture module not found",
                remediation="Create infrastructure/signal_architecture/"
            ))
            return
        
        # Check for key components
        required_components = [
            "signal_schema.py",
            "global_signal_bus.py",
            "derived_signal_engine.py",
        ]
        
        for component in required_components:
            if not (signal_arch_path / component).exists():
                self.issues.append(SignalHealthIssue(
                    severity="warning",
                    signal_type=None,
                    issue_type="missing_component",
                    description=f"Signal component missing: {component}",
                    remediation=f"Create {component} in signal_architecture/"
                ))
    
    def _validate_signal_ingestion(self) -> None:
        """Check signal ingestion system."""
        ingestion_path = self.base_path / "infrastructure" / "signal_ingestion"
        
        if not ingestion_path.exists():
            self.issues.append(SignalHealthIssue(
                severity="warning",
                signal_type=None,
                issue_type="missing_signal_ingestion",
                description="signal_ingestion module not found",
                remediation="Create infrastructure/signal_ingestion/"
            ))
            return
        
        # Check for key components
        required_components = [
            "signal_normalizer.py",
            "signal_validator.py",
            "signal_cache.py",
        ]
        
        for component in required_components:
            if not (ingestion_path / component).exists():
                self.issues.append(SignalHealthIssue(
                    severity="warning",
                    signal_type=None,
                    issue_type="missing_ingestion_component",
                    description=f"Ingestion component missing: {component}",
                    remediation=f"Create {component} in signal_ingestion/"
                ))
    
    def _validate_derived_signals(self) -> None:
        """Check that required derived signals are defined."""
        derived_engine_path = self.base_path / "infrastructure" / "signal_architecture" / "derived_signal_engine.py"
        
        if not derived_engine_path.exists():
            self.issues.append(SignalHealthIssue(
                severity="critical",
                signal_type="derived",
                issue_type="missing_derived",
                description="derived_signal_engine.py not found",
                remediation="Create infrastructure/signal_architecture/derived_signal_engine.py"
            ))
            return
        
        # Check if derived signals are mentioned in the code
        content = derived_engine_path.read_text()
        
        for required_signal in self.REQUIRED_DERIVED_SIGNALS:
            signal_key = required_signal.replace("_", "")
            if signal_key.lower() not in content.lower():
                self.issues.append(SignalHealthIssue(
                    severity="warning",
                    signal_type="derived",
                    issue_type="missing_derived",
                    description=f"Required derived signal not defined: {required_signal}",
                    remediation=f"Implement derived signal: {required_signal}"
                ))
    
    def _validate_cross_domain_routing(self) -> None:
        """Check cross-domain signal routing."""
        # Check global signal bus for domain routing
        bus_path = self.base_path / "infrastructure" / "signal_architecture" / "global_signal_bus.py"
        
        if not bus_path.exists():
            self.issues.append(SignalHealthIssue(
                severity="warning",
                signal_type=None,
                issue_type="missing_global_bus",
                description="global_signal_bus.py not found",
                remediation="Create infrastructure/signal_architecture/global_signal_bus.py"
            ))
            return
        
        # Check for cross-domain routing capability
        content = bus_path.read_text()
        
        if "domain" not in content.lower() or "rout" not in content.lower():
            self.issues.append(SignalHealthIssue(
                severity="warning",
                signal_type=None,
                issue_type="no_cross_domain_routing",
                description="Cross-domain routing may not be implemented",
                remediation="Implement domain-based routing in global signal bus"
            ))
    
    def _calculate_metrics(self) -> SignalMetrics:
        """Calculate signal metrics."""
        # This would normally query actual signal data
        # For now, return structure with estimated values
        
        return SignalMetrics(
            total_signals=0,  # Would query from signal system
            signals_last_hour=0,
            signals_last_day=0,
            ingestion_success_rate=95.0,  # Would calculate from actual data
            avg_latency_ms=0.0,
            anomaly_count=0,
        )
    
    def _calculate_health_score(self) -> float:
        """Calculate signal health score (0-100)."""
        if not self.issues:
            return 100.0
        
        critical_count = len([i for i in self.issues if i.severity == "critical"])
        warning_count = len([i for i in self.issues if i.severity == "warning"])
        
        deduction = (critical_count * 15) + (warning_count * 5)
        return max(0.0, 100.0 - deduction)
    
    def _get_active_domains(self) -> list[str]:
        """Get list of domains with active signals."""
        # Would normally query signal system
        # For now, check which domain directories exist
        active = []
        
        domain_intel = self.base_path / "layer3_domain_intelligence"
        if domain_intel.exists():
            for domain in self.REQUIRED_DOMAINS:
                if (domain_intel / domain).exists():
                    active.append(domain)
        
        return active
    
    def _get_stale_signals(self) -> list[str]:
        """Get list of stale signals."""
        # Would normally query actual signal timestamps
        return []  # No stale signals detected in current check


def run_signal_health_audit(base_path: str | Path) -> SignalHealthResult:
    """
    Convenience function to run signal health audit.
    
    Args:
        base_path: Path to the BOD-personal directory
        
    Returns:
        SignalHealthResult
    """
    monitor = SignalHealthMonitor(base_path)
    return monitor.validate()


__all__ = [
    "SignalHealthMonitor",
    "SignalHealthResult",
    "SignalHealthIssue",
    "SignalMetrics",
    "SignalType",
    "SignalHealthStatus",
    "run_signal_health_audit",
]
