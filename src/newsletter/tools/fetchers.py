import os
import requests
import feedparser
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from newsletter.tools.parsers import clean_text

# --- Configurations ---
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, application/rss+xml, text/xml'
}

def fetch_rss_feed(feed_url: str, max_results: int = 3) -> List[Dict[str, str]]:
    """Generic parser for RSS/Atom feeds with intelligent abstract hunting."""
    try:
        response = requests.get(feed_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        
        if not feed.entries and feed.bozo:
            return [{"error": f"Parse Error. Snippet: {response.text[:100]}"}]

        results = []
        for entry in feed.entries[:max_results]:
            raw_abstract = "No abstract available."
            
            # Intelligent abstract hunting (DC, Content, Summary, Description)
            if 'dc_description' in entry and entry.dc_description:
                raw_abstract = entry.dc_description
            elif 'content' in entry and entry.content:
                raw_abstract = entry.content[0].value
            elif 'summary' in entry and entry.summary:
                raw_abstract = entry.summary
            elif 'description' in entry and entry.description:
                raw_abstract = entry.description
                
            summary = clean_text(raw_abstract)
            results.append({
                'title': entry.get('title', 'No Title'),
                'url': entry.get('link', 'No Link'),
                'content': summary[:500] + '...' if len(summary) > 500 else summary
            })
        return results
    except Exception as e:
        return [{"error": f"RSS Fetch Error: {str(e)}"}]

def fetch_doaj_keyword(keyword: str, max_results: int = 3) -> List[Dict[str, str]]:
    """Fetches immediate OA articles from DOAJ based on keywords."""
    safe_keyword = urllib.parse.quote(keyword)
    url = f'https://doaj.org/api/search/articles/{safe_keyword}'
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', [])[:max_results]:
            bib = item.get('bibjson', {})
            links = bib.get('link', [])
            abstract = clean_text(bib.get('abstract', 'No abstract available.'))
            
            results.append({
                'title': bib.get('title', 'No Title'),
                'url': links[0].get('url') if links else 'No URL',
                'content': abstract[:500] + '...' if len(abstract) > 500 else abstract
            })
        return results
    except Exception as e:
        return [{"error": f"DOAJ Error: {str(e)}"}]

def fetch_newsapi(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """Fetches general geoscience news from NewsAPI."""
    if not NEWS_API_KEY:
        return [{"error": "NEWS_API_KEY missing"}]
        
    url = f"https://newsapi.org/v2/everything?q={urllib.parse.quote(query)}&pageSize={max_results}&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        articles = response.json().get('articles', [])
        
        results = []
        for a in articles:
            desc = clean_text(str(a.get('description', 'No description available.')))
            results.append({
                'title': a.get('title', 'No Title'),
                'url': a.get('url', 'No URL'),
                'content': desc[:500] + '...' if len(desc) > 500 else desc
            })
        return results
    except Exception as e:
        return [{"error": f"NewsAPI Error: {str(e)}"}]

def search_arxiv(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """Parses Arxiv XML response for academic papers."""
    url = f"https://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(query)}&start=0&max_results={max_results}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        results = []
        for entry in root.findall('atom:entry', ns):
            summary = clean_text(entry.find('atom:summary', ns).text)
            results.append({
                "title": clean_text(entry.find('atom:title', ns).text),
                "url": entry.find('atom:id', ns).text,
                "content": summary[:500] + "..."
            })
        return results
    except Exception as e:
        return [{"error": f"Arxiv Error: {str(e)}"}]

def search_tavily(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Searches the web using Tavily. Optimized for LLMs, includes direct answers."""
    if not TAVILY_API_KEY:
        return [{"error": "TAVILY_API_KEY missing"}]

    url = "https://api.tavily.com/search"
    params = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "basic",
        "max_results": max_results,
        "include_images": False,
        "include_answer": True # Enabled from your new code
    }

    try:
        resp = requests.post(url, json=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = []
        # Inject the direct answer as the first result if available
        if data.get("answer"):
            results.append({
                "title": "Tavily AI Direct Answer",
                "url": "Tavily AI",
                "content": clean_text(data["answer"])
            })

        for r in data.get('results', []):
            results.append({
                "title": r.get('title', 'No Title'),
                "url": r.get('url', 'No URL'),
                "content": clean_text(r.get('content', ''))
            })
        return results
    except Exception as e:
        return [{"error": f"Tavily Error: {str(e)}"}]
