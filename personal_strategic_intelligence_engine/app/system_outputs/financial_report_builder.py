"""Financial Report Builder - generates financial intelligence reports.

This module provides financial-specific report generation.
"""
from app.system_outputs.output_generator import get_output_generator


class FinancialReportBuilder:
    """Generates financial intelligence reports."""
    
    def build(self):
        """Build financial report."""
        generator = get_output_generator()
        return generator.generate_financial_report()
    
    def build_summary(self):
        """Build financial summary."""
        generator = get_output_generator()
        report = generator.generate_financial_report()
        
        return {
            "portfolio_value": report.portfolio_value,
            "daily_return": report.daily_return,
            "current_drawdown": report.current_drawdown,
            "risk_exposure": report.risk_exposure,
            "liquidity_status": report.liquidity_status,
        }


def get_financial_report_builder():
    """Get financial report builder instance."""
    return FinancialReportBuilder()
