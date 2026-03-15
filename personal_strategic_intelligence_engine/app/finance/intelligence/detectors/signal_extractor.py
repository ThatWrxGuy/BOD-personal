"""Signal Extractor - converts risks and opportunities into normalized FinancialSignal objects."""
from typing import Any, Dict, List

from app.finance.intelligence.models.financial_risk import FinancialRisk, RiskType, Severity as RiskSeverity
from app.finance.intelligence.models.financial_opportunity import FinancialOpportunity, OpportunityType
from app.finance.intelligence.models.financial_signal import FinancialSignal, SignalType, Severity


class SignalExtractor:
    """
    Converts risks and opportunities into normalized FinancialSignal objects.
    """

    @staticmethod
    def extract(
        risks: List[FinancialRisk],
        opportunities: List[FinancialOpportunity],
    ) -> List[FinancialSignal]:
        """
        Convert risks and opportunities into normalized signals.

        Args:
            risks: List of detected financial risks
            opportunities: List of detected financial opportunities

        Returns:
            List of FinancialSignal objects
        """
        signals = []

        # Convert risks to signals
        for risk in risks:
            signal = SignalExtractor._convert_risk_to_signal(risk)
            signals.append(signal)

        # Convert opportunities to signals
        for opportunity in opportunities:
            signal = SignalExtractor._convert_opportunity_to_signal(opportunity)
            signals.append(signal)

        # Sort by severity (critical first)
        signals.sort(key=lambda s: SignalExtractor._severity_order(s.severity), reverse=True)

        return signals

    @staticmethod
    def _convert_risk_to_signal(risk: FinancialRisk) -> FinancialSignal:
        """Convert a FinancialRisk to a FinancialSignal."""
        # Map risk severity to signal severity
        severity = SignalExtractor._map_risk_severity(risk.severity)

        return FinancialSignal.create(
            profile_id=risk.profile_id,
            signal_type=SignalType.RISK,
            severity=severity,
            title=f"Risk: {risk.risk_type.value.replace('_', ' ').title()}",
            description=risk.description,
            metric_reference=risk.trigger_metric,
            metric_value=risk.trigger_value,
            threshold_reference=risk.recommended_mitigation,
        )

    @staticmethod
    def _convert_opportunity_to_signal(opportunity: FinancialOpportunity) -> FinancialSignal:
        """Convert a FinancialOpportunity to a FinancialSignal."""
        # Opportunities are generally positive, so severity is lower
        # But they can be important to highlight
        severity = Severity.MEDIUM

        return FinancialSignal.create(
            profile_id=opportunity.profile_id,
            signal_type=SignalType.OPPORTUNITY,
            severity=severity,
            title=f"Opportunity: {opportunity.opportunity_type.value.replace('_', ' ').title()}",
            description=opportunity.description,
            metric_reference=opportunity.trigger_metric,
            metric_value=opportunity.trigger_value,
            threshold_reference=opportunity.expected_benefit,
        )

    @staticmethod
    def _map_risk_severity(risk_severity: RiskSeverity) -> Severity:
        """Map risk severity to signal severity."""
        mapping = {
            RiskSeverity.CRITICAL: Severity.CRITICAL,
            RiskSeverity.HIGH: Severity.HIGH,
            RiskSeverity.MEDIUM: Severity.MEDIUM,
            RiskSeverity.LOW: Severity.LOW,
        }
        return mapping.get(risk_severity, Severity.MEDIUM)

    @staticmethod
    def _severity_order(severity: Severity) -> int:
        """Return numeric order for severity sorting."""
        order = {
            Severity.CRITICAL: 4,
            Severity.HIGH: 3,
            Severity.MEDIUM: 2,
            Severity.LOW: 1,
        }
        return order.get(severity, 0)
