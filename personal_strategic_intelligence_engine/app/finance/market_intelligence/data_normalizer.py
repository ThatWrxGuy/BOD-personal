"""Data Normalizer for Multi-Asset Market Data - BB-FIN-014"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

from app.finance.market_intelligence.market_intelligence_models import (
    AssetSignal,
    CrossAssetSnapshot,
    TrendDirection,
)

logger = logging.getLogger(__name__)


# Standard instrument universe
EQUITY_INDICES = {
    "SPY": {"name": "S&P 500 ETF", "asset_class": "equity_index"},
    "QQQ": {"name": "NASDAQ 100 ETF", "asset_class": "equity_index"},
    "IWM": {"name": "Russell 2000 ETF", "asset_class": "equity_index"},
    "DIA": {"name": "Dow Jones ETF", "asset_class": "equity_index"},
}

SECTOR_ETFS = {
    "XLF": {"name": "Financial Sector", "asset_class": "sector"},
    "XLK": {"name": "Technology Sector", "asset_class": "sector"},
    "XLE": {"name": "Energy Sector", "asset_class": "sector"},
    "XLV": {"name": "Healthcare Sector", "asset_class": "sector"},
    "XLI": {"name": "Industrials Sector", "asset_class": "sector"},
    "XLP": {"name": "Consumer Staples Sector", "asset_class": "sector"},
    "XLY": {"name": "Consumer Discretionary Sector", "asset_class": "sector"},
    "XLU": {"name": "Utilities Sector", "asset_class": "sector"},
}

BOND_ETFS = {
    "TLT": {"name": "20+ Year Treasury Bond ETF", "asset_class": "bond"},
    "IEF": {"name": "7-10 Year Treasury Bond ETF", "asset_class": "bond"},
    "SHY": {"name": "1-3 Year Treasury Bond ETF", "asset_class": "bond"},
    "HYG": {"name": "High Yield Corporate Bond ETF", "asset_class": "credit"},
    "LQD": {"name": "Investment Grade Corporate Bond ETF", "asset_class": "credit"},
}

COMMODITY_ETFS = {
    "GLD": {"name": "Gold Trust", "asset_class": "commodity"},
    "USO": {"name": "Oil Fund", "asset_class": "commodity"},
    "DBC": {"name": "Commodity Index", "asset_class": "commodity"},
}

FX_PROXIES = {
    "UUP": {"name": "US Dollar Index ETF", "asset_class": "fx"},
    "DXY": {"name": "US Dollar Index", "asset_class": "fx"},
}

CRYPTO_PROXIES = {
    "BTC": {"name": "Bitcoin", "asset_class": "crypto"},
    "ETH": {"name": "Ethereum", "asset_class": "crypto"},
}

VOLATILITY_INDICES = {
    "VIX": {"name": "CBOE Volatility Index", "asset_class": "volatility"},
}


class DataNormalizer:
    """Normalizes raw market data across asset classes."""

    def __init__(self):
        self.instrument_universe = self._build_universe()
        self._price_cache: Dict[str, float] = {}
        self._change_cache: Dict[str, float] = {}

    def _build_universe(self) -> Dict[str, Dict[str, str]]:
        """Build the complete instrument universe."""
        universe = {}
        universe.update(EQUITY_INDICES)
        universe.update(SECTOR_ETFS)
        universe.update(BOND_ETFS)
        universe.update(COMMODITY_ETFS)
        universe.update(FX_PROXIES)
        universe.update(CRYPTO_PROXIES)
        universe.update(VOLATILITY_INDICES)
        return universe

    def get_instrument_info(self, symbol: str) -> Optional[Dict[str, str]]:
        """Get instrument metadata."""
        return self.instrument_universe.get(symbol.upper())

    def normalize_price_data(
        self,
        symbol: str,
        price: float,
        previous_close: Optional[float] = None,
        volume: Optional[float] = None,
    ) -> AssetSignal:
        """Normalize price data into an AssetSignal."""
        symbol = symbol.upper()
        info = self.get_instrument_info(symbol)
        
        if not info:
            logger.warning(f"Unknown symbol: {symbol}, using defaults")
            info = {"name": symbol, "asset_class": "unknown"}

        # Calculate change percentage
        change_pct = None
        if previous_close and previous_close > 0:
            change_pct = ((price - previous_close) / previous_close) * 100

        return AssetSignal(
            symbol=symbol,
            name=info.get("name", symbol),
            asset_class=info.get("asset_class", "unknown"),
            price=price,
            change_pct=change_pct,
            volume=volume,
        )

    def normalize_market_data(
        self,
        equity_prices: Dict[str, float],
        sector_prices: Dict[str, float],
        bond_prices: Dict[str, float],
        commodity_prices: Dict[str, float],
        fx_prices: Dict[str, float],
        crypto_prices: Dict[str, float],
        vix_level: Optional[float] = None,
        yields: Optional[Dict[str, float]] = None,
        credit_spreads: Optional[Dict[str, float]] = None,
    ) -> CrossAssetSnapshot:
        """Normalize all market data into a CrossAssetSnapshot."""
        
        # Build equity signals
        equities = []
        for symbol, price in equity_prices.items():
            signal = self.normalize_price_data(symbol, price)
            equities.append(signal)
            self._price_cache[symbol] = price

        # Build sector signals
        sectors = []
        for symbol, price in sector_prices.items():
            signal = self.normalize_price_data(symbol, price)
            sectors.append(signal)

        # Build bond signals
        bonds = []
        for symbol, price in bond_prices.items():
            signal = self.normalize_price_data(symbol, price)
            bonds.append(signal)

        # Build commodity signals
        commodities = []
        for symbol, price in commodity_prices.items():
            signal = self.normalize_price_data(symbol, price)
            commodities.append(signal)

        # Build FX signal (use first available)
        dollar = None
        if fx_prices:
            first_fx = list(fx_prices.items())[0]
            dollar = self.normalize_price_data(first_fx[0], first_fx[1])

        # Build crypto signals
        crypto = []
        for symbol, price in crypto_prices.items():
            signal = self.normalize_price_data(symbol, price)
            crypto.append(signal)

        return CrossAssetSnapshot(
            timestamp=datetime.utcnow(),
            equities=equities,
            sectors=sectors,
            bonds=bonds,
            yields=yields or {},
            vix=vix_level,
            commodities=commodities,
            dollar=dollar,
            crypto=crypto,
            credit_spreads=credit_spreads or {},
        )

    def calculate_relative_strength(
        self,
        symbol: str,
        benchmark: str = "SPY",
        lookback_days: int = 20,
    ) -> Optional[float]:
        """
        Calculate relative strength of symbol vs benchmark.
        Returns value > 0 if outperformance, < 0 if underperformance.
        """
        # This would need historical data - placeholder for now
        # In production, would query price history
        return None

    def detect_missing_data(self, snapshot: CrossAssetSnapshot) -> List[str]:
        """Identify any missing or stale data in the snapshot."""
        missing = []
        
        if not snapshot.equities:
            missing.append("equities")
        if not snapshot.sectors:
            missing.append("sectors")
        if not snapshot.bonds:
            missing.append("bonds")
        if snapshot.vix is None:
            missing.append("vix")
            
        return missing

    def standardize_score(self, value: float, min_val: float, max_val: float) -> float:
        """Standardize a raw value to -1 to 1 range."""
        if max_val == min_val:
            return 0.0
        normalized = (value - min_val) / (max_val - min_val)
        return (normalized * 2) - 1  # Map to -1 to 1

    def get_universe_summary(self) -> Dict[str, List[str]]:
        """Get summary of available instrument universe."""
        return {
            "equities": list(EQUITY_INDICES.keys()),
            "sectors": list(SECTOR_ETFS.keys()),
            "bonds": list(BOND_ETFS.keys()),
            "commodities": list(COMMODITY_ETFS.keys()),
            "fx": list(FX_PROXIES.keys()),
            "crypto": list(CRYPTO_PROXIES.keys()),
            "volatility": list(VOLATILITY_INDICES.keys()),
        }


# Singleton instance
_normalizer: Optional[DataNormalizer] = None


def get_normalizer() -> DataNormalizer:
    """Get the singleton DataNormalizer instance."""
    global _normalizer
    if _normalizer is None:
        _normalizer = DataNormalizer()
    return _normalizer
