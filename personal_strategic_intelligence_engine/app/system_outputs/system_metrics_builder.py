"""System Metrics Builder - generates system performance reports.

This module provides system metrics-specific report generation.
"""
from app.system_outputs.output_generator import get_output_generator


class SystemMetricsBuilder:
    """Generates system performance reports."""
    
    def build(self):
        """Build system metrics report."""
        generator = get_output_generator()
        return generator.generate_system_metrics_report()
    
    def build_summary(self):
        """Build system metrics summary."""
        generator = get_output_generator()
        report = generator.generate_system_metrics_report()
        
        return {
            "signals_processed": report.signals_processed,
            "agents_active": report.agents_active,
            "agent_cycles_completed": report.agent_cycles_completed,
            "proposals_generated": report.proposals_generated,
            "proposals_approved": report.proposals_approved,
            "executions_completed": report.executions_completed,
            "execution_success_rate": report.execution_success_rate,
            "uptime_seconds": report.uptime_seconds,
        }


def get_system_metrics_builder():
    """Get system metrics builder instance."""
    return SystemMetricsBuilder()
