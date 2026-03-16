"""Universe Manager.

This module defines and manages the security universes for selection.
"""
from typing import Optional
from datetime import datetime

from app.finance.security_selection.selection_models import (
    SecurityCategory,
    UniverseDefinition,
)


class UniverseManager:
    """Manages security universes for analysis."""
    
    # Default universes
    DEFAULT_CORE_ETFS = ["SPY", "QQQ", "DIA", "IWM", "VOO", "VTI"]
    
    DEFAULT_QUALITY_STOCKS = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
        "JPM", "V", "UNH", "HD", "PG", "MA", "DIS", "PYPL",
    ]
    
    DEFAULT_DIVIDEND = ["SCHD", "VYM", "VNQ", "VIG", "DVY", "HDV"]
    
    DEFAULT_TACTICAL = ["SPY", "QQQ", "IWM", "TLT", "GLD", "SLV", "UNG"]
    
    def __init__(self):
        """Initialize universe manager."""
        self._universes: dict[str, UniverseDefinition] = {}
        self._initialize_default_universes()
        
    def _initialize_default_universes(self):
        """Initialize default universes."""
        # Core ETFs
        self._universes["core_etfs"] = UniverseDefinition(
            name="Core ETFs",
            category=SecurityCategory.CORE,
            symbols=self.DEFAULT_CORE_ETFS,
            description="Core equity ETFs for portfolio foundation",
        )
        
        # Quality stocks
        self._universes["quality_stocks"] = UniverseDefinition(
            name="Quality Stocks",
            category=SecurityCategory.INVESTMENT,
            symbols=self.DEFAULT_QUALITY_STOCKS,
            description="High quality large-cap stocks",
        )
        
        # Dividend
        self._universes["dividend"] = UniverseDefinition(
            name="Dividend",
            category=SecurityCategory.INCOME,
            symbols=self.DEFAULT_DIVIDEND,
            description="Dividend-focused ETFs and stocks",
        )
        
        # Tactical
        self._universes["tactical"] = UniverseDefinition(
            name="Tactical",
            category=SecurityCategory.TACTICAL,
            symbols=self.DEFAULT_TACTICAL,
            description="Tactical trading candidates",
        )
        
    def get_universe(self, name: str) -> Optional[UniverseDefinition]:
        """Get a specific universe."""
        return self._universes.get(name)
    
    def get_all_universes(self) -> list[UniverseDefinition]:
        """Get all universes."""
        return list(self._universes.values())
    
    def get_universe_by_category(self, category: SecurityCategory) -> list[UniverseDefinition]:
        """Get universes by category."""
        return [
            u for u in self._universes.values()
            if u.category == category
        ]
    
    def get_core_universe(self) -> UniverseDefinition:
        """Get core ETF universe."""
        return self._universes["core_etfs"]
    
    def get_tactical_universe(self) -> UniverseDefinition:
        """Get tactical universe."""
        return self._universes["tactical"]
    
    def get_investment_universe(self) -> UniverseDefinition:
        """Get investment universe."""
        return self._universes.get("quality_stocks")
    
    def get_income_universe(self) -> UniverseDefinition:
        """Get income universe."""
        return self._universes.get("dividend")
    
    def get_combined_universe(self, categories: Optional[list[SecurityCategory]] = None) -> list[str]:
        """Get combined universe from multiple categories."""
        if categories is None:
            # Return all unique symbols
            symbols = set()
            for universe in self._universes.values():
                symbols.update(universe.symbols)
            return sorted(list(symbols))
        
        symbols = set()
        for category in categories:
            for universe in self.get_universe_by_category(category):
                symbols.update(universe.symbols)
        
        return sorted(list(symbols))
    
    def add_universe(self, universe: UniverseDefinition):
        """Add a new universe."""
        self._universes[universe.name.lower().replace(" ", "_")] = universe
    
    def add_to_universe(self, universe_name: str, symbols: list[str]):
        """Add symbols to an existing universe."""
        universe = self._universes.get(universe_name)
        if universe:
            for symbol in symbols:
                if symbol not in universe.symbols:
                    universe.symbols.append(symbol)
            universe.updated_at = datetime.now()
    
    def remove_from_universe(self, universe_name: str, symbols: list[str]):
        """Remove symbols from a universe."""
        universe = self._universes.get(universe_name)
        if universe:
            universe.symbols = [s for s in universe.symbols if s not in symbols]
            universe.updated_at = datetime.now()
    
    def create_custom_universe(
        self,
        name: str,
        category: SecurityCategory,
        symbols: list[str],
        description: str = "",
    ) -> UniverseDefinition:
        """Create a custom universe."""
        universe = UniverseDefinition(
            name=name,
            category=category,
            symbols=symbols,
            description=description,
        )
        self.add_universe(universe)
        return universe
    
    def get_universe_stats(self) -> dict:
        """Get universe statistics."""
        stats = {
            "total_universes": len(self._universes),
            "total_symbols": len(self.get_combined_universe()),
            "by_category": {},
        }
        
        for category in SecurityCategory:
            universes = self.get_universe_by_category(category)
            symbols = set()
            for u in universes:
                symbols.update(u.symbols)
            stats["by_category"][category.value] = {
                "universe_count": len(universes),
                "symbol_count": len(symbols),
            }
        
        return stats


# Global instance
_universe_manager: Optional[UniverseManager] = None


def get_universe_manager() -> UniverseManager:
    """Get the global universe manager."""
    global _universe_manager
    
    if _universe_manager is None:
        _universe_manager = UniverseManager()
    
    return _universe_manager
