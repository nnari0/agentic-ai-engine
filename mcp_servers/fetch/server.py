"""MCP Web Fetch Server.

Exposes a `fetch_page` tool that downloads a web page and returns its
clean text content. Designed to run as a standalone SSE server so the
ADK summarizer agent can call it via McpToolset.

Run locally:
    python server.py

Docker:
    docker build -t mcp-fetch . && docker run -p 8002:8002 mcp-fetch
"""

import os

import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

HOST: str = os.getenv("MCP_HOST", "0.0.0.0")
PORT: int = int(os.getenv("MCP_PORT", "8002"))

mcp = FastMCP("web-fetch-server", host=HOST, port=PORT)

_REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; WebFetchMCPBot/1.0)"
    ),
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
}

_NOISE_TAGS = ["script", "style", "nav", "footer", "aside", "header", "noscript", "form"]


@mcp.tool()
async def fetch_page(url: str) -> str:
    """Fetch a web page and return its title and main text content.

    Strips navigation, scripts, and other non-content elements so the
    returned text is ready for the model to read and summarize.

    Args:
        url: Full URL of the page to fetch (e.g. https://example.com/article).

    Returns:
        Page title followed by the cleaned body text, or an error message.
    """
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30.0,
            headers=_REQUEST_HEADERS,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        return f"HTTP error {exc.response.status_code} fetching {url}"
    except httpx.RequestError as exc:
        return f"Request failed for {url}: {exc}"

    soup = BeautifulSoup(response.text, "lxml")

    for tag in soup(_NOISE_TAGS):
        tag.decompose()

    title = soup.title.get_text(strip=True) if soup.title else ""
    body_text = soup.get_text(separator="\n", strip=True)
    lines = [line for line in body_text.splitlines() if line.strip()]
    clean_text = "\n".join(lines)

    return f"# {title}\n\n{clean_text}" if title else clean_text


if __name__ == "__main__":
    mcp.run(transport="sse")
