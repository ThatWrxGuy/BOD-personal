"""Finance Domain Data Models.

Canonical models for finance domain data including:
- Economic series data
- Market/company data
- Regulatory filings
- Financial news
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class EconomicSeriesRecord(BaseModel):
    """Macroeconomic time series data."""
    record_id: UUID = Field(default_factory=uuid4)
    series_id: str = Field(..., description="Series identifier (e.g., GDP, CPI)")
    series_name: str = Field(..., description="Human-readable series name")
    value: float = Field(..., description="Current value")
    unit: str = Field(..., description="Unit of measurement")
    frequency: str = Field(..., description="Data frequency (monthly, quarterly, etc.)")
    period: str = Field(..., description="Time period")
    period_date: datetime = Field(..., description="Period date")
    source_id: str = Field("finance_macro_us", description="Source identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MarketSnapshot(BaseModel):
    """Market data snapshot."""
    snapshot_id: UUID = Field(default_factory=uuid4)
    symbol: str = Field(..., description="Market symbol")
    price: float = Field(..., description="Current price")
    volume: int = Field(0, description="Trading volume")
    open_price: float = Field(..., description="Open price")
    high_price: float = Field(..., description="High price")
    low_price: float = Field(..., description="Low price")
    close_price: float = Field(..., description="Close price")
    change_percent: float = Field(0, description="Percent change")
    timestamp: datetime = Field(..., description="Snapshot timestamp")
    source_id: str = Field("finance_market_quotes", description="Source identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FilingRecord(BaseModel):
    """SEC filing record."""
    filing_id: UUID = Field(default_factory=uuid4)
    company_name: str = Field(..., description="Company name")
    ticker: str = Field(..., description="Stock ticker")
    filing_type: str = Field(..., description="Filing type (10-K, 10-Q, etc.)")
    filing_date: datetime = Field(..., description="Filing date")
    period_of_report: Optional[str] = Field(None, description="Period of report")
    sec_url: str = Field(..., description="SEC URL")
    summary: Optional[str] = Field(None, description="Filing summary")
    source_id: str = Field("finance_filings_sec", description="Source identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FinanceNewsDocument(BaseModel):
    """Financial news article."""
    document_id: UUID = Field(default_factory=uuid4)
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Article content")
    summary: Optional[str] = Field(None, description="Article summary")
    url: str = Field(..., description="Article URL")
    published_at: datetime = Field(..., description="Publication date")
    source_name: str = Field(..., description="News source")
    tickers_mentioned: List[str] = Field(default_factory=list, description="Tickers mentioned")
    topics: List[str] = Field(default_factory=list, description="Topics/tags")
    sentiment: Optional[str] = Field(None, description="Sentiment (positive, negative, neutral)")
    source_id: str = Field("finance_news_approved", description="Source identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
