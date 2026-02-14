"""
Stock market data extraction using yfinance.
Handles NSE/BSE tickers for Indian stocks.
"""
import yfinance as yf
import pandas as pd
from typing import Dict, Optional
from datetime import datetime, timedelta


def get_stock_data(ticker: str) -> Dict:
    """
    Fetch comprehensive stock data for a given ticker with robust error handling.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE.NS')
        
    Returns:
        Dictionary containing stock data and metrics
    """
    try:
        print(f"🔍 Attempting to fetch data for {ticker}...")
        
        # Create ticker object
        stock = yf.Ticker(ticker)
        
        # Try to get historical data first (most reliable)
        print(f"📊 Fetching historical data...")
        hist = stock.history(period="1y", timeout=30)
        
        if hist.empty:
            print(f"⚠️ No historical data found for {ticker}")
            # Try shorter period as fallback
            hist = stock.history(period="1mo", timeout=30)
            
        if hist.empty:
            raise ValueError(f"No data available for ticker {ticker}. Please check if the ticker symbol is correct.")
        
        print(f"✅ Got {len(hist)} days of historical data")
        
        # Calculate current price from historical data
        current_price = float(hist['Close'].iloc[-1])
        
        # Try to get info, but don't fail if it doesn't work
        info = {}
        try:
            print(f"📝 Fetching company info...")
            info = stock.info
            print(f"✅ Company info retrieved")
        except Exception as e:
            print(f"⚠️ Could not fetch detailed company info: {str(e)}")
            print(f"ℹ️  Continuing with basic data only...")
        
        # Build result with safe .get() calls
        result = {
            "ticker": ticker,
            "company": info.get("longName") or info.get("shortName") or ticker.split('.')[0],
            "current_price": round(current_price, 2),
            "pe_ratio": info.get("trailingPE"),
            "market_cap": info.get("marketCap"),
            "week_52_high": info.get("fiftyTwoWeekHigh") or float(hist['High'].max()),
            "week_52_low": info.get("fiftyTwoWeekLow") or float(hist['Low'].min()),
            "target_high": info.get("targetHighPrice"),
            "target_low": info.get("targetLowPrice"),
            "target_mean": info.get("targetMeanPrice"),
            "target_median": info.get("targetMedianPrice"),
            "num_analysts": info.get("numberOfAnalystOpinions"),
            "sector": info.get("sector", "Unknown"),
            "volume": int(hist['Volume'].iloc[-1]) if len(hist) > 0 else None,
            "historical_data": hist
        }
        
        print(f"✅ Successfully fetched data for {result['company']}")
        return result
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error fetching stock data for {ticker}: {error_msg}")
        raise Exception(f"Error fetching stock data for {ticker}: {error_msg}")


def get_historical_prices(ticker: str, period: str = "1y") -> pd.DataFrame:
    """
    Fetch historical price data with better error handling.
    
    Args:
        ticker: Stock ticker symbol
        period: Data period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
        
    Returns:
        DataFrame with historical OHLCV data
    """
    try:
        print(f"📈 Fetching {period} historical data for {ticker}...")
        stock = yf.Ticker(ticker)
        
        # Fetch with timeout
        hist = stock.history(period=period, timeout=30)
        
        if hist.empty:
            print(f"⚠️ No data for period {period}, trying 6 months...")
            hist = stock.history(period="6mo", timeout=30)
            
        if hist.empty:
            raise ValueError(f"No historical data available for {ticker}")
        
        # Reset index to make Date a column
        hist = hist.reset_index()
        
        print(f"✅ Retrieved {len(hist)} data points")
        return hist
        
    except Exception as e:
        print(f"❌ Error fetching historical prices: {str(e)}")
        raise Exception(f"Error fetching historical prices for {ticker}: {str(e)}")


def search_ticker(company_name: str) -> Optional[str]:
    """
    Search for a ticker symbol by company name.
    For Indian stocks, tries both NSE (.NS) and BSE (.BO) suffixes.
    
    Args:
        company_name: Name of the company
        
    Returns:
        Ticker symbol or None if not found
    """
    try:
        # Common Indian company ticker mappings
        indian_tickers = {
            "reliance": "RELIANCE.NS",
            "reliance industries": "RELIANCE.NS",
            "tcs": "TCS.NS",
            "tata consultancy": "TCS.NS",
            "infosys": "INFY.NS",
            "hdfc bank": "HDFCBANK.NS",
            "icici bank": "ICICIBANK.NS",
            "bharti airtel": "BHARTIARTL.NS",
            "airtel": "BHARTIARTL.NS",
            "wipro": "WIPRO.NS",
            "ltim": "LTIM.NS",
            "hcl tech": "HCLTECH.NS",
            "kaynes": "KAYNES.NS",
            "kaynes technology": "KAYNES.NS",
        }
        
        # Check if it's already a ticker
        if "." in company_name:
            return company_name.upper()
        
        # Try direct lookup
        company_lower = company_name.lower().strip()
        if company_lower in indian_tickers:
            return indian_tickers[company_lower]
        
        # Try adding .NS suffix for NSE
        ticker_ns = f"{company_name.upper()}.NS"
        stock = yf.Ticker(ticker_ns)
        if stock.info.get("regularMarketPrice"):
            return ticker_ns
        
        # Try adding .BO suffix for BSE
        ticker_bo = f"{company_name.upper()}.BO"
        stock = yf.Ticker(ticker_bo)
        if stock.info.get("regularMarketPrice"):
            return ticker_bo
        
        return None
    except:
        return None
