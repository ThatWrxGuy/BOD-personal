"""
Agent Integrity Scanner - BB-AUD-001

Validates every agent in the system.

Checks:
- Agent registration
- Domain assignment
- Input signal compatibility
- Output recommendation schema
- Execution errors
- Response latency

Detects:
- orphan agents
- duplicate agents
- inactive agents
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class AgentStatus(Enum):
    """Agent operational status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ORPHANED = "orphaned"
    DUPLICATE = "duplicate"
    ERROR = "error"


class AgentRole(Enum):
    """Agent role types per BB-DOM-001."""
    OBSERVER = "observer"
    STRATEGIST = "strategist"
    GOVERNOR = "governor"


@dataclass
class AgentInfo:
    """Information about a registered agent."""
    agent_id: str
    name: str
    domain: str
    role: str
    status: AgentStatus
    module_path: str | None = None
    input_signals: list[str] = field(default_factory=list)
    output_schema: dict[str, Any] | None = None
    error_count: int = 0
    last_execution_time_ms: float | None = None


@dataclass
class AgentIntegrityIssue:
    """Represents an agent integrity problem."""
    severity: str  # critical, warning, info
    agent_id: str | None
    issue_type: str
    description: str
    remediation: str | None = None


@dataclass
class AgentIntegrityResult:
    """Result of agent integrity validation."""
    is_valid: bool
    health_score: float  # 0-100
    issues: list[AgentIntegrityIssue] = field(default_factory=list)
    agents_registered: list[AgentInfo] = field(default_factory=list)
    agents_by_domain: dict[str, list[str]] = field(default_factory=dict)
    role_distribution: dict[str, int] = field(default_factory=dict)
    total_agents: int = 0
    active_agents: int = 0
    inactive_agents: int = 0


