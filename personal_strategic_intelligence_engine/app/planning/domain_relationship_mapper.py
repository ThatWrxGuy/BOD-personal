"""Domain relationship mapper for cross-domain planning."""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.planning.plan_types import DOMAIN_RELATIONSHIPS
from app.core.logging import get_logger

logger = get_logger(__name__)


class DomainRelationshipMapper:
    """Maps relationships between life domains."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def analyze_relationships(
        self,
        domains: List[str],
    ) -> Dict[str, Any]:
        """Analyze relationships between specified domains."""
        
        relationships = []
        
        # Find all defined relationships between these domains
        for rel_id, rel_data in DOMAIN_RELATIONSHIPS.items():
            if rel_data["source"] in domains and rel_data["target"] in domains:
                relationships.append({
                    "id": rel_id,
                    "source": rel_data["source"],
                    "target": rel_data["target"],
                    "relationship": rel_data["relationship"],
                    "description": rel_data["description"],
                })
        
        return {
            "domains": domains,
            "relationships": relationships,
            "relationship_count": len(relationships),
        }
    
    async def get_impact_chain(
        self,
        starting_domain: str,
    ) -> List[Dict[str, Any]]:
        """Get the chain of impacts from a starting domain."""
        
        chain = []
        visited = set()
        
        def traverse(domain: str, path: List[str]):
            if domain in visited:
                return
            
            visited.add(domain)
            path.append(domain)
            
            # Find relationships where this domain is the source
            for rel_id, rel_data in DOMAIN_RELATIONSHIPS.items():
                if rel_data["source"] == domain:
                    chain.append({
                        "from": domain,
                        "to": rel_data["target"],
                        "relationship": rel_data["relationship"],
                        "description": rel_data["description"],
                    })
                    traverse(rel_data["target"], path)
        
        traverse(starting_domain, [])
        
        return chain
    
    async def detect_interdomain_patterns(
        self,
        domain_data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Detect patterns that span multiple domains."""
        
        patterns = []
        
        # Check for health → productivity relationship
        health_metrics = domain_data.get("health", {})
        productivity_metrics = domain_data.get("productivity", {})
        
        if health_metrics and productivity_metrics:
            # Check if health issues might affect productivity
            health_status = health_metrics.get("status")
            if health_status == "needs_improvement":
                patterns.append({
                    "type": "domain_impact",
                    "source_domain": "health",
                    "target_domain": "productivity",
                    "description": "Health issues may be impacting productivity",
                    "confidence": 0.7,
                    "recommendation": "Address health concerns to improve productivity",
                })
        
        # Check for workload → health relationship
        productivity_data = domain_data.get("productivity", {})
        
        if productivity_data:
            # Check for high workload indicators
            workload_indicators = productivity_data.get("workload", {})
            
            if workload_indicators.get("is_high"):
                patterns.append({
                    "type": "domain_impact",
                    "source_domain": "productivity",
                    "target_domain": "health",
                    "description": "High workload may be affecting health",
                    "confidence": 0.8,
                    "recommendation": "Consider reducing workload to protect health",
                })
        
        # Check financial → productivity
        financial_data = domain_data.get("financial", {})
        
        if financial_data:
            financial_stress = financial_data.get("stress_level", "low")
            
            if financial_stress == "high":
                patterns.append({
                    "type": "domain_impact",
                    "source_domain": "financial",
                    "target_domain": "productivity",
                    "description": "Financial stress may be affecting focus and productivity",
                    "confidence": 0.6,
                    "recommendation": "Address financial concerns to improve productivity",
                })
        
        return patterns
    
    async def calculate_domain_synergies(
        self,
        domains: List[str],
    ) -> Dict[str, Any]:
        """Calculate potential synergies between domains."""
        
        synergies = []
        
        # Check for positive relationships that can be leveraged
        for rel_id, rel_data in DOMAIN_RELATIONSHIPS.items():
            if rel_data["relationship"] == "positive" and rel_data["source"] in domains:
                synergies.append({
                    "domains": [rel_data["source"], rel_data["target"]],
                    "synergy_type": "leveraged",
                    "description": f"Improving {rel_data['source']} can boost {rel_data['target']}",
                })
        
        # Check for negative relationships that can be mitigated
        for rel_id, rel_data in DOMAIN_RELATIONSHIPS.items():
            if rel_data["relationship"] == "negative" and rel_data["source"] in domains:
                synergies.append({
                    "domains": [rel_data["source"], rel_data["target"]],
                    "synergy_type": "mitigated",
                    "description": f"Managing {rel_data['source']} can protect {rel_data['target']}",
                })
        
        return {
            "potential_synergies": synergies,
            "leverage_count": sum(1 for s in synergies if s["synergy_type"] == "leveraged"),
            "mitigation_count": sum(1 for s in synergies if s["synergy_type"] == "mitigated"),
        }


