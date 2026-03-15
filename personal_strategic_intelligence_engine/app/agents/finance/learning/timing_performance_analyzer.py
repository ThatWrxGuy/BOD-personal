"""Timing Performance Analyzer.

Analyzes outcomes based on execution timing decisions.
"""

from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict

from app.agents.finance.learning.learning_models import (
    SignalOutcomeRecord,
    SignalOutcome,
    TimingDecision,
    TimingPerformance,
    TimingPerformanceReport,
)


class TimingPerformanceAnalyzer:
    """Analyzes performance by timing decisions."""
    
    def __init__(self):
        self.timing_decisions = [
            TimingDecision.ENTER_NOW,
            TimingDecision.WAIT_FOR_PULLBACK,
            TimingDecision.WAIT_FOR_CONFIRMATION,
            TimingDecision.AVOID_ENTRY,
            TimingDecision.DEFER_SIGNAL,
        ]
    
    def analyze(
        self,
        records: List[SignalOutcomeRecord],
    ) -> TimingPerformanceReport:
        """Analyze timing decision performance."""
        
        if not records:
            return self._empty_report()
        
        resolved = [r for r in records if r.outcome != SignalOutcome.PENDING]
        
        if not resolved:
            return self._empty_report()
        
        # Analyze each timing decision
        timing_performances = []
        
        for decision in self.timing_decisions:
            decision_records = [
                r for r in resolved
                if r.timing_decision == decision
            ]
            
            if not decision_records:
                continue
            
            perf = self._calculate_performance(decision_records)
            timing_performances.append(perf)
        
        # Find specific performance categories
        breakout = self._find_decision_performance(resolved, "enter_now")
        pullback = self._find_decision_performance(resolved, "wait_for_pullback")
        confirmation = self._find_decision_performance(resolved, "wait_for_confirmation")
        avoidance = self._find_decision_performance(resolved, "avoid_entry")
        
        # Generate recommendations
        recommendations = self._generate_recommendations(timing_performances)
        
        return TimingPerformanceReport(
            timestamp=datetime.now(),
            timing_decisions=timing_performances,
            breakout_entry_performance=breakout,
            pullback_entry_performance=pullback,
            confirmation_performance=confirmation,
            avoidance_performance=avoidance,
            timing_recommendations=recommendations,
        )
    
    def _calculate_performance(
        self,
        records: List[SignalOutcomeRecord],
    ) -> TimingPerformance:
        """Calculate performance metrics for timing decision."""
        
        wins = [r for r in records if r.outcome == SignalOutcome.WIN]
        losses = [r for r in records if r.outcome == SignalOutcome.LOSS]
        
        win_rate = len(wins) / len(records) * 100 if records else 0
        
        pnls = [r.profit_loss for r in records if r.profit_loss is not None]
        avg_pnl = sum(pnls) / len(pnls) if pnls else 0
        
        # Expectancy = win_rate * avg_win - loss_rate * avg_loss
        loss_rate = len(losses) / len(records) if records else 0
        win_pnls = [r.profit_loss for r in wins if r.profit_loss and r.profit_loss > 0]
        loss_pnls = [r.profit_loss for r in losses if r.profit_loss and r.profit_loss < 0]
        
        avg_win = sum(win_pnls) / len(win_pnls) if win_pnls else 0
        avg_loss = abs(sum(loss_pnls) / len(loss_pnls)) if loss_pnls else 0
        
        expectancy = (win_rate / 100 * avg_win) - (loss_rate * avg_loss)
        
        return TimingPerformance(
            timing_decision=records[0].timing_decision,
            signal_count=len(records),
            win_count=len(wins),
            win_rate=win_rate,
            avg_profit_loss=avg_pnl,
            expectancy=expectancy,
        )
    
    def _find_decision_performance(
        self,
        records: List[SignalOutcomeRecord],
        decision_value: str,
    ) -> Optional[TimingPerformance]:
        """Find performance for a specific decision type."""
        
        decision_records = [
            r for r in records
            if r.timing_decision.value == decision_value
        ]
        
        if not decision_records:
            return None
        
        return self._calculate_performance(decision_records)
    
    def _generate_recommendations(
        self,
        performances: List[TimingPerformance],
    ) -> Dict[str, str]:
        """Generate timing recommendations."""
        
        if not performances:
            return {"status": "insufficient_data"}
        
        recommendations = {}
        
        # Find best and worst
        best = max(performances, key=lambda p: p.expectancy)
        worst = min(performances, key=lambda p: p.expectancy)
        
        if best.expectancy > 0:
            recommendations[f"best_timing"] = (
                f"{best.timing_decision.value} has highest expectancy: {best.expectancy:.2f}"
            )
        
        if worst.expectancy < -10:
            recommendations[f"worst_timing"] = (
                f"{worst.timing_decision.value} has poor expectancy: {worst.expectancy:.2f}"
            )
        
        # Analyze enter_now vs wait_for_pullback
        enter_now = next((p for p in performances if p.timing_decision == TimingDecision.ENTER_NOW), None)
        wait_pullback = next((p for p in performances if p.timing_decision == TimingDecision.WAIT_FOR_PULLBACK), None)
        
        if enter_now and wait_pullback:
            if wait_pullback.expectancy > enter_now.expectancy:
                recommendations["pullback_vs_immediate"] = (
                    "Waiting for pullback outperforms immediate entry by "
                    f"{wait_pullback.expectancy - enter_now.expectancy:.2f}"
                )
            elif enter_now.expectancy > wait_pullback.expectancy:
                recommendations["immediate_vs_pullback"] = (
                    "Immediate entry outperforms waiting for pullback by "
                    f"{enter_now.expectancy - wait_pullback.expectancy:.2f}"
                )
        
        return recommendations
    
    def _empty_report(self) -> TimingPerformanceReport:
        """Return empty report."""
        return TimingPerformanceReport(
            timestamp=datetime.now(),
            timing_decisions=[],
            breakout_entry_performance=None,
            pullback_entry_performance=None,
            confirmation_performance=None,
            avoidance_performance=None,
            timing_recommendations={"status": "no_data"},
        )


def create_analyzer() -> TimingPerformanceAnalyzer:
    """Create a new timing performance analyzer."""
    return TimingPerformanceAnalyzer()
