"""
BB-INT-007: Executive Brief Formatter

Formats the Executive Brief for various output modes.

Responsibilities:
- Console formatting
- JSON output
- Future UI integration

Usage:
    from app.intelligence.executive_brief import BriefFormatter
    
    formatter = BriefFormatter()
    print(formatter.format_console(brief))
    print(formatter.format_json(brief))
"""

import json
from datetime import datetime

from .executive_brief_models import (
    ExecutiveBrief,
    SystemStatus,
    StrategicPosture,
    MarketRegime,
)


class BriefFormatter:
    """
    Formats Executive Brief for different output modes.
    """
    
    def format_console(self, brief: ExecutiveBrief, width: int = 80) -> str:
        """
        Format brief for console output.
        
        Args:
            brief: ExecutiveBrief to format
            width: Console width
            
        Returns:
            Formatted string
        """
        lines = []
        
        # Header
        lines.append("=" * width)
        lines.append("BUSY BEE EXECUTIVE INTELLIGENCE BRIEF".center(width))
        lines.append("=" * width)
        lines.append(f"Date: {brief.date.strftime('%Y-%m-%d')}")
        lines.append(f"Cycle ID: {brief.strategic_cycle_id}")
        lines.append(f"Status: {brief.system_status.value.upper()}")
        lines.append("")
        
        # Executive Summary
        lines.append("-" * width)
        lines.append("EXECUTIVE SUMMARY".center(width))
        lines.append("-" * width)
        es = brief.executive_summary
        lines.append(f"System Status: {es.system_status.value.upper()}")
        lines.append(f"Strategic Posture: {es.strategic_posture.value.upper()}")
        lines.append(f"Readiness: {es.readiness_score:.0f}/100")
        lines.append("")
        lines.append("Narrative:")
        lines.append(f"  {es.narrative}")
        lines.append("")
        
        # Top Priorities
        if es.top_priorities:
            lines.append("TOP STRATEGIC PRIORITIES:")
            for i, p in enumerate(es.top_priorities, 1):
                lines.append(f"  {i}. {p}")
            lines.append("")
        
        # Critical Alerts
        if es.critical_alerts:
            lines.append("CRITICAL ALERTS:")
            for alert in es.critical_alerts:
                lines.append(f"  ⚠️ {alert}")
            lines.append("")
        
        # Domain Scores
        lines.append("-" * width)
        lines.append("DOMAIN HEALTH SCORES".center(width))
        lines.append("-" * width)
        
        domains = [
            ("Finance", brief.finance_domain),
            ("Health", brief.health_domain),
            ("Career", brief.career_domain),
            ("Relationships", brief.relationships_domain),
            ("Intelligence", brief.intelligence_domain),
            ("Life Architecture", brief.life_architecture_domain),
        ]
        
        for name, domain in domains:
            if domain:
                score_bar = self._make_score_bar(domain.score)
                lines.append(f"{name:20} {score_bar} {domain.score:.0f}%")
        lines.append("")
        
        # Daily Action Plan
        if brief.daily_action_plan:
            lines.append("-" * width)
            lines.append("DAILY ACTION PLAN".center(width))
            lines.append("-" * width)
            
            plan = brief.daily_action_plan
            lines.append(f"Focus Areas: {', '.join(plan.focus_areas)}")
            lines.append(f"Total Time: {plan.total_estimated_minutes} minutes")
            lines.append("")
            
            for action in plan.actions[:5]:
                priority_emoji = "🔴" if action.priority == 1 else "🟡" if action.priority <= 2 else "🟢"
                lines.append(f"{priority_emoji} [{action.domain.upper()}] {action.action}")
                lines.append(f"   Est: {action.estimated_minutes} min")
            lines.append("")
        
        # Weekly Adjustments
        if brief.weekly_adjustments:
            lines.append("-" * width)
            lines.append("WEEKLY ADJUSTMENTS".center(width))
            lines.append("-" * width)
            
            for adj in brief.weekly_adjustments.adjustments:
                lines.append(f"• {adj.domain.title()}: {adj.action}")
            lines.append("")
        
        # Long-term Outlook
        if brief.long_term_outlook:
            lines.append("-" * width)
            lines.append("LONG-TERM STRATEGIC OUTLOOK".center(width))
            lines.append("-" * width)
            
            lt = brief.long_term_outlook
            if lt.timeline_1_year:
                lines.append("1-Year Goals:")
                for item in lt.timeline_1_year[:2]:
                    lines.append(f"  → {item}")
            if lt.timeline_3_years:
                lines.append("3-Year Goals:")
                for item in lt.timeline_3_years[:2]:
                    lines.append(f"  → {item}")
            if lt.timeline_5_years:
                lines.append("5-Year Goals:")
                for item in lt.timeline_5_years[:2]:
                    lines.append(f"  → {item}")
            lines.append("")
        
        # SPY Trade Brief
        if brief.spy_trade_brief:
            lines.append("-" * width)
            lines.append("SPY 0DTE TRADE BRIEF".center(width))
            lines.append("-" * width)
            
            tb = brief.spy_trade_brief
            lines.append(f"Market Regime: {tb.market_regime.value}")
            lines.append(f"SPY Price: ${tb.spy_price:.2f}")
            lines.append(f"Support: ${tb.support_level:.2f}")
            lines.append(f"Resistance: ${tb.resistance_level:.2f}")
            lines.append("")
            lines.append(f"Strategy: {tb.strategy}")
            lines.append(f"Entry: {tb.entry_trigger}")
            lines.append(f"Strike: {tb.strike_selection}")
            lines.append(f"Position Size: {tb.position_size} contracts")
            lines.append(f"Risk/Reward: {tb.risk_reward_ratio:.1f}R")
            lines.append(f"Confidence: {tb.confidence_score*100:.0f}%")
            lines.append("")
        
        # System Health
        if brief.system_health:
            lines.append("-" * width)
            lines.append("SYSTEM HEALTH".center(width))
            lines.append("-" * width)
            
            sh = brief.system_health
            lines.append(f"Overall Score: {sh.overall_score:.0f}/100")
            lines.append(f"Architecture: {sh.architecture_score:.0f}%")
            lines.append(f"Agent Registry: {sh.agent_registry_score:.0f}%")
            lines.append(f"Signal Health: {sh.signal_health_score:.0f}%")
            lines.append(f"Governance: {sh.governance_score:.0f}%")
            lines.append("")
        
        # Footer
        lines.append("=" * width)
        lines.append(f"Generated: {brief.generated_at.strftime('%Y-%m-%d %H:%M:%S')}".center(width))
        lines.append("=" * width)
        
        return "\n".join(lines)
    
    def _make_score_bar(self, score: float, length: int = 20) -> str:
        """Create a visual score bar."""
        filled = int((score / 100) * length)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}]"
    
    def format_json(self, brief: ExecutiveBrief) -> str:
        """
        Format brief as JSON.
        
        Args:
            brief: ExecutiveBrief to format
            
        Returns:
            JSON string
        """
        def serialize(obj):
            if hasattr(obj, '__dict__'):
                return serialize(obj.__dict__)
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif hasattr(obj, 'value'):
                return obj.value
            elif isinstance(obj, list):
                return [serialize(i) for i in obj]
            elif isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            return obj
        
        data = {
            "id": brief.id,
            "date": brief.date.isoformat(),
            "strategic_cycle_id": brief.strategic_cycle_id,
            "system_status": brief.system_status.value,
            "strategic_posture": brief.strategic_posture.value,
            "signals_processed": brief.signals_processed,
            "active_recommendations": brief.active_recommendations,
            "risk_alerts": brief.risk_alerts,
            "executive_summary": {
                "system_status": brief.executive_summary.system_status.value,
                "strategic_posture": brief.executive_summary.strategic_posture.value,
                "top_priorities": brief.executive_summary.top_priorities,
                "critical_alerts": brief.executive_summary.critical_alerts,
                "narrative": brief.executive_summary.narrative,
                "readiness_score": brief.executive_summary.readiness_score,
            },
            "domain_health": {
                "finance": brief.finance_domain.score if brief.finance_domain else 0,
                "health": brief.health_domain.score if brief.health_domain else 0,
                "career": brief.career_domain.score if brief.career_domain else 0,
                "relationships": brief.relationships_domain.score if brief.relationships_domain else 0,
                "intelligence": brief.intelligence_domain.score if brief.intelligence_domain else 0,
                "life_architecture": brief.life_architecture_domain.score if brief.life_architecture_domain else 0,
            },
            "daily_actions": [
                {
                    "id": a.id,
                    "domain": a.domain,
                    "action": a.action,
                    "priority": a.priority,
                    "minutes": a.estimated_minutes,
                }
                for a in (brief.daily_action_plan.actions if brief.daily_action_plan else [])
            ],
            "system_health": {
                "overall_score": brief.system_health.overall_score if brief.system_health else 0,
            },
            "generated_at": brief.generated_at.isoformat(),
            "version": brief.version,
        }
        
        return json.dumps(data, indent=2)
    
    def format_summary(self, brief: ExecutiveBrief) -> str:
        """
        Format brief as short summary.
        
        Args:
            brief: ExecutiveBrief to format
            
        Returns:
            Summary string
        """
        lines = []
        
        lines.append(f"📊 Executive Brief - {brief.date.strftime('%Y-%m-%d')}")
        lines.append(f"Status: {brief.system_status.value.upper()}")
        lines.append(f"Posture: {brief.strategic_posture.value.upper()}")
        lines.append("")
        
        # Domain scores
        lines.append("Domain Scores:")
        for domain in brief.get_all_domains():
            if domain:
                lines.append(f"  {domain.display_name}: {domain.score:.0f}%")
        
        # Actions
        if brief.daily_action_plan:
            lines.append(f"\nToday's Actions: {len(brief.daily_action_plan.actions)} items")
        
        return "\n".join(lines)


__all__ = [
    "BriefFormatter",
]
