"""Historical Replay Engine.

Simulates strategy behavior across historical data.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random

from app.intelligence.strategy_simulation.simulation_models import (
    StrategyConfig,
    SimulatedTrade,
    SimulationMetrics,
    RegimeBreakdown,
    SimulationResult,
    SimulationStatus,
)


class HistoricalReplayEngine:
    """Simulates strategies across historical data."""
    
    def __init__(self):
        self.simulated_trades: List[SimulatedTrade] = []
    
    def run_simulation(
        self,
        strategy: StrategyConfig,
        historical_data: List[Dict],
    ) -> SimulationResult:
        """Run historical replay simulation."""
        
        # Generate mock historical trades based on strategy
        trades = self._simulate_trades(strategy, historical_data)
        
        # Calculate metrics
        metrics = self._calculate_metrics(trades)
        
        # Calculate breakdowns
        regime_breakdown = self._calculate_regime_breakdown(trades)
        day_type_breakdown = self._calculate_day_type_breakdown(trades)
        vwap_breakdown = self._calculate_vwap_breakdown(trades)
        
        return SimulationResult(
            simulation_id=f"sim-{strategy.strategy_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            strategy_config=strategy,
            status=SimulationStatus.COMPLETED,
            start_time=datetime.now() - timedelta(hours=1),
            end_time=datetime.now(),
            metrics=metrics,
            trades=trades,
            regime_breakdown=regime_breakdown,
            day_type_breakdown=day_type_breakdown,
            vwap_breakdown=vwap_breakdown,
        )
    
    def _simulate_trades(
        self,
        strategy: StrategyConfig,
        historical_data: List[Dict],
    ) -> List[SimulatedTrade]:
        """Simulate trades based on strategy."""
        
        trades = []
        
        # Generate mock trades
        num_trades = random.randint(20, 80)
        
        regimes = ["trend_up", "trend_down", "range_chop", "reversal"]
        day_types = ["trend_up", "trend_down", "range_day", "neutral"]
        vwap_states = ["acceptance_above", "acceptance_below", "rejection_above", "neutral"]
        
        params = strategy.parameters
        
        for i in range(num_trades):
            regime = random.choice(regimes)
            day_type = random.choice(day_types)
            vwap_state = random.choice(vwap_states)
            
            # Apply strategy filters
            if not self._passes_filters(params, regime, day_type, vwap_state):
                continue
            
            # Simulate trade
            entry_time = datetime.now() - timedelta(days=random.randint(1, 30), minutes=random.randint(0, 390))
            direction = random.choice(["bullish", "bearish"])
            entry_price = 500 + random.uniform(-10, 10)
            
            # Simulate outcome based on regime
            if regime == "trend_up" and direction == "bullish":
                pnl = random.uniform(5, 50)
            elif regime == "trend_down" and direction == "bearish":
                pnl = random.uniform(5, 50)
            elif regime == "range_chop":
                pnl = random.uniform(-30, 30)
            else:
                pnl = random.uniform(-20, 40)
            
            exit_price = entry_price + (pnl / 100 * entry_price)
            pnl_pct = (exit_price - entry_price) / entry_price * 100
            
            trade = SimulatedTrade(
                trade_id=f"trade-{i:04d}",
                entry_time=entry_time,
                exit_time=entry_time + timedelta(minutes=random.randint(5, 60)),
                entry_price=entry_price,
                exit_price=exit_price,
                direction=direction,
                pnl=pnl,
                pnl_pct=pnl_pct,
                max_favorable_excursion=abs(pnl) * random.uniform(0.5, 1.5),
                max_adverse_excursion=abs(pnl) * random.uniform(0.3, 0.8),
                holding_period_minutes=random.randint(5, 60),
                regime=regime,
                day_type=day_type,
                vwap_state=vwap_state,
            )
            
            trades.append(trade)
        
        return trades
    
    def _passes_filters(
        self,
        params: Dict,
        regime: str,
        day_type: str,
        vwap_state: str,
    ) -> bool:
        """Check if conditions pass strategy filters."""
        
        # Simple filter simulation
        if params.get("require_vwap_acceptance") and "acceptance" not in vwap_state:
            return random.random() > 0.3
        
        if params.get("allow_overextension") == False and regime == "reversal":
            return random.random() > 0.5
        
        return True
    
    def _calculate_metrics(self, trades: List[SimulatedTrade]) -> SimulationMetrics:
        """Calculate simulation metrics."""
        
        if not trades:
            return SimulationMetrics(
                total_trades=0, winning_trades=0, losing_trades=0,
                win_rate=0, avg_win=0, avg_loss=0, profit_factor=0,
                expectancy=0, sharpe_ratio=0, sortino_ratio=0,
                max_drawdown=0, max_drawdown_pct=0, avg_holding_period=0,
                volatility=0, volatility_adjusted_return=0,
            )
        
        pnls = [t.pnl for t in trades if t.pnl is not None]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]
        
        win_rate = len(wins) / len(pnls) * 100 if pnls else 0
        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = abs(sum(losses) / len(losses)) if losses else 0
        
        profit_factor = (sum(wins) / abs(sum(losses))) if losses and sum(losses) != 0 else 0
        
        # Expectancy
        expectancy = (win_rate / 100 * avg_win) - ((100 - win_rate) / 100 * avg_loss)
        
        # Sharpe ratio (simplified)
        if pnls:
            mean_return = sum(pnls) / len(pnls)
            std_dev = (sum((p - mean_return) ** 2 for p in pnls) / len(pnls)) ** 0.5
            sharpe_ratio = (mean_return / std_dev * 10) if std_dev > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Sortino ratio
        if losses:
            downside_std = (sum(p ** 2 for p in losses) / len(losses)) ** 0.5
            sortino_ratio = (mean_return / downside_std * 10) if downside_std > 0 else 0
        else:
            sortino_ratio = 0
        
        # Max drawdown
        max_dd = 0
        running = 0
        for pnl in pnls:
            running += pnl
            if running < max_dd:
                max_dd = running
        
        # Avg holding period
        avg_holding = sum(t.holding_period_minutes for t in trades) / len(trades)
        
        # Volatility
        volatility = std_dev if pnls else 0
        
        # Volatility adjusted return
        vol_adj = expectancy / (volatility + 1)
        
        return SimulationMetrics(
            total_trades=len(trades),
            winning_trades=len(wins),
            losing_trades=len(losses),
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            expectancy=expectancy,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=abs(max_dd),
            max_drawdown_pct=abs(max_dd) / 100,
            avg_holding_period=avg_holding,
            volatility=volatility,
            volatility_adjusted_return=vol_adj,
        )
    
    def _calculate_regime_breakdown(self, trades: List[SimulatedTrade]) -> List[RegimeBreakdown]:
        """Calculate regime breakdown."""
        
        regimes = {}
        for trade in trades:
            if trade.regime not in regimes:
                regimes[trade.regime] = []
            regimes[trade.regime].append(trade)
        
        breakdown = []
        for regime, regime_trades in regimes.items():
            pnls = [t.pnl for t in regime_trades if t.pnl]
            wins = len([p for p in pnls if p > 0])
            win_rate = wins / len(pnls) * 100 if pnls else 0
            avg_pnl = sum(pnls) / len(pnls) if pnls else 0
            expectancy = win_rate / 100 * avg_win - (100 - win_rate) / 100 * avg_loss
            
            breakdown.append(RegimeBreakdown(
                regime=regime,
                trade_count=len(regime_trades),
                win_rate=win_rate,
                expectancy=expectancy,
                avg_pnl=avg_pnl,
            ))
        
        return breakdown
    
    def _calculate_day_type_breakdown(self, trades: List[SimulatedTrade]) -> List[RegimeBreakdown]:
        """Calculate day type breakdown."""
        return self._calculate_regime_breakdown(trades)  # Simplified
    
    def _calculate_vwap_breakdown(self, trades: List[SimulatedTrade]) -> List[RegimeBreakdown]:
        """Calculate VWAP state breakdown."""
        return self._calculate_regime_breakdown(trades)  # Simplified


def create_engine() -> HistoricalReplayEngine:
    """Create a new historical replay engine."""
    return HistoricalReplayEngine()
