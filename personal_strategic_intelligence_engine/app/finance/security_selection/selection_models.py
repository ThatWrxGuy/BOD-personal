"""Security Selection Models.

This module defines the core data models for security selection.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from dataclasses import dataclass, field


class SecurityCategory(Enum):
    """Category of security."""
    CORE = "core"              # Core holdings (SPY, QQQ)
    INVESTMENT = "investment"  # Long-term investments
    TACTICAL = "tactical"      # Short-term tactical
    INCOME = "income"          # Income/dividend
    OPTIONS = "options"        # Options candidates
    WATCHLIST = "watchlist"    # CEO watchlist


class ConvictionLevel(Enum):
    """Conviction level for recommendations."""
    LOW = "low"           # Informational only
    MODERATE = "moderate" # Valid opportunity
    HIGH = "high"         # Strong candidate
    EXCEPTIONAL = "exceptional"  # Priority allocation


class ScreeningResult(Enum):
    """Result of security screening."""
    PASSED = "passed"
    FAILED = "failed"
    REVIEW = "review"


class StrategyType(Enum):
    """Type of investment strategy."""
    INVESTMENT = "investment"     # Long-term
    SWING = "swing"              # Medium-term
    TACTICAL = "tactical"        # Short-term
    INTRADAY = "intraday"        # Same-day
    OPTIONS = "options"          # Options-based


@dataclass
class SecurityProfile:
    """Core security attributes."""
    symbol: str
    name: str
    category: SecurityCategory
    price: Decimal
    change_percent: float
    volume: int
    avg_volume: int
    market_cap: Optional[float] = None
    sector: Optional[str] = None
    
    # Options-specific (if applicable)
    has_options: bool = False
    options_volume: Optional[int] = None
    options_open_interest: Optional[int] = None
    put_call_ratio: Optional[float] = None


@dataclass
class ScreenCriteria:
    """Screening criteria for security filtering."""
    min_volume: int = 500000
    min_avg_volume: int = 300000
    min_market_cap: float = 1_000_000_000  # $1B
    max_spread_percent: float = 2.0
    min_price: Decimal = Decimal("1.00")
    max_price: Optional[Decimal] = None
    
    # Options-specific
    min_options_volume: int = 10000
    max_put_call_ratio: float = 2.5
    
    # Technical
    min_relative_strength: float = -20.0
    

@dataclass
class ScreenResult:
    """Result of screening a security."""
    symbol: str
    result: ScreeningResult
    reasons_passed: list[str] = field(default_factory=list)
    reasons_failed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    score: float = 0.0


@dataclass
class FactorScore:
    """Individual factor score."""
    factor_name: str
    score: float           # 0-100
    weight: float          # 0-1
    contribution: float    # score * weight
    details: dict = field(default_factory=dict)


@dataclass
class SecurityScore:
    """Complete security scoring."""
    symbol: str
    category: SecurityCategory
    
    # Individual factor scores
    trend_quality: float = 0.0
    momentum: float = 0.0
    relative_strength: float = 0.0
    liquidity: float = 0.0
    volatility_quality: float = 0.0
    risk_reward: float = 0.0
    fundamental_quality: float = 0.0
    options_quality: float = 0.0
    
    # Calculated
    total_score: float = 0.0
    factor_scores: list[FactorScore] = field(default_factory=list)
    
    # Weights used
    weights: dict = field(default_factory=dict)
    
    def calculate_total(self):
        """Calculate weighted total score."""
        total = 0.0
        self.factor_scores = []
        
        factors = [
            ("trend_quality", self.trend_quality, self.weights.get("trend_quality", 0.20)),
            ("momentum", self.momentum, self.weights.get("momentum", 0.20)),
            ("relative_strength", self.relative_strength, self.weights.get("relative_strength", 0.15)),
            ("liquidity", self.liquidity, self.weights.get("liquidity", 0.15)),
            ("volatility_quality", self.volatility_quality, self.weights.get("volatility_quality", 0.10)),
            ("risk_reward", self.risk_reward, self.weights.get("risk_reward", 0.20)),
        ]
        
        for name, score, weight in factors:
            contribution = score * weight
            total += contribution
            self.factor_scores.append(FactorScore(
                factor_name=name,
                score=score,
                weight=weight,
                contribution=contribution
            ))
        
        self.total_score = total
        return total


@dataclass
class RankedOpportunity:
    """Ranked investment opportunity."""
    rank: int
    symbol: str
    category: SecurityCategory
    score: float
    conviction: ConvictionLevel
    
    # Allocation fit
    allocation_bucket: str
    
    # Details
    score_breakdown: dict = field(default_factory=dict)
    rationale: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SecurityRecommendation:
    """Structured security recommendation."""
    id: str
    symbol: str
    name: str
    category: SecurityCategory
    score: float
    conviction: ConvictionLevel
    
    # Allocation
    allocation_bucket: str
    suggested_weight: float  # Percentage
    
    # Rationale
    rationale: list[str] = field(default_factory=list)
    positive_factors: list[str] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)
    
    # Metadata
    strategy_type: StrategyType = StrategyType.INVESTMENT
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, approved, rejected
    
    # For tactical
    time_horizon: Optional[str] = None  # intraday, swing, position


@dataclass
class UniverseDefinition:
    """Security universe definition."""
    name: str
    category: SecurityCategory
    symbols: list[str]
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SelectionReport:
    """Security selection report."""
    timestamp: datetime
    universe_size: int
    screened_size: int
    
    # Top picks
    top_investment: Optional[RankedOpportunity] = None
    top_tactical: Optional[RankedOpportunity] = None
    
    # All ranked
    ranked_opportunities: list[RankedOpportunity] = field(default_factory=list)
    
    # Statistics
    average_score: float = 0.0
    high_conviction_count: int = 0
    
    # Changes from previous
    new_additions: list[str] = field(default_factory=list)
    removals: list[str] = field(default_factory=list)
