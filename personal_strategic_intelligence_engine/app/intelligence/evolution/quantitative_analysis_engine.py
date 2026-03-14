"""Quantitative Analysis Engine.

Evaluates tactical signals using quantitative analysis.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random

from app.intelligence.evolution.evolution_models import (
    QuantitativeMetrics,
    RegimeType,
)


class QuantitativeAnalysisEngine:
    """Performs quantitative analysis on tactical signals."""
    
    def __init__(self):
        self.regimes = [
            RegimeType.TREND_UP,
            RegimeType.TREND_DOWN,
            RegimeType.RANGE_CHOP,
            RegimeType.VOLATILITY_EXPAND,
            RegimeType.VOLATILITY_COMPRESS,
        ]
    
    def analyze_signals(
        self,
        signal_records: List[Dict],
    ) -> Dict[str, QuantitativeMetrics]:
        """Analyze signals across different dimensions."""
        
        results = {}
        
        # Overall metrics
        results["overall"] = self._calculate_metrics(signal_records)
        
        # By regime
        for regime in self.regimes:
            regime_signals = self._filter_by_regime(signal_records, regime)
            if regime_signals:
                results[regime.value] = self._calculate_metrics(regime_signals)
        
        return results
    
    def _calculate_metrics(self, signals: List[Dict]) -> QuantitativeMetrics:
        """Calculate quantitative metrics from signals."""
        
        if not signals:
            return QuantitativeMetrics(
                expectancy=0,
                sharpe_ratio=0,
                sortino_ratio=0,
                win_rate=0,
                avg_win=0,
                avg_loss=0,
                max_drawdown=0,
                volatility_adjusted_return=0,
                reliability_index=0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
            )
        
        # Extract P&L
        pnls = [s.get("profit_loss", 0) or 0 for s in signals if s.get("profit_loss")]
        
        if not pnls:
            return QuantitativeMetrics(
                expectancy=0,
                sharpe_ratio=0,
                sortino_ratio=0,
                win_rate=0,
                avg_win=0,
                avg_loss=0,
                max_drawdown=0,
                volatility_adjusted_return=0,
                reliability_index=0,
                total_trades=len(signals),
                winning_trades=0,
                losing_trades=0,
            )
        
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]
        
        win_rate = len(wins) / len(pnls) * 100 if pnls else 0
        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = abs(sum(losses) / len(losses)) if losses else 0
        
        # Expectancy
        expectancy = (win_rate / 100 * avg_win) - ((100 - win_rate) / 100 * avg_loss)
        
        # Sharpe ratio (simplified)
        if pnls:
            mean_return = sum(pnls) / len(pnls)
            std_dev = (sum((p - mean_return) ** 2 for p in pnls) / len(pnls)) ** 0.5
            sharpe_ratio = (mean_return / std_dev * 100) if std_dev > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Sortino ratio (downside deviation)
        if losses:
            downside_std = (sum(p ** 2 for p in losses) / len(losses)) ** 0.5
            sortino_ratio = (mean_return / downside_std * 100) if downside_std > 0 else 0
        else:
            sortino_ratio = 0
        
        # Max drawdown
        max_dd = self._calculate_max_drawdown(pnls)
        
        # Volatility adjusted return
        vol_adj_return = expectancy / (std_dev if std_dev > 0 else 1)
        
        # Reliability index (how consistent wins are)
        reliability = win_rate * (1 - (abs(avg_loss) / (avg_win + abs(avg_loss)) if avg_win + abs(avg_loss) > 0 else 0))
        
        return QuantitativeMetrics(
            expectancy=expectancy,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            max_drawdown=max_dd,
            volatility_adjusted_return=vol_adj_return,
            reliability_index=reliability,
            total_trades=len(signals),
            winning_trades=len(wins),
            losing_trades=len(losses),
        )
    
    def _calculate_max_drawdown(self, pnls: List[float]) -> float:
        """Calculate maximum drawdown."""
        if not pnls:
            return 0
        
        running = 0
        max_dd = 0
        
        for pnl in pnls:
            running += pnl
            if running < 0:
                max_dd = min(max_dd, running)
        
        return abs(max_dd)
    
    def _filter_by_regime(self, signals: List[Dict], regime: RegimeType) -> List[Dict]:
        """Filter signals by regime."""
        return [s for s in signals if s.get("regime") == regime.value]
    
    def analyze_by_day_type(self, signals: List[Dict]) -> Dict[str, QuantitativeMetrics]:
        """Analyze by day type."""
        day_types = {}
        
        for signal in signals:
            dt = signal.get("day_type", "unknown")
            if dt not in day_types:
                day_types[dt] = []
            day_types[dt].append(signal)
        
        return {
            dt: self._calculate_metrics(sigs)
            for dt, sigs in day_types.items()
            if sigs
        }
    
    def analyze_by_vwap_state(self, signals: List[Dict]) -> Dict[str, QuantitativeMetrics]:
        """Analyze by VWAP state."""
        vwap_states = {}
        
        for signal in signals:
            state = signal.get("vwap_state", "unknown")
            if state not in vwap_states:
                vwap_states[state] = []
            vwap_states[state].append(signal)
        
        return {
            state: self._calculate_metrics(sigs)
            for state, sigs in vwap_states.items()
            if sigs
        }
    
    def analyze_by_timing(self, signals: List[Dict]) -> Dict[str, QuantitativeMetrics]:
        """Analyze by timing decision."""
        timing_decisions = {}
        
        for signal in signals:
            timing = signal.get("timing_decision", "unknown")
            if timing not in timing_decisions:
                timing_decisions[timing] = []
            timing_decisions[timing].append(signal)
        
        return {
            timing: self._calculate_metrics(sigs)
            for timing, sigs in timing_decisions.items()
            if sigs
        }


def create_engine() -> QuantitativeAnalysisEngine:
    """Create a new quantitative analysis engine."""
    return QuantitativeAnalysisEngine()
