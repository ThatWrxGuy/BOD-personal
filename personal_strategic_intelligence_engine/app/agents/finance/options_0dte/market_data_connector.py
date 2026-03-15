"""Market Data Connector for SPY 0DTE Options.

Provides pluggable market data ingestion for SPY 1-minute OHLCV and options chain data.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional
import random

from app.agents.finance.options_0dte.options_signal_models import (
    OptionContract,
    OptionsChain,
    MarketDataSnapshot,
    OptionType,
)


class MarketDataProvider(ABC):
    """Abstract base class for market data providers."""
    
    @abstractmethod
    async def get_spy_snapshot(self) -> MarketDataSnapshot:
        """Get current SPY market data snapshot."""
        pass
    
    @abstractmethod
    async def get_spy_1min_bars(self, bars: int = 60) -> list[MarketDataSnapshot]:
        """Get historical 1-minute bars for SPY."""
        pass
    
    @abstractmethod
    async def get_options_chain(self, expiration_date: datetime) -> OptionsChain:
        """Get options chain for SPY for given expiration."""
        pass


class MockMarketDataProvider(MarketDataProvider):
    """Mock market data provider for testing and development."""
    
    def __init__(self, base_price: float = 500.0):
        self.base_price = base_price
        self.current_price = base_price
    
    async def get_spy_snapshot(self) -> MarketDataSnapshot:
        """Get current SPY market data snapshot."""
        # Simulate current price movement
        price_change = random.gauss(0, 0.001)
        self.current_price = self.base_price * (1 + price_change)
        
        change_percent = ((self.current_price - self.base_price) / self.base_price) * 100
        
        return MarketDataSnapshot(
            timestamp=datetime.now(),
            ticker="SPY",
            current_price=self.current_price,
            open_price=self.base_price,
            high_price=self.current_price * 1.002,
            low_price=self.current_price * 0.998,
            volume=random.randint(1000000, 5000000),
            change_percent=change_percent,
            open=self.base_price,
            high=self.current_price * 1.002,
            low=self.current_price * 0.998,
            close=self.current_price,
            rsi_14=random.uniform(30, 70),
            ema_9=self.current_price * random.uniform(0.995, 1.005),
            ema_21=self.current_price * random.uniform(0.99, 1.01),
        )
    
    async def get_spy_1min_bars(self, bars: int = 60) -> list[MarketDataSnapshot]:
        """Get historical 1-minute bars for SPY."""
        snapshots = []
        current = self.base_price
        
        for i in range(bars, 0, -1):
            timestamp = datetime.now() - timedelta(minutes=i)
            
            # Random walk
            change = random.gauss(0, 0.0005)
            current = current * (1 + change)
            
            change_percent = ((current - self.base_price) / self.base_price) * 100
            
            snapshots.append(MarketDataSnapshot(
                timestamp=timestamp,
                ticker="SPY",
                current_price=current,
                open_price=self.base_price,
                high_price=current * 1.001,
                low_price=current * 0.999,
                volume=random.randint(100000, 500000),
                change_percent=change_percent,
                open=current * 0.999,
                high=current * 1.001,
                low=current * 0.999,
                close=current,
                rsi_14=random.uniform(30, 70),
                ema_9=current * random.uniform(0.995, 1.005),
                ema_21=current * random.uniform(0.99, 1.01),
            ))
        
        # Update current price to last bar
        self.current_price = current
        
        return snapshots
    
    async def get_options_chain(self, expiration_date: datetime) -> OptionsChain:
        """Get options chain for SPY for given expiration."""
        # Get current underlying price
        snapshot = await self.get_spy_snapshot()
        underlying = snapshot.current_price
        
        # Generate strikes around current price
        strikes = []
        atm_strike = round(underlying)
        
        # Generate strikes from -10 to +10 around ATM
        for offset in range(-10, 11):
            strikes.append(atm_strike + offset)
        
        calls = []
        puts = []
        
        for strike in strikes:
            # Calculate moneyness
            moneyness = (strike - underlying) / underlying
            
            # Simulate option prices and greeks
            # More OTM = cheaper, lower delta
            if strike >= underlying:
                # Call options
                call_price = self._calculate_option_price(underlying, strike, "call", expiration_date)
                delta = self._calculate_delta(underlying, strike, "call", moneyness)
                gamma = random.uniform(0.01, 0.15)
                theta = random.uniform(-0.5, -0.05)
                vega = random.uniform(0.01, 0.15)
                iv = random.uniform(0.10, 0.25)
            else:
                # Put options
                call_price = 0.0
                delta = 0.0
                gamma = 0.0
                theta = 0.0
                vega = 0.0
                iv = 0.0
            
            if strike <= underlying:
                # Put options
                put_price = self._calculate_option_price(underlying, strike, "put", expiration_date)
                put_delta = self._calculate_delta(underlying, strike, "put", moneyness)
                put_gamma = random.uniform(0.01, 0.15)
                put_theta = random.uniform(-0.5, -0.05)
                put_vega = random.uniform(0.01, 0.15)
                put_iv = random.uniform(0.10, 0.25)
                
                # Calculate bid/ask spread
                spread = put_price * 0.02  # 2% spread
                
                contract = OptionContract(
                    ticker="SPY",
                    expiration_date=expiration_date,
                    strike=strike,
                    option_type=OptionType.PUT,
                    bid=put_price - spread / 2,
                    ask=put_price + spread / 2,
                    last=put_price,
                    volume=random.randint(10, 10000),
                    open_interest=random.randint(100, 50000),
                    delta=put_delta,
                    gamma=put_gamma,
                    vega=put_vega,
                    theta=put_theta,
                    rho=0.0,
                    implied_volatility=put_iv,
                )
                puts.append(contract)
            
            if strike >= underlying and call_price > 0:
                # Calculate bid/ask spread
                spread = call_price * 0.02  # 2% spread
                
                contract = OptionContract(
                    ticker="SPY",
                    expiration_date=expiration_date,
                    strike=strike,
                    option_type=OptionType.CALL,
                    bid=call_price - spread / 2,
                    ask=call_price + spread / 2,
                    last=call_price,
                    volume=random.randint(10, 10000),
                    open_interest=random.randint(100, 50000),
                    delta=delta,
                    gamma=gamma,
                    vega=vega,
                    theta=theta,
                    rho=0.0,
                    implied_volatility=iv,
                )
                calls.append(contract)
        
        return OptionsChain(
            ticker="SPY",
            expiration_date=expiration_date,
            timestamp=datetime.now(),
            calls=calls,
            puts=puts,
            underlying_price=underlying,
        )
    
    def _calculate_option_price(
        self,
        underlying: float,
        strike: float,
        option_type: str,
        expiration: datetime,
    ) -> float:
        """Calculate simulated option price."""
        # Simplified Black-Scholes approximation
        time_to_expiry = max((expiration - datetime.now()).total_seconds() / 86400, 0.001)
        moneyness = (underlying - strike) if option_type == "call" else (strike - underlying)
        
        # Base price from moneyness
        if option_type == "call":
            base_price = max(underlying - strike, 0.1)
        else:
            base_price = max(strike - underlying, 0.1)
        
        # Add time value
        time_value = base_price * (1 - 1 / (1 + time_to_expiry * 10))
        
        return max(base_price + time_value * 0.5, 0.1)
    
    def _calculate_delta(
        self,
        underlying: float,
        strike: float,
        option_type: str,
        moneyness: float,
    ) -> float:
        """Calculate simulated delta."""
        if option_type == "call":
            if moneyness > 0:
                return min(0.95, 0.5 + moneyness * 10)
            else:
                return max(0.05, 0.5 + moneyness * 10)
        else:
            if moneyness < 0:
                return max(-0.95, -0.5 - moneyness * 10)
            else:
                return min(-0.05, -0.5 - moneyness * 10)


class MarketDataConnector:
    """Main connector class for market data ingestion."""
    
    def __init__(self, provider: Optional[MarketDataProvider] = None):
        self.provider = provider or MockMarketDataProvider()
    
    async def get_current_market_data(self) -> MarketDataSnapshot:
        """Get current market snapshot."""
        return await self.provider.get_spy_snapshot()
    
    async def get_historical_bars(self, bars: int = 60) -> list[MarketDataSnapshot]:
        """Get historical 1-minute bars."""
        return await self.provider.get_spy_1min_bars(bars)
    
    async def get_spy_options_chain(
        self,
        expiration_date: Optional[datetime] = None,
    ) -> OptionsChain:
        """Get SPY options chain for expiration."""
        if expiration_date is None:
            # Default to next expiration (today if weekday, next weekday)
            now = datetime.now()
            if now.weekday() < 4:  # Monday-Thursday
                expiration_date = now
            else:  # Friday
                expiration_date = now + timedelta(days=3)
        
        return await self.provider.get_options_chain(expiration_date)
    
    async def get_0dte_expiration_date(self) -> datetime:
        """Get the current 0DTE expiration date."""
        now = datetime.now()
        
        # If it's a weekday and before 4 PM, today is 0DTE
        if now.weekday() < 5 and now.hour < 16:
            return now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        # Otherwise, next trading day
        days_ahead = 1
        if now.weekday() == 4:  # Friday
            days_ahead = 3  # Monday
        elif now.weekday() == 5:  # Saturday
            days_ahead = 2  # Monday
        
        return (now + timedelta(days=days_ahead)).replace(
            hour=16, minute=0, second=0, microsecond=0
        )
    
    async def get_all_0dte_contracts(self) -> OptionsChain:
        """Get all 0DTE contracts for today."""
        expiration = await self.get_0dte_expiration_date()
        return await self.get_spy_options_chain(expiration)
