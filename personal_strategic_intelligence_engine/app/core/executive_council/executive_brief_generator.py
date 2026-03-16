"""Executive Brief Generator - BB-CORE-022

Generates the final strategic briefing for the CEO.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from app.core.executive_council.council_models import (
    Domain,
    DomainRecommendation,
    RankedRecommendation,
    Conflict,
    AlignmentScore,
    CouncilCycleResult,
)

logger = logging.getLogger(__name__)


class ExecutiveBriefGenerator:
    """Generates executive strategic briefs."""
    
    def __init__(self):
        pass
    
    def generate_brief(
        self,
        ranked: List[RankedRecommendation],
        conflicts: List[Conflict],
        alignment_scores: List[AlignmentScore],
        finance_context: Optional[Dict] = None,
    ) -> CouncilCycleResult:
        """Generate the executive brief."""
        
        # Extract top priority
        top_priority = ""
        if ranked:
            top_priority = ranked[0].recommendation.title
        
        # Generate summary
        summary = self._generate_summary(ranked, conflicts, alignment_scores)
        
        # Extract action items
        action_items = self._extract_action_items(ranked)
        
        # Generate alerts
        alerts = self._generate_alerts(ranked, conflicts)
        
        # Track domains represented
        domains = list(set(r.recommendation.domain for r in ranked))
        
        result = CouncilCycleResult(
            timestamp=datetime.utcnow(),
            recommendations=[r.recommendation for r in ranked],
            ranked_recommendations=ranked,
            conflicts=conflicts,
            alignment_scores=alignment_scores,
            top_priority_title=top_priority,
            brief_summary=summary,
            action_items=action_items,
            alerts=alerts,
            domains_represented=domains,
        )
        
        logger.info(f"Generated executive brief: {len(action_items)} action items, {len(alerts)} alerts")
        
        return result
    
    def _generate_summary(
        self,
        ranked: List[RankedRecommendation],
        conflicts: List[Conflict],
        alignment_scores: List[AlignmentScore],
    ) -> str:
        """Generate the brief summary."""
        
        lines = []
        
        # Number of recommendations
        lines.append(f"Council reviewed {len(ranked)} domain recommendations.")
        
        # Top recommendation
        if ranked:
            top = ranked[0]
            lines.append(f"Top priority: {top.recommendation.title} ({top.recommendation.domain.value})")
        
        # Conflicts
        if conflicts:
            resolved = [c for c in conflicts if c.resolved]
            lines.append(f"Resolved {len(resolved)} inter-domain conflicts.")
        
        # Alignment summary
        if alignment_scores:
            avg_alignment = sum(a.score for a in alignment_scores) / len(alignment_scores)
            lines.append(f"Overall strategic alignment: {avg_alignment:.0%}")
        
        return " ".join(lines)
    
    def _extract_action_items(self, ranked: List[RankedRecommendation]) -> List[str]:
        """Extract actionable items from ranked recommendations."""
        
        action_items = []
        
        # Take top 5 recommendations
        for rec in ranked[:5]:
            for item in rec.recommendation.action_items:
                action_items.append(f"[{rec.recommendation.domain.value.upper()}] {item}")
        
        return action_items[:10]  # Max 10 action items
    
    def _generate_alerts(
        self,
        ranked: List[RankedRecommendation],
        conflicts: List[Conflict],
    ) -> List[str]:
        """Generate alerts."""
        
        alerts = []
        
        # Critical priorities
        for rec in ranked:
            if rec.recommendation.priority.value == "critical":
                alerts.append(f"CRITICAL: {rec.recommendation.title}")
        
        # Unresolved conflicts
        unresolved = [c for c in conflicts if not c.resolved]
        if unresolved:
            for c in unresolved:
                alerts.append(f"CONFLICT: {c.domain_a.value} vs {c.domain_b.value}")
        
        # Health domain high priority (always worth noting)
        health_recs = [r for r in ranked if r.recommendation.domain == Domain.HEALTH]
        if health_recs and health_recs[0].recommendation.priority.value in ["critical", "high"]:
            alerts.append("HEALTH ALERT: High-priority health recommendation")
        
        return alerts
    
    def format_brief_text(
        self,
        result: CouncilCycleResult,
        finance_context: Optional[Dict] = None,
    ) -> str:
        """Format brief as readable text."""
        
        lines = []
        
        # Header
        lines.append("=" * 60)
        lines.append("EXECUTIVE STRATEGIC BRIEF")
        lines.append("=" * 60)
        lines.append(f"Date: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Finance Context
        if finance_context:
            lines.append("MARKET ENVIRONMENT")
            lines.append("-" * 40)
            regime = finance_context.get("regime", "Unknown")
            posture = finance_context.get("capital_posture", "Unknown")
            lines.append(f"Regime: {regime}")
            lines.append(f"Capital Posture: {posture}")
            lines.append("")
        
        # Top Priority
        lines.append("TOP STRATEGIC PRIORITIES")
        lines.append("-" * 40)
        
        for i, rec in enumerate(result.ranked_recommendations[:5], 1):
            domain = rec.recommendation.domain.value.upper()
            title = rec.recommendation.title
            priority = rec.recommendation.priority.value
            lines.append(f"{i}. [{domain}] {title} [{priority}]")
        
        lines.append("")
        
        # Action Items
        if result.action_items:
            lines.append("ACTION ITEMS")
            lines.append("-" * 40)
            for item in result.action_items[:8]:
                lines.append(f"• {item}")
            lines.append("")
        
        # Alerts
        if result.alerts:
            lines.append("KEY ALERTS")
            lines.append("-" * 40)
            for alert in result.alerts:
                lines.append(f"⚠ {alert}")
            lines.append("")
        
        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 40)
        lines.append(result.brief_summary)
        lines.append("")
        
        return "\n".join(lines)


_brief_generator: Optional[ExecutiveBriefGenerator] = None


def get_executive_brief_generator() -> ExecutiveBriefGenerator:
    """Get the executive brief generator."""
    global _brief_generator
    
    if _brief_generator is None:
        _brief_generator = ExecutiveBriefGenerator()
    
    return _brief_generator
