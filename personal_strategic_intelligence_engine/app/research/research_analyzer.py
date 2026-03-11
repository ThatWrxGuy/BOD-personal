"""Research analyzer for data analysis."""
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.core.logging import get_logger

logger = get_logger(__name__)


class ResearchAnalyzer:
    """Analyzes research data and extracts insights."""
    
    def __init__(self):
        pass
    
    async def analyze(
        self,
        topic: str,
        source_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Analyze source results and extract insights."""
        
        key_findings = []
        supporting_evidence = []
        risk_analysis = {}
        
        # Process each source result
        for result in source_results:
            if not result.get("success", False):
                continue
            
            data = result.get("data", [])
            
            for item in data:
                item_type = item.get("type", "unknown")
                
                # Extract findings based on type
                if item_type == "market_overview":
                    key_findings.append({
                        "type": "market_analysis",
                        "description": item.get("summary", ""),
                        "source": result.get("source", "unknown"),
                        "confidence": 0.7,
                    })
                
                elif item_type == "economic_indicator":
                    key_findings.append({
                        "type": "economic_analysis",
                        "description": item.get("summary", ""),
                        "source": result.get("source", "unknown"),
                        "confidence": 0.65,
                    })
                
                elif item_type == "llm_analysis":
                    key_findings.append({
                        "type": "ai_analysis",
                        "description": item.get("summary", ""),
                        "confidence": item.get("confidence", 0.5),
                        "considerations": item.get("considerations", []),
                    })
                
                elif item_type == "internal_knowledge":
                    supporting_evidence.append({
                        "type": "internal_data",
                        "description": item.get("summary", ""),
                        "sources": item.get("sources", []),
                    })
        
        # Calculate overall confidence
        if key_findings:
            confidences = [f.get("confidence", 0.5) for f in key_findings]
            overall_confidence = sum(confidences) / len(confidences)
        else:
            overall_confidence = 0.3
        
        # Generate risk analysis
        risk_analysis = await self._analyze_risks(topic, key_findings)
        
        # Generate recommended actions
        recommended_actions = self._generate_recommendations(topic, key_findings)
        
        return {
            "key_findings": key_findings,
            "supporting_evidence": supporting_evidence,
            "risk_analysis": risk_analysis,
            "recommended_actions": recommended_actions,
            "confidence_score": overall_confidence,
            "analyzed_at": datetime.utcnow().isoformat(),
        }
    
    async def _analyze_risks(
        self,
        topic: str,
        findings: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Analyze potential risks from findings."""
        
        risks = []
        
        # Look for risk indicators in findings
        risk_keywords = ["volatility", "uncertainty", "decline", "risk", "threat", "downside"]
        
        for finding in findings:
            description = finding.get("description", "").lower()
            
            if any(keyword in description for keyword in risk_keywords):
                risks.append({
                    "type": "identified_risk",
                    "description": finding.get("description", ""),
                    "severity": "medium",
                })
        
        # Default risk if none found
        if not risks:
            risks.append({
                "type": "general_uncertainty",
                "description": "Standard research uncertainty applies",
                "severity": "low",
            })
        
        return {
            "identified_risks": risks,
            "overall_risk_level": "medium" if len(risks) > 2 else "low",
        }
    
    def _generate_recommendations(
        self,
        topic: str,
        findings: List[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        """Generate recommended actions based on findings."""
        
        recommendations = []
        
        if not findings:
            recommendations.append({
                "action": "conduct_additional_research",
                "description": "Insufficient data - recommend additional research",
                "priority": "high",
            })
            return recommendations
        
        # Generate recommendations based on findings
        recommendations.append({
            "action": "review_findings",
            "description": f"Review {len(findings)} key findings for {topic}",
            "priority": "medium",
        })
        
        recommendations.append({
            "action": "validate_with_sources",
            "description": "Validate findings with primary sources",
            "priority": "medium",
        })
        
        # Look for actionable items
        for finding in findings:
            finding_type = finding.get("type", "")
            
            if finding_type == "market_analysis":
                recommendations.append({
                    "action": "consult_financial_advisor",
                    "description": "Consider consulting financial advisor for market insights",
                    "priority": "low",
                })
            
            elif finding_type == "ai_analysis":
                recommendations.append({
                    "action": "verify_with_expert",
                    "description": "Verify AI-generated analysis with expert input",
                    "priority": "medium",
                })
        
        return recommendations
    
    def _generate_summary(
        self,
        topic: str,
        findings: List[Dict[str, Any]],
    ) -> str:
        """Generate a text summary of findings."""
        
        if not findings:
            return f"Research on '{topic}' did not yield sufficient data for analysis."
        
        summary_parts = [
            f"Research Analysis: {topic}",
            "",
            f"Analysis identified {len(findings)} key findings:",
        ]
        
        for i, finding in enumerate(findings[:5], 1):
            description = finding.get("description", "No description")
            summary_parts.append(f"{i}. {description[:100]}...")
        
        return "\n".join(summary_parts)


async def get_research_analyzer() -> ResearchAnalyzer:
    """Get research analyzer instance."""
    return ResearchAnalyzer()
