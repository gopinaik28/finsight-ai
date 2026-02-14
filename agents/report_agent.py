"""
Report Agent - Generates comprehensive investment report using LLM.
"""
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from models.schemas import AgentState, InvestmentReport

load_dotenv()


def report_agent(state: AgentState) -> AgentState:
    """
    Generate comprehensive investment report.
    
    Args:
        state: Current agent state with all analysis complete
        
    Returns:
        Updated state with investment report
    """
    try:
        messages = state.get("messages", [])
        messages.append("🔄 Report Agent: Generating investment brief...")
        
        # Collect all data
        company_name = state.get("company_name", "")
        ticker = state.get("ticker", "")
        market_data = state.get("market_data")
        sentiment = state.get("sentiment")
        research = state.get("research")
        forecast = state.get("forecast")
        
        # Initialize Gemini LLM
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError("Google API key not configured")
        
        llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.7
        )
        
        # Create comprehensive prompt
        prompt = f"""You are a senior financial analyst at Goldman Sachs. Generate a professional investment brief for {company_name} ({ticker}).

MARKET DATA:
- Current Price: ₹{market_data.current_price if market_data else 'N/A'}
- P/E Ratio: {market_data.pe_ratio if market_data and market_data.pe_ratio else 'N/A'}
- Market Cap: ₹{market_data.market_cap/10000000 if market_data and market_data.market_cap else 'N/A'} Cr
- 52-Week High/Low: ₹{market_data.week_52_high if market_data else 'N/A'} / ₹{market_data.week_52_low if market_data else 'N/A'}
- RSI: {market_data.rsi if market_data else 'N/A'}
- Technical Signal: {market_data.signal if market_data else 'N/A'}
- Sector: {market_data.sector if market_data else 'N/A'}

SENTIMENT ANALYSIS:
- Overall Sentiment: {sentiment.label if sentiment else 'N/A'} ({sentiment.overall_score if sentiment else 'N/A'})
- Articles Analyzed: {sentiment.total_articles if sentiment else 'N/A'}
- Positive/Negative: {sentiment.positive_count if sentiment else 'N/A'}/{sentiment.negative_count if sentiment else 'N/A'}
- Key Events: {', '.join(sentiment.key_events[:3]) if sentiment and sentiment.key_events else 'N/A'}

RESEARCH INSIGHTS:
- Key Findings: {', '.join(research.key_findings) if research else 'N/A'}
- Revenue Growth: {research.revenue_growth if research else 'N/A'}
- Major Risks: {', '.join(research.major_risks) if research else 'N/A'}
- Management Outlook: {research.management_outlook if research else 'N/A'}

PRICE FORECAST (30 days):
- Target Price: ₹{forecast.predicted_price if forecast else 'N/A'}
- Upside Potential: {forecast.upside_percentage if forecast else 'N/A'}%
- Confidence: {forecast.confidence_score if forecast else 'N/A'}
- Range: ₹{forecast.lower_band if forecast else 'N/A'} - ₹{forecast.upper_band if forecast else 'N/A'}

Based on all this data, provide:
1. recommendation: One of [STRONG BUY, BUY, HOLD, SELL, STRONG SELL]
2. executive_summary: 2-3 sentence overview of the investment opportunity
3. financial_snapshot: Brief summary of key financial metrics
4. catalysts: List of 3-5 positive catalysts/opportunities
5. risks: List of 3-5 key risks to watch
6. forecast_summary: Summary of price forecast and key drivers
7. sentiment_summary: Summary of market sentiment and news impact

Format as JSON with these exact keys. Be professional, data-driven, and actionable.
"""
        
        # Get structured output
        structured_llm = llm.with_structured_output(InvestmentReport)
        report = structured_llm.invoke(prompt)
        
        # Ensure generated_at is set
        if not report.generated_at:
            report.generated_at = datetime.now()
        
        messages.append(f"✅ Report Agent: Investment brief complete - {report.recommendation}")
        
        return {
            **state,
            "report": report,
            "messages": messages,
            "current_agent": "report"
        }
        
    except Exception as e:
        messages = state.get("messages", [])
        messages.append(f"❌ Report Agent Error: {str(e)}")
        
        # Fallback report
        market_data = state.get("market_data")
        sentiment = state.get("sentiment")
        forecast = state.get("forecast")
        
        # Simple recommendation logic
        if forecast and forecast.upside_percentage > 10 and sentiment and sentiment.overall_score > 0.3:
            recommendation = "BUY"
        elif forecast and forecast.upside_percentage < -5:
            recommendation = "SELL"
        else:
            recommendation = "HOLD"
        
        fallback_report = InvestmentReport(
            recommendation=recommendation,
            executive_summary=f"{state.get('company_name')} shows mixed signals. Technical analysis and sentiment suggest a {recommendation} position.",
            financial_snapshot=f"Current price: ₹{market_data.current_price if market_data else 'N/A'}, PE: {market_data.pe_ratio if market_data and market_data.pe_ratio else 'N/A'}",
            catalysts=["Strong market position", "Sector tailwinds", "Positive sentiment"],
            risks=["Market volatility", "Regulatory changes", "Competition"],
            forecast_summary=f"30-day target: ₹{forecast.predicted_price if forecast else 'N/A'}",
            sentiment_summary=f"Market sentiment: {sentiment.label if sentiment else 'Neutral'}",
            generated_at=datetime.now()
        )
        
        return {
            **state,
            "report": fallback_report,
            "messages": messages,
            "error": str(e)
        }
