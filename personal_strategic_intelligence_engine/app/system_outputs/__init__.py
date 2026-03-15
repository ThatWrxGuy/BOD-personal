"""System Outputs - PSIE operational output interface and intelligence reports.

This module provides PSIE operational outputs:
- output_collector.py - Collects raw outputs from all subsystems
- output_generator.py - Transforms outputs into intelligence summaries
- strategy_report_builder.py - Strategy activity reports
- execution_report_builder.py - Execution activity reports
- financial_report_builder.py - Financial intelligence reports
- learning_report_builder.py - Learning insight reports
- system_metrics_builder.py - System performance reports
- eod_report_builder.py - End-of-Day reports

Output Categories:
- Strategy Outputs: proposals, approvals, rejections
- Execution Outputs: executed actions and results
- Financial Intelligence: portfolio metrics
- Learning Insights: strategy performance
- System Intelligence: signals, health, metrics
"""
from app.system_outputs.output_models import (
    OutputCategory,
    DecisionStatus,
    RiskLevel,
    StrategyOutput,
    ExecutionOutput,
    FinancialOutput,
    LearningOutput,
    SystemOutput,
    KnowledgeOutput,
    StrategyReport,
    ExecutionReport,
    FinancialReport,
    LearningReport,
    SystemMetricsReport,
    EODReport,
    OutputsOverview,
)

from app.system_outputs.output_collector import (
    OutputCollector,
    get_output_collector,
    reset_output_collector,
)

from app.system_outputs.output_generator import (
    OutputGenerator,
    get_output_generator,
    reset_output_generator,
)

from app.system_outputs.routes import router

__all__ = [
    # Models
    "OutputCategory",
    "DecisionStatus",
    "RiskLevel",
    "StrategyOutput",
    "ExecutionOutput",
    "FinancialOutput",
    "LearningOutput",
    "SystemOutput",
    "KnowledgeOutput",
    "StrategyReport",
    "ExecutionReport",
    "FinancialReport",
    "LearningReport",
    "SystemMetricsReport",
    "EODReport",
    "OutputsOverview",
    # Collectors
    "OutputCollector",
    "get_output_collector",
    "reset_output_collector",
    # Generators
    "OutputGenerator",
    "get_output_generator",
    "reset_output_generator",
    # Routes
    "router",
]
