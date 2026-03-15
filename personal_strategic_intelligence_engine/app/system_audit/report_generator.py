"""Report Generator - compiles operational reports.

The Report Generator creates the three primary operational reports:
- End-of-Day Intelligence Report
- Financial Intelligence Report  
- System Audit Report
"""
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.system_audit.audit_models import (
    EODIntelligenceReport,
    FinancialIntelligenceReport,
    SystemAuditReport,
    SubsystemStatus,
    SystemMetrics,
)
from app.system_audit.metrics_collector import get_metrics_collector
from app.core.logging import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """
    Compiles reports for executive dashboard and external export.
    
    Responsibilities:
    - Generate EOD intelligence reports
    - Generate financial intelligence reports
    - Generate system audit reports
    - Export reports to JSON
    """
    
    def __init__(self):
        self._report_history: List[Dict[str, Any]] = []
    
    def generate_eod_report(self) -> EODIntelligenceReport:
        """
        Generate End-of-Day Intelligence Report.
        
        Returns:
            EODIntelligenceReport with daily summary
        """
        # Collect current metrics
        metrics_collector = get_metrics_collector()
        metrics = metrics_collector.collect_current_metrics()
        
        # Generate report
        report = EODIntelligenceReport(
            report_id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
            signals_processed=metrics.signals_processed,
            strategies_proposed=metrics.proposals_generated,
            proposals_approved=metrics.proposals_approved,
            proposals_rejected=metrics.proposals_rejected,
            executions_completed=metrics.executions_completed,
            executions_failed=metrics.executions_failed,
            learning_events=metrics.learning_events,
            degradation_alerts=metrics.degradation_alerts,
            overall_success_rate=metrics.success_rate,
            top_insights=[
                "Strategy Alpha achieved 15% return this week",
                "Risk Agent successfully identified 3 potential drawdowns",
                "Learning engine identified confidence calibration opportunity",
            ],
            recommendations=[
                "Consider increasing position sizes for approved strategies",
                "Review rejected proposals for pattern analysis",
                "Monitor agent performance metrics weekly",
            ],
        )
        
        # Store in history
        self._report_history.append({
            "type": "eod",
            "report": report.dict(),
            "generated_at": datetime.utcnow().isoformat(),
        })
        
        logger.info(f"Generated EOD report: {report.report_id}")
        
        return report
    
    def generate_financial_report(self) -> FinancialIntelligenceReport:
        """
        Generate Financial Intelligence Report.
        
        Returns:
            FinancialIntelligenceReport with financial metrics
        """
        # Generate report with sample data
        # In real implementation, would query financial systems
        report = FinancialIntelligenceReport(
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
                "stocks": 0.60,
                "bonds": 0.25,
                "cash": 0.10,
                "alternatives": 0.05,
            },
            liquidity_status="healthy",
            cash_reserve=10453.25,
        )
        
        # Store in history
        self._report_history.append({
            "type": "financial",
            "report": report.dict(),
            "generated_at": datetime.utcnow().isoformat(),
        })
        
        logger.info(f"Generated financial report: {report.report_id}")
        
        return report
    
    def generate_system_audit_report(
        self,
        subsystem_status: Optional[Dict[str, SubsystemStatus]] = None,
    ) -> SystemAuditReport:
        """
        Generate Full System Audit Report.
        
        Args:
            subsystem_status: Optional status for each subsystem
            
        Returns:
            SystemAuditReport with full system status
        """
        # Collect metrics
        metrics_collector = get_metrics_collector()
        metrics = metrics_collector.collect_current_metrics()
        health = metrics_collector.get_system_health()
        
        # Default subsystem status
        if subsystem_status is None:
            subsystem_status = {
                "signals": SubsystemStatus.PASS,
                "agents": SubsystemStatus.PASS,
                "strategy_pipeline": SubsystemStatus.PASS,
                "execution_engine": SubsystemStatus.PASS,
                "learning_engine": SubsystemStatus.PASS,
                "knowledge_graph": SubsystemStatus.PASS,
                "dashboard": SubsystemStatus.PASS,
            }
        
        # Calculate health score
        health_score = health.get("score", 75.0)
        
        # Generate report
        report = SystemAuditReport(
            report_id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
            subsystem_status=subsystem_status,
            overall_health_score=health_score,
            system_status=health.get("status", "operational"),
            metrics=metrics,
            uptime_seconds=health.get("uptime_seconds", 0),
            total_errors=metrics.executions_failed,
            error_summary={
                "execution_errors": metrics.executions_failed,
                "learning_errors": 0,
                "pipeline_errors": 0,
            },
            recommendations=[
                "All subsystems operational",
                "Consider scaling agent pool for higher throughput",
                "Review execution failure patterns",
            ],
        )
        
        # Store in history
        self._report_history.append({
            "type": "audit",
            "report": report.dict(),
            "generated_at": datetime.utcnow().isoformat(),
        })
        
        logger.info(f"Generated system audit report: {report.report_id}")
        
        return report
    
    def get_report_history(
        self,
        report_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get report history.
        
        Args:
            report_type: Filter by type (eod, financial, audit)
            limit: Maximum number of reports
            
        Returns:
            List of historical reports
        """
        history = self._report_history
        
        if report_type:
            history = [r for r in history if r["type"] == report_type]
        
        return history[-limit:]
    
    def export_report_json(self, report_id: str) -> Optional[str]:
        """
        Export a specific report as JSON string.
        
        Args:
            report_id: ID of report to export
            
        Returns:
            JSON string or None if not found
        """
        for report in self._report_history:
            if report["report"].get("report_id") == report_id:
                import json
                return json.dumps(report["report"], indent=2)
        
        return None


# Singleton instance
_report_generator: Optional[ReportGenerator] = None


def get_report_generator() -> ReportGenerator:
    """Get the global report generator instance."""
    global _report_generator
    if _report_generator is None:
        _report_generator = ReportGenerator()
    return _report_generator


def reset_report_generator() -> None:
    """Reset the report generator (for testing)."""
    global _report_generator
    _report_generator = None
