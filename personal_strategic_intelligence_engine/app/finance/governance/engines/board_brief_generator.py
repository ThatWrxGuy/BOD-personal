"""Board Brief Generator - produces a structured Financial Intelligence Brief for the board."""
from typing import Any, Dict, List, Optional

from app.finance.governance.models.financial_board_brief import (
    FinancialBoardBrief,
    FinancialStatus,
    RiskLevel,
    ConfidenceLevel,
)
from app.finance.intelligence.models.financial_risk import FinancialRisk
from app.finance.intelligence.models.financial_opportunity import FinancialOpportunity
from app.finance.intelligence.models.financial_recommendation import FinancialRecommendation


class BoardBriefGenerator:
    """
    Produces a structured Financial Intelligence Brief for the board.
    
    Input:
    - Financial state
    - Financial signals
    - Financial recommendations
    - Scenario outputs
    
    Output:
    - FinancialBoardBrief
    """

    @staticmethod
    def generate(
        financial_state: Dict[str, Any],
        risks: Optional[List[FinancialRisk]] = None,
        opportunities: Optional[List[FinancialOpportunity]] = None,
        recommendations: Optional[List[FinancialRecommendation]] = None,
        scenario_summary: Optional[Dict[str, Any]] = None,
    ) -> FinancialBoardBrief:
        """
        Generate a board-ready financial intelligence brief.

        Args:
            financial_state: Current financial state
            risks: Detected financial risks
            opportunities: Detected financial opportunities
            recommendations: Generated recommendations
            scenario_summary: Summary of scenario simulations

        Returns:
            FinancialBoardBrief ready for board presentation
        """
        profile_id = financial_state.get("profile_id", 0)
        
        # Extract key metrics
        net_worth = financial_state.get("net_worth", 0)
        free_cash_flow = financial_state.get("free_cash_flow", 0)
        liquid_reserves = financial_state.get("liquid_assets", 0)
        debt_exposure = financial_state.get("total_debt", 0)
        
        # Determine financial status
        financial_status = BoardBriefGenerator._determine_financial_status(
            net_worth, free_cash_flow, liquid_reserves, debt_exposure
        )
        
        # Determine risk level
        risk_level = BoardBriefGenerator._determine_risk_level(
            risks or [], financial_state
        )
        
        # Determine confidence level
        confidence_level = BoardBriefGenerator._determine_confidence_level(
            recommendations or []
        )
        
        # Extract top risks
        top_risks = BoardBriefGenerator._extract_top_risks(risks or [])
        
        # Extract top opportunities
        top_opportunities = BoardBriefGenerator._extract_top_opportunities(opportunities or [])
        
        # Generate recommended actions
        recommended_actions = BoardBriefGenerator._generate_recommended_actions(
            recommendations or [], risk_level
        )
        
        return FinancialBoardBrief.create(
            profile_id=profile_id,
            financial_status=financial_status,
            risk_level=risk_level,
            confidence_level=confidence_level,
            net_worth=net_worth,
            free_cash_flow=free_cash_flow,
            liquid_reserves=liquid_reserves,
            debt_exposure=debt_exposure,
            top_risks=top_risks,
            top_opportunities=top_opportunities,
            recommended_actions=recommended_actions,
            scenario_summary=scenario_summary or {},
        )

    @staticmethod
    def _determine_financial_status(
        net_worth: float,
        free_cash_flow: float,
        liquid_reserves: float,
        debt_exposure: float,
    ) -> FinancialStatus:
        """Determine overall financial status."""
        # At risk: negative net worth or negative cash flow
        if net_worth < 0 or free_cash_flow < 0:
            return FinancialStatus.AT_RISK
        
        # Watch: low reserves relative to debt
        if debt_exposure > 0 and liquid_reserves / debt_exposure < 0.2:
            return FinancialStatus.WATCH
        
        # Stable: everything looks good
        return FinancialStatus.STABLE

    @staticmethod
    def _determine_risk_level(
        risks: List[FinancialRisk],
        financial_state: Dict[str, Any],
    ) -> RiskLevel:
        """Determine overall risk level."""
        from app.finance.intelligence.models.financial_risk import Severity
        
        # Check for critical risks
        critical_count = sum(1 for r in risks if r.severity == Severity.CRITICAL)
        if critical_count > 0:
            return RiskLevel.CRITICAL
        
        # Check for high risks
        high_count = sum(1 for r in risks if r.severity == Severity.HIGH)
        if high_count >= 2:
            return RiskLevel.HIGH
        if high_count == 1:
            # Check emergency fund
            emergency_months = financial_state.get("emergency_fund_months", 0)
            if emergency_months < 3:
                return RiskLevel.HIGH
        
        # Check for moderate risks
        medium_count = sum(1 for r in risks if r.severity == Severity.MEDIUM)
        if medium_count >= 3:
            return RiskLevel.MODERATE
        
        return RiskLevel.LOW

    @staticmethod
    def _determine_confidence_level(
        recommendations: List[FinancialRecommendation],
    ) -> ConfidenceLevel:
        """Determine confidence level based on recommendations."""
        if not recommendations:
            return ConfidenceLevel.MODERATE
        
        # Calculate average confidence
        avg_confidence = sum(r.confidence_score for r in recommendations) / len(recommendations)
        
        if avg_confidence >= 0.85:
            return ConfidenceLevel.HIGH
        elif avg_confidence >= 0.70:
            return ConfidenceLevel.MODERATE
        else:
            return ConfidenceLevel.LOW

    @staticmethod
    def _extract_top_risks(risks: List[FinancialRisk]) -> List[str]:
        """Extract top risks as strings."""
        from app.finance.intelligence.models.financial_risk import Severity
        
        # Sort by severity
        sorted_risks = sorted(risks, key=lambda r: (
            [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW].index(r.severity)
        ))
        
        # Return top 5
        return [r.description[:100] for r in sorted_risks[:5]]

    @staticmethod
    def _extract_top_opportunities(opportunities: List[FinancialOpportunity]) -> List[str]:
        """Extract top opportunities as strings."""
        # Return top 5
        return [opp.description[:100] for opp in opportunities[:5]]

    @staticmethod
    def _generate_recommended_actions(
        recommendations: List[FinancialRecommendation],
        risk_level: RiskLevel,
    ) -> List[str]:
        """Generate recommended actions from recommendations."""
        from app.finance.intelligence.models.financial_recommendation import Priority
        
        # Filter to high priority recommendations
        priority_recs = [r for r in recommendations if r.priority in [Priority.HIGH, Priority.CRITICAL]]
        
        # If not enough, include medium
        if len(priority_recs) < 3:
            priority_recs.extend([r for r in recommendations if r.priority == Priority.MEDIUM])
        
        # Sort by confidence
        priority_recs.sort(key=lambda r: r.confidence_score, reverse=True)
        
        # Return top 5
        return [f"{r.title}: {r.summary[:80]}" for r in priority_recs[:5]]

    @staticmethod
    def generate_executive_summary(brief: FinancialBoardBrief) -> str:
        """
        Generate an executive summary text.

        Args:
            brief: The financial board brief

        Returns:
            Formatted executive summary string
        """
        lines = [
            "=" * 60,
            "FINANCIAL INTELLIGENCE BRIEF",
            "=" * 60,
            "",
            f"Financial Status: {brief.financial_status.value.upper()}",
            f"Risk Level: {brief.risk_level.value.upper()}",
            f"Confidence Level: {brief.confidence_level.value.upper()}",
            "",
            "-" * 40,
            "KEY METRICS",
            "-" * 40,
            f"Net Worth: ${brief.net_worth:,.2f}",
            f"Free Cash Flow: ${brief.free_cash_flow:,.2f}/month",
            f"Liquid Reserves: ${brief.liquid_reserves:,.2f}",
            f"Debt Exposure: ${brief.debt_exposure:,.2f}",
            "",
        ]
        
        if brief.top_risks:
            lines.extend([
                "-" * 40,
                "TOP RISKS",
                "-" * 40,
            ])
            for i, risk in enumerate(brief.top_risks[:3], 1):
                lines.append(f"{i}. {risk}")
            lines.append("")
        
        if brief.recommended_actions:
            lines.extend([
                "-" * 40,
                "RECOMMENDED ACTIONS",
                "-" * 40,
            ])
            for i, action in enumerate(brief.recommended_actions[:3], 1):
                lines.append(f"{i}. {action}")
            lines.append("")
        
        lines.extend([
            "-" * 40,
            f"Generated: {brief.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
        ])
        
        return "\n".join(lines)
