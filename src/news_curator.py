"""
News Curator - Ingests real-time financial news from trusted RSS and feeds
"""
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from src.config import TRUSTED_SOURCES

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_rss_feed(query: str, lang: str = "th", region: str = "TH", limit: int = 8) -> List[Dict[str, Any]]:
    """Fetch articles from Google News RSS feed for a specific query."""
    articles = []
    try:
        encoded_q = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_q}&hl={lang}&gl={region}&ceid={region}:{lang}"
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml_data = resp.read()
            
        root = ET.fromstring(xml_data)
        items = root.findall(".//item")
        
        for item in items[:limit]:
            title = item.find("title").text if item.find("title") is not None else ""
            link = item.find("link").text if item.find("link") is not None else ""
            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
            source_el = item.find("source")
            source_name = source_el.text if source_el is not None else "Financial News"
            
            # Clean title (Google News often appends ' - SourceName')
            clean_title = title.rsplit(" - ", 1)[0] if " - " in title else title
            
            articles.append({
                "title": clean_title.strip(),
                "source": source_name.strip(),
                "link": link.strip(),
                "pub_date": pub_date.strip()
            })
    except Exception as e:
        print(f"[NewsCurator] Error fetching query '{query}': {e}")
        
    return articles

def get_curated_raw_news() -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch both Thai and Global financial news across trusted regulatory and market domains.
    """
    # 1. Thai Market & Regulators (SET, BOT, SEC, NESDC, BOI)
    thai_query = "หุ้นไทย OR SET Index OR ธนาคารแห่งประเทศไทย OR ก.ล.ต. OR สภาพัฒน์ OR BOI"
    thai_articles = fetch_rss_feed(thai_query, lang="th", region="TH", limit=10)
    
    # 2. Global Economy & Commodities (Wall Street, Fed, Treasury, Oil, Gold)
    global_query = "Federal Reserve OR Wall Street OR Treasury Yield OR Crude Oil OR Inflation"
    global_articles = fetch_rss_feed(global_query, lang="en-US", region="US", limit=10)
    
    return {
        "thai_articles": thai_articles,
        "global_articles": global_articles
    }

if __name__ == "__main__":
    news = get_curated_raw_news()
    print(f"Fetched {len(news['thai_articles'])} Thai news and {len(news['global_articles'])} Global news.")
    for item in news['thai_articles'][:3]:
        print(f"- [{item['source']}] {item['title']}")
