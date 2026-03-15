"""Risk Detector - analyzes financial metrics and detects risk conditions."""
from typing import Any, Dict, List

from app.finance.intelligence.models.financial_risk import FinancialRisk, RiskType, Severity


class RiskDetector:
    """
    Analyzes financial metrics produced by the Finance State Engine
    and detects risk conditions.
    """

    # Risk thresholds
    DTI_THRESHOLD_CRITICAL = 0.45
    DTI_THRESHOLD_HIGH = 0.36
    DTI_THRESHOLD_MEDIUM = 0.28
    
    EMERGENCY_FUND_MONTHS_CRITICAL = 1
    EMERGENCY_FUND_MONTHS_LOW = 3
    EMERGENCY_FUND_MONTHS_MEDIUM = 6
    
    CASH_FLOW_NEGATIVE_CRITICAL = 0
    CASH_FLOW_NEGATIVE_HIGH = -500
    
    CREDIT_CARD_INTEREST_THRESHOLD = 20.0
    
    ASSET_CONCENTRATION_THRESHOLD = 0.50
    
    VOLATILITY_THRESHOLD_HIGH = 0.4
    VOLATILITY_THRESHOLD_MEDIUM = 0.25

    @staticmethod
    def detect(
        financial_state: Dict[str, Any],
        financial_metrics: Dict[str, Any],
    ) -> List[FinancialRisk]:
        """
        Detect risk conditions from financial state and metrics.

        Args:
            financial_state: The canonical financial state
            financial_metrics: Additional financial metrics

        Returns:
            List of FinancialRisk objects
        """
        risks = []
        profile_id = financial_state.get("profile_id", 0)

        # Check Debt-to-Income Risk
        dti_risks = RiskDetector._check_debt_to_income(
            financial_state, profile_id
        )
        risks.extend(dti_risks)

        # Check Liquidity Risk
        liquidity_risks = RiskDetector._check_liquidity(
            financial_state, profile_id
        )
        risks.extend(liquidity_risks)

        # Check Cash Flow Risk
        cash_flow_risks = RiskDetector._check_cash_flow(
            financial_state, profile_id
        )
        risks.extend(cash_flow_risks)

        # Check High Interest Debt Risk
        high_interest_risks = RiskDetector._check_high_interest_debt(
            financial_state, profile_id
        )
        risks.extend(high_interest_risks)

        # Check Asset Concentration Risk
        concentration_risks = RiskDetector._check_asset_concentration(
            financial_state, profile_id
        )
        risks.extend(concentration_risks)

        # Check Volatility Exposure Risk
        volatility_risks = RiskDetector._check_volatility_exposure(
            financial_state, profile_id
        )
        risks.extend(volatility_risks)

        return risks

    @staticmethod
    def _check_debt_to_income(
        financial_state: Dict[str, Any],
        profile_id: int,
    ) -> List[FinancialRisk]:
        """Check debt-to-income ratio risks."""
        risks = []
        dti = financial_state.get("debt_to_income_ratio", 0)

        if dti > RiskDetector.DTI_THRESHOLD_CRITICAL:
            risks.append(FinancialRisk.create(
                profile_id=profile_id,
                risk_type=RiskType.HIGH_DEBT_TO_INCOME,
                severity=Severity.CRITICAL,
                description=f"Debt-to-income ratio of {dti:.1%} significantly exceeds safe levels. This indicates excessive debt burden relative to income.",
                trigger_metric="debt_to_income_ratio",
                trigger_value=dti,
                recommended_mitigation="Prioritize debt reduction. Consider debt consolidation or seek additional income sources to reduce DTI below 36%."
            ))
        elif dti > RiskDetector.DTI_THRESHOLD_HIGH:
            risks.append(FinancialRisk.create(
                profile_id=profile_id,
                risk_type=RiskType.HIGH_DEBT_TO_INCOME,
                severity=Severity.HIGH,
                description=f"Debt-to-income ratio of {dti:.1%} is elevated. Financial flexibility may be constrained.",
                trigger_metric="debt_to_income_ratio",
                trigger_value=dti,
                recommended_mitigation="Develop a debt reduction plan. Focus on high-interest debt first to improve DTI."
            ))

        return risks

    @staticmethod
    def _check_liquidity(
        financial_state: Dict[str, Any],
        profile_id: int,
    ) -> List[FinancialRisk]:
        """Check liquidity/emergency fund risks."""
        risks = []
        emergency_months = financial_state.get("emergency_fund_months", 0)

        if emergency_months < RiskDetector.EMERGENCY_FUND_MONTHS_CRITICAL:
            risks.append(FinancialRisk.create(
                profile_id=profile_id,
                risk_type=RiskType.LOW_LIQUIDITY,
                severity=Severity.CRITICAL,
                description=f"Emergency fund of only {emergency_months:.1f} months is critically low. Vulnerable to unexpected expenses.",
                trigger_metric="emergency_fund_months",
                trigger_value=emergency_months,
                recommended_mitigation="IMMEDIATE ACTION: Build emergency fund to at least 3 months of expenses. Reduce discretionary spending."
            ))
        elif emergency_months < RiskDetector.EMERGENCY_FUND_MONTHS_LOW:
            risks.append(FinancialRisk.create(
                profile_id=profile_id,
                risk_type=RiskType.EMERGENCY_FUND_INSUFFICIENT,
                severity=Severity.HIGH,
                description=f"Emergency fund of {emergency_months:.1f} months is below recommended minimum of 3 months.",
                trigger_metric="emergency_fund_months",
                trigger_value=emergency_months,
                recommended_mitigation="Prioritize building emergency fund to 3 months before major financial decisions."
            ))
        elif emergency_months < RiskDetector.EMERGENCY_FUND_MONTHS_MEDIUM:
            risks.append(FinancialRisk.create(
                profile_id=profile_id,
                risk_type=RiskType.LOW_LIQUIDITY,
                severity=Severity.MEDIUM,
                description=f"Emergency fund of {emergency_months:.1f} months is adequate but could be stronger.",
                trigger_metric="emergency_fund_months",
                trigger_value=emergency_months,
                recommended_mitigation="Consider increasing emergency fund to 6 months for additional financial security."
            ))

        return risks

    @staticmethod
    def _check_cash_flow(
        financial_state: Dict[str, Any],
        profile_id: int,
    ) -> List[FinancialRisk]:
        """Check negative cash flow risks."""
        risks = []
        fcf = financial_state.get("free_cash_flow", 0)

        if fcf < RiskDetector.CASH_FLOW_NEGATIVE_CRITICAL:
            risks.append(FinancialRisk.create(
                profile_id=profile_id,
                risk_type=RiskType.NEGATIVE_CASH_FLOW,
                severity=Severity.CRITICAL,
                description=f"Negative free cash flow of ${fcf:,.2f} per month. Spending exceeds income.",
                trigger_metric="free_cash_flow",
                trigger_value=fcf,
                recommended_mitigation="URGENT: Reduce expenses or increase income immediately. Consider reviewing all discretionary spending."
            ))
        elif fcf < RiskDetector.CASH_FLOW_NEGATIVE_HIGH:
            risks.append(FinancialRisk.create(
                profile_id=profile_id,
                risk_type=RiskType.NEGATIVE_CASH_FLOW,
                severity=Severity.HIGH,
                description=f"Free cash flow of ${fcf:,.2f} is negative. Financial buffer is being depleted.",
                trigger_metric="free_cash_flow",
                trigger_value=fcf,
                recommended_mitigation="Address cash flow deficit. Review expenses and identify areas for reduction."
            ))

        return risks

    @staticmethod
    def _check_high_interest_debt(
        financial_state: Dict[str, Any],
        profile_id: int,
    ) -> List[FinancialRisk]:
        """Check for high interest debt (credit cards, etc.)."""
        risks = []
        
        revolving_debt = financial_state.get("revolving_debt_balance", 0)
        liabilities = financial_state.get("liabilities_by_category", {})
        credit_card_debt = liabilities.get("credit_card", 0)

        if credit_card_debt > 0:
            # In a full implementation, we would check actual interest rates
            # For now, we assume credit card debt has high interest
            risks.append(FinancialRisk.create(
                profile_id=profile_id,
                risk_type=RiskType.HIGH_INTEREST_DEBT,
                severity=Severity.HIGH,
                description=f"Credit card debt of ${credit_card_debt:,.2f} is likely incurring high interest charges.",
                trigger_metric="credit_card_balance",
                trigger_value=credit_card_debt,
                recommended_mitigation="Prioritize paying off credit card debt. Consider balance transfer to lower interest card or debt consolidation."
            ))

        return risks

    @staticmethod
    def _check_asset_concentration(
        financial_state: Dict[str, Any],
        profile_id: int,
    ) -> List[FinancialRisk]:
        """Check for asset concentration risks."""
        risks = []
        assets_by_category = financial_state.get("assets_by_category", {})
        total_assets = financial_state.get("total_assets", 0)

        if total_assets > 0:
            for category, value in assets_by_category.items():
                concentration = value / total_assets
                if concentration > RiskDetector.ASSET_CONCENTRATION_THRESHOLD:
                    risks.append(FinancialRisk.create(
                        profile_id=profile_id,
                        risk_type=RiskType.ASSET_CONCENTRATION,
                        severity=Severity.MEDIUM,
                        description=f"{category} represents {concentration:.1%} of total assets, indicating lack of diversification.",
                        trigger_metric=f"asset_concentration_{category}",
                        trigger_value=concentration,
                        recommended_mitigation=f"Consider diversifying {category} holdings to reduce concentration risk."
                    ))

        return risks

    @staticmethod
    def _check_volatility_exposure(
        financial_state: Dict[str, Any],
        profile_id: int,
    ) -> List[FinancialRisk]:
        """Check for high volatility exposure in assets."""
        # This would require volatility data from assets
        # For now, return empty list as we don't have per-asset volatility data
        return []
