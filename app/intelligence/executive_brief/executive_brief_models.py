"""
BB-INT-007: Executive Intelligence Brief Data Models

Comprehensive data models for the Executive Intelligence Brief system.

These models support:
- Domain-level intelligence aggregation
- Agent signal collection
- Trade intelligence (SPY 0DTE)
- Daily/Weekly/Long-term action planning
- System health monitoring

Usage:
    from app.intelligence.executive_brief import (
        ExecutiveBrief,
        DomainReport,
        AgentReport,
        DailyActionPlan,
        SystemHealth,
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SystemStatus(Enum):
    """System operational status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"


class StrategicPosture(Enum):
    """Strategic posture of the system."""
    OFFENSIVE = "offensive"
    DEFENSIVE = "defensive"
    GROWTH = "growth"
    CONSERVATIVE = "conservative"
    NEUTRAL = "neutral"


class MarketRegime(Enum):
    """Market regime for trade intelligence."""
    BULL_TRENDING = "bull_trending"
    BEAR_TRENDING = "bear_trending"
    CONSOLIDATION = "consolidation"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"


class RiskLevel(Enum):
    """Risk level enumeration."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ============== Agent Models ==============

@dataclass
class AgentReport:
    """Report from a single agent."""
    agent_name: str
    agent_id: str
    role: str  # observer, strategist, governor
    domain: str
    insights: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    alerts: list[str] = field(default_factory=list)
    confidence_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


# ============== Domain Models ==============

@dataclass
class DomainReport:
    """Comprehensive report for a single domain."""
    domain_name: str
    display_name: str
    score: float  # 0-100
    
    # Agent aggregations
    agents: list[AgentReport] = field(default_factory=list)
    
    # Aggregated outputs
    insights: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    alerts: list[str] = field(default_factory=list)
    
    # Status
    status: SystemStatus = SystemStatus.HEALTHY
    trend: str = "stable"  # improving, declining, stable
    
    # Metrics
    active_signals: int = 0
    pending_actions: int = 0
    
    def get_top_recommendations(self, limit: int = 3) -> list[str]:
        """Get top recommendations from domain."""
        return self.recommendations[:limit]


@dataclass
class DomainHealthOverview:
    """Overview of all domain health."""
    finance_score: float
    health_score: float
    career_score: float
    relationships_score: float
    intelligence_score: float
    life_architecture_score: float
    
    overall_health: float = 0.0
    
    def __post_init__(self):
        """Calculate overall health."""
        self.overall_health = (
            self.finance_score +
            self.health_score +
            self.career_score +
            self.relationships_score +
            self.intelligence_score +
            self.life_architecture_score
        ) / 6


# ============== Trade Intelligence Models ==============

@dataclass
class SpyTradeBrief:
    """SPY 0DTE trade intelligence."""
    # Market analysis
    market_regime: MarketRegime
    spy_price: float
    support_level: float
    resistance_level: float
    volatility: float
    
    # Trade setup
    strategy: str  # bullish, bearish, neutral
    entry_trigger: str
    strike_selection: str
    expiration: str
    
    # Position management
    position_size: int
    profit_target_pct: float
    stop_loss_pct: float
    risk_reward_ratio: float
    
    # Confidence
    confidence_score: float
    reasoning: str
    
    # Timing
    best_entry_window: str
    suggested_exit: str


# ============== Action Plan Models ==============

@dataclass
class DailyAction:
    """A single daily action."""
    id: str
    domain: str
    action: str
    priority: int  # 1-5
    estimated_minutes: int
    category: str  # finance, health, career, etc.
    completed: bool = False


@dataclass
class DailyActionPlan:
    """Daily action plan."""
    date: datetime
    focus_areas: list[str] = field(default_factory=list)
    actions: list[DailyAction] = field(default_factory=list)
    
    total_estimated_minutes: int = 0
    
    def add_action(self, action: DailyAction) -> None:
        """Add action to plan."""
        self.actions.append(action)
        self.total_estimated_minutes += action.estimated_minutes


@dataclass
class WeeklyAdjustment:
    """Weekly strategic adjustment."""
    domain: str
    focus: str
    action: str
    expected_impact: str


@dataclass
class WeeklyAdjustments:
    """Weekly adjustments container."""
    week_start: datetime
    adjustments: list[WeeklyAdjustment] = field(default_factory=list)
    
    def get_by_domain(self, domain: str) -> list[WeeklyAdjustment]:
        """Get adjustments for a specific domain."""
        return [a for a in self.adjustments if a.domain == domain]


@dataclass
class LongTermOutlook:
    """Long-term strategic outlook."""
    timeline_1_year: list[str] = field(default_factory=list)
    timeline_3_years: list[str] = field(default_factory=list)
    timeline_5_years: list[str] = field(default_factory=list)
    
    milestones: list[dict] = field(default_factory=list)


# ============== Executive Summary ==============

@dataclass
class ExecutiveSummarySection:
    """Executive summary section."""
    system_status: SystemStatus
    strategic_posture: StrategicPosture
    
    top_priorities: list[str] = field(default_factory=list)
    critical_alerts: list[str] = field(default_factory=list)
    
    opportunities: list[str] = field(default_factory=list)
    threats: list[str] = field(default_factory=list)
    
    readiness_score: float = 0.0
    
    narrative: str = ""  # Chief of Staff narrative


# ============== System Health ==============

@dataclass
class SystemHealth:
    """System health metrics."""
    overall_score: float
    
    # Component scores
    architecture_score: float
    agent_registry_score: float
    signal_health_score: float
    governance_score: float
    data_integrity_score: float
    
    # Status
    status: SystemStatus
    
    # Issues
    critical_issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    
    last_audit: datetime | None = None


# ============== Main Executive Brief ==============

@dataclass
class ExecutiveBrief:
    """
    Complete BB-INT-007 Executive Intelligence Brief.
    
    This is the primary command interface for the CEO.
    """
    # Identification
    id: str
    date: datetime
    strategic_cycle_id: str
    
    # System status
    system_status: SystemStatus = SystemStatus.HEALTHY
    strategic_posture: StrategicPosture = StrategicPosture.NEUTRAL
    
    # Intelligence metrics
    signals_processed: int = 0
    active_recommendations: int = 0
    risk_alerts: int = 0
    
    # Core sections
    executive_summary: ExecutiveSummarySection = field(default_factory=lambda: ExecutiveSummarySection(
        system_status=SystemStatus.HEALTHY,
        strategic_posture=StrategicPosture.NEUTRAL
    ))
    domain_overview: DomainHealthOverview | None = None
    
    # Domain reports
    finance_domain: DomainReport | None = None
    health_domain: DomainReport | None = None
    career_domain: DomainReport | None = None
    relationships_domain: DomainReport | None = None
    intelligence_domain: DomainReport | None = None
    life_architecture_domain: DomainReport | None = None
    
    # Trade intelligence
    spy_trade_brief: SpyTradeBrief | None = None
    
    # Action plans
    daily_action_plan: DailyActionPlan | None = None
    weekly_adjustments: WeeklyAdjustments | None = None
    long_term_outlook: LongTermOutlook | None = None
    
    # System health
    system_health: SystemHealth | None = None
    
    # Metadata
    version: str = "2.0"
    generated_at: datetime = field(default_factory=datetime.now)
    
    # Getters for domain reports
    def get_domain_report(self, domain: str) -> DomainReport | None:
        """Get domain report by name."""
        domain_map = {
            "finance": self.finance_domain,
            "health": self.health_domain,
            "career": self.career_domain,
            "relationships": self.relationships_domain,
            "intelligence": self.intelligence_domain,
            "life_architecture": self.life_architecture_domain,
        }
        return domain_map.get(domain)
    
    def get_all_domains(self) -> list[DomainReport]:
        """Get all domain reports."""
        return [
            d for d in [
                self.finance_domain,
                self.health_domain,
                self.career_domain,
                self.relationships_domain,
                self.intelligence_domain,
                self.life_architecture_domain,
            ]
            if d is not None
        ]


# ============== Helper Functions ==============

def create_domain_report(
    domain_name: str,
    display_name: str,
    agents: list[AgentReport] | None = None
) -> DomainReport:
    """Create a domain report from agents."""
    agents = agents or []
    
    # Aggregate insights, recommendations, alerts
    insights = []
    recommendations = []
    alerts = []
    
    for agent in agents:
        insights.extend(agent.insights)
        recommendations.extend(agent.recommendations)
        alerts.extend(agent.alerts)
    
    # Calculate score (simplified)
    score = 75.0  # Default
    if agents:
        avg_confidence = sum(a.confidence_score for a in agents) / len(agents)
        score = 50 + (avg_confidence * 50)
    
    return DomainReport(
        domain_name=domain_name,
        display_name=display_name,
        score=score,
        agents=agents,
        insights=insights[:5],  # Top 5
        recommendations=recommendations[:3],  # Top 3
        alerts=alerts,
        active_signals=len(insights),
    )


def create_agent_report(
    agent_name: str,
    agent_id: str,
    role: str,
    domain: str,
    insights: list[str] | None = None,
    recommendations: list[str] | None = None,
    alerts: list[str] | None = None,
    confidence: float = 0.5
) -> AgentReport:
    """Create an agent report."""
    return AgentReport(
        agent_name=agent_name,
        agent_id=agent_id,
        role=role,
        domain=domain,
        insights=insights or [],
        recommendations=recommendations or [],
        alerts=alerts or [],
        confidence_score=confidence,
    )


__all__ = [
    # Enums
    "SystemStatus",
    "StrategicPosture",
    "MarketRegime",
    "RiskLevel",
    
    # Agent
    "AgentReport",
    
    # Domain
    "DomainReport",
    "DomainHealthOverview",
    
    # Trade
    "SpyTradeBrief",
    
    # Actions
    "DailyAction",
    "DailyActionPlan",
    "WeeklyAdjustment",
    "WeeklyAdjustments",
    "LongTermOutlook",
    
    # Summary
    "ExecutiveSummarySection",
    
    # Health
    "SystemHealth",
    
    # Main
    "ExecutiveBrief",
    
    # Helpers
    "create_domain_report",
    "create_agent_report",
]
