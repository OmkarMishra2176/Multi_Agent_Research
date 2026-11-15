from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from rich import print
load_dotenv()

tavili = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query : str) -> str:
    """Retrieves up-to-date, credible information from across the web, delivering relevant 
    article titles, source URLs, and concise summaries for quick insights."""
    result = tavili.search(query = query , max_results = 3)
    
    out = []

    for r in result['results']:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:200]}\n"
        )
    
    return "\n----\n".join(out)


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:1800]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"