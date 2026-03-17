"""
Executive Brief Models - BB-INT-004

Structured data models for BB-CORE-030 compliant Executive Brief output.

This module defines the complete Executive Brief structure including:
- Executive Summary
- Strategic Priorities with impact/urgency scoring
- Domain-specific recommendations
- Risk Alerts
- Daily/Weekly/Long-term action plans
- Learning Insights
- System Health Status

Usage:
    from outputs.executive_brief_models import (
        ExecutiveBrief,
        StrategicPriority,
        RiskAlert,
        DailyAction,
        Recommendation,
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class PriorityLevel(Enum):
    """Priority levels for strategic items."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class UrgencyLevel(Enum):
    """Urgency levels for action items."""
    IMMEDIATE = "immediate"
    THIS_WEEK = "this_week"
    THIS_MONTH = "this_month"
    QUARTERLY = "quarterly"
    LONG_TERM = "long_term"


class ImpactLevel(Enum):
    """Impact levels for strategic items."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskSeverity(Enum):
    """Risk severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SystemHealthStatus(Enum):
    """System health status values."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class StrategicPriority:
    """A single strategic priority with structured attributes."""
    domain: str
    priority: int  # 1-10 ranking
    impact: ImpactLevel
    urgency: UrgencyLevel
    title: str
    description: str
    recommended_action: str
    rationale: str = ""
    estimated_duration: str = ""
    

@dataclass
class RiskAlert:
    """A risk alert with severity and details."""
    severity: RiskSeverity
    domain: str
    title: str
    description: str
    mitigation: str = ""
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class Recommendation:
    """A domain-specific recommendation."""
    domain: str
    category: str  # financial, health, operational, strategic
    title: str
    description: str
    action_items: list[str] = field(default_factory=list)
    priority: PriorityLevel = PriorityLevel.MEDIUM
    requires_approval: bool = False  # For financial items


@dataclass
class DailyAction:
    """A single daily action item."""
    domain: str
    action: str
    estimated_time: str  # e.g., "15 minutes", "1 hour"
    priority: PriorityLevel = PriorityLevel.MEDIUM
    completed: bool = False


@dataclass
class WeeklyAdjustment:
    """A weekly strategic adjustment recommendation."""
    domain: str
    title: str
    description: str
    action: str


@dataclass
class LongTermAction:
    """A long-term strategic action."""
    domain: str
    title: str
    description: str
    target_timeline: str  # e.g., "3 years", "5 years"
    milestones: list[str] = field(default_factory=list)


@dataclass
class LearningInsight:
    """A learning insight from behavioral analysis."""
    category: str
    insight: str
    confidence: float = 0.0  # 0-1
    suggested_action: str = ""


@dataclass
class DomainSummary:
    """Rich domain summary."""
    domain: str
    status: str
    summary: str
    key_metrics: dict[str, Any] = field(default_factory=dict)
    trends: list[str] = field(default_factory=list)


@dataclass
class SystemHealthSummary:
    """System health status summary."""
    overall_status: SystemHealthStatus
    score: float  # 0-100
    architecture_health: float = 0.0
    agent_health: float = 0.0
    signal_health: float = 0.0
    governance_health: float = 0.0
    data_health: float = 0.0
    issues: list[str] = field(default_factory=list)


@dataclass
class ExecutiveSummary:
    """Executive summary section."""
    system_status: SystemHealthStatus
    primary_focus_areas: list[str]
    top_priorities: list[str]
    alert_summary: str
    overall_readiness: str  # e.g., "Ready to execute", "Needs attention"


@dataclass
class ExecutiveBrief:
    """
    Complete BB-CORE-030 compliant Executive Brief.
    
    This is the primary output artifact for the CEO.
    """
    # Identification
    id: str
    timestamp: datetime = field(default_factory=datetime.now)
    version: str = "2.0"  # BB-INT-004 version
    
    # Core sections
    executive_summary: ExecutiveSummary = field(default_factory=lambda: ExecutiveSummary(
        system_status=SystemHealthStatus.UNKNOWN,
        primary_focus_areas=[],
        top_priorities=[],
        alert_summary="",
        overall_readiness=""
    ))
    
    # Strategic content
    strategic_priorities: list[StrategicPriority] = field(default_factory=list)
    strategic_recommendations: list[Recommendation] = field(default_factory=list)
    financial_recommendations: list[Recommendation] = field(default_factory=list)
    health_recommendations: list[Recommendation] = field(default_factory=list)
    operational_recommendations: list[Recommendation] = field(default_factory=list)
    
    # Alerts and actions
    risk_alerts: list[RiskAlert] = field(default_factory=list)
    daily_actions: list[DailyAction] = field(default_factory=list)
    weekly_adjustments: list[WeeklyAdjustment] = field(default_factory=list)
    long_term_actions: list[LongTermAction] = field(default_factory=list)
    
    # Insights
    learning_insights: list[LearningInsight] = field(default_factory=list)
    
    # Domain coverage
    domain_summaries: list[DomainSummary] = field(default_factory=list)
    
    # System status
    system_health: SystemHealthSummary = field(default_factory=lambda: SystemHealthSummary(
        overall_status=SystemHealthStatus.UNKNOWN,
        score=0.0
    ))
    
    # Metadata
    generated_by: str = "PSIP"
    confidence_score: float = 0.0


# ============== Helper Functions ==============

def create_default_brief(brief_id: str) -> ExecutiveBrief:
    """Create a default ExecutiveBrief with empty structure."""
    return ExecutiveBrief(id=brief_id)


def add_strategic_priority(
    brief: ExecutiveBrief,
    domain: str,
    priority: int,
    impact: ImpactLevel,
    urgency: UrgencyLevel,
    title: str,
    description: str,
    recommended_action: str,
    rationale: str = "",
    estimated_duration: str = ""
) -> None:
    """Add a strategic priority to the brief."""
    sp = StrategicPriority(
        domain=domain,
        priority=priority,
        impact=impact,
        urgency=urgency,
        title=title,
        description=description,
        recommended_action=recommended_action,
        rationale=rationale,
        estimated_duration=estimated_duration
    )
    brief.strategic_priorities.append(sp)


def add_risk_alert(
    brief: ExecutiveBrief,
    severity: RiskSeverity,
    domain: str,
    title: str,
    description: str,
    mitigation: str = ""
) -> None:
    """Add a risk alert to the brief."""
    alert = RiskAlert(
        severity=severity,
        domain=domain,
        title=title,
        description=description,
        mitigation=mitigation
    )
    brief.risk_alerts.append(alert)


def add_daily_action(
    brief: ExecutiveBrief,
    domain: str,
    action: str,
    estimated_time: str,
    priority: PriorityLevel = PriorityLevel.MEDIUM
) -> None:
    """Add a daily action to the brief."""
    daily = DailyAction(
        domain=domain,
        action=action,
        estimated_time=estimated_time,
        priority=priority
    )
    brief.daily_actions.append(daily)


def add_recommendation(
    brief: ExecutiveBrief,
    domain: str,
    category: str,
    title: str,
    description: str,
    action_items: list[str] | None = None,
    priority: PriorityLevel = PriorityLevel.MEDIUM,
    requires_approval: bool = False
) -> None:
    """Add a recommendation to the brief."""
    rec = Recommendation(
        domain=domain,
        category=category,
        title=title,
        description=description,
        action_items=action_items or [],
        priority=priority,
        requires_approval=requires_approval
    )
    
    # Add to appropriate category
    if category == "financial":
        brief.financial_recommendations.append(rec)
    elif category == "health":
        brief.health_recommendations.append(rec)
    elif category == "operational":
        brief.operational_recommendations.append(rec)
    else:
        brief.strategic_recommendations.append(rec)


__all__ = [
    # Enums
    "PriorityLevel",
    "UrgencyLevel", 
    "ImpactLevel",
    "RiskSeverity",
    "SystemHealthStatus",
    
    # Core classes
    "ExecutiveBrief",
    "ExecutiveSummary",
    "StrategicPriority",
    "RiskAlert",
    "Recommendation",
    "DailyAction",
    "WeeklyAdjustment",
    "LongTermAction",
    "LearningInsight",
    "DomainSummary",
    "SystemHealthSummary",
    
    # Helper functions
    "create_default_brief",
    "add_strategic_priority",
    "add_risk_alert",
    "add_daily_action",
    "add_recommendation",
]