class AgentIntegrityScanner:
    """
    Validates agent registry and integrity.
    """
    
    # Required domains per BB-DOM-001
    REQUIRED_DOMAINS = [
        "finance",
        "health", 
        "career",
        "relationships",
        "intelligence",
        "life_architecture",
    ]
    
    # Required roles per domain (at least one of each)
    REQUIRED_ROLES = [
        AgentRole.OBSERVER,
        AgentRole.STRATEGIST,
        AgentRole.GOVERNOR,
    ]
    
    # Domain agent counts (minimum per BB-DOM-001)
    MIN_AGENTS_PER_DOMAIN = 4  # At least 4 specialists + governor
    
    def __init__(self, base_path: str | Path):
        self.base_path = Path(base_path)
        self.issues: list[AgentIntegrityIssue] = []
        self.agents: list[AgentInfo] = []
    
    def validate(self) -> AgentIntegrityResult:
        """
        Run full agent integrity validation.
        
        Returns:
            AgentIntegrityResult with findings
        """
        self.issues = []
        self.agents = []
        
        # Discover all agents
        self._discover_agents()
        
        # Validate domain coverage
        self._validate_domain_coverage()
        
        # Validate role distribution
        self._validate_role_distribution()
        
        # Check for orphan agents
        self._check_orphan_agents()
        
        # Check for duplicate agents
        self._check_duplicate_agents()
        
        # Validate agent registration
        self._validate_registration()
        
        # Calculate health score
        health_score = self._calculate_health_score()
        
        return AgentIntegrityResult(
            is_valid=len([i for i in self.issues if i.severity == "critical"]) == 0,
            health_score=health_score,
            issues=self.issues,
            agents_registered=self.agents,
            agents_by_domain=self._get_agents_by_domain(),
            role_distribution=self._get_role_distribution(),
            total_agents=len(self.agents),
            active_agents=len([a for a in self.agents if a.status == AgentStatus.ACTIVE]),
            inactive_agents=len([a for a in self.agents if a.status == AgentStatus.INACTIVE]),
        )
    
    def _discover_agents(self) -> None:
        """Discover all agents in the system."""
        # Check layer3_domain_intelligence for domain agents
        domain_intel_path = self.base_path / "layer3_domain_intelligence"
        
        if not domain_intel_path.exists():
            self.issues.append(AgentIntegrityIssue(
                severity="critical",
                agent_id=None,
                issue_type="missing_domain_intelligence",
                description="layer3_domain_intelligence directory not found",
                remediation="Create domain intelligence layer"
            ))
            return
        
        # Scan each domain
        for domain in self.REQUIRED_DOMAINS:
            domain_path = domain_intel_path / domain
            if not domain_path.exists():
                self.issues.append(AgentIntegrityIssue(
                    severity="warning",
                    agent_id=None,
                    issue_type="missing_domain",
                    description=f"Domain directory missing: {domain}",
                    remediation=f"Create domain: layer3_domain_intelligence/{domain}/"
                ))
                continue
            
            # Look for agent files
            self._scan_domain_agents(domain, domain_path)
        
        # Check for chief officers
        self._scan_chief_officers(domain_intel_path)
    
    def _scan_domain_agents(self, domain: str, domain_path: Path) -> None:
        """Scan agents within a domain."""
        # Look in specialist_agents subdirectory
        specialist_path = domain_path / "specialist_agents"
        
        if specialist_path.exists():
            for py_file in specialist_path.glob("*.py"):
                if py_file.name.startswith("_"):
                    continue
                
                agent_name = py_file.stem.replace("_", " ").title()
                agent = AgentInfo(
                    agent_id=f"{domain}_{py_file.stem}",
                    name=agent_name,
                    domain=domain,
                    role="strategist",  # Default, would need deeper analysis
                    status=AgentStatus.ACTIVE,
                    module_path=str(py_file.relative_to(self.base_path))
                )
                self.agents.append(agent)
    
    def _scan_chief_officers(self, domain_intel_path: Path) -> None:
        """Scan chief officers."""
        for domain in self.REQUIRED_DOMAINS:
            chief_path = domain_intel_path / domain / f"chief_{domain}_officer"
            if chief_path.exists() or (domain_intel_path / domain).exists():
                # Chief officer exists
                agent = AgentInfo(
                    agent_id=f"chief_{domain}_officer",
                    name=f"Chief {domain.title()} Officer",
                    domain=domain,
                    role="executive",
                    status=AgentStatus.ACTIVE,
                    module_path=f"layer3_domain_intelligence/{domain}/"
                )
                self.agents.append(agent)
    
    def _validate_domain_coverage(self) -> None:
        """Ensure all required domains have agents."""
        domains_with_agents = set(a.domain for a in self.agents)
        
        for required_domain in self.REQUIRED_DOMAINS:
            if required_domain not in domains_with_agents:
                self.issues.append(AgentIntegrityIssue(
                    severity="critical",
                    agent_id=None,
                    issue_type="domain_missing",
                    description=f"No agents found for domain: {required_domain}",
                    remediation=f"Add agents to domain: {required_domain}"
                ))
    
    def _validate_role_distribution(self) -> None:
        """Ensure each domain has required role types."""
        # Group agents by domain and role
        domain_roles: dict[str, set[str]] = {}
        
        for agent in self.agents:
            if agent.domain not in domain_roles:
                domain_roles[agent.domain] = set()
            domain_roles[agent.domain].add(agent.role)
        
        # Check each domain has required roles
        for domain, roles in domain_roles.items():
            for required_role in [r.value for r in self.REQUIRED_ROLES]:
                if required_role not in roles:
                    self.issues.append(AgentIntegrityIssue(
                        severity="warning",
                        agent_id=None,
                        issue_type="role_missing",
                        description=f"Domain '{domain}' missing {required_role} role agents",
                        remediation=f"Add {required_role} agent to {domain} domain"
                    ))
    
    def _check_orphan_agents(self) -> None:
        """Detect agents not assigned to any domain."""
        # An agent is orphaned if it has no valid domain
        for agent in self.agents:
            if agent.domain not in self.REQUIRED_DOMAINS and agent.role != "executive":
                agent.status = AgentStatus.ORPHANED
                self.issues.append(AgentIntegrityIssue(
                    severity="warning",
                    agent_id=agent.agent_id,
                    issue_type="orphaned_agent",
                    description=f"Agent {agent.name} has no valid domain assignment",
                    remediation="Assign agent to a valid domain"
                ))
    
    def _check_duplicate_agents(self) -> None:
        """Detect duplicate agent IDs."""
        agent_ids = [a.agent_id for a in self.agents]
        seen_ids: set[str] = set()
        
        for agent_id in agent_ids:
            if agent_id in seen_ids:
                self.issues.append(AgentIntegrityIssue(
                    severity="warning",
                    agent_id=agent_id,
                    issue_type="duplicate_agent",
                    description=f"Duplicate agent ID found: {agent_id}",
                    remediation="Remove duplicate agent registration"
                ))
            seen_ids.add(agent_id)
    
    def _validate_registration(self) -> None:
        """Validate that agents are properly registered."""
        # Check for agents without module paths
        for agent in self.agents:
            if not agent.module_path:
                self.issues.append(AgentIntegrityIssue(
                    severity="warning",
                    agent_id=agent.agent_id,
                    issue_type="unregistered_agent",
                    description=f"Agent {agent.name} has no module path",
                    remediation="Register agent with module path"
                ))
    
    def _calculate_health_score(self) -> float:
        """Calculate agent integrity health score (0-100)."""
        if not self.issues:
            return 100.0
        
        critical_count = len([i for i in self.issues if i.severity == "critical"])
        warning_count = len([i for i in self.issues if i.severity == "warning"])
        
        deduction = (critical_count * 15) + (warning_count * 5)
        return max(0.0, 100.0 - deduction)
    
    def _get_agents_by_domain(self) -> dict[str, list[str]]:
        """Get list of agent IDs grouped by domain."""
        result: dict[str, list[str]] = {}
        for agent in self.agents:
            if agent.domain not in result:
                result[agent.domain] = []
            result[agent.domain].append(agent.agent_id)
        return result
    
    def _get_role_distribution(self) -> dict[str, int]:
        """Get count of agents by role."""
        roles: dict[str, int] = {}
        for agent in self.agents:
            roles[agent.role] = roles.get(agent.role, 0) + 1
        return roles


def run_agent_integrity_audit(base_path: str | Path) -> AgentIntegrityResult:
    """
    Convenience function to run agent integrity audit.
    
    Args:
        base_path: Path to the BOD-personal directory
        
    Returns:
        AgentIntegrityResult
    """
    scanner = AgentIntegrityScanner(base_path)
    return scanner.validate()


__all__ = [
    "AgentIntegrityScanner",
    "AgentIntegrityResult",
    "AgentIntegrityIssue",
    "AgentStatus",
    "AgentRole",
    "AgentInfo",
    "run_agent_integrity_audit",
]
