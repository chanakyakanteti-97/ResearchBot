"""
Tools available to the AI Agent.

Each function here is something the agent can CHOOSE to call on its own.
The agent decides: what to search, which pages to read, when to stop.
"""

import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS


def web_search(query: str) -> str:
    """
    Search the web using DuckDuckGo (no API key needed).
    Returns top 5 results as formatted text.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))

        if not results:
            return "No search results found for this query."

        output = f"Search results for: '{query}'\n\n"
        for i, r in enumerate(results, 1):
            output += f"[{i}] {r['title']}\n"
            output += f"    URL: {r['href']}\n"
            output += f"    Summary: {r['body']}\n\n"

        return output

    except Exception as e:
        return f"Search failed: {str(e)}"


def read_webpage(url: str) -> str:
    """
    Fetch and extract clean text from a webpage.
    Strips all HTML, ads, nav bars — just the main content.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove noise elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()

        # Extract clean text
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if len(line.strip()) > 40]
        clean_text = "\n".join(lines)

        # Limit length so we don't overflow the LLM context
        from app.config import MAX_WEBPAGE_CHARS
        if len(clean_text) > MAX_WEBPAGE_CHARS:
            clean_text = clean_text[:MAX_WEBPAGE_CHARS] + "\n\n[...content truncated...]"

        return f"Content from {url}:\n\n{clean_text}"

    except requests.exceptions.Timeout:
        return f"Timeout reading {url} — page took too long to load."
    except requests.exceptions.HTTPError as e:
        return f"HTTP error reading {url}: {e}"
    except Exception as e:
        return f"Could not read {url}: {str(e)}"


# Map tool name → actual function
# The agent calls tools by name — this is how we execute them
TOOL_REGISTRY = {
    "web_search": web_search,
    "read_webpage": read_webpage,
}


def execute_tool(name: str, args: dict) -> str:
    """Execute a tool by name with given arguments."""
    if name not in TOOL_REGISTRY:
        return f"Unknown tool: {name}"
    return TOOL_REGISTRY[name](**args)
