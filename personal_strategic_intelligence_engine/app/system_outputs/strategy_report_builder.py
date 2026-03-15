"""Strategy Report Builder - generates strategy activity reports.

This module provides strategy-specific report generation.
"""
from app.system_outputs.output_generator import get_output_generator


class StrategyReportBuilder:
    """Generates strategy activity reports."""
    
    def build(self):
        """Build strategy report."""
        generator = get_output_generator()
        return generator.generate_strategy_report()
    
    def build_summary(self):
        """Build strategy summary."""
        generator = get_output_generator()
        report = generator.generate_strategy_report()
        
        return {
            "strategies_proposed": report.strategies_proposed,
            "strategies_approved": report.strategies_approved,
            "strategies_rejected": report.strategies_rejected,
            "average_confidence": report.average_confidence,
            "top_strategy": report.top_strategy,
        }


def get_strategy_report_builder():
    """Get strategy report builder instance."""
    return StrategyReportBuilder()
