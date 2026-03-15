"""SPY 0DTE Tactical Agent.

Core tactical agent for analyzing SPY 0DTE options and generating trading signals.
"""

import uuid
from datetime import datetime
from typing import Optional

from app.agents.finance.options_0dte.options_signal_models import (
    OptionsSignal,
    OptionType,
    MarketDataSnapshot,
    OptionsChain,
)
from app.agents.finance.options_0dte.signal_engine import (
    generate_signal_score,
    rank_contracts,
    should_suppress_signal,
)
from app.agents.finance.options_0dte.market_data_connector import (
    MarketDataConnector,
    MarketDataProvider,
)
from app.agents.finance.options_0dte.signal_logger import SignalLogger
from app.agents.finance.options_0dte.paper_trade_simulator import (
    PaperTradeSimulator,
    SimulationConfig,
)


class SPY0DTETacticalAgent:
    """
    SPY 0DTE Tactical Agent.
    
    Monitors SPY price action and options chain to identify short-duration
    opportunities in 0DTE options with high delta acceleration potential.
    """
    
    def __init__(
        self,
        provider: Optional[MarketDataProvider] = None,
        config: Optional[SimulationConfig] = None,
    ):
        """
        Initialize SPY 0DTE Tactical Agent.
        
        Args:
            provider: Market data provider (uses MockProvider if None)
            config: Paper trade simulation config
        """
        self.connector = MarketDataConnector(provider)
        self.logger = SignalLogger()
        self.simulator = PaperTradeSimulator(config or SimulationConfig())
        
        # Historical data for delta velocity calculation
        self.previous_deltas: dict[str, float] = {}
        self.last_analysis_time: Optional[datetime] = None
    
    async def observe_market(self) -> MarketDataSnapshot:
        """
        Observe current market conditions.
        
        Returns:
            MarketDataSnapshot for SPY
        """
        return await self.connector.get_current_market_data()
    
    async def analyze_option_chain(
        self,
        expiration_date: Optional[datetime] = None,
    ) -> OptionsChain:
        """
        Analyze the SPY options chain.
        
        Args:
            expiration_date: Expiration date (defaults to 0DTE)
        
        Returns:
            OptionsChain with all contracts
        """
        return await self.connector.get_spy_options_chain(expiration_date)
    
    async def score_option_contracts(
        self,
        contracts: list,
        market_data: MarketDataSnapshot,
        options_chain: Optional[OptionsChain] = None,
    ) -> list[tuple]:
        """
        Score all option contracts.
        
        Args:
            contracts: List of option contracts
            market_data: Current market snapshot
            options_chain: Full options chain
        
        Returns:
            List of (contract, score, confidence, features) tuples
        """
        scored = []
        
        for contract in contracts:
            # Get previous delta for velocity calculation
            contract_key = f"{contract.strike}_{contract.option_type.value}"
            prev_delta = self.previous_deltas.get(contract_key)
            
            # Generate signal score
            score, confidence, features = generate_signal_score(
                contract=contract,
                market_data=market_data,
                options_chain=options_chain,
                historical_delta=prev_delta,
            )
            
            # Store current delta for next iteration
            self.previous_deltas[contract_key] = contract.delta
            
            scored.append((contract, score, confidence, features))
        
        return scored
    
    async def rank_candidate_strikes(
        self,
        options_chain: OptionsChain,
        market_data: MarketDataSnapshot,
        option_type: Optional[str] = None,
        top_n: int = 10,
    ) -> list:
        """
        Rank candidate strikes by signal score.
        
        Args:
            options_chain: Full options chain
            market_data: Current market data
            option_type: Filter by "call" or "put" (optional)
            top_n: Number of top candidates to return
        
        Returns:
            Ranked list of (contract, score, confidence, features)
        """
        # Get contracts based on option type filter
        if option_type == "call":
            contracts = options_chain.calls
        elif option_type == "put":
            contracts = options_chain.puts
        else:
            contracts = options_chain.calls + options_chain.puts
        
        # Score and rank contracts
        ranked = rank_contracts(contracts, market_data, options_chain, top_n)
        
        return ranked
    
    async def generate_signal(
        self,
        options_chain: Optional[OptionsChain] = None,
        market_data: Optional[MarketDataSnapshot] = None,
        option_type: Optional[str] = None,
    ) -> OptionsSignal:
        """
        Generate a trading signal for SPY 0DTE options.
        
        Args:
            options_chain: Options chain (will fetch if None)
            market_data: Market data (will fetch if None)
            option_type: Filter to "call" or "put" (optional)
        
        Returns:
            OptionsSignal with highest score
        """
        # Fetch data if not provided
        if market_data is None:
            market_data = await self.observe_market()
        
        if options_chain is None:
            options_chain = await self.connector.get_all_0dte_contracts()
        
        # Get ranked candidates
        ranked = await self.rank_candidate_strikes(
            options_chain, market_data, option_type
        )
        
        if not ranked:
            raise ValueError("No viable option contracts found")
        
        # Get top candidate
        contract, signal_score, confidence, features = ranked[0]
        
        # Check if signal should be suppressed
        should_suppress, reason = should_suppress_signal(contract, market_data, features)
        
        if should_suppress:
            # Try next candidate
            for contract, signal_score, confidence, features in ranked[1:]:
                should_suppress, reason = should_suppress_signal(contract, market_data, features)
                if not should_suppress:
                    break
            else:
                # All candidates suppressed
                raise ValueError(f"All candidates suppressed: {reason}")
        
        # Build reasoning summary
        reasoning = self._build_reasoning_summary(
            contract, signal_score, confidence, features
        )
        
        # Create signal
        signal = OptionsSignal(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            ticker=contract.ticker,
            expiration_date=contract.expiration_date,
            strike=contract.strike,
            option_type=contract.option_type,
            delta=contract.delta,
            gamma=contract.gamma,
            vega=contract.vega,
            theta=contract.theta,
            spread=contract.spread,
            volume=contract.volume,
            open_interest=contract.open_interest,
            signal_score=signal_score,
            confidence_score=confidence,
            bid_price=contract.bid,
            ask_price=contract.ask,
            mid_price=contract.mid_price,
            underlying_price=options_chain.underlying_price,
            implied_volatility=contract.implied_volatility,
            reasoning_summary=reasoning,
        )
        
        # Log signal
        self.logger.log_signal(signal)
        self.logger.store_signal_history(signal)
        
        # Update last analysis time
        self.last_analysis_time = datetime.now()
        
        return signal
    
    async def run_scan(
        self,
        option_type: Optional[str] = None,
        top_n: int = 10,
    ) -> dict:
        """
        Run a full scan of SPY 0DTE options.
        
        Args:
            option_type: Filter by "call" or "put" (optional)
            top_n: Number of top signals to return
        
        Returns:
            Dictionary with market data, options chain, and signals
        """
        # Observe market
        market_data = await self.observe_market()
        
        # Analyze options chain
        options_chain = await self.connector.get_all_0dte_contracts()
        
        # Get ranked candidates
        ranked = await self.rank_candidate_strikes(
            options_chain, market_data, option_type, top_n
        )
        
        # Convert to signals
        signals = []
        for contract, score, confidence, features in ranked:
            if features.get("suppressed"):
                continue
            
            reasoning = self._build_reasoning_summary(contract, score, confidence, features)
            
            signal = OptionsSignal(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                ticker=contract.ticker,
                expiration_date=contract.expiration_date,
                strike=contract.strike,
                option_type=contract.option_type,
                delta=contract.delta,
                gamma=contract.gamma,
                vega=contract.vega,
                theta=contract.theta,
                spread=contract.spread,
                volume=contract.volume,
                open_interest=contract.open_interest,
                signal_score=score,
                confidence_score=confidence,
                bid_price=contract.bid,
                ask_price=contract.ask,
                mid_price=contract.mid_price,
                underlying_price=options_chain.underlying_price,
                implied_volatility=contract.implied_volatility,
                reasoning_summary=reasoning,
            )
            signals.append(signal)
        
        # Log all signals
        for signal in signals:
            self.logger.log_signal(signal)
            self.logger.store_signal_history(signal)
        
        # Run paper trade simulations for top signals
        simulated_trades = []
        for signal in signals[:3]:  # Simulate top 3
            price_series = self.simulator.generate_realistic_price_series(
                signal,
                duration_minutes=30,
                volatility_percent=20.0,
                trend_bias=0.0,
            )
            trade = self.simulator.run_simulation(signal, price_series)
            self.logger.log_simulated_trade(trade)
            simulated_trades.append(trade)
        
        self.last_analysis_time = datetime.now()
        
        return {
            "market_data": market_data.to_dict(),
            "options_chain": options_chain.to_dict(),
            "signals": [s.to_dict() for s in signals],
            "simulated_trades": [t.to_dict() for t in simulated_trades],
            "analysis_time": datetime.now().isoformat(),
        }
    
    def _build_reasoning_summary(
        self,
        contract,
        signal_score: float,
        confidence: float,
        features: dict,
    ) -> str:
        """Build a reasoning summary for the signal."""
        reasons = []
        
        # Delta velocity
        if features.get("delta_velocity", 0) > 0.5:
            reasons.append("High delta acceleration potential")
        
        # Gamma exposure
        if features.get("gamma_exposure", 0) > 50:
            reasons.append("Strong gamma exposure")
        
        # Liquidity
        if features.get("liquidity_score", 0) > 60:
            reasons.append("Good liquidity conditions")
        
        # Momentum alignment
        if features.get("momentum_alignment", 0) > 70:
            reasons.append("Aligned with market momentum")
        
        # Time decay warning
        if features.get("time_decay_risk", 0) > 70:
            reasons.append("Caution: High theta decay risk")
        
        # Spread quality
        if features.get("spread_quality", 0) > 70:
            reasons.append("Tight bid-ask spread")
        
        if not reasons:
            reasons.append("Moderate signal characteristics")
        
        return " | ".join(reasons)
    
    def get_signal_history(self, limit: int = 100) -> list[dict]:
        """Get signal history."""
        return self.logger.get_signal_history(limit)
    
    def get_performance_summary(self) -> dict:
        """Get performance summary from simulations."""
        return {
            "logger_metrics": self.logger.get_performance_metrics(),
            "simulator_metrics": self.simulator.get_performance_summary(),
        }
