"""
Pydantic schemas for structured output from agents.
All data models used across the FinSight AI platform.
"""
from datetime import datetime
from typing import List, Optional, TypedDict
from pydantic import BaseModel, Field


class MarketData(BaseModel):
    """Market data and technical indicators for a company."""
    company: str = Field(description="Company name")
    ticker: str = Field(description="Stock ticker symbol")
    current_price: float = Field(description="Current stock price")
    pe_ratio: Optional[float] = Field(default=None, description="Price-to-Earnings ratio")
    market_cap: Optional[float] = Field(default=None, description="Market capitalization")
    week_52_high: Optional[float] = Field(default=None, description="52-week high price")
    week_52_low: Optional[float] = Field(default=None, description="52-week low price")
    target_high: Optional[float] = Field(default=None, description="Analyst target high price")
    target_low: Optional[float] = Field(default=None, description="Analyst target low price")
    target_mean: Optional[float] = Field(default=None, description="Analyst mean target price")
    target_median: Optional[float] = Field(default=None, description="Analyst median target price")
    num_analysts: Optional[int] = Field(default=None, description="Number of analysts covering the stock")
    rsi: Optional[float] = Field(default=None, description="Relative Strength Index")
    macd: Optional[str] = Field(default=None, description="MACD signal description")
    signal: str = Field(description="Trading signal recommendation")
    sector: Optional[str] = Field(default=None, description="Company sector")
    volume: Optional[int] = Field(default=None, description="Trading volume")


class SentimentResult(BaseModel):
    """News sentiment analysis results."""
    total_articles: int = Field(description="Total number of articles analyzed")
    positive_count: int = Field(description="Number of positive articles")
    negative_count: int = Field(description="Number of negative articles")
    neutral_count: int = Field(description="Number of neutral articles")
    overall_score: float = Field(description="Overall sentiment score (-1 to 1)")
    label: str = Field(description="Sentiment label: Bullish/Bearish/Neutral")
    key_events: List[str] = Field(default_factory=list, description="Key events from news")


class ResearchInsight(BaseModel):
    """Research insights from RAG or LLM analysis."""
    key_findings: List[str] = Field(default_factory=list, description="Key research findings")
    revenue_growth: Optional[str] = Field(default=None, description="Revenue growth analysis")
    major_risks: List[str] = Field(default_factory=list, description="Identified major risks")
    management_outlook: Optional[str] = Field(default=None, description="Management outlook and guidance")


class ForecastResult(BaseModel):
    """Price forecast results from Prophet model."""
    predicted_price: float = Field(description="Predicted future price")
    upside_percentage: float = Field(description="Upside potential percentage")
    confidence_score: float = Field(description="Forecast confidence score 0-1")
    upper_band: float = Field(description="Upper confidence band")
    lower_band: float = Field(description="Lower confidence band")
    forecast_period_days: int = Field(description="Forecast period in days")
    key_driver: str = Field(description="Main driver for the forecast")


class InvestmentReport(BaseModel):
    """Complete investment analysis report."""
    recommendation: str = Field(description="Investment recommendation: STRONG BUY/BUY/HOLD/SELL/STRONG SELL")
    executive_summary: str = Field(description="Executive summary of the analysis")
    financial_snapshot: str = Field(description="Financial snapshot and key metrics")
    catalysts: List[str] = Field(default_factory=list, description="Positive catalysts")
    risks: List[str] = Field(default_factory=list, description="Risk factors")
    forecast_summary: str = Field(description="Price forecast summary")
    sentiment_summary: str = Field(description="Market sentiment summary")
    generated_at: datetime = Field(default_factory=datetime.now, description="Report generation timestamp")


class AgentState(TypedDict, total=False):
    """State that flows through the LangGraph agents."""
    company_name: str
    ticker: str
    market_data: Optional[MarketData]
    sentiment: Optional[SentimentResult]
    research: Optional[ResearchInsight]
    forecast: Optional[ForecastResult]
    report: Optional[InvestmentReport]
    messages: List[str]
    current_agent: str
    historical_prices: Optional[object]  # pd.DataFrame
    error: Optional[str]
