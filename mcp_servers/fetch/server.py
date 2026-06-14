"""MCP Web Fetch Server.

Exposes a `fetch_page` tool that downloads a web page and returns its
clean text content. Designed to run as a standalone SSE server so the
ADK summarizer agent can call it via McpToolset.

Run locally:
    python server.py

Docker:
    docker build -t mcp-fetch . && docker run -p 8002:8002 mcp-fetch
"""

import ipaddress
import os
import socket
from urllib.parse import urlparse

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

# Cap on redirects we follow manually so each hop can be re-validated.
_MAX_REDIRECTS = 5


class _UnsafeUrlError(ValueError):
    """Raised when a URL targets a non-public or otherwise disallowed host."""


def _assert_safe_url(url: str) -> None:
    """Reject URLs that could be used for SSRF.

    Only ``http``/``https`` are allowed, and the host must resolve
    exclusively to public IP addresses.  This blocks access to the cloud
    metadata endpoint (169.254.169.254), loopback, and private/internal
    networks regardless of how the URL is spelled (IP, hostname, or a
    hostname that resolves to a private address).
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise _UnsafeUrlError(f"Unsupported URL scheme: {parsed.scheme or '(none)'}")

    host = parsed.hostname
    if not host:
        raise _UnsafeUrlError("URL has no host")

    try:
        addr_infos = socket.getaddrinfo(host, parsed.port or None)
    except socket.gaierror as exc:
        raise _UnsafeUrlError(f"Could not resolve host '{host}': {exc}") from exc

    for *_, sockaddr in addr_infos:
        ip = ipaddress.ip_address(sockaddr[0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            raise _UnsafeUrlError(
                f"Host '{host}' resolves to a non-public address ({ip}) – blocked"
            )


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
    # Follow redirects manually so every hop is re-validated — otherwise a
    # public URL could redirect to an internal/metadata address (SSRF).
    try:
        async with httpx.AsyncClient(
            follow_redirects=False,
            timeout=30.0,
            headers=_REQUEST_HEADERS,
        ) as client:
            current_url = url
            for _ in range(_MAX_REDIRECTS + 1):
                _assert_safe_url(current_url)
                response = await client.get(current_url)
                if response.is_redirect and response.headers.get("location"):
                    current_url = str(response.next_request.url)
                    continue
                response.raise_for_status()
                break
            else:
                return f"Too many redirects fetching {url}"
    except _UnsafeUrlError as exc:
        return f"Refused to fetch {url}: {exc}"
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
