"""Strategic analysis service - shared logic for strategic modules.

This service provides shared analysis utilities to prevent circular dependencies
between Detection, Planning, and Reviews modules.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger

logger = get_logger(__name__)


class StrategicAnalysisService:
    """Shared strategic analysis utilities."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def analyze_signal_strength(
        self,
        signal_data: Dict[str, Any],
    ) -> float:
        """Analyze signal strength (0.0 - 1.0)."""
        
        confidence = signal_data.get("confidence_score", 0.5)
        severity = signal_data.get("severity", "medium")
        
        severity_multipliers = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.3,
        }
        
        return confidence * severity_multipliers.get(severity, 0.5)
    
    async def classify_domain_impact(
        self,
        domain: str,
        magnitude: float,
    ) -> Dict[str, Any]:
        """Classify impact across domains."""
        
        return {
            "domain": domain,
            "magnitude": magnitude,
            "impact_level": self._calculate_impact_level(magnitude),
            "affected_areas": self._get_affected_areas(domain),
        }
    
    def _calculate_impact_level(self, magnitude: float) -> str:
        """Calculate impact level from magnitude."""
        
        if magnitude >= 0.8:
            return "critical"
        elif magnitude >= 0.6:
            return "high"
        elif magnitude >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _get_affected_areas(self, domain: str) -> List[str]:
        """Get affected areas based on domain."""
        
        domain_areas = {
            "financial": ["budget", "cash_flow", "investments"],
            "health": ["wellness", "energy", "productivity"],
            "productivity": ["output", "efficiency", "collaboration"],
            "strategic": ["goals", "timeline", "resources"],
        }
        
        return domain_areas.get(domain, ["general"])
    
    async def detect_conflicts(
        self,
        recommendations: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Detect conflicting recommendations."""
        
        conflicts = []
        
        # Simple conflict detection
        for i, rec1 in enumerate(recommendations):
            for rec2 in recommendations[i+1:]:
                if self._is_conflicting(rec1, rec2):
                    conflicts.append({
                        "recommendation_1": rec1.get("title"),
                        "recommendation_2": rec2.get("title"),
                        "conflict_type": "opposite_direction",
                    })
        
        return conflicts
    
    def _is_conflicting(self, rec1: Dict, rec2: Dict) -> bool:
        """Check if two recommendations conflict."""
        
        # Simple heuristic: opposite actions on same domain
        if rec1.get("domain") == rec2.get("domain"):
            action1 = rec1.get("action", "")
            action2 = rec2.get("action", "")
            
            opposites = [("increase", "decrease"), ("more", "less")]
            return any((a1 in action1 and a2 in action2) or (a2 in action1 and a1 in action2) 
                      for a1, a2 in opposites)
        
        return False
    
    async def calculate_urgency(
        self,
        time_horizon_days: int,
        severity: str,
    ) -> float:
        """Calculate urgency score (0.0 - 1.0)."""
        
        time_factor = min(1.0, 30 / max(1, time_horizon_days))
        
        severity_factors = {
            "critical": 1.0,
            "high": 0.75,
            "medium": 0.5,
            "low": 0.25,
        }
        
        return time_factor * severity_factors.get(severity, 0.5)
    
    async def aggregate_insights(
        self,
        insights: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Aggregate multiple insights into summary."""
        
        if not insights:
            return {"summary": "No insights available"}
        
        return {
            "total_insights": len(insights),
            "by_severity": self._count_by_severity(insights),
            "by_domain": self._count_by_domain(insights),
            "top_priorities": self._get_top_priorities(insights),
        }
    
    def _count_by_severity(self, insights: List[Dict]) -> Dict[str, int]:
        """Count insights by severity."""
        
        counts = {}
        for insight in insights:
            sev = insight.get("severity", "unknown")
            counts[sev] = counts.get(sev, 0) + 1
        return counts
    
    def _count_by_domain(self, insights: List[Dict]) -> Dict[str, int]:
        """Count insights by domain."""
        
        counts = {}
        for insight in insights:
            dom = insight.get("domain", "unknown")
            counts[dom] = counts.get(dom, 0) + 1
        return counts
    
    def _get_top_priorities(self, insights: List[Dict]) -> List[Dict]:
        """Get top priority insights."""
        
        sorted_insights = sorted(
            insights,
            key=lambda x: x.get("urgency", 0.5),
            reverse=True,
        )
        
        return sorted_insights[:5]


async def get_strategic_analysis_service(session: AsyncSession) -> StrategicAnalysisService:
    """Get strategic analysis service instance."""
    return StrategicAnalysisService(session)
