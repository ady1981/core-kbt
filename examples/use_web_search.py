import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

from kbt_core.ai_function_impl.research_agent.tavily_helper import web_search

load_dotenv()

def main():
    query = "machine learning applications in healthcare"
    results = web_search(query, limit_n=2)
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"URL: {result['url']}")
        print(f"Content preview: {result['content'][:200]}...")

if __name__ == "__main__":
    main()