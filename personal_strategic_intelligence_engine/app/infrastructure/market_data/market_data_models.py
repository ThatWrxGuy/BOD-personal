"""Market Data Models - BB-INF-007

Canonical data models for live market data integrity.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class EnvironmentMode(str, Enum):
    """Environment modes for market data."""
    LIVE = "live"
    PAPER = "paper"
    BACKTEST = "backtest"
    DEV = "dev"


class AssetType(str, Enum):
    """Asset types for market data."""
    EQUITY = "equity"
    OPTION = "option"
    ETF = "etf"
    INDEX = "index"
    FOREX = "forex"
    CRYPTO = "crypto"


class MarketSession(str, Enum):
    """Market session states."""
    PRE_MARKET = "pre_market"
    REGULAR = "regular"
    AFTER_HOURS = "after_hours"
    CLOSED = "closed"
    EXTENDED_HOURS = "extended_hours"


class ValidationStatus(str, Enum):
    """Validation status for quotes."""
    VALID = "valid"
    STALE = "stale"
    INVALID = "invalid"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


class ProviderStatus(str, Enum):
    """Market data provider status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


class LivePriceQuote(BaseModel):
    """Canonical live price quote model."""
    # Core identification
    symbol: str = Field(..., description="Ticker symbol")
    asset_type: AssetType = Field(default=AssetType.EQUITY)
    
    # Price data
    last_price: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    mid_price: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None
    
    # Timestamps
    quote_timestamp: Optional[datetime] = None  # When the quote was generated
    provider_timestamp: Optional[datetime] = None  # When provider sent the quote
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)  # When we received it
    
    # Source metadata
    provider_name: str = "unknown"
    
    # Validity flags
    is_live: bool = False
    is_stale: bool = True
    is_cached: bool = False
    
    # Performance
    latency_ms: Optional[float] = None
    
    # Session
    market_session: MarketSession = MarketSession.CLOSED
    
    # Confidence and validation
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.0)
    validation_status: ValidationStatus = ValidationStatus.INVALID
    
    # Error handling
    error_message: Optional[str] = None
    
    def get_age_seconds(self) -> float:
        """Get age of quote in seconds."""
        if self.quote_timestamp:
            return (datetime.utcnow() - self.quote_timestamp).total_seconds()
        return float('inf')
    
    def is_fresh(self, max_age_seconds: float = 15.0) -> bool:
        """Check if quote is fresh enough."""
        return self.get_age_seconds() <= max_age_seconds


class PriceValidationResult(BaseModel):
    """Result of price validation for decisioning."""
    symbol: str
    approved_for_decisioning: bool = False
    
    # Validation checks
    passed_freshness_check: bool = False
    passed_session_check: bool = False
    passed_range_check: bool = False
    passed_integrity_check: bool = False
    
    # Details
    staleness_seconds: float = 0.0
    failure_reason: Optional[str] = None
    
    # Quote reference
    quote: Optional[LivePriceQuote] = None
    
    # Context
    use_case: str = "general"
    validated_at: datetime = Field(default_factory=datetime.utcnow)


class MarketDataPolicy(BaseModel):
    """Policy configuration for market data handling."""
    
    # Freshness thresholds (in seconds)
    equity_max_age_seconds: float = 15.0
    equity_warning_age_seconds: float = 5.0
    
    option_max_age_seconds: float = 5.0
    option_warning_age_seconds: float = 2.0
    
    etf_max_age_seconds: float = 15.0
    index_max_age_seconds: float = 60.0
    
    # Reporting thresholds
    reporting_max_age_seconds: float = 300.0
    reporting_warning_age_seconds: float = 60.0
    
    # Strict mode
    strict_mode: bool = True
    
    # Environment
    environment: EnvironmentMode = EnvironmentMode.DEV
    
    # Fallback permissions
    allow_fallback_in_paper: bool = True
    allow_fallback_in_backtest: bool = True
    allow_fallback_in_dev: bool = True
    allow_fallback_in_live: bool = False
    
    # Emergency degradation
    emergency_degradation_policy: str = "block"  # block, warn, or allow


class ProviderHealth(BaseModel):
    """Health status of a market data provider."""
    provider_name: str
    status: ProviderStatus = ProviderStatus.UNKNOWN
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    failure_count: int = 0
    avg_latency_ms: float = 0.0
    success_rate: float = 0.0


class MarketDataIntegrityReport(BaseModel):
    """Integrity report for market data operations."""
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Summary stats
    total_requests: int = 0
    valid_live_quotes: int = 0
    stale_quotes_blocked: int = 0
    invalid_quotes_rejected: int = 0
    fallback_attempts_blocked: int = 0
    provider_failures: int = 0
    
    # By symbol
    by_symbol: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    
    # By module
    by_module: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    
    # Provider health
    provider_health: Dict[str, ProviderHealth] = Field(default_factory=dict)


class QuoteRequest(BaseModel):
    """Request for a market data quote."""
    symbol: str
    asset_type: AssetType = AssetType.EQUITY
    context: str = "general"  # trading, reporting, analysis, etc.
    allow_cached: bool = False
    require_live: bool = True


# Prohibited patterns - these should never be used in production
PROHIBITED_PATTERNS = [
    "default_price",
    "fallback_price",
    "static_price",
    "hardcoded_price",
    "placeholder_price",
    "mock_price",
    "fake_price",
    "SPY_PRICE",
    "DEFAULT_QUOTE",
]
