"""
Market Data Agent - Fetches stock data and calculates technical indicators.
"""
import os
from typing import Dict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from models.schemas import AgentState, MarketData
from tools.stock_tools import get_stock_data, search_ticker
from tools.technical_indicators import (
    calculate_rsi,
    calculate_macd,
    calculate_moving_averages,
    generate_technical_signal
)

load_dotenv()


def market_data_agent(state: AgentState) -> AgentState:
    """
    Fetch market data and technical indicators for a company.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with market data
    """
    try:
        company_name = state.get("company_name", "")
        messages = state.get("messages", [])
        messages.append("🔄 Market Data Agent: Starting analysis...")
        
        # Find ticker symbol
        ticker = search_ticker(company_name)
        if not ticker:
            # Try the company name as-is with .NS suffix
            ticker = f"{company_name}.NS"
        
        messages.append(f"📊 Market Data Agent: Found ticker {ticker}")
        
        # Fetch stock data
        stock_data = get_stock_data(ticker)
        historical_data = stock_data.get("historical_data")
        
        # Calculate technical indicators
        prices = historical_data['Close']
        rsi = calculate_rsi(prices)
        macd = calculate_macd(prices)
        sma = calculate_moving_averages(prices)
        
        # Generate trading signal
        signal = generate_technical_signal(
            rsi=rsi,
            macd=macd,
            sma=sma,
            current_price=stock_data["current_price"]
        )
        
        # MACD description
        macd_desc = "Bullish" if macd.get("macd", 0) > macd.get("signal", 0) else "Bearish"
        
        # Create MarketData object
        market_data = MarketData(
            company=stock_data["company"],
            ticker=ticker,
            current_price=stock_data["current_price"],
            pe_ratio=stock_data.get("pe_ratio"),
            market_cap=stock_data.get("market_cap"),
            week_52_high=stock_data.get("week_52_high"),
            week_52_low=stock_data.get("week_52_low"),
            target_high=stock_data.get("target_high"),
            target_low=stock_data.get("target_low"),
            target_mean=stock_data.get("target_mean"),
            target_median=stock_data.get("target_median"),
            num_analysts=stock_data.get("num_analysts"),
            rsi=rsi,
            macd=macd_desc,
            signal=signal,
            sector=stock_data.get("sector"),
            volume=stock_data.get("volume")
        )
        
        messages.append(f"✅ Market Data Agent: Analysis complete - {ticker} @ ₹{stock_data['current_price']}")
        
        return {
            **state,
            "ticker": ticker,
            "market_data": market_data,
            "historical_prices": historical_data,
            "messages": messages,
            "current_agent": "market_data"
        }
        
    except Exception as e:
        messages = state.get("messages", [])
        messages.append(f"❌ Market Data Agent Error: {str(e)}")
        return {
            **state,
            "messages": messages,
            "error": str(e)
        }
