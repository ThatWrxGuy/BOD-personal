"""Recommendation Engine - generates structured financial recommendations from detected signals."""
from typing import Any, Dict, List

from app.finance.intelligence.models.financial_signal import FinancialSignal, SignalType, Severity
from app.finance.intelligence.models.financial_risk import RiskType
from app.finance.intelligence.models.financial_opportunity import OpportunityType
from app.finance.intelligence.models.financial_recommendation import FinancialRecommendation, Priority, ActionClass


class RecommendationEngine:
    """
    Generates structured financial recommendations from detected signals.
    """

    @staticmethod
    def generate(
        financial_state: Dict[str, Any],
        signals: List[FinancialSignal],
    ) -> List[FinancialRecommendation]:
        """
        Generate recommendations from financial signals.

        Args:
            financial_state: The canonical financial state
            signals: List of detected financial signals

        Returns:
            List of FinancialRecommendation objects
        """
        recommendations = []
        profile_id = financial_state.get("profile_id", 0)

        # Analyze signals and generate appropriate recommendations
        for signal in signals:
            if signal.signal_type == SignalType.RISK:
                rec = RecommendationEngine._generate_risk_recommendation(
                    financial_state, signal, profile_id
                )
                if rec:
                    recommendations.append(rec)
            elif signal.signal_type == SignalType.OPPORTUNITY:
                rec = RecommendationEngine._generate_opportunity_recommendation(
                    financial_state, signal, profile_id
                )
                if rec:
                    recommendations.append(rec)

        # Sort by priority
        recommendations.sort(
            key=lambda r: RecommendationEngine._priority_order(r.priority), 
            reverse=True
        )

        return recommendations

    @staticmethod
    def _generate_risk_recommendation(
        financial_state: Dict[str, Any],
        signal: FinancialSignal,
        profile_id: int,
    ) -> FinancialRecommendation:
        """Generate recommendation based on risk signal."""
        
        # Map signal severity to recommendation priority
        priority = RecommendationEngine._map_severity_to_priority(signal.severity)
        
        if "debt_to_income" in signal.metric_reference or signal.title.lower().find("debt") >= 0:
            return RecommendationEngine._create_debt_recommendation(
                financial_state, signal, profile_id, priority
            )
        elif "emergency_fund" in signal.metric_reference or "liquidity" in signal.metric_reference:
            return RecommendationEngine._create_liquidity_recommendation(
                financial_state, signal, profile_id, priority
            )
        elif "cash_flow" in signal.metric_reference or signal.title.lower().find("cash flow") >= 0:
            return RecommendationEngine._create_cashflow_recommendation(
                financial_state, signal, profile_id, priority
            )
        elif "credit_card" in signal.metric_reference or "high_interest" in signal.metric_reference:
            return RecommendationEngine._create_high_interest_debt_recommendation(
                financial_state, signal, profile_id, priority
            )
        elif "concentration" in signal.metric_reference:
            return RecommendationEngine._create_diversification_recommendation(
                financial_state, signal, profile_id, priority
            )
        
        # Default recommendation
        return FinancialRecommendation.create(
            profile_id=profile_id,
            title=f"Address: {signal.title}",
            summary=signal.description,
            rationale=f"Risk detected: {signal.description}",
            priority=priority,
            confidence_score=0.75,
            expected_benefit="Risk mitigation improves financial stability.",
            downside_risk="Action may require short-term lifestyle adjustments.",
            action_class=ActionClass.ADVISORY,
        )

    @staticmethod
    def _generate_opportunity_recommendation(
        financial_state: Dict[str, Any],
        signal: FinancialSignal,
        profile_id: int,
    ) -> FinancialRecommendation:
        """Generate recommendation based on opportunity signal."""
        
        if "debt_payoff" in signal.title.lower() or "debt" in signal.description.lower():
            return FinancialRecommendation.create(
                profile_id=profile_id,
                title="Accelerate Debt Payoff",
                summary=f"Use available cash flow to reduce high-interest debt faster.",
                rationale=f"Opportunity identified: {signal.description}",
                priority=Priority.HIGH,
                confidence_score=0.80,
                expected_benefit="Reduce interest costs and achieve debt freedom sooner.",
                downside_risk="Requires redirecting funds from other uses.",
                action_class=ActionClass.ADVISORY,
            )
        elif "investment" in signal.title.lower() or "invest" in signal.description.lower():
            return FinancialRecommendation.create(
                profile_id=profile_id,
                title="Optimize Investment Allocation",
                summary="Deploy excess cash toward investment accounts for growth.",
                rationale=f"Opportunity identified: {signal.description}",
                priority=Priority.MEDIUM,
                confidence_score=0.75,
                expected_benefit="Long-term wealth accumulation through compound growth.",
                downside_risk="Market volatility may affect short-term values.",
                action_class=ActionClass.ADVISORY,
            )
        elif "reserve" in signal.title.lower() or "emergency" in signal.description.lower():
            return FinancialRecommendation.create(
                profile_id=profile_id,
                title="Optimize Reserve Allocation",
                summary="Redistribute excess reserves to higher-yielding accounts.",
                rationale=f"Opportunity identified: {signal.description}",
                priority=Priority.MEDIUM,
                confidence_score=0.85,
                expected_benefit="Improved returns on liquid assets.",
                downside_risk="Slightly reduced accessibility of funds.",
                action_class=ActionClass.ADVISORY,
            )
        elif "savings" in signal.title.lower():
            return FinancialRecommendation.create(
                profile_id=profile_id,
                title="Explore High-Yield Savings Options",
                summary="Consider moving savings to higher-yield accounts.",
                rationale=f"Opportunity identified: {signal.description}",
                priority=Priority.LOW,
                confidence_score=0.90,
                expected_benefit="Higher interest earnings on savings.",
                downside_risk="May require account迁移.",
                action_class=ActionClass.ADVISORY,
            )
        
        # Default opportunity recommendation
        return FinancialRecommendation.create(
            profile_id=profile_id,
            title=f"Consider: {signal.title}",
            summary=signal.description,
            rationale=f"Opportunity identified: {signal.description}",
            priority=Priority.MEDIUM,
            confidence_score=0.70,
            expected_benefit="Potential improvement in financial position.",
            downside_risk="Depends on individual circumstances.",
            action_class=ActionClass.ADVISORY,
        )

    @staticmethod
    def _create_debt_recommendation(
        financial_state: Dict[str, Any],
        signal: FinancialSignal,
        profile_id: int,
        priority: Priority,
    ) -> FinancialRecommendation:
        """Create debt-related recommendation."""
        dti = signal.metric_value
        return FinancialRecommendation.create(
            profile_id=profile_id,
            title="Debt Reduction Plan",
            summary=f"Develop a structured debt reduction plan to lower DTI from {dti:.1%}.",
            rationale=f"High debt-to-income ratio of {dti:.1%} constrains financial flexibility.",
            priority=priority,
            confidence_score=0.80,
            expected_benefit="Improved debt-to-income ratio and increased borrowing capacity.",
            downside_risk="Requires sustained discipline and potential lifestyle changes.",
            action_class=ActionClass.ADVISORY,
        )

    @staticmethod
    def _create_liquidity_recommendation(
        financial_state: Dict[str, Any],
        signal: FinancialSignal,
        profile_id: int,
        priority: Priority,
    ) -> FinancialRecommendation:
        """Create liquidity/emergency fund recommendation."""
        months = signal.metric_value
        return FinancialRecommendation.create(
            profile_id=profile_id,
            title="Build Emergency Reserve",
            summary=f"Build emergency fund to {max(6, months + 3):.0f}+ months of expenses.",
            rationale=f"Current emergency fund of {months:.1f} months is insufficient.",
            priority=priority,
            confidence_score=0.85,
            expected_benefit="Financial security and peace of mind for unexpected expenses.",
            downside_risk="Requires reducing other spending temporarily.",
            action_class=ActionClass.ADVISORY,
        )

    @staticmethod
    def _create_cashflow_recommendation(
        financial_state: Dict[str, Any],
        signal: FinancialSignal,
        profile_id: int,
        priority: Priority,
    ) -> FinancialRecommendation:
        """Create cash flow adjustment recommendation."""
        fcf = signal.metric_value
        return FinancialRecommendation.create(
            profile_id=profile_id,
            title="Address Cash Flow Deficit",
            summary=f"Reduce expenses or increase income to achieve positive cash flow.",
            rationale=f"Current free cash flow of ${fcf:,.2f} is negative.",
            priority=priority,
            confidence_score=0.75,
            expected_benefit="Achieving positive cash flow enables savings and investment.",
            downside_risk="May require significant lifestyle adjustments.",
            action_class=ActionClass.ADVISORY,
        )

    @staticmethod
    def _create_high_interest_debt_recommendation(
        financial_state: Dict[str, Any],
        signal: FinancialSignal,
        profile_id: int,
        priority: Priority,
    ) -> FinancialRecommendation:
        """Create high interest debt recommendation."""
        balance = signal.metric_value
        return FinancialRecommendation.create(
            profile_id=profile_id,
            title="Attack High-Interest Debt",
            summary=f"Prioritize paying off ${balance:,.2f} in high-interest debt.",
            rationale="Credit card and high-interest debt erodes wealth through interest charges.",
            priority=priority,
            confidence_score=0.85,
            expected_benefit="Significant interest savings and improved cash flow.",
            downside_risk="Requires redirecting funds from other uses.",
            action_class=ActionClass.ADVISORY,
        )

    @staticmethod
    def _create_diversification_recommendation(
        financial_state: Dict[str, Any],
        signal: FinancialSignal,
        profile_id: int,
        priority: Priority,
    ) -> FinancialRecommendation:
        """Create diversification recommendation."""
        return FinancialRecommendation.create(
            profile_id=profile_id,
            title="Diversify Asset Allocation",
            summary="Reduce concentration risk through portfolio diversification.",
            rationale="Single asset class represents excessive portfolio concentration.",
            priority=priority,
            confidence_score=0.70,
            expected_benefit="Reduced risk through broader diversification.",
            downside_risk="May incur transaction costs or tax implications.",
            action_class=ActionClass.ADVISORY,
        )

    @staticmethod
    def _map_severity_to_priority(severity: Severity) -> Priority:
        """Map signal severity to recommendation priority."""
        mapping = {
            Severity.CRITICAL: Priority.CRITICAL,
            Severity.HIGH: Priority.HIGH,
            Severity.MEDIUM: Priority.MEDIUM,
            Severity.LOW: Priority.LOW,
        }
        return mapping.get(severity, Priority.MEDIUM)

    @staticmethod
    def _priority_order(priority: Priority) -> int:
        """Return numeric order for priority sorting."""
        order = {
            Priority.CRITICAL: 4,
            Priority.HIGH: 3,
            Priority.MEDIUM: 2,
            Priority.LOW: 1,
        }
        return order.get(priority, 0)