class TradeoffAnalyzer:
    """Analyzes tradeoffs between competing priorities."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def analyze_tradeoffs(
        self,
        domains: List[str],
        goals: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Analyze tradeoffs between domain goals."""
        
        tradeoffs = []
        
        # Define common tradeoff scenarios
        tradeoff_scenarios = [
            {
                "domains": ["productivity", "health"],
                "description": "More work hours can improve productivity but harm health",
                "impact": "High workload → Health decline → Long-term productivity loss",
                "mitigation": "Schedule regular breaks and maintain work-life balance",
            },
            {
                "domains": ["financial", "lifestyle"],
                "description": "Aggressive saving reduces current lifestyle quality",
                "impact": "Reduced spending → Lower satisfaction → Potential burnout",
                "mitigation": "Balance savings with intentional lifestyle investments",
            },
            {
                "domains": ["projects", "focus"],
                "description": "More projects dilute focus and reduce quality",
                "impact": "Context switching → Lower quality outcomes",
                "mitigation": "Limit concurrent projects and prioritize ruthlessly",
            },
        ]
        
        for scenario in tradeoff_scenarios:
            if any(d in scenario["domains"] for d in domains):
                tradeoffs.append(scenario)
        
        return tradeoffs
    
    async def quantify_impact(
        self,
        tradeoff: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Quantify the potential impact of a tradeoff."""
        
        domains = tradeoff.get("domains", [])
        
        impact_analysis = {}
        
        for domain in domains:
            if domain == "productivity":
                impact_analysis[domain] = {
                    "positive": context.get("productivity_gain", 0),
                    "negative": context.get("health_impact", 0),
                    "net": context.get("productivity_gain", 0) - context.get("health_impact", 0),
                }
            elif domain == "health":
                impact_analysis[domain] = {
                    "positive": context.get("health_improvement", 0),
                    "negative": context.get("workload_impact", 0),
                    "net": context.get("health_improvement", 0) - context.get("workload_impact", 0),
                }
            elif domain == "financial":
                impact_analysis[domain] = {
                    "positive": context.get("savings_increase", 0),
                    "negative": context.get("lifestyle_impact", 0),
                    "net": context.get("savings_increase", 0) - context.get("lifestyle_impact", 0),
                }
        
        return {
            "tradeoff": tradeoff.get("description"),
            "impact_by_domain": impact_analysis,
            "recommendation": self._generate_recommendation(impact_analysis),
        }
    
    def _generate_recommendation(self, impact_analysis: Dict[str, Any]) -> str:
        """Generate a recommendation based on impact analysis."""
        
        # Check if any domain has negative net impact
        for domain, analysis in impact_analysis.items():
            if analysis.get("net", 0) < 0:
                return f"Consider reducing {domain} focus to avoid negative impact"
        
        return "Tradeoff appears manageable with current approach"


async def get_domain_relationship_mapper(session: AsyncSession) -> DomainRelationshipMapper:
    """Get domain relationship mapper instance."""
    return DomainRelationshipMapper(session)


async def get_tradeoff_analyzer(session: AsyncSession) -> TradeoffAnalyzer:
    """Get tradeoff analyzer instance."""
    return TradeoffAnalyzer(session)
