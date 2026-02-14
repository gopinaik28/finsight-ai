"""
Forecast Agent - Price forecasting using Prophet with sentiment as external regressor.
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from prophet import Prophet
from models.schemas import AgentState, ForecastResult

load_dotenv()


def forecast_agent(state: AgentState) -> AgentState:
    """
    Generate price forecast using Prophet model.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with forecast results
    """
    try:
        messages = state.get("messages", [])
        messages.append("🔄 Forecast Agent: Generating price predictions...")
        
        # Get historical prices
        historical_prices = state.get("historical_prices")
        if historical_prices is None or historical_prices.empty:
            raise ValueError("['Date'] not in index")
        
        # Ensure Date is a column, not index
        if 'Date' not in historical_prices.columns:
            historical_prices = historical_prices.reset_index()
        
        # Get sentiment score as external factor
        sentiment = state.get("sentiment")
        sentiment_score = sentiment.overall_score if sentiment else 0.0
        
        # Prepare data for Prophet
        df = historical_prices[['Date', 'Close']].copy()
        df.columns = ['ds', 'y']
        df['ds'] = pd.to_datetime(df['ds'])
        
        # Add sentiment as external regressor (constant value across historical data)
        df['sentiment'] = sentiment_score
        
        # Initialize and fit Prophet model
        messages.append("📈 Forecast Agent: Training Prophet model...")
        
        # Suppress Prophet logging
        import logging
        logging.getLogger('prophet').setLevel(logging.WARNING)
        logging.getLogger('cmdstanpy').setLevel(logging.WARNING)
        
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05,
            interval_width=0.95,
            uncertainty_samples=0  # Disable MCMC sampling to avoid stan_backend issues
        )
        
        # Add sentiment as regressor
        model.add_regressor('sentiment')
        
        # Fit model
        with pd.option_context('mode.chained_assignment', None):
            model.fit(df)
        
        # Create future dataframe (30 days)
        forecast_days = 30
        future = model.make_future_dataframe(periods=forecast_days)
        future['sentiment'] = sentiment_score
        
        # Generate forecast
        forecast = model.predict(future)
        
        # Get the predicted price for last day
        predicted_price = forecast['yhat'].iloc[-1]
        upper_band = forecast['yhat_upper'].iloc[-1]
        lower_band = forecast['yhat_lower'].iloc[-1]
        
        # Calculate current price
        current_price = df['y'].iloc[-1]
        
        # Calculate upside
        upside_percentage = ((predicted_price - current_price) / current_price) * 100
        
        # Calculate confidence score (based on band width)
        band_width = upper_band - lower_band
        confidence_score = max(0.3, min(0.9, 1 - (band_width / predicted_price)))
        
        # Determine key driver
        if sentiment_score > 0.3:
            key_driver = "Strong positive sentiment driving bullish forecast"
        elif sentiment_score < -0.3:
            key_driver = "Negative sentiment creating cautious outlook"
        else:
            key_driver = "Technical trends and historical patterns"
        
        # Create ForecastResult object
        forecast_result = ForecastResult(
            predicted_price=round(predicted_price, 2),
            upside_percentage=round(upside_percentage, 2),
            confidence_score=round(confidence_score, 2),
            upper_band=round(upper_band, 2),
            lower_band=round(lower_band, 2),
            forecast_period_days=forecast_days,
            key_driver=key_driver
        )
        
        messages.append(
            f"✅ Forecast Agent: 30-day target ₹{predicted_price:.2f} "
            f"({'+' if upside_percentage > 0 else ''}{upside_percentage:.1f}%)"
        )
        
        return {
            **state,
            "forecast": forecast_result,
            "messages": messages,
            "current_agent": "forecast"
        }
        
    except Exception as e:
        messages = state.get("messages", [])
        messages.append(f"❌ Forecast Agent Error: {str(e)}")
        messages.append("📊 Using advanced fallback forecasting method...")
        
        # Advanced fallback using linear regression
        try:
            historical_prices = state.get("historical_prices")
            
            # Ensure Date column exists
            if 'Date' not in historical_prices.columns:
                historical_prices = historical_prices.reset_index()
           
            # Get sentiment
            sentiment = state.get("sentiment")
            sentiment_score = sentiment.overall_score if sentiment else 0.0
            
            # Use last 90 days for trend
            recent_data = historical_prices.tail(90).copy()
            current_price = recent_data['Close'].iloc[-1]
            
            # Calculate linear trend
            prices = recent_data['Close'].values
            days = np.arange(len(prices))
            
            # Fit linear regression
            coefficients = np.polyfit(days, prices, 1)
            slope, intercept = coefficients
            
            # Project 30 days forward
            forecast_days = 30
            future_day = len(prices) + forecast_days
            predicted_price = slope * future_day + intercept
            
            # Adjust based on sentiment
            sentiment_adjustment = 1 + (sentiment_score * 0.05)  # -5% to +5% based on sentiment
            predicted_price = predicted_price * sentiment_adjustment
            
            # Calculate upside
            upside = ((predicted_price - current_price) / current_price) * 100
            
            # Calculate confidence bands based on historical volatility
            volatility = recent_data['Close'].pct_change().std()
            band_width = predicted_price * volatility * np.sqrt(forecast_days)
            upper_band = predicted_price + band_width
            lower_band = max(0, predicted_price - band_width)
            
            # Determine key driver
            if abs(sentiment_score) > 0.3:
                sentiment_desc = "positive" if sentiment_score > 0 else "negative"
                key_driver = f"Linear trend analysis with {sentiment_desc} sentiment weighting"
            else:
                key_driver = "Linear trend extrapolation from 90-day price history"
            
            fallback_forecast = ForecastResult(
                predicted_price=round(predicted_price, 2),
                upside_percentage=round(upside, 2),
                confidence_score=0.65,  # Higher confidence than simple average
                upper_band=round(upper_band, 2),
                lower_band=round(lower_band, 2),
                forecast_period_days=forecast_days,
                key_driver=key_driver
            )
            
            messages.append(f"✅ Forecast Agent: 30-day target ₹{predicted_price:.2f} ({'+' if upside > 0 else ''}{upside:.1f}%)")
            
            return {
                **state,
                "forecast": fallback_forecast,
                "messages": messages,
                "current_agent": "forecast"
            }
        except Exception as fallback_error:
            messages.append(f"❌ Forecast Agent: Could not generate forecast - {str(fallback_error)}")
            return {
                **state,
                "messages": messages,
                "error": str(e)
            }
