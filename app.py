"""
FinSight AI - Multi-Agent Financial Intelligence Platform
Streamlit Frontend Application
"""
import os
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import json
from agents.orchestrator import run_analysis
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="FinSight AI - Financial Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .recommendation-buy {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
    }
    .recommendation-sell {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
    }
    .recommendation-hold {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


def generate_pdf_report(state, filename="report.pdf"):
    """Generate PDF report from analysis results."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # Title
    pdf.cell(0, 10, "FinSight AI - Investment Report", ln=True, align="C")
    pdf.ln(5)
    
    # Company info
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Company: {state.get('company_name', 'N/A')}", ln=True)
    pdf.cell(0, 10, f"Ticker: {state.get('ticker', 'N/A')}", ln=True)
    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(5)
    
    report = state.get('report')
    if report:
        # Recommendation
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Recommendation: {report.recommendation}", ln=True)
        pdf.ln(3)
        
        # Executive Summary
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Executive Summary:", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 5, report.executive_summary)
        pdf.ln(3)
        
        # Catalysts
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Key Catalysts:", ln=True)
        pdf.set_font("Arial", "", 10)
        for catalyst in report.catalysts:
            pdf.multi_cell(0, 5, f"• {catalyst}")
        pdf.ln(3)
        
        # Risks
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Risk Factors:", ln=True)
        pdf.set_font("Arial", "", 10)
        for risk in report.risks:
            pdf.multi_cell(0, 5, f"• {risk}")
    
    # Save
    pdf.output(filename)
    return filename


def main():
    # Header
    st.markdown('<h1 class="main-header">🔍 FinSight AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Multi-Agent Financial Intelligence Platform</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/increase-profits.png", width=80)
        st.markdown("### About")
        st.info("""
        **FinSight AI** uses multiple AI agents working together to provide comprehensive investment analysis:
        
        - 📊 Market Data Agent
        - 📰 Sentiment Analysis
        - 🔬 Research Insights
        - 📈 Price Forecasting
        - 📄 Report Generation
        """)
        
        st.markdown("### Tech Stack")
        st.markdown("""
        - LangGraph (Multi-Agent)
        - Google Gemini 2.0 Flash
        - FinBERT (Sentiment)
        - Prophet (Forecasting)
        - FAISS + BM25 (RAG)
        """)
    
    # Input section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        company_name = st.text_input(
            "Enter Company Name",
            value="Reliance Industries",
            placeholder="e.g., Reliance Industries, TCS, Infosys"
        )
        analyze_button = st.button("🚀 Analyze Company", type="primary", use_container_width=True)
    
    # Analysis
    if analyze_button:
        if not company_name:
            st.error("Please enter a company name!")
            return
        
        # Check API keys
        if not os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY") == "your_gemini_api_key_here":
            st.error("⚠️ Google Gemini API key not configured! Please add it to your .env file.")
            st.code("GOOGLE_API_KEY=your_api_key_here")
            return
        
        # Run analysis
        with st.spinner("🤖 AI Agents are analyzing... This may take 2-3 minutes..."):
            try:
                state = run_analysis(company_name)
                
                # Store in session state
                st.session_state['analysis_state'] = state
                st.session_state['analyzed_company'] = company_name
                
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                st.exception(e)
                return
    
    # Display results if analysis exists
    if 'analysis_state' in st.session_state:
        state = st.session_state['analysis_state']
        
        # Agent activity log
        with st.expander("📋 Agent Activity Log", expanded=False):
            messages = state.get('messages', [])
            for msg in messages:
                st.text(msg)
        
        # Main tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Market Overview",
            "📰 Sentiment Analysis",
            "🔬 Research Insights",
            "📈 Price Forecast",
            "📄 Investment Report"
        ])
        
        # TAB 1: Market Overview
        with tab1:
            market_data = state.get('market_data')
            historical = state.get('historical_prices')
            
            if market_data:
                # SECTION 1: Current Stock Price (PROMINENT)
                st.markdown(f"### 📊 {market_data.company} ({market_data.ticker})")
                
                # Big current price display
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"## Current Price")
                    st.markdown(f"# ₹{market_data.current_price:,.2f}")
                    if market_data.signal:
                        signal_color = "green" if "BUY" in market_data.signal.upper() else "red" if "SELL" in market_data.signal.upper() else "orange"
                        st.markdown(f"<h3 style='color:{signal_color};'>Signal: {market_data.signal}</h3>", unsafe_allow_html=True)
                
                with col2:
                    st.metric("RSI", f"{market_data.rsi:.1f}" if market_data.rsi else "N/A")
                    st.metric("MACD", market_data.macd or "N/A")
                
                with col3:
                    st.metric("Sector", market_data.sector or "N/A")
                    st.metric("Volume", f"{market_data.volume:,}" if market_data.volume else "N/A")
                
                st.divider()
                
                # SECTION 2: Analyst Price Targets
                if market_data.target_mean or market_data.target_high or market_data.target_low:
                    st.markdown("### 🎯 Analyst Price Targets")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Target Mean",
                            f"₹{market_data.target_mean:,.2f}" if market_data.target_mean else "N/A",
                            delta=f"{((market_data.target_mean - market_data.current_price) / market_data.current_price * 100):.1f}%" if market_data.target_mean else None
                        )
                    
                    with col2:
                        st.metric(
                            "Target High",
                            f"₹{market_data.target_high:,.2f}" if market_data.target_high else "N/A",
                            delta=f"{((market_data.target_high - market_data.current_price) / market_data.current_price * 100):.1f}%" if market_data.target_high else None
                        )
                    
                    with col3:
                        st.metric(
                            "Target Low",
                            f"₹{market_data.target_low:,.2f}" if market_data.target_low else "N/A",
                            delta=f"{((market_data.target_low - market_data.current_price) / market_data.current_price * 100):.1f}%" if market_data.target_low else None
                        )
                    
                    with col4:
                        st.metric(
                            "Analysts Covering",
                            market_data.num_analysts if market_data.num_analysts else "N/A"
                        )
                    
                    st.divider()
                
                # SECTION 3: Key Metrics Row
                st.markdown("### 📈 Key Metrics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("P/E Ratio", f"{market_data.pe_ratio:.2f}" if market_data.pe_ratio else "N/A")
                
                with col2:
                    st.metric("52-Week High", f"₹{market_data.week_52_high:,.2f}" if market_data.week_52_high else "N/A")
                
                with col3:
                    st.metric("52-Week Low", f"₹{market_data.week_52_low:,.2f}" if market_data.week_52_low else "N/A")
                
                with col4:
                    st.metric(
                        "Market Cap",
                        f"₹{market_data.market_cap/10000000:,.2f} Cr" if market_data.market_cap else "N/A"
                    )
                
                st.divider()
                
                # SECTION 4: Price Chart (Simple)
                if historical is not None and not historical.empty:
                    st.markdown("### 📉 Price Chart (1 Year)")
                    
                    # Ensure Date is a column, not index
                    if 'Date' not in historical.columns:
                        historical = historical.reset_index()
                    
                    # Simple candlestick chart
                    fig = go.Figure(data=[go.Candlestick(
                        x=historical['Date'],
                        open=historical['Open'],
                        high=historical['High'],
                        low=historical['Low'],
                        close=historical['Close'],
                        name='Price'
                    )])
                    
                    # Add target mean line if available
                    if market_data.target_mean:
                        fig.add_hline(
                            y=market_data.target_mean,
                            line_dash="dash",
                            line_color="green",
                            annotation_text=f"Analyst Target: ₹{market_data.target_mean:.2f}",
                            annotation_position="right"
                        )
                    
                    fig.update_layout(
                        title=f"{market_data.ticker} Stock Price",
                        yaxis_title="Price (₹)",
                        xaxis_title="Date",
                        template="plotly_dark",
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("❌ **Market Data Not Available**")
                st.info("""
                **Possible reasons:**
                - The company ticker could not be found
                - Stock data is unavailable from Yahoo Finance
                - There was a network timeout
                
                **What you can try:**
                1. Enter the exact NSE/BSE ticker symbol (e.g., 'RELIANCE.NS', 'TCS.NS')
                2. Check the Agent Activity Log above for detailed error messages
                3. Try a different company name
                """)
        
        # TAB 2: Sentiment Analysis
        with tab2:
            sentiment = state.get('sentiment')
            if sentiment:
                # Overall sentiment
                col1, col2 = st.columns([1, 2])
                with col1:
                    # Sentiment score with color
                    sentiment_color = "green" if sentiment.overall_score > 0.2 else "red" if sentiment.overall_score < -0.2 else "orange"
                    st.markdown(f"### {sentiment.label}")
                    st.markdown(f"<h1 style='color:{sentiment_color};text-align:center;'>{sentiment.overall_score:+.2f}</h1>", unsafe_allow_html=True)
                    st.markdown(f"**{sentiment.total_articles} articles analyzed**")
                
                with col2:
                    # Sentiment distribution pie chart
                    fig = px.pie(
                        values=[sentiment.positive_count, sentiment.neutral_count, sentiment.negative_count],
                        names=['Positive', 'Neutral', 'Negative'],
                        title='Sentiment Distribution',
                        color_discrete_sequence=['#38ef7d', '#f5576c', '#f45c43']
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Key events
                st.markdown("### 📰 Key Events")
                for event in sentiment.key_events:
                    sentiment_type = event.split(':')[0].strip()
                    event_text = ':'.join(event.split(':')[1:]).strip()
                    
                    if 'POSITIVE' in sentiment_type:
                        st.success(f"✅ {event_text}")
                    elif 'NEGATIVE' in sentiment_type:
                        st.error(f"❌ {event_text}")
                    else:
                        st.info(f"ℹ️ {event_text}")
        
        # TAB 3: Research Insights
        with tab3:
            research = state.get('research')
            if research:
                # Key findings
                st.markdown("### 🔑 Key Findings")
                for finding in research.key_findings:
                    st.markdown(f"- {finding}")
                
                st.divider()
                
                # Revenue growth
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 📈 Revenue Growth")
                    st.info(research.revenue_growth)
                
                with col2:
                    st.markdown("### 💼 Management Outlook")
                    st.info(research.management_outlook)
                
                # Risks
                st.markdown("### ⚠️ Major Risks")
                for risk in research.major_risks:
                    st.warning(f"• {risk}")
        
        # TAB 4: Price Forecast
        with tab4:
            forecast = state.get('forecast')
            market_data = state.get('market_data')
            
            if forecast and market_data:
                # Forecast metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(
                        "Current Price",
                        f"₹{market_data.current_price:,.2f}"
                    )
                with col2:
                    st.metric(
                        "30-Day Target",
                        f"₹{forecast.predicted_price:,.2f}",
                        delta=f"{forecast.upside_percentage:+.2f}%"
                    )
                with col3:
                    st.metric(
                        "Confidence",
                        f"{forecast.confidence_score*100:.0f}%"
                    )
                with col4:
                    st.metric(
                        "Forecast Range",
                        f"₹{forecast.lower_band:,.0f} - ₹{forecast.upper_band:,.0f}"
                    )
                
                # Forecast chart with Technical Indicators
                historical = state.get('historical_prices')
                if historical is not None and not historical.empty:
                    # Ensure Date is a column
                    if 'Date' not in historical.columns:
                        historical = historical.reset_index()
                    
                    st.markdown("### 📈 Price Forecast with Technical Analysis")
                    
                    # Checkboxes for indicators
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        show_sma20 = st.checkbox("SMA 20", value=False, key="forecast_sma20")
                    with col2:
                        show_sma50 = st.checkbox("SMA 50", value=False, key="forecast_sma50")
                    with col3:
                        show_ema20 = st.checkbox("EMA 20", value=False, key="forecast_ema20")
                    with col4:
                        show_rsi = st.checkbox("RSI Bands", value=False, key="forecast_rsi")
                    
                    # Get last 6 months for display
                    recent_data = historical.tail(180).copy()
                    
                    # Calculate indicators on full data, then slice
                    from tools.technical_indicators import calculate_moving_averages
                    sma_data = calculate_moving_averages(historical['Close'])
                    historical_with_indicators = historical.copy()
                    historical_with_indicators['SMA_20'] = sma_data.get('sma_20')
                    historical_with_indicators['SMA_50'] = sma_data.get('sma_50')
                    historical_with_indicators['EMA_20'] = historical['Close'].ewm(span=20, adjust=False).mean()
                    
                    # Get recent data with indicators
                    recent_data = historical_with_indicators.tail(180)
                    
                    fig = go.Figure()
                    
                    # Historical prices
                    fig.add_trace(go.Scatter(
                        x=recent_data['Date'],
                        y=recent_data['Close'],
                        mode='lines',
                        name='Historical Price',
                        line=dict(color='#667eea', width=2)
                    ))
                    
                    # Add technical indicators based on checkboxes
                    if show_sma20:
                        fig.add_trace(go.Scatter(
                            x=recent_data['Date'],
                            y=recent_data['SMA_20'],
                            mode='lines',
                            name='SMA 20',
                            line=dict(color='orange', width=2)
                        ))
                    
                    if show_sma50:
                        fig.add_trace(go.Scatter(
                            x=recent_data['Date'],
                            y=recent_data['SMA_50'],
                            mode='lines',
                            name='SMA 50',
                            line=dict(color='purple', width=2)
                        ))
                    
                    if show_ema20:
                        fig.add_trace(go.Scatter(
                            x=recent_data['Date'],
                            y=recent_data['EMA_20'],
                            mode='lines',
                            name='EMA 20',
                            line=dict(color='cyan', width=2, dash='dash')
                        ))
                    
                    # Add RSI annotations
                    if show_rsi and market_data.rsi:
                        if market_data.rsi > 70:
                            fig.add_annotation(
                                x=recent_data['Date'].iloc[-1],
                                y=recent_data['Close'].max(),
                                text=f"⚠️ RSI Overbought ({market_data.rsi:.1f})",
                                showarrow=True,
                                arrowhead=2,
                                arrowcolor="red",
                                bgcolor="rgba(255,0,0,0.2)"
                            )
                        elif market_data.rsi < 30:
                            fig.add_annotation(
                                x=recent_data['Date'].iloc[-1],
                                y=recent_data['Close'].min(),
                                text=f"💡 RSI Oversold ({market_data.rsi:.1f})",
                                showarrow=True,
                                arrowhead=2,
                                arrowcolor="green",
                                bgcolor="rgba(0,255,0,0.2)"
                            )
                    
                    # Add current price point
                    fig.add_trace(go.Scatter(
                        x=[recent_data['Date'].iloc[-1]],
                        y=[market_data.current_price],
                        mode='markers',
                        name='Current Price',
                        marker=dict(color='yellow', size=10)
                    ))
                    
                    # Add forecast line
                    fig.add_trace(go.Scatter(
                        x=[recent_data['Date'].iloc[-1], recent_data['Date'].iloc[-1]],
                        y=[market_data.current_price, forecast.predicted_price],
                        mode='lines+markers',
                        name='Forecast',
                        line=dict(color='#38ef7d', width=3, dash='dash'),
                        marker=dict(size=10)
                    ))
                    
                    # Add confidence band
                    fig.add_trace(go.Scatter(
                        x=[recent_data['Date'].iloc[-1], recent_data['Date'].iloc[-1]],
                        y=[forecast.lower_band, forecast.upper_band],
                        fill='tonexty',
                        mode='none',
                        name='Confidence Band',
                        fillcolor='rgba(56, 239, 125, 0.2)'
                    ))
                    
                    fig.update_layout(
                        title='Price Forecast',
                        yaxis_title='Price (₹)',
                        xaxis_title='Date',
                        template='plotly_dark',
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Key driver
                st.info(f"**Key Driver:** {forecast.key_driver}")
        
        # TAB 5: Investment Report
        with tab5:
            report = state.get('report')
            if report:
                # Recommendation badge
                rec = report.recommendation
                if 'BUY' in rec:
                    st.markdown(f'<div class="recommendation-buy">🎯 {rec}</div>', unsafe_allow_html=True)
                elif 'SELL' in rec:
                    st.markdown(f'<div class="recommendation-sell">⚠️ {rec}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="recommendation-hold">⏸️ {rec}</div>', unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Executive Summary
                st.markdown("### 📋 Executive Summary")
                st.write(report.executive_summary)
                
                st.markdown("---")
                
                # Financial Snapshot
                st.markdown("### 💰 Financial Snapshot")
                st.info(report.financial_snapshot)
                
                # Two columns
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### ✅ Key Catalysts")
                    for catalyst in report.catalysts:
                        st.success(f"• {catalyst}")
                
                with col2:
                    st.markdown("### ⚠️ Risk Factors")
                    for risk in report.risks:
                        st.warning(f"• {risk}")
                
                st.markdown("---")
                
                # Forecast & Sentiment
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 📈 Forecast Summary")
                    st.write(report.forecast_summary)
                
                with col2:
                    st.markdown("### 📰 Sentiment Summary")
                    st.write(report.sentiment_summary)
                
                st.markdown("---")
                
                # Download buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    # PDF download
                    if st.button("📄 Download PDF Report", use_container_width=True):
                        output_dir = "output/generated_reports"
                        os.makedirs(output_dir, exist_ok=True)
                        filename = os.path.join(output_dir, f"{state.get('ticker', 'report')}_{datetime.now().strftime('%Y%m%d')}.pdf")
                        generate_pdf_report(state, filename)
                        st.success(f"✅ Report saved to {filename}")
                
                with col2:
                    # JSON download
                    json_data = {
                        "company": state.get('company_name'),
                        "ticker": state.get('ticker'),
                        "recommendation": rec,
                        "market_data": state.get('market_data').dict() if state.get('market_data') else {},
                        "sentiment": state.get('sentiment').dict() if state.get('sentiment') else {},
                        "forecast": state.get('forecast').dict() if state.get('forecast') else {},
                        "generated_at": datetime.now().isoformat()
                    }
                    
                    st.download_button(
                        label="💾 Download JSON Data",
                        data=json.dumps(json_data, indent=2, default=str),
                        file_name=f"{state.get('ticker', 'report')}_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json",
                        use_container_width=True
                    )


if __name__ == "__main__":
    main()
