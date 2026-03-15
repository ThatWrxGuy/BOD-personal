"""Opportunity and risk classifiers."""
from typing import Dict, List, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.detection.detection_types import (
    DomainType,
    DetectionSeverity,
    DetectionEventType,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpportunityClassifier:
    """Classifies opportunities from detected events."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def classify_opportunity(
        self,
        event_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Classify an event as an opportunity."""
        
        opportunity_type = self._determine_opportunity_type(event_data)
        
        return {
            "type": DetectionEventType.OPPORTUNITY,
            "opportunity_type": opportunity_type,
            "title": f"Opportunity: {self._get_opportunity_title(opportunity_type)}",
            "description": self._get_opportunity_description(event_data, opportunity_type),
            "potential_value": self._estimate_potential_value(event_data),
            "time_sensitivity": self._assess_time_sensitivity(event_data),
            "confidence": self._calculate_confidence(event_data),
            "recommended_action": self._get_recommended_action(opportunity_type),
        }
    
    def _determine_opportunity_type(self, event_data: Dict[str, Any]) -> str:
        """Determine the type of opportunity."""
        
        domain = event_data.get("domain", "")
        
        if domain == DomainType.FINANCIAL:
            return "financial_investment"
        elif domain == DomainType.HEALTH:
            return "health_improvement"
        elif domain == DomainType.PRODUCTIVITY:
            return "productivity_gain"
        elif domain == DomainType.PROJECTS:
            return "project_acceleration"
        
        return "strategic_opportunity"
    
    def _get_opportunity_title(self, opportunity_type: str) -> str:
        """Get a title for the opportunity type."""
        
        titles = {
            "financial_investment": "Investment Opportunity Detected",
            "health_improvement": "Health Optimization Opportunity",
            "productivity_gain": "Productivity Enhancement Opportunity",
            "project_acceleration": "Project Acceleration Opportunity",
            "strategic_opportunity": "Strategic Opportunity Available",
        }
        
        return titles.get(opportunity_type, "Opportunity Detected")
    
    def _get_opportunity_description(
        self,
        event_data: Dict[str, Any],
        opportunity_type: str,
    ) -> str:
        """Generate an opportunity description."""
        
        descriptions = {
            "financial_investment": "Analysis suggests favorable conditions for financial investment or portfolio rebalancing.",
            "health_improvement": "Data indicates potential for health optimization through adjusted routines.",
            "productivity_gain": "Opportunity identified to improve productivity through process changes.",
            "project_acceleration": "Conditions favor accelerated project completion.",
            "strategic_opportunity": "Strategic opportunity identified that warrants consideration.",
        }
        
        return descriptions.get(opportunity_type, "An opportunity has been identified.")
    
    def _estimate_potential_value(self, event_data: Dict[str, Any]) -> str:
        """Estimate potential value of the opportunity."""
        
        confidence = event_data.get("confidence", 0.5)
        
        if confidence > 0.8:
            return "high"
        elif confidence > 0.5:
            return "medium"
        
        return "low"
    
    def _assess_time_sensitivity(self, event_data: Dict[str, Any]) -> str:
        """Assess how time-sensitive the opportunity is."""
        
        severity = event_data.get("severity", "")
        
        if severity == DetectionSeverity.CRITICAL:
            return "high"
        elif severity == DetectionSeverity.HIGH:
            return "medium"
        
        return "low"
    
    def _calculate_confidence(self, event_data: Dict[str, Any]) -> float:
        """Calculate confidence in the opportunity."""
        
        base_confidence = event_data.get("confidence", 0.5)
        
        # Adjust based on available data
        if event_data.get("source_signals"):
            base_confidence = min(0.9, base_confidence + 0.1)
        
        return base_confidence
    
    def _get_recommended_action(self, opportunity_type: str) -> str:
        """Get recommended action for the opportunity."""
        
        actions = {
            "financial_investment": "Review investment options and consult with Finance Agent",
            "health_improvement": "Consult with Health Agent for optimization recommendations",
            "productivity_gain": "Review workflow with Operations Agent",
            "project_acceleration": "Prioritize resource allocation to accelerate project",
            "strategic_opportunity": "Initiate strategic review with board agents",
        }
        
        return actions.get(opportunity_type, "Conduct further analysis")


class RiskClassifier:
    """Classifies risks from detected events."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def classify_risk(
        self,
        event_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Classify an event as a risk."""
        
        risk_type = self._determine_risk_type(event_data)
        
        return {
            "type": DetectionEventType.RISK,
            "risk_type": risk_type,
            "title": f"Risk: {self._get_risk_title(risk_type)}",
            "description": self._get_risk_description(event_data, risk_type),
            "severity": self._assess_risk_severity(event_data),
            "probability": self._estimate_probability(event_data),
            "mitigation_suggestion": self._get_mitigation_suggestion(risk_type),
            "confidence": self._calculate_confidence(event_data),
        }
    
    def _determine_risk_type(self, event_data: Dict[str, Any]) -> str:
        """Determine the type of risk."""
        
        domain = event_data.get("domain", "")
        
        if domain == DomainType.FINANCIAL:
            return "financial_exposure"
        elif domain == DomainType.HEALTH:
            return "health_risk"
        elif domain == DomainType.PRODUCTIVITY:
            return "operational_risk"
        elif domain == DomainType.PROJECTS:
            return "project_risk"
        
        return "strategic_risk"
    
    def _get_risk_title(self, risk_type: str) -> str:
        """Get a title for the risk type."""
        
        titles = {
            "financial_exposure": "Financial Risk Detected",
            "health_risk": "Health Risk Identified",
            "operational_risk": "Operational Risk Warning",
            "project_risk": "Project Risk Alert",
            "strategic_risk": "Strategic Risk Noted",
        }
        
        return titles.get(risk_type, "Risk Detected")
    
    def _get_risk_description(
        self,
        event_data: Dict[str, Any],
        risk_type: str,
    ) -> str:
        """Generate a risk description."""
        
        descriptions = {
            "financial_exposure": "Analysis indicates elevated financial risk that warrants attention.",
            "health_risk": "Data suggests potential health risks that should be addressed.",
            "operational_risk": "Operational patterns indicate potential efficiency issues.",
            "project_risk": "Project indicators suggest elevated risk of delays or failure.",
            "strategic_risk": "Strategic analysis indicates potential misalignment or risk.",
        }
        
        return descriptions.get(risk_type, "A potential risk has been identified.")
    
    def _assess_risk_severity(self, event_data: Dict[str, Any]) -> str:
        """Assess the severity of the risk."""
        
        # Check for explicit severity
        if "severity" in event_data:
            return event_data["severity"]
        
        # Infer from confidence and patterns
        confidence = event_data.get("confidence", 0.5)
        
        if confidence > 0.8:
            return DetectionSeverity.HIGH
        elif confidence > 0.5:
            return DetectionSeverity.MEDIUM
        
        return DetectionSeverity.LOW
    
    def _estimate_probability(self, event_data: Dict[str, Any]) -> float:
        """Estimate probability of risk materializing."""
        
        confidence = event_data.get("confidence", 0.5)
        
        # Probability is related to confidence
        return min(0.95, confidence * 1.2)
    
    def _get_mitigation_suggestion(self, risk_type: str) -> str:
        """Get mitigation suggestion for the risk."""
        
        suggestions = {
            "financial_exposure": "Review portfolio allocation and consult with Risk Agent",
            "health_risk": "Consult with Health Agent and consider lifestyle adjustments",
            "operational_risk": "Review workflows with Operations Agent",
            "project_risk": "Conduct project review and risk assessment",
            "strategic_risk": "Initiate strategic review with governance",
        }
        
        return suggestions.get(risk_type, "Conduct risk assessment")
    
    def _calculate_confidence(self, event_data: Dict[str, Any]) -> float:
        """Calculate confidence in the risk classification."""
        
        base_confidence = event_data.get("confidence", 0.5)
        
        if event_data.get("source_signals"):
            base_confidence = min(0.9, base_confidence + 0.1)
        
        return base_confidence


async def get_opportunity_classifier(session: AsyncSession) -> OpportunityClassifier:
    """Get opportunity classifier instance."""
    return OpportunityClassifier(session)


async def get_risk_classifier(session: AsyncSession) -> RiskClassifier:
    """Get risk classifier instance."""
    return RiskClassifier(session)
