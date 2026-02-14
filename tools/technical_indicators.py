"""
Technical indicators calculation for stock analysis.
Includes RSI, MACD, and Moving Averages.
"""
import pandas as pd
import numpy as np
from typing import Dict


def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
        prices: Series of closing prices
        period: RSI period (default 14)
        
    Returns:
        RSI value (0-100)
    """
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi.iloc[-1], 2)
    except Exception as e:
        return None


def calculate_macd(prices: pd.Series) -> Dict:
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    Args:
        prices: Series of closing prices
        
    Returns:
        Dictionary with MACD line, signal line, and histogram
    """
    try:
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            "macd": round(macd_line.iloc[-1], 2),
            "signal": round(signal_line.iloc[-1], 2),
            "histogram": round(histogram.iloc[-1], 2)
        }
    except Exception as e:
        return {"macd": None, "signal": None, "histogram": None}


def calculate_moving_averages(prices: pd.Series) -> Dict:
    """
    Calculate Simple Moving Averages for different periods.
    
    Args:
        prices: Series of closing prices
        
    Returns:
        Dictionary with SMA values
    """
    try:
        return {
            "sma_20": round(prices.rolling(window=20).mean().iloc[-1], 2),
            "sma_50": round(prices.rolling(window=50).mean().iloc[-1], 2),
            "sma_200": round(prices.rolling(window=200).mean().iloc[-1], 2) if len(prices) >= 200 else None
        }
    except Exception as e:
        return {"sma_20": None, "sma_50": None, "sma_200": None}


def generate_technical_signal(rsi: float, macd: Dict, sma: Dict, current_price: float) -> str:
    """
    Generate a human-readable technical trading signal.
    
    Args:
        rsi: RSI value
        macd: MACD dictionary
        sma: Moving averages dictionary
        current_price: Current stock price
        
    Returns:
        Technical signal description
    """
    signals = []
    
    # RSI signals
    if rsi:
        if rsi < 30:
            signals.append("RSI Oversold - Potential Buy Zone")
        elif rsi > 70:
            signals.append("RSI Overbought - Caution")
        else:
            signals.append("RSI Neutral")
    
    # MACD signals
    if macd.get("macd") and macd.get("signal"):
        if macd["macd"] > macd["signal"]:
            signals.append("MACD Bullish Crossover")
        else:
            signals.append("MACD Bearish")
    
    # Moving average signals
    if sma.get("sma_20") and sma.get("sma_50"):
        if current_price > sma["sma_20"] > sma["sma_50"]:
            signals.append("Strong Uptrend")
        elif current_price < sma["sma_20"] < sma["sma_50"]:
            signals.append("Downtrend")
        else:
            signals.append("Sideways Movement")
    
    if not signals:
        return "Insufficient data for technical signal"
    
    return " | ".join(signals)
