"""Execution Report Builder - generates execution activity reports.

This module provides execution-specific report generation.
"""
from app.system_outputs.output_generator import get_output_generator


class ExecutionReportBuilder:
    """Generates execution activity reports."""
    
    def build(self):
        """Build execution report."""
        generator = get_output_generator()
        return generator.generate_execution_report()
    
    def build_summary(self):
        """Build execution summary."""
        generator = get_output_generator()
        report = generator.generate_execution_report()
        
        return {
            "executions_today": report.executions_today,
            "successful_executions": report.successful_executions,
            "failed_executions": report.failed_executions,
            "execution_success_rate": report.execution_success_rate,
            "by_action_type": report.by_action_type,
        }


def get_execution_report_builder():
    """Get execution report builder instance."""
    return ExecutionReportBuilder()
