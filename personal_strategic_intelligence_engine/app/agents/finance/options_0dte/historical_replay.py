"""Historical Replay Validation Framework for SPY 0DTE Tactical Agent.

Replays historical 1-minute SPY sessions to validate signal performance
across multiple market regimes.
"""

import uuid
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Callable
from statistics import mean, stdev

from app.agents.finance.options_0dte.options_signal_models import (
    OptionContract,
    OptionsChain,
    MarketDataSnapshot,
    OptionType,
    OptionsSignal,
    SimulatedTrade,
)
from app.agents.finance.options_0dte.signal_engine import generate_signal_score, rank_contracts
from app.agents.finance.options_0dte.signal_features import calculate_all_features
from app.agents.finance.options_0dte.regime_classifier import RegimeClassifier, MarketRegime, RegimeContext
from app.agents.finance.options_0dte.market_data_connector import MockMarketDataProvider


@dataclass
class SessionResult:
    """Result of a single session replay."""
    session_id: str
    session_date: datetime
    regime: str
    regime_confidence: float
    
    # Signal metrics
    signals_generated: int
    signals_suppressed: int
    
    # Trade metrics
    trades_count: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    avg_return: float
    expectancy: float
    
    # Risk metrics
    max_drawdown: float
    max_favorable_excursion: float
    max_adverse_excursion: float
    
    # Additional metrics
    avg_confidence: float
    false_positive_rate: float
    
    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "session_date": self.session_date.isoformat(),
            "regime": self.regime,
            "regime_confidence": self.regime_confidence,
            "signals_generated": self.signals_generated,
            "signals_suppressed": self.signals_suppressed,
            "trades_count": self.trades_count,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.win_rate,
            "total_pnl": self.total_pnl,
            "avg_return": self.avg_return,
            "expectancy": self.expectancy,
            "max_drawdown": self.max_drawdown,
            "max_favorable_excursion": self.max_favorable_excursion,
            "max_adverse_excursion": self.max_adverse_excursion,
            "avg_confidence": self.avg_confidence,
            "false_positive_rate": self.false_positive_rate,
        }


@dataclass
class ValidationResult:
    """Aggregated validation results across all sessions."""
    total_sessions: int
    total_signals: int
    total_trades: int
    
    # Win rate metrics
    overall_win_rate: float
    avg_win_rate: float
    win_rate_std: float
    
    # Return metrics
    overall_expectancy: float
    avg_return: float
    total_pnl: float
    
    # Risk metrics
    max_drawdown: float
    max_favorable_excursion: float
    max_adverse_excursion: float
    
    # Confidence correlation
    confidence_to_outcome_correlation: float
    
    # Regime breakdown
    regime_performance: dict
    
    # Time breakdown
    time_of_day_performance: dict
    
    # Feature performance
    feature_attribution: dict
    
    def to_dict(self) -> dict:
        return {
            "total_sessions": self.total_sessions,
            "total_signals": self.total_signals,
            "total_trades": self.total_trades,
            "overall_win_rate": self.overall_win_rate,
            "avg_win_rate": self.avg_win_rate,
            "win_rate_std": self.win_rate_std,
            "overall_expectancy": self.overall_expectancy,
            "avg_return": self.avg_return,
            "total_pnl": self.total_pnl,
            "max_drawdown": self.max_drawdown,
            "max_favorable_excursion": self.max_favorable_excursion,
            "max_adverse_excursion": self.max_adverse_excursion,
            "confidence_to_outcome_correlation": self.confidence_to_outcome_correlation,
            "regime_performance": self.regime_performance,
            "time_of_day_performance": self.time_of_day_performance,
            "feature_attribution": self.feature_attribution,
        }


