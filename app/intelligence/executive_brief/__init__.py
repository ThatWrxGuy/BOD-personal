"""
BB-INT-007: Executive Intelligence Brief System

Complete module for generating Executive Intelligence Briefs.

Usage:
    from app.intelligence.executive_brief import (
        ExecutiveBriefGenerator,
        BriefFormatter,
        AgentSignalCollector,
    )
    
    # Generate brief
    generator = ExecutiveBriefGenerator()
    brief = generator.generate(psip)
    
    # Format output
    formatter = BriefFormatter()
    print(formatter.format_console(brief))
"""

from .executive_brief_models import (
    ExecutiveBrief,
    DomainReport,
    AgentReport,
    DomainHealthOverview,
    SpyTradeBrief,
    DailyAction,
    DailyActionPlan,
    WeeklyAdjustment,
    WeeklyAdjustments,
    LongTermOutlook,
    ExecutiveSummarySection,
    SystemHealth,
    SystemStatus,
    StrategicPosture,
    MarketRegime,
    RiskLevel,
)

from .agent_signal_collector import AgentSignalCollector
from .domain_intelligence_aggregator import DomainIntelligenceAggregator
from .spy_trade_brief_engine import SpyTradeBriefEngine
from .executive_brief_generator import ExecutiveBriefGenerator
from .brief_formatter import BriefFormatter


__all__ = [
    # Models
    "ExecutiveBrief",
    "DomainReport",
    "AgentReport",
    "DomainHealthOverview",
    "SpyTradeBrief",
    "DailyAction",
    "DailyActionPlan",
    "WeeklyAdjustment",
    "WeeklyAdjustments",
    "LongTermOutlook",
    "ExecutiveSummarySection",
    "SystemHealth",
    
    # Enums
    "SystemStatus",
    "StrategicPosture",
    "MarketRegime",
    "RiskLevel",
    
    # Components
    "AgentSignalCollector",
    "DomainIntelligenceAggregator",
    "SpyTradeBriefEngine",
    "ExecutiveBriefGenerator",
    "BriefFormatter",
]
