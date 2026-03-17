"""
Outputs Layer - Executive Briefs and Domain Reports
"""

from .executive_briefs.executive_brief_generator import ExecutiveBriefGenerator, ExecutiveBrief
from .executive_briefs.executive_brief_generator_v2 import ExecutiveBriefGeneratorV2

from .executive_brief_models import (
    ExecutiveBrief as ExecutiveBriefV2,
    ExecutiveSummary,
    StrategicPriority,
    RiskAlert,
    Recommendation,
    DailyAction,
    WeeklyAdjustment,
    LongTermAction,
    LearningInsight,
    DomainSummary,
    SystemHealthSummary,
    PriorityLevel,
    UrgencyLevel,
    ImpactLevel,
    RiskSeverity,
    SystemHealthStatus,
)


__all__ = [
    # V1 (legacy)
    "ExecutiveBriefGenerator",
    "ExecutiveBrief",
    # V2 - BB-INT-004
    "ExecutiveBriefGeneratorV2",
    "ExecutiveBriefV2",
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
    "PriorityLevel",
    "UrgencyLevel",
    "ImpactLevel",
    "RiskSeverity",
    "SystemHealthStatus",
]
