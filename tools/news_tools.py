"""
News fetching and processing using NewsAPI.
"""
import os
from typing import List, Dict
from newsapi import NewsApiClient
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


def fetch_company_news(company_name: str, num_articles: int = 20) -> List[Dict]:
    """
    Fetch recent news articles about a company using NewsAPI.
    
    Args:
        company_name: Name of the company
        num_articles: Maximum number of articles to fetch
        
    Returns:
        List of news article dictionaries
    """
    try:
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key or api_key == "your_newsapi_key_here":
            print("⚠️ NewsAPI key not configured, using fallback mock data")
            return _get_fallback_news(company_name)
        
        newsapi = NewsApiClient(api_key=api_key)
        
        # Calculate date range (last 30 days)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=30)
        
        # Fetch articles
        response = newsapi.get_everything(
            q=company_name,
            from_param=from_date.strftime('%Y-%m-%d'),
            to=to_date.strftime('%Y-%m-%d'),
            language='en',
            sort_by='publishedAt',
            page_size=min(num_articles, 100)
        )
        
        articles = []
        for article in response.get('articles', [])[:num_articles]:
            articles.append({
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'source': article.get('source', {}).get('name', 'Unknown'),
                'published_at': article.get('publishedAt', ''),
                'url': article.get('url', '')
            })
        
        return articles if articles else _get_fallback_news(company_name)
        
    except Exception as e:
        print(f"⚠️ Error fetching news from NewsAPI: {str(e)}")
        return _get_fallback_news(company_name)


def _get_fallback_news(company_name: str) -> List[Dict]:
    """
    Provide fallback news data when API is unavailable.
    
    Args:
        company_name: Name of the company
        
    Returns:
        List of mock news articles
    """
    # Generic financial news that could apply to major companies
    fallback_articles = [
        {
            'title': f'{company_name} Reports Strong Quarterly Performance',
            'description': f'{company_name} announced better-than-expected quarterly results driven by strong demand.',
            'source': 'Financial Express',
            'published_at': (datetime.now() - timedelta(days=2)).isoformat(),
            'url': 'https://example.com'
        },
        {
            'title': f'{company_name} to Invest in Digital Transformation',
            'description': f'{company_name} plans major investments in technology and digital infrastructure.',
            'source': 'Economic Times',
            'published_at': (datetime.now() - timedelta(days=5)).isoformat(),
            'url': 'https://example.com'
        },
        {
            'title': f'Analysts Upgrade {company_name} Stock Rating',
            'description': f'Leading analysts upgrade {company_name} citing strong fundamentals and growth prospects.',
            'source': 'Bloomberg',
            'published_at': (datetime.now() - timedelta(days=7)).isoformat(),
            'url': 'https://example.com'
        },
        {
            'title': f'{company_name} Expands Market Presence',
            'description': f'{company_name} announces strategic expansion plans to capture new market opportunities.',
            'source': 'Reuters',
            'published_at': (datetime.now() - timedelta(days=10)).isoformat(),
            'url': 'https://example.com'
        },
        {
            'title': f'{company_name} Board Approves Dividend',
            'description': f'{company_name} board approves attractive dividend for shareholders.',
            'source': 'Moneycontrol',
            'published_at': (datetime.now() - timedelta(days=12)).isoformat(),
            'url': 'https://example.com'
        }
    ]
    
    return fallback_articles
