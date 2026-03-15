"""Learning Report Builder - generates learning insight reports.

This module provides learning-specific report generation.
"""
from app.system_outputs.output_generator import get_output_generator


class LearningReportBuilder:
    """Generates learning insight reports."""
    
    def build(self):
        """Build learning report."""
        generator = get_output_generator()
        return generator.generate_learning_report()
    
    def build_summary(self):
        """Build learning summary."""
        generator = get_output_generator()
        report = generator.generate_learning_report()
        
        return {
            "learning_events": report.learning_events,
            "strategy_improvements": report.strategy_improvements,
            "degradation_alerts": report.degradation_alerts,
            "confidence_adjustments": report.confidence_adjustments,
        }


def get_learning_report_builder():
    """Get learning report builder instance."""
    return LearningReportBuilder()
