"""Regime Performance Analyzer.

Analyzes tactical performance by market regime.
"""

from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict

from app.agents.finance.learning.learning_models import (
    SignalOutcomeRecord,
    SignalOutcome,
    SignalDirection,
    RegimePerformance,
    RegimePerformanceReport,
)


class RegimePerformanceAnalyzer:
    """Analyzes performance by market regime."""
    
    def __init__(self):
        self.regimes = [
            "trend_up",
            "trend_down",
            "range_chop",
            "reversal",
            "unknown",
        ]
        
        self.vwap_states = [
            "acceptance_above",
            "acceptance_below",
            "rejection_above",
            "rejection_below",
            "neutral",
        ]
        
        self.volatility_states = [
            "healthy_expansion",
            "compression",
            "spike",
            "collapse",
            "normal",
        ]
    
    def analyze(
        self,
        records: List[SignalOutcomeRecord],
    ) -> RegimePerformanceReport:
        """Analyze performance by regime."""
        
        if not records:
            return self._empty_report()
        
        resolved = [r for r in records if r.outcome != SignalOutcome.PENDING]
        
        if not resolved:
            return self._empty_report()
        
        # Analyze by day type
        day_type_perf = self._analyze_by_category(resolved, "regime")
        
        # Analyze by VWAP state
        vwap_perf = self._analyze_by_category(resolved, "vwap_state")
        
        # Analyze by volatility
        vol_perf = self._analyze_by_category(resolved, "regime")  # Mock for now
        
        # Find best regimes for calls and puts
        calls = [r for r in resolved if r.direction == SignalDirection.BULLISH]
        puts = [r for r in resolved if r.direction == SignalDirection.BEARISH]
        
        best_calls = self._find_best_regimes(calls)
        best_puts = self._find_best_regimes(puts)
        
        # Find worst environments
        worst = self._find_worst_environments(resolved)
        
        # Generate regime confidence modifiers
        modifiers = self._generate_modifiers(day_type_perf)
        
        return RegimePerformanceReport(
            timestamp=datetime.now(),
            day_type_performance=day_type_perf,
            vwap_state_performance=vwap_perf,
            volatility_performance=vol_perf,
            best_regimes_for_calls=best_calls,
            best_regimes_for_puts=best_puts,
            worst_environments=worst,
            regime_confidence_modifiers=modifiers,
        )
    
    def _analyze_by_category(
        self,
        records: List[SignalOutcomeRecord],
        category: str,
    ) -> List[RegimePerformance]:
        """Analyze performance by a specific category."""
        
        if category == "regime":
            items = [(r.regime.value if hasattr(r.regime, 'value') else r.regime) for r in records]
        elif category == "vwap_state":
            items = [r.vwap_state for r in records]
        else:
            items = ["normal"] * len(records)
        
        grouped = defaultdict(lambda: {"wins": 0, "total": 0, "pnl": 0})
        
        for record, item in zip(records, items):
            grouped[item]["total"] += 1
            if record.outcome == SignalOutcome.WIN:
                grouped[item]["wins"] += 1
            if record.profit_loss:
                grouped[item]["pnl"] += record.profit_loss
        
        performances = []
        for item, stats in grouped.items():
            if stats["total"] == 0:
                continue
            
            win_rate = stats["wins"] / stats["total"] * 100
            avg_pnl = stats["pnl"] / stats["total"]
            expectancy = win_rate / 100 * avg_pnl
            
            # Determine best direction
            item_records = [r for r, i in zip(records, items) if i == item]
            call_wins = len([r for r in item_records if r.direction == SignalDirection.BULLISH and r.outcome == SignalOutcome.WIN])
            put_wins = len([r for r in item_records if r.direction == SignalDirection.BEARISH and r.outcome == SignalOutcome.WIN])
            
            best_dir = None
            if call_wins > put_wins:
                best_dir = SignalDirection.BULLISH
            elif put_wins > call_wins:
                best_dir = SignalDirection.BEARISH
            
            performances.append(RegimePerformance(
                regime=item,
                signal_count=stats["total"],
                win_count=stats["wins"],
                win_rate=win_rate,
                avg_profit_loss=avg_pnl,
                expectancy=expectancy,
                best_for_direction=best_dir,
            ))
        
        return performances
    
    def _find_best_regimes(self, records: List[SignalOutcomeRecord]) -> List[str]:
        """Find best performing regimes for a direction."""
        if not records:
            return []
        
        by_regime = defaultdict(lambda: {"wins": 0, "total": 0})
        
        for record in records:
            regime = record.regime.value if hasattr(record.regime, 'value') else record.regime
            by_regime[regime]["total"] += 1
            if record.outcome == SignalOutcome.WIN:
                by_regime[regime]["wins"] += 1
        
        # Calculate win rates and sort
        regimes = []
        for regime, stats in by_regime.items():
            if stats["total"] >= 3:  # Minimum threshold
                win_rate = stats["wins"] / stats["total"]
                regimes.append((regime, win_rate))
        
        regimes.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in regimes[:3]]
    
    def _find_worst_environments(self, records: List[SignalOutcomeRecord]) -> List[str]:
        """Find worst performing environments."""
        if not records:
            return []
        
        by_regime = defaultdict(lambda: {"wins": 0, "total": 0, "pnl": 0})
        
        for record in records:
            regime = record.regime.value if hasattr(record.regime, 'value') else record.regime
            by_regime[regime]["total"] += 1
            if record.outcome == SignalOutcome.WIN:
                by_regime[regime]["wins"] += 1
            if record.profit_loss:
                by_regime[regime]["pnl"] += record.profit_loss
        
        regimes = []
        for regime, stats in by_regime.items():
            if stats["total"] >= 3:
                win_rate = stats["wins"] / stats["total"]
                expectancy = win_rate * (stats["pnl"] / stats["total"])
                regimes.append((regime, expectancy))
        
        regimes.sort(key=lambda x: x[1])
        return [r[0] for r in regimes[:3]]
    
    def _generate_modifiers(self, performances: List[RegimePerformance]) -> Dict[str, float]:
        """Generate confidence modifiers based on regime."""
        modifiers = {}
        
        # Find average expectancy
        if not performances:
            return modifiers
        
        avg_expectancy = sum(p.expectancy for p in performances) / len(performances)
        
        for perf in performances:
            if perf.expectancy > avg_expectancy * 1.2:
                modifiers[perf.regime] = 10.0  # Boost confidence
            elif perf.expectancy < avg_expectancy * 0.5:
                modifiers[perf.regime] = -10.0  # Reduce confidence
            else:
                modifiers[perf.regime] = 0.0
        
        return modifiers
    
    def _empty_report(self) -> RegimePerformanceReport:
        """Return empty report."""
        return RegimePerformanceReport(
            timestamp=datetime.now(),
            day_type_performance=[],
            vwap_state_performance=[],
            volatility_performance=[],
            best_regimes_for_calls=[],
            best_regimes_for_puts=[],
            worst_environments=[],
            regime_confidence_modifiers={},
        )


def create_analyzer() -> RegimePerformanceAnalyzer:
    """Create a new regime performance analyzer."""
    return RegimePerformanceAnalyzer()
