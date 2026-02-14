"""
News Sentiment Agent - Fetches news and performs sentiment analysis using FinBERT.
"""
import os
from typing import List, Dict
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
from models.schemas import AgentState, SentimentResult
from tools.news_tools import fetch_company_news

load_dotenv()

# Global variables for model caching
_finbert_model = None
_finbert_tokenizer = None


def load_finbert_model():
    """Load FinBERT model for sentiment analysis. Cached for performance."""
    global _finbert_model, _finbert_tokenizer
    
    if _finbert_model is None:
        try:
            print("📥 Loading FinBERT model from HuggingFace...")
            _finbert_tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
            _finbert_model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
            print("✅ FinBERT model loaded successfully")
        except Exception as e:
            print(f"⚠️ Error loading FinBERT: {str(e)}")
            return None
    
    return _finbert_model, _finbert_tokenizer


def analyze_sentiment_finbert(texts: List[str]) -> List[Dict]:
    """
    Analyze sentiment of texts using FinBERT.
    
    Args:
        texts: List of text strings to analyze
        
    Returns:
        List of sentiment results
    """
    try:
        model, tokenizer = load_finbert_model()
        if model is None:
            return [{"label": "neutral", "score": 0.5} for _ in texts]
        
        sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model=model,
            tokenizer=tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )
        
        results = []
        for text in texts:
            if not text or len(text.strip()) < 10:
                results.append({"label": "neutral", "score": 0.5})
                continue
            
            # Truncate long texts
            truncated_text = text[:512]
            result = sentiment_analyzer(truncated_text)[0]
            results.append(result)
        
        return results
    except Exception as e:
        print(f"⚠️ Error in sentiment analysis: {str(e)}")
        return [{"label": "neutral", "score": 0.5} for _ in texts]


def news_sentiment_agent(state: AgentState) -> AgentState:
    """
    Fetch news and analyze sentiment for a company.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with sentiment analysis
    """
    try:
        company_name = state.get("company_name", "")
        messages = state.get("messages", [])
        messages.append("🔄 News Sentiment Agent: Fetching news...")
        
        # Fetch news articles
        articles = fetch_company_news(company_name, num_articles=20)
        messages.append(f"📰 News Sentiment Agent: Found {len(articles)} articles")
        
        # Analyze sentiment
        texts_to_analyze = [
            f"{article['title']}. {article['description']}"
            for article in articles
            if article.get('title') or article.get('description')
        ]
        
        messages.append("🤖 News Sentiment Agent: Running FinBERT sentiment analysis...")
        sentiments = analyze_sentiment_finbert(texts_to_analyze)
        
        # Aggregate results
        positive_count = sum(1 for s in sentiments if s['label'].lower() == 'positive')
        negative_count = sum(1 for s in sentiments if s['label'].lower() == 'negative')
        neutral_count = sum(1 for s in sentiments if s['label'].lower() == 'neutral')
        
        # Calculate overall score (-1 to 1)
        total = len(sentiments) if sentiments else 1
        overall_score = (positive_count - negative_count) / total
        
        # Determine label
        if overall_score > 0.2:
            label = "Bullish"
        elif overall_score < -0.2:
            label = "Bearish"
        else:
            label = "Neutral"
        
        # Extract key events (top 5 most impactful headlines)
        key_events = []
        for i, (article, sentiment) in enumerate(zip(articles[:5], sentiments[:5])):
            title = article.get('title', 'No title')
            sentiment_label = sentiment['label'].upper()
            key_events.append(f"{sentiment_label}: {title}")
        
        # Create SentimentResult object
        sentiment_result = SentimentResult(
            total_articles=len(articles),
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count,
            overall_score=round(overall_score, 3),
            label=label,
            key_events=key_events
        )
        
        messages.append(f"✅ News Sentiment Agent: {label} sentiment ({overall_score:.2f})")
        
        return {
            **state,
            "sentiment": sentiment_result,
            "messages": messages,
            "current_agent": "news_sentiment"
        }
        
    except Exception as e:
        messages = state.get("messages", [])
        messages.append(f"❌ News Sentiment Agent Error: {str(e)}")
        return {
            **state,
            "messages": messages,
            "error": str(e)
        }
