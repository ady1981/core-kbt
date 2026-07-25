import os

from dotenv import load_dotenv
from tavily import TavilyClient
import yaml

from .common import fetch_webpage_content

load_dotenv()

TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY')
client = TavilyClient(TAVILY_API_KEY)

tavily_client = TavilyClient(TAVILY_API_KEY)


def web_search(query: str, limit_n: int = 1) -> dict:
    """Search the web and return only raw content strings.
    
    Args:
        query: Search query to execute
        limit_n: Maximum number of results to return (default: 1)
    
    Returns:
        List of raw content strings from search results
    """
    search_results = tavily_client.search(    query=query,
                                              search_depth="advanced",
                                              max_results=limit_n
                                              )
    return [{'url': c['url'],
             'content': fetch_webpage_content(c['url'])}
            for c in search_results['results']]