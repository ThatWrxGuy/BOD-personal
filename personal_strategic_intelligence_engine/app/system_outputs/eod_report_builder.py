"""EOD Report Builder - generates End-of-Day intelligence reports.

This module provides EOD report generation.
"""
from app.system_outputs.output_generator import get_output_generator


class EODReportBuilder:
    """Generates End-of-Day intelligence reports."""
    
    def build(self):
        """Build EOD report."""
        generator = get_output_generator()
        return generator.generate_eod_report()
    
    def build_summary(self):
        """Build EOD summary."""
        generator = get_output_generator()
        report = generator.generate_eod_report()
        
        return {
            "signals_processed": report.signals_processed,
            "strategies_proposed": report.strategies_proposed,
            "proposals_approved": report.proposals_approved,
            "executions_completed": report.executions_completed,
            "learning_events": report.learning_events,
            "overall_success_rate": report.overall_success_rate,
        }


def get_eod_report_builder():
    """Get EOD report builder instance."""
    return EODReportBuilder()
