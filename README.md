# 🔮 FinSight AI

**Multi-Agent Financial Intelligence Platform for Indian Stock Market Analysis**

FinSight AI is a production-ready AI-powered platform that provides comprehensive investment analysis for Indian stocks using multiple specialized AI agents working together.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## ✨ Features

### 🤖 **5 Specialized AI Agents**

1. **📊 Market Data Agent** - Real-time stock data, analyst targets, technical indicators
2. **📰 Sentiment Analysis Agent** - News analysis with FinBERT AI (20+ sources)
3. **🔍 Research Agent** - RAG-powered insights from PDFs + Gemini knowledge  
4. **📈 Forecast Agent** - 30-day price predictions using Prophet + sentiment
5. **📝 Report Generation Agent** - Professional investment recommendations

### 💡 **Key Capabilities**

- **Real-time Market Data**: Live prices, P/E ratios, 52-week ranges, market cap
- **Analyst Price Targets**: Mean/high/low targets with upside percentages
- **Technical Analysis**: RSI, MACD, SMA, EMA with interactive chart toggles
- **Sentiment Analysis**: Bullish/bearish scoring from financial news
- **Price Forecasting**: ML-based predictions with confidence bands
- **PDF Research**: RAG system for analyzing annual reports
- **Professional Reports**: BUY/HOLD/SELL recommendations with reasoning

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Google Gemini API key ([Get here](https://ai.google.dev/))
- NewsAPI key ([Get here](https://newsapi.org/))

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/finsight-ai.git
cd finsight-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### Configuration

Edit `.env` file:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
NEWS_API_KEY=your_news_api_key_here
```

### Run the Application

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501`

---

## 📖 Usage

### Basic Analysis

1. Enter a company name (e.g., "Reliance", "TCS", "Infosys")
2. Or use ticker symbols (e.g., "RELIANCE.NS", "TCS.NS")
3. Click **"Analyze Company"**
4. View results across 5 tabs:
   - **Market Overview**: Current price, analyst targets, candlestick chart
   - **Sentiment Analysis**: News sentiment with key events
   - **Research Insights**: AI-generated research summary
   - **Price Forecast**: 30-day prediction with technical indicators
   - **Investment Report**: Final BUY/HOLD/SELL recommendation

### Technical Indicators

In the **Forecast** tab, toggle indicators:
- ☑️ **SMA 20**: 20-day simple moving average (orange)
- ☑️ **SMA 50**: 50-day simple moving average (purple)
- ☑️ **EMA 20**: 20-day exponential moving average (cyan)
- ☑️ **RSI Bands**: Overbought (>70) / Oversold (<30) alerts

### Supported Companies

- **Auto-detection** for most NSE/BSE listed stocks
- **Pre-configured**: Reliance, TCS, Infosys, HDFC Bank, ICICI Bank, Airtel, Wipro, HCL Tech, LTIM, Kaynes Technology
- **Enter ticker directly**: `COMPANYNAME.NS` or `COMPANYNAME.BO`

---

## 🏗️ Architecture

### Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit |
| **LLM** | Google Gemini 2.5 Flash |
| **Multi-Agent** | LangGraph |
| **Embedding** | Google Gemini Embeddings |
| **Vector DB** | FAISS |
| **Sentiment** | FinBERT (Hugging Face) |
| **Forecasting** | Prophet + Linear Regression |
| **Market Data** | yfinance (Yahoo Finance) |
| **News** | NewsAPI |
| **Charts** | Plotly |

### Project Structure

```
finsight-ai/
├── agents/                  # AI agent implementations
│   ├── market_data_agent.py
│   ├── news_sentiment_agent.py
│   ├── research_agent.py
│   ├── forecast_agent.py
│   ├── report_agent.py
│   └── orchestrator.py      # LangGraph coordination
├── models/
│   └── schemas.py           # Pydantic data models
├── tools/
│   ├── stock_tools.py       # yfinance integration
│   ├── news_tools.py        # NewsAPI integration
│   └── technical_indicators.py
├── rag/
│   ├── vector_store.py      # FAISS vector DB
│   ├── ingest.py            # PDF processing
│   └── hybrid_search.py     # RAG retrieval
├── data/
│   └── reports/             # Place annual reports here (PDFs)
├── app.py                   # Streamlit frontend
├── requirements.txt
└── README.md
```

---

## 🔧 Advanced Configuration

### Add Custom Stock Tickers

Edit `tools/stock_tools.py`, line 131:

```python
indian_tickers = {
    "your company": "TICKER.NS",
    # Add more here
}
```

### Upload Annual Reports

1. Place PDF reports in `data/reports/`
2. App will automatically index them on startup
3. RAG agent will use them for research

### Prophet Forecasting

If Prophet fails, the system uses an advanced **linear regression fallback** with sentiment weighting for reliable predictions.

---

## 📊 Example Output

### Market Overview
- **Current Price**: ₹1,419.60
- **Analyst Target**: ₹1,716.50 (+20.9% upside)
- **37 analysts** covering the stock
- P/E Ratio, 52-week range, market cap

### Sentiment
- **Score**: +0.40 (Bullish)
- 20 articles analyzed
- Key events extracted

### Forecast
- **30-Day Target**: ₹1,450.00 (+2.1%)
- Confidence: 65%
- Key Driver: Linear trend with positive sentiment weighting

### Report
- **Recommendation**: BUY
- Executive summary with catalysts and risks

---

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:

- PDF export for reports
- Stock comparison feature
- Portfolio tracker
- Real-time alerts
- Sector analysis
- Enhanced fundamentals (P/B, ROE, Dividend Yield)

---



---

## ⚠️ Disclaimer

This software is for **educational and informational purposes only**. It is **not financial advice**. Always do your own research and consult with a qualified financial advisor before making investment decisions. The developers are not responsible for any financial losses incurred using this software.

---

## 🙏 Acknowledgments

- **Google Gemini** - LLM and embeddings
- **Prophet** - Time series forecasting
- **FinBERT** - Financial sentiment analysis
- **yfinance** - Market data
- **LangGraph** - Multi-agent orchestration
- **Streamlit** - Beautiful UI framework

---

## 📧 Contact

For questions, issues, or suggestions:
- Open an issue on GitHub
- Email: gopidhanavath1@gmail.com
  

---

**Built with ❤️ for the Indian stock market**
