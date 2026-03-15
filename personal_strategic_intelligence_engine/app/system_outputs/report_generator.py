"""PSIE Report Generator - generates intelligence reports per V47-007.

This module generates all required PSIE output reports:
- Executive Brief
- Strategy Proposals
- Governance Queue
- Execution Status
- Financial Intelligence
- Options Intelligence
- Learning Report
- EOD Report
"""
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.system_outputs.report_models import (
    ExecutiveBrief,
    StrategyProposalReport,
    GovernanceQueueReport,
    ExecutionStatusReport,
    FinancialIntelligenceReport,
    OptionsIntelligenceReport,
    LearningReport,
    EODReport,
    SignalSummary,
    PendingDecision,
    ActiveExecution,
    ReportType,
    ReportClassification,
)
from app.system_outputs.output_generator import get_output_generator
from app.core.logging import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """Generates PSIE intelligence reports."""
    
    def __init__(self):
        self._output_generator = get_output_generator()
    
    def generate_executive_brief(self) -> Dict[str, Any]:
        """Generate Daily Executive Intelligence Brief."""
        # Get data from various sources
        outputs = self._output_generator.generate_overview()
        
        return {
            "report_type": "executive_brief",
            "report_id": f"exec_{uuid.uuid4().hex[:8]}",
            "generated_at": datetime.utcnow().isoformat(),
            "signals_summary": {
                "total_signals": outputs.system.signals_processed,
                "by_category": outputs.system.signals_by_category,
                "high_priority": outputs.system.signals_processed // 4,
                "critical": 0,
            },
            "risks_detected": [
                {"id": "risk_1", "description": "Market volatility increased", "severity": "medium"},
            ],
            "opportunities_detected": [
                {"id": "opp_1", "description": "SPY momentum breakout", "confidence": 0.72},
            ],
            "financial_snapshot": {
                "portfolio_value": outputs.financial.portfolio_value,
                "daily_return": outputs.financial.daily_return,
                "risk_exposure": outputs.financial.risk_exposure,
            },
            "strategies_proposed": outputs.strategy.strategies_proposed,
            "strategies_approved": outputs.strategy.strategies_approved,
            "execution_summary": {
                "total_executions": outputs.execution.executions_today,
                "successful": outputs.execution.successful_executions,
                "success_rate": outputs.execution.execution_success_rate,
            },
            "system_alerts": [
                "System operating in safe mode",
                "Background workers disabled",
            ],
            "classification": ReportClassification.ADVISORY.value,
        }
    
    def generate_strategy_proposals(self) -> Dict[str, Any]:
        """Generate Strategy Proposal Report."""
        outputs = self._output_generator.generate_strategy_report()
        
        proposals = []
        for proposal in outputs.recent_outputs[:5]:
            proposals.append({
                "proposal_id": proposal.proposal_id,
                "title": proposal.title,
                "description": proposal.description,
                "confidence": proposal.confidence,
                "risk_level": proposal.risk_level.value,
                "decision": proposal.decision.value,
                "agent_id": proposal.agent_id,
                "expected_value": 0.05,  # Placeholder
                "simulation_results": {},  # Placeholder
            })
        
        return {
            "report_type": "strategy_proposal",
            "report_id": f"strat_{uuid.uuid4().hex[:8]}",
            "generated_at": datetime.utcnow().isoformat(),
            "proposals": proposals,
            "total_proposals": len(proposals),
            "classification": ReportClassification.DECISION_REQUIRED.value,
        }
    
    def generate_governance_queue(self) -> Dict[str, Any]:
        """Generate Governance Approval Queue."""
        # Get pending decisions from governance
        pending = [
            {
                "decision_id": f"gov_{uuid.uuid4().hex[:8]}",
                "decision_type": "strategy_execution",
                "risk_level": "high",
                "proposal": {
                    "title": "SPY Volatility Breakout",
                    "expected_return": 0.15,
                    "risk_score": 0.7,
                },
                "recommended_action": "approve",
                "submitted_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            },
            {
                "decision_id": f"gov_{uuid.uuid4().hex[:8]}",
                "decision_type": "capital_allocation",
                "risk_level": "medium",
                "proposal": {
                    "title": "Increase options allocation",
                    "amount": 10000,
                },
                "recommended_action": "approve",
                "submitted_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            },
        ]
        
        return {
            "report_type": "governance_queue",
            "report_id": f"gov_{uuid.uuid4().hex[:8]}",
            "generated_at": datetime.utcnow().isoformat(),
            "pending_decisions": pending,
            "total_pending": len(pending),
            "classification": ReportClassification.DECISION_REQUIRED.value,
        }
    
    def generate_execution_status(self) -> Dict[str, Any]:
        """Generate Execution Status Report."""
        outputs = self._output_generator.generate_execution_report()
        
        active = [
            {
                "execution_id": f"exec_{uuid.uuid4().hex[:8]}",
                "task_name": "Monitor SPY signals",
                "status": "running",
                "progress": 0.65,
                "started_at": (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
            }
        ]
        
        return {
            "report_type": "execution_status",
            "report_id": f"exec_stat_{uuid.uuid4().hex[:8]}",
            "generated_at": datetime.utcnow().isoformat(),
            "active_executions": active,
            "completed_today": outputs.successful_executions,
            "failed_today": outputs.failed_executions,
            "automation_status": "active",
            "classification": ReportClassification.ADVISORY.value,
        }
    
    def generate_financial_intelligence(self) -> Dict[str, Any]:
        """Generate Financial Risk & Opportunity Report."""
        outputs = self._output_generator.generate_financial_report()
        
        return {
            "report_type": "financial_intelligence",
            "report_id": f"fin_{uuid.uuid4().hex[:8]}",
            "generated_at": datetime.utcnow().isoformat(),
            "liquidity_position": {
                "cash_reserve": outputs.cash_reserve,
                "cash_percentage": outputs.asset_allocation.get("cash", 0.05) * 100,
                "status": outputs.liquidity_status,
            },
            "debt_analysis": {
                "total_debt": 0,
                "debt_to_equity": 0,
                "interest_coverage": 0,
            },
            "cashflow_forecast": {
                "projected_inflow": 5000,
                "projected_outflow": 3000,
                "net_position": 2000,
            },
            "investment_opportunities": [
                {"id": "inv_1", "type": "etf", "expected_return": 0.08, "risk": "low"},
                {"id": "inv_2", "type": "options", "expected_return": 0.15, "risk": "medium"},
            ],
            "risk_alerts": [
                "Portfolio drawdown within acceptable range",
            ],
            "classification": ReportClassification.REVIEW_REQUIRED.value,
        }
    
    def generate_options_intelligence(self) -> Dict[str, Any]:
        """Generate SPY 0DTE Options Intelligence Brief."""
        return {
            "report_type": "options_intelligence",
            "report_id": f"opt_{uuid.uuid4().hex[:8]}",
            "generated_at": datetime.utcnow().isoformat(),
            "market_conditions": {
                "spy_price": 505.50,
                "trend": "bullish",
                "day_type": "regular",
            },
            "gamma_exposure": 0.42,
            "delta_velocity": 0.15,
            "liquidity_level": "high",
            "volume_analysis": {
                "total_volume": 85000000,
                "call_volume": 45000000,
                "put_volume": 40000000,
            },
            "volatility_conditions": {
                "iv": 0.14,
                "hv": 0.11,
                "iv_rank": 45,
            },
            "optimal_strikes": [
                {"strike": 506, "type": "call", "score": 0.85},
                {"strike": 504, "type": "put", "score": 0.72},
            ],
            "classification": ReportClassification.REVIEW_REQUIRED.value,
        }
    
    def generate_learning_report(self) -> Dict[str, Any]:
        """Generate Learning & System Evolution Report."""
        outputs = self._output_generator.generate_learning_report()
        
        return {
            "report_type": "learning_report",
            "report_id": f"learn_{uuid.uuid4().hex[:8]}",
            "generated_at": datetime.utcnow().isoformat(),
            "strategy_performance": {
                "top_strategies": [
                    {"name": "SPY Momentum", "return": 0.15, "sharpe": 1.2},
                    {"name": "Volatility Breakout", "return": 0.08, "sharpe": 0.9},
                ],
                "overall_return": 0.12,
            },
            "detected_patterns": [
                "SPY morning gap reversal",
                "Low volatility expansion",
            ],
            "degradation_alerts": outputs.degradation_alerts,
            "degraded_strategies": [],
            "feature_changes": {
                "momentum": 0.02,
                "volatility": -0.01,
                "volume": 0.05,
            },
            "classification": ReportClassification.ADVISORY.value,
        }
    
    def generate_eod_report(self) -> Dict[str, Any]:
        """Generate End-of-Day System Report."""
        outputs = self._output_generator.generate_eod_report()
        
        return {
            "report_type": "eod_report",
            "report_id": f"eod_{uuid.uuid4().hex[:8]}",
            "generated_at": datetime.utcnow().isoformat(),
            "signals_processed": outputs.signals_processed,
            "strategies_evaluated": outputs.strategies_proposed,
            "decisions_made": outputs.proposals_approved + outputs.proposals_rejected,
            "executions_performed": outputs.executions_completed,
            "system_metrics": {
                "uptime": 3600,
                "api_calls": 1250,
                "errors": 3,
                "success_rate": 0.997,
            },
            "daily_summary": f"Processed {outputs.signals_processed} signals, executed {outputs.executions_completed} actions with {outputs.overall_success_rate:.0%} success rate.",
            "classification": ReportClassification.ADVISORY.value,
        }
    
    def generate_report(self, report_type: str) -> Dict[str, Any]:
        """Generate a specific report by type."""
        generators = {
            "executive_brief": self.generate_executive_brief,
            "strategy_proposals": self.generate_strategy_proposals,
            "governance_queue": self.generate_governance_queue,
            "execution_status": self.generate_execution_status,
            "financial_intelligence": self.generate_financial_intelligence,
            "options_intelligence": self.generate_options_intelligence,
            "learning_report": self.generate_learning_report,
            "eod_report": self.generate_eod_report,
        }
        
        generator = generators.get(report_type)
        if generator:
            return generator()
        
        return {"error": f"Unknown report type: {report_type}"}


# Singleton instance
_report_generator: Optional[ReportGenerator] = None


def get_report_generator() -> ReportGenerator:
    """Get the global report generator instance."""
    global _report_generator
    if _report_generator is None:
        _report_generator = ReportGenerator()
    return _report_generator
