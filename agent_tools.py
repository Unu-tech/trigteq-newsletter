import openai
from typing import List, Dict, Any
import os
import requests
import re
import xml.etree.ElementTree as ET
import qrcode
from qrcode.image.styledpil import StyledPilImage
from typing import Optional, Dict, List, Any, Tuple
from ddgs import DDGS  # pip install duckduckgo-search
import openai

# --- Configuration ---
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

def search_arxiv_raw(query: str, max_results: int = 5) -> List[Dict]:
    """Parses Arxiv XML response."""
    url = f"https://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    try:
        resp = requests.get(url, timeout=20)
        root = ET.fromstring(resp.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        results = []
        for entry in root.findall('atom:entry', ns):
            results.append({
                "title": entry.find('atom:title', ns).text.strip(),
                "summary": entry.find('atom:summary', ns).text.strip()[:500] + "...", # Truncate summary
                "link": entry.find('atom:id', ns).text
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]

def search_tavily_raw(query: str, max_results: int = 5) -> List[Dict]:
    """
    Searches the web using Tavily. Optimized for LLMs.
    """
    if not TAVILY_API_KEY:
        return [{"error": "Tavily API key is missing."}]
        
    url = "https://api.tavily.com/search"
    params = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "basic",
        "max_results": max_results,
        "include_images": False,
        "include_answer": True
    }
    
    try:
        resp = requests.post(url, json=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        results = []
        # Add the direct answer if available
        if data.get("answer"):
            results.append({
                "title": "Direct Answer",
                "content": data["answer"],
                "url": "Tavily AI"
            })
            
        for r in data.get('results', []):
            results.append({
                "title": r.get('title'),
                "content": r.get('content'),
                "url": r.get('url')
            })
        return results
    except Exception as e:
        return [{"error": f"Tavily search failed: {e}"}]

def search_arxiv_papers(query: str) -> str:
    """
    Searches Arxiv for scientific papers. Returns Title, Summary, and Link.
    Use this for technical, academic, or scientific queries.
    """
    results = search_arxiv_raw(query, max_results=3)
    
    # Format as a clean string for the LLM to read easily
    output = f"Found {len(results)} papers for '{query}':\n"
    for r in results:
        output += f"- {r['title']}\n  Summary: {r['summary']}\n  Link: {r['link']}\n\n"
    return output

def search_general_knowledge(query: str) -> str:
    """
    Performs a general web search for current events, news, or facts.
    Use this for: "Who is the CEO of OpenAI?", "Latest Python version?", "Stock market news".
    Do NOT use for: Restaurants (use find_places) or Academic papers (use search_arxiv).
    """
    results = search_tavily_raw(query, max_results=3)
    
    if results and "error" in results[0]:
        return f"Search Error: {results[0]['error']}"

    output = f"Web Search Results for '{query}':\n"
    for r in results:
        # Truncate content to avoid token overflow
        snippet = r.get('content', '')[:1000] 
        output += f"- {r['title']}\n  Snippet: {snippet}...\n  Source: {r['url']}\n\n"
        
    return output