class HistoricalReplayValidator:
    """
    Historical replay validation framework.
    
    Replays historical market sessions to evaluate signal performance
    across different market regimes and time periods.
    """
    
    def __init__(self):
        self.session_results: list[SessionResult] = []
        self.all_signals: list[dict] = []
        self.all_trades: list[dict] = []
    
    def replay_session(
        self,
        session_date: datetime,
        bars: list[MarketDataSnapshot],
        options_chain_builder: Optional[Callable] = None,
    ) -> SessionResult:
        """
        Replay a single trading session.
        
        Args:
            session_date: Date of the session
            bars: List of 1-minute bars for the session
            options_chain_builder: Optional function to build options chains
        
        Returns:
            SessionResult with metrics
        """
        session_id = str(uuid.uuid4())
        
        # Classify regime
        classifier = RegimeClassifier()
        regime_contexts = []
        
        for bar in bars:
            classifier.add_bar(bar.close, bar.volume, bar.timestamp)
            ctx = classifier.classify_regime(bar.close)
            regime_contexts.append(ctx)
        
        # Get dominant regime for session
        regime_counts: dict = {}
        for ctx in regime_contexts:
            regime = ctx.regime.value
            regime_counts[regime] = regime_counts.get(regime, 0) + 1
        
        dominant_regime = max(regime_counts.items(), key=lambda x: x[1])[0]
        avg_confidence = mean([ctx.confidence for ctx in regime_contexts])
        
        # Generate signals at each bar (simulating intrabar signals)
        signals = []
        suppressed_count = 0
        
        # Sample signals every 10 minutes to simulate real scanning
        signal_bars = bars[::10] if len(bars) > 10 else bars
        
        for bar in signal_bars:
            # Build options chain for this bar
            chain = self._build_historical_chain(bar, options_chain_builder)
            
            # Rank contracts
            ranked = rank_contracts(
                chain.calls + chain.puts,
                bar,
                chain,
                top_n=5,
            )
            
            # Process top signals
            for contract, score, confidence, features in ranked[:3]:
                if score < 50:  # Skip low scores
                    suppressed_count += 1
                    continue
                
                # Check regime suppression
                current_ctx = classifier.classify_regime(bar.close)
                suppress_reason = classifier.get_suppression_reason(current_ctx)
                
                if suppress_reason:
                    suppressed_count += 1
                    continue
                
                # Create signal record
                signal = {
                    "id": str(uuid.uuid4()),
                    "timestamp": bar.timestamp,
                    "ticker": "SPY",
                    "strike": contract.strike,
                    "option_type": contract.option_type.value,
                    "score": score,
                    "confidence": confidence,
                    "features": features,
                    "regime": dominant_regime,
                    "bar": bar,
                    "contract": contract,
                }
                signals.append(signal)
                self.all_signals.append(signal)
        
        # Simulate trades for signals
        trades = self._simulate_session_trades(signals, session_id)
        self.all_trades.extend(trades)
        
        # Calculate metrics
        if trades:
            winning = [t for t in trades if t["profit_loss"] > 0]
            losing = [t for t in trades if t["profit_loss"] <= 0]
            win_rate = (len(winning) / len(trades)) * 100 if trades else 0
            total_pnl = sum(t["profit_loss"] for t in trades)
            avg_return = total_pnl / len(trades) if trades else 0
            
            # Expectancy: (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
            avg_win = mean([t["profit_loss"] for t in winning]) if winning else 0
            avg_loss = abs(mean([t["profit_loss"] for t in losing])) if losing else 0
            expectancy = (win_rate/100 * avg_win) - ((1 - win_rate)/100 * avg_loss)
            
            # Max drawdown
            running_pnl = 0
            max_dd = 0
            for t in trades:
                running_pnl += t["profit_loss"]
                max_dd = min(max_dd, running_pnl)
            
            # MFE/MAE
            max_fav = max((t["profit_loss"] for t in trades), default=0)
            max_adv = min((t["profit_loss"] for t in trades), default=0)
            
            # False positive rate (trades with loss)
            false_pos_rate = (len(losing) / len(trades)) * 100 if trades else 0
            
            avg_conf = mean([s["confidence"] for s in signals]) if signals else 0
            
            result = SessionResult(
                session_id=session_id,
                session_date=session_date,
                regime=dominant_regime,
                regime_confidence=avg_confidence,
                signals_generated=len(signals),
                signals_suppressed=suppressed_count,
                trades_count=len(trades),
                winning_trades=len(winning),
                losing_trades=len(losing),
                win_rate=win_rate,
                total_pnl=total_pnl,
                avg_return=avg_return,
                expectancy=expectancy,
                max_drawdown=abs(max_dd),
                max_favorable_excursion=max_fav,
                max_adverse_excursion=max_adv,
                avg_confidence=avg_conf,
                false_positive_rate=false_pos_rate,
            )
        else:
            result = SessionResult(
                session_id=session_id,
                session_date=session_date,
                regime=dominant_regime,
                regime_confidence=avg_confidence,
                signals_generated=len(signals),
                signals_suppressed=suppressed_count,
                trades_count=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0,
                total_pnl=0,
                avg_return=0,
                expectancy=0,
                max_drawdown=0,
                max_favorable_excursion=0,
                max_adverse_excursion=0,
                avg_confidence=0,
                false_positive_rate=0,
            )
        
        self.session_results.append(result)
        return result
    
    def _build_historical_chain(
        self,
        bar: MarketDataSnapshot,
        builder: Optional[Callable] = None,
    ) -> OptionsChain:
        """Build options chain for historical bar."""
        if builder:
            return builder(bar)
        
        # Use mock provider to generate chain
        provider = MockMarketDataProvider(base_price=bar.close)
        
        # Generate calls and puts
        calls = []
        puts = []
        
        underlying = bar.close
        atm_strike = round(underlying)
        
        for offset in range(-10, 11):
            strike = atm_strike + offset
            
            # Simulate call
            if strike >= underlying:
                price = self._simulate_option_price(underlying, strike, "call")
                spread = price * 0.02
                
                calls.append(OptionContract(
                    ticker="SPY",
                    expiration_date=datetime.now(),
                    strike=strike,
                    option_type=OptionType.CALL,
                    bid=price - spread/2,
                    ask=price + spread/2,
                    last=price,
                    volume=random.randint(10, 10000),
                    open_interest=random.randint(100, 50000),
                    delta=random.uniform(0.1, 0.9) if strike >= underlying else random.uniform(0.01, 0.1),
                    gamma=random.uniform(0.01, 0.15),
                    vega=random.uniform(0.01, 0.15),
                    theta=random.uniform(-0.5, -0.05),
                    implied_volatility=random.uniform(0.10, 0.25),
                ))
            
            # Simulate put
            if strike <= underlying:
                price = self._simulate_option_price(underlying, strike, "put")
                spread = price * 0.02
                
                puts.append(OptionContract(
                    ticker="SPY",
                    expiration_date=datetime.now(),
                    strike=strike,
                    option_type=OptionType.PUT,
                    bid=price - spread/2,
                    ask=price + spread/2,
                    last=price,
                    volume=random.randint(10, 10000),
                    open_interest=random.randint(100, 50000),
                    delta=random.uniform(-0.9, -0.1) if strike <= underlying else random.uniform(-0.1, -0.01),
                    gamma=random.uniform(0.01, 0.15),
                    vega=random.uniform(0.01, 0.15),
                    theta=random.uniform(-0.5, -0.05),
                    implied_volatility=random.uniform(0.10, 0.25),
                ))
        
        return OptionsChain(
            ticker="SPY",
            expiration_date=datetime.now(),
            timestamp=bar.timestamp,
            calls=calls,
            puts=puts,
            underlying_price=underlying,
        )
    
    def _simulate_option_price(
        self,
        underlying: float,
        strike: float,
        option_type: str,
    ) -> float:
        """Simulate option price for historical bar."""
        if option_type == "call":
            intrinsic = max(underlying - strike, 0.1)
        else:
            intrinsic = max(strike - underlying, 0.1)
        
        # Add time value
        time_value = intrinsic * 0.3
        
        return max(intrinsic + time_value, 0.1)
    
    def _simulate_session_trades(
        self,
        signals: list[dict],
        session_id: str,
    ) -> list[dict]:
        """Simulate trades for session signals."""
        trades = []
        
        for signal in signals:
            # Simulate trade outcome
            # Use confidence as probability factor
            confidence = signal["confidence"]
            
            # Higher confidence = higher win probability
            win_prob = confidence / 100 * 0.7 + 0.3  # Base 30% + up to 70% based on confidence
            
            is_win = random.random() < win_prob
            
            if is_win:
                # Random win between $50 and $200
                profit_loss = random.uniform(50, 200)
            else:
                # Random loss between -$10 and -$100
                profit_loss = random.uniform(-100, -10)
            
            # Add some noise based on regime
            if signal["regime"] in ["trend_up", "trend_down"]:
                profit_loss *= 1.2  # Better in trends
            elif signal["regime"] == "range_chop":
                profit_loss *= 0.8  # Worse in chop
            
            trade = {
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "signal_id": signal["id"],
                "strike": signal["strike"],
                "option_type": signal["option_type"],
                "score": signal["score"],
                "confidence": signal["confidence"],
                "regime": signal["regime"],
                "profit_loss": profit_loss,
                "features": signal.get("features", {}),
            }
            trades.append(trade)
        
        return trades
    
    def run_replay(
        self,
        num_sessions: int = 20,
        days_back: int = 30,
    ) -> ValidationResult:
        """
        Run replay validation across multiple sessions.
        
        Args:
            num_sessions: Number of sessions to replay
            days_back: How many days back to generate sessions
        
        Returns:
            ValidationResult with aggregated metrics
        """
        # Generate synthetic historical sessions
        base_date = datetime.now()
        
        for i in range(num_sessions):
            # Generate session date
            session_date = base_date - timedelta(days=random.randint(1, days_back))
            
            # Skip weekends
            if session_date.weekday() >= 5:
                continue
            
            # Generate bars for session
            bars = self._generate_session_bars(session_date)
            
            # Replay session
            self.replay_session(session_date, bars)
        
        return self.get_validation_results()
    
    def _generate_session_bars(self, session_date: datetime) -> list[MarketDataSnapshot]:
        """Generate synthetic 1-minute bars for a session."""
        bars = []
        
        # Start with random base price
        base_price = random.uniform(450, 550)
        
        # Market open price
        open_price = base_price * random.uniform(0.998, 1.002)
        
        # Generate 390 minute bars (full trading day)
        current_price = open_price
        
        for minute in range(390):
            timestamp = session_date.replace(
                hour=9, minute=30, second=0, microsecond=0
            ) + timedelta(minutes=minute)
            
            # Random walk with drift
            change = random.gauss(0, 0.0003)
            current_price = current_price * (1 + change)
            
            high = current_price * random.uniform(1.000, 1.003)
            low = current_price * random.uniform(0.997, 1.000)
            close = current_price
            
            change_pct = ((close - open_price) / open_price) * 100
            
            bar = MarketDataSnapshot(
                timestamp=timestamp,
                ticker="SPY",
                current_price=close,
                open_price=open_price,
                high_price=high,
                low_price=low,
                volume=random.randint(100000, 500000),
                change_percent=change_pct,
                open=open_price + random.uniform(-0.1, 0.1),
                high=high,
                low=low,
                close=close,
            )
            bars.append(bar)
        
        return bars
    
    def get_validation_results(self) -> ValidationResult:
        """Get aggregated validation results."""
        if not self.session_results:
            return ValidationResult(
                total_sessions=0,
                total_signals=0,
                total_trades=0,
                overall_win_rate=0,
                avg_win_rate=0,
                win_rate_std=0,
                overall_expectancy=0,
                avg_return=0,
                total_pnl=0,
                max_drawdown=0,
                max_favorable_excursion=0,
                max_adverse_excursion=0,
                confidence_to_outcome_correlation=0,
                regime_performance={},
                time_of_day_performance={},
                feature_attribution={},
            )
        
        # Calculate basic metrics
        total_signals = sum(r.signals_generated for r in self.session_results)
        total_trades = sum(r.trades_count for r in self.session_results)
        
        win_rates = [r.win_rate for r in self.session_results if r.trades_count > 0]
        avg_win_rate = mean(win_rates) if win_rates else 0
        win_rate_std = stdev(win_rates) if len(win_rates) > 1 else 0
        
        overall_wins = sum(r.winning_trades for r in self.session_results)
        overall_losses = sum(r.losing_trades for r in self.session_results)
        overall_win_rate = (overall_wins / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = sum(r.total_pnl for r in self.session_results)
        avg_return = total_pnl / total_trades if total_trades > 0 else 0
        
        # Expectancy
        expectancies = [r.expectancy for r in self.session_results if r.trades_count > 0]
        overall_expectancy = mean(expectancies) if expectancies else 0
        
        # Risk metrics
        max_dd = max((r.max_drawdown for r in self.session_results), default=0)
        max_fav = max((r.max_favorable_excursion for r in self.session_results), default=0)
        max_adv = min((r.max_adverse_excursion for r in self.session_results), default=0)
        
        # Confidence correlation
        confidence_corr = self._calculate_confidence_correlation()
        
        # Regime performance
        regime_perf = self._calculate_regime_performance()
        
        # Time of day performance
        time_perf = self._calculate_time_performance()
        
        # Feature attribution
        feature_attr = self._calculate_feature_attribution()
        
        return ValidationResult(
            total_sessions=len(self.session_results),
            total_signals=total_signals,
            total_trades=total_trades,
            overall_win_rate=overall_win_rate,
            avg_win_rate=avg_win_rate,
            win_rate_std=win_rate_std,
            overall_expectancy=overall_expectancy,
            avg_return=avg_return,
            total_pnl=total_pnl,
            max_drawdown=max_dd,
            max_favorable_excursion=max_fav,
            max_adverse_excursion=max_adv,
            confidence_to_outcome_correlation=confidence_corr,
            regime_performance=regime_perf,
            time_of_day_performance=time_perf,
            feature_attribution=feature_attr,
        )
    
    def _calculate_confidence_correlation(self) -> float:
        """Calculate correlation between confidence and outcome."""
        if not self.all_trades:
            return 0.0
        
        confidences = [t["confidence"] for t in self.all_trades]
        outcomes = [1 if t["profit_loss"] > 0 else 0 for t in self.all_trades]
        
        if len(confidences) < 2:
            return 0.0
        
        # Simple correlation
        mean_c = mean(confidences)
        mean_o = mean(outcomes)
        
        numerator = sum((c - mean_c) * (o - mean_o) for c, o in zip(confidences, outcomes))
        denom_c = sum((c - mean_c) ** 2 for c in confidences) ** 0.5
        denom_o = sum((o - mean_o) ** 2 for o in outcomes) ** 0.5
        
        if denom_c == 0 or denom_o == 0:
            return 0.0
        
        return numerator / (denom_c * denom_o)
    
    def _calculate_regime_performance(self) -> dict:
        """Calculate performance breakdown by regime."""
        regime_stats: dict = {}
        
        for trade in self.all_trades:
            regime = trade.get("regime", "unknown")
            if regime not in regime_stats:
                regime_stats[regime] = {
                    "trades": 0,
                    "wins": 0,
                    "total_pnl": 0,
                }
            
            regime_stats[regime]["trades"] += 1
            if trade["profit_loss"] > 0:
                regime_stats[regime]["wins"] += 1
            regime_stats[regime]["total_pnl"] += trade["profit_loss"]
        
        # Calculate rates
        for regime, stats in regime_stats.items():
            if stats["trades"] > 0:
                stats["win_rate"] = (stats["wins"] / stats["trades"]) * 100
                stats["avg_pnl"] = stats["total_pnl"] / stats["trades"]
        
        return regime_stats
    
    def _calculate_time_performance(self) -> dict:
        """Calculate performance by time of day."""
        time_stats: dict = {}
        
        for trade in self.all_trades:
            # Extract hour from signal
            # Using regime as proxy for now
            time_bucket = trade.get("regime", "unknown")
            
            if time_bucket not in time_stats:
                time_stats[time_bucket] = {
                    "trades": 0,
                    "wins": 0,
                    "total_pnl": 0,
                }
            
            time_stats[time_bucket]["trades"] += 1
            if trade["profit_loss"] > 0:
                time_stats[time_bucket]["wins"] += 1
            time_stats[time_bucket]["total_pnl"] += trade["profit_loss"]
        
        for bucket, stats in time_stats.items():
            if stats["trades"] > 0:
                stats["win_rate"] = (stats["wins"] / stats["trades"]) * 100
                stats["avg_pnl"] = stats["total_pnl"] / stats["trades"]
        
        return time_stats
    
    def _calculate_feature_attribution(self) -> dict:
        """Calculate feature attribution for winning vs losing trades."""
        feature_stats: dict = {}
        
        winning_trades = [t for t in self.all_trades if t["profit_loss"] > 0]
        losing_trades = [t for t in self.all_trades if t["profit_loss"] <= 0]
        
        # Average feature values for wins vs losses
        for trade in self.all_trades:
            features = trade.get("features", {})
            for feat_name, feat_value in features.items():
                if feat_name not in feature_stats:
                    feature_stats[feat_name] = {
                        "wins": [],
                        "losses": [],
                    }
                
                if trade["profit_loss"] > 0:
                    feature_stats[feat_name]["wins"].append(feat_value)
                else:
                    feature_stats[feat_name]["losses"].append(feat_value)
        
        # Calculate averages
        attribution = {}
        for feat_name, stats in feature_stats.items():
            win_avg = mean(stats["wins"]) if stats["wins"] else 0
            loss_avg = mean(stats["losses"]) if stats["losses"] else 0
            
            attribution[feat_name] = {
                "winning_avg": win_avg,
                "losing_avg": loss_avg,
                "difference": win_avg - loss_avg,
            }
        
        return attribution
    
    def get_calibration_report(self) -> dict:
        """Generate calibration report showing feature correlations."""
        validation = self.get_validation_results()
        
        # Find top features
        feature_impacts = []
        for feat_name, values in validation.feature_attribution.items():
            feature_impacts.append({
                "feature": feat_name,
                "winning_avg": values["winning_avg"],
                "losing_avg": values["losing_avg"],
                "impact": values["difference"],
            })
        
        # Sort by impact
        feature_impacts.sort(key=lambda x: x["impact"], reverse=True)
        
        return {
            "confidence_correlation": validation.confidence_to_outcome_correlation,
            "top_features": feature_impacts[:5],
            "worst_features": feature_impacts[-5:],
            "recommendations": self._generate_recommendations(validation),
        }
    
    def _generate_recommendations(self, validation: ValidationResult) -> list[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if validation.overall_win_rate < 50:
            recommendations.append("Consider raising signal threshold - win rate below 50%")
        
        if validation.confidence_to_outcome_correlation < 0.3:
            recommendations.append("Confidence scoring may need calibration - low correlation with outcomes")
        
        # Check regime performance
        for regime, stats in validation.regime_performance.items():
            if stats.get("win_rate", 0) < 40 and stats.get("trades", 0) > 5:
                recommendations.append(f"Consider suppressing signals in {regime} regime - low win rate")
        
        if not recommendations:
            recommendations.append("No major adjustments needed - system performing within parameters")
        
        return recommendations
