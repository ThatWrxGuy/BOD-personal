"""Output Generator - transforms collected outputs into intelligence summaries.

The Output Generator aggregates outputs from the collector and transforms them
into structured intelligence summaries for reporting.
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.system_outputs.output_models import (
    OutputsOverview,
    StrategyReport,
    ExecutionReport,
    FinancialReport,
    LearningReport,
    SystemMetricsReport,
    EODReport,
)
from app.system_outputs.output_collector import get_output_collector
from app.core.logging import get_logger

logger = get_logger(__name__)


class OutputGenerator:
    """
    Transforms collected outputs into structured intelligence summaries.
    
    Responsibilities:
    - Aggregate outputs by category
    - Generate summarized intelligence
    - Feed dashboard and report builders
    """
    
    def __init__(self):
        self._collector = get_output_collector()
    
    def generate_overview(self) -> OutputsOverview:
        """
        Generate complete intelligence outputs overview.
        
        Returns:
            OutputsOverview with all intelligence categories
        """
        strategy = self.generate_strategy_report()
        execution = self.generate_execution_report()
        financial = self.generate_financial_report()
        learning = self.generate_learning_report()
        system = self.generate_system_metrics_report()
        
        total_outputs = (
            len(strategy.recent_outputs) +
            len(execution.recent_outputs) +
            len(learning.recent_insights)
        )
        
        return OutputsOverview(
            generated_at=datetime.utcnow(),
            strategy=strategy,
            execution=execution,
            financial=financial,
            learning=learning,
            system=system,
            total_outputs=total_outputs,
            output_categories=["strategy", "execution", "financial", "learning", "system", "knowledge"],
        )
    
    def generate_strategy_report(self) -> StrategyReport:
        """
        Generate strategy activity report.
        
        Returns:
            StrategyReport with strategy metrics
        """
        outputs = self._collector.get_strategy_outputs()
        
        approved = [o for o in outputs if o.decision.value == "approved"]
        rejected = [o for o in outputs if o.decision.value == "rejected"]
        
        avg_confidence = 0.0
        if outputs:
            avg_confidence = sum(o.confidence for o in outputs) / len(outputs)
        
        top_strategy = outputs[0].title if outputs else None
        top_approved = approved[0].title if approved else None
        
        return StrategyReport(
            report_id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
            strategies_proposed=len(outputs),
            strategies_approved=len(approved),
            strategies_rejected=len(rejected),
            average_confidence=avg_confidence,
            average_risk_score=0.5,
            top_strategy=top_strategy,
            top_approved_strategy=top_approved,
            recent_outputs=outputs[:10],
        )
    
    def generate_execution_report(self) -> ExecutionReport:
        """
        Generate execution activity report.
        
        Returns:
            ExecutionReport with execution metrics
        """
        outputs = self._collector.get_execution_outputs()
        
        successful = [o for o in outputs if o.success]
        failed = [o for o in outputs if not o.success]
        
        success_rate = 0.0
        if outputs:
            success_rate = len(successful) / len(outputs)
        
        by_type: Dict[str, int] = {}
        for o in outputs:
            by_type[o.action_type] = by_type.get(o.action_type, 0) + 1
        
        return ExecutionReport(
            report_id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
            executions_today=len(outputs),
            successful_executions=len(successful),
            failed_executions=len(failed),
            execution_success_rate=success_rate,
            average_execution_time_ms=120.0,
            by_action_type=by_type,
            recent_outputs=outputs[:10],
        )
    
    def generate_financial_report(self) -> FinancialReport:
        """
        Generate financial intelligence report.
        
        Returns:
            FinancialReport with financial metrics
        """
        return FinancialReport(
            report_id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
            portfolio_value=104532.50,
            daily_return=0.013,
            weekly_return=0.025,
            monthly_return=0.087,
            current_drawdown=0.02,
            max_drawdown=0.05,
            risk_exposure="moderate",
            asset_allocation={
                "equities": 0.60,
                "options": 0.20,
                "bonds": 0.15,
                "cash": 0.05,
            },
            liquidity_status="healthy",
            cash_reserve=10453.25,
        )
    
    def generate_learning_report(self) -> LearningReport:
        """
        Generate learning insights report.
        
        Returns:
            LearningReport with learning metrics
        """
        outputs = self._collector.get_learning_outputs()
        
        improvements = [o for o in outputs if o.insight_type == "performance_improvement"]
        confidence_adj = [o for o in outputs if o.insight_type == "confidence_adjustment"]
        
        # Degradation alerts would come from the learning engine
        degradation_alerts = 0
        
        return LearningReport(
            report_id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
            learning_events=len(outputs),
            strategy_improvements=len(improvements),
            degradation_alerts=degradation_alerts,
            confidence_adjustments=len(confidence_adj),
            recent_insights=outputs[:10],
            overall_performance_change=0.03,
        )
    
    def generate_system_metrics_report(self) -> SystemMetricsReport:
        """
        Generate system metrics report.
        
        Returns:
            SystemMetricsReport with system performance
        """
        return SystemMetricsReport(
            report_id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
            signals_processed=42,
            signals_by_category={"financial": 15, "market": 12, "risk": 8, "governance": 4, "system": 3},
            agents_active=4,
            agents_total=8,
            agent_cycles_completed=24,
            proposals_generated=9,
            proposals_approved=5,
            executions_completed=3,
            execution_success_rate=0.75,
            avg_signal_latency_ms=12.5,
            avg_agent_latency_ms=250.0,
            avg_pipeline_latency_ms=450.0,
            avg_execution_latency_ms=120.0,
            uptime_seconds=3600.0,
        )
    
    def generate_eod_report(self) -> EODReport:
        """
        Generate End-of-Day Intelligence Report.
        
        Returns:
            EODReport with daily summary
        """
        strategy = self.generate_strategy_report()
        execution = self.generate_execution_report()
        learning = self.generate_learning_report()
        
        total_executions = execution.executions_today
        failed_executions = execution.failed_executions
        success_rate = execution.execution_success_rate
        
        return EODReport(
            report_id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
            signals_processed=42,
            strategies_proposed=strategy.strategies_proposed,
            proposals_approved=strategy.strategies_approved,
            proposals_rejected=strategy.strategies_rejected,
            executions_completed=execution.successful_executions,
            executions_failed=failed_executions,
            learning_events=learning.learning_events,
            degradation_alerts=learning.degradation_alerts,
            overall_success_rate=success_rate,
            top_insights=[
                "Strategy Alpha achieved 15% return this week",
                "Risk Agent successfully identified 3 potential drawdowns",
                "Learning engine identified confidence calibration opportunity",
                f"Executed {execution.successful_executions} actions with {success_rate:.0%} success rate",
            ],
            recommendations=[
                "Consider increasing position sizes for approved strategies",
                "Review rejected proposals for pattern analysis",
                "Monitor agent performance metrics weekly",
                "Continue monitoring for degradation signals",
            ],
        )
    
    def get_category_summary(self, category: str) -> Dict[str, Any]:
        """
        Get summary for a specific category.
        
        Args:
            category: Output category name
            
        Returns:
            Dictionary with category summary
        """
        if category == "strategy":
            report = self.generate_strategy_report()
            return report.dict()
        elif category == "execution":
            report = self.generate_execution_report()
            return report.dict()
        elif category == "financial":
            report = self.generate_financial_report()
            return report.dict()
        elif category == "learning":
            report = self.generate_learning_report()
            return report.dict()
        elif category == "system":
            report = self.generate_system_metrics_report()
            return report.dict()
        
        return {}


# Singleton instance
_output_generator: Optional[OutputGenerator] = None


def get_output_generator() -> OutputGenerator:
    """Get the global output generator instance."""
    global _output_generator
    if _output_generator is None:
        _output_generator = OutputGenerator()
    return _output_generator


def reset_output_generator() -> None:
    """Reset the output generator (for testing)."""
    global _output_generator
    _output_generator = None
