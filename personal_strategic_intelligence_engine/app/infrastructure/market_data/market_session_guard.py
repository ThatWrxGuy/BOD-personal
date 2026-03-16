"""Market Session Guard - BB-INF-007

Validates quotes against market session rules.
"""

from datetime import datetime, time
from typing import Optional
import logging

from app.infrastructure.market_data.market_data_models import (
    LivePriceQuote,
    PriceValidationResult,
    MarketSession,
)

logger = logging.getLogger(__name__)


class MarketSessionGuard:
    """Validates quotes against market session rules."""
    
    # Trading hours (Eastern Time)
    REGULAR_OPEN = time(9, 30)
    REGULAR_CLOSE = time(16, 0)
    
    PRE_MARKET_OPEN = time(4, 0)
    PRE_MARKET_END = time(9, 30)
    
    AFTER_HOURS_OPEN = time(16, 0)
    AFTER_HOURS_CLOSE = time(20, 0)
    
    def __init__(self):
        pass
    
    def validate(
        self,
        quote: LivePriceQuote,
        require_regular_session: bool = False,
    ) -> PriceValidationResult:
        """Validate quote against market session."""
        
        result = PriceValidationResult(
            symbol=quote.symbol,
            quote=quote,
        )
        
        # Check if quote is from valid session
        session = quote.market_session
        
        if require_regular_session and session != MarketSession.REGULAR:
            result.passed_session_check = False
            result.failure_reason = f"Requires regular session, got {session.value}"
            result.approved_for_decisioning = False
            return result
        
        # Extended hours validation
        if session == MarketSession.PRE_MARKET or session == MarketSession.AFTER_HOURS:
            # Pre/after market - warn but allow
            logger.warning(f"Quote for {quote.symbol} from {session.value} - limited liquidity")
        
        # Check if market is closed
        if session == MarketSession.CLOSED:
            result.passed_session_check = True  # Allow but note
            result.failure_reason = "Market closed - using last close price"
            # Don't block, but note the limitation
        
        result.passed_session_check = True
        result.approved_for_decisioning = True
        
        return result
    
    def get_current_session(self) -> MarketSession:
        """Get current market session based on time."""
        
        now = datetime.utcnow()
        
        # Convert to Eastern Time (approximate)
        # In production, use proper timezone handling
        hour = now.hour
        
        # UTC to ET offset (approximately)
        et_hour = (hour - 5) % 24
        
        current_time = time(et_hour, now.minute)
        
        if self.PRE_MARKET_OPEN <= current_time < self.PRE_MARKET_END:
            return MarketSession.PRE_MARKET
        elif self.REGULAR_OPEN <= current_time < self.REGULAR_CLOSE:
            return MarketSession.REGULAR
        elif self.AFTER_HOURS_OPEN <= current_time < self.AFTER_HOURS_CLOSE:
            return MarketSession.AFTER_HOURS
        else:
            return MarketSession.CLOSED
    
    def is_trading_open(self) -> bool:
        """Check if market is currently open for regular trading."""
        return self.get_current_session() == MarketSession.REGULAR


_session_guard: Optional[MarketSessionGuard] = None


def get_market_session_guard() -> MarketSessionGuard:
    """Get the market session guard."""
    global _session_guard
    
    if _session_guard is None:
        _session_guard = MarketSessionGuard()
    
    return _session_guard
