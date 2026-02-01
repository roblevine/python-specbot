"""
Web Browser Tool

Fetches and reads content from web pages using BeautifulSoup.
Extracts readable text content and truncates for LLM context limits.

Feature: 024-add-langchain-tools
Task: T018
"""

import asyncio
from typing import Any
from urllib.parse import urlparse

from src.services.tools.base import BaseTool, ToolResult
from src.services.tools import register_tool
from src.utils.logger import get_logger
from src.utils.ssrf_protection import validate_url_for_ssrf, SSRFProtectionError

logger = get_logger(__name__)

# Timeout for browser operations (seconds)
BROWSER_TIMEOUT = 60

# Maximum content length to return (characters)
MAX_CONTENT_LENGTH = 4000


@register_tool
class WebBrowserTool(BaseTool):
    """
    Web browser tool for fetching and reading web page content.

    Uses requests + BeautifulSoup for lightweight page fetching.
    Extracts readable text and truncates to fit LLM context limits.
    """

    @property
    def id(self) -> str:
        return "web-browser"

    @property
    def name(self) -> str:
        return "Browse URL"

    @property
    def description(self) -> str:
        return "Fetch and read content from a web page URL to get detailed information."

    async def execute(self, url: str = "", **kwargs: Any) -> ToolResult:
        """
        Fetch and read content from a URL.

        Args:
            url: URL to fetch

        Returns:
            ToolResult with page content
        """
        if not url or not url.strip():
            return ToolResult(
                success=False,
                error="URL cannot be empty",
                error_code="INVALID_ARGS"
            )

        url = url.strip()

        # Add https:// if no scheme provided
        parsed = urlparse(url)
        if not parsed.scheme:
            url = "https://" + url
            parsed = urlparse(url)

        # Validate URL format and check for SSRF vulnerabilities
        try:
            hostname, resolved_ip = validate_url_for_ssrf(url)
            logger.info(f"URL validated: {hostname} -> {resolved_ip}")
        except SSRFProtectionError as e:
            logger.warning(f"URL blocked by SSRF protection: {e}")
            return ToolResult(
                success=False,
                error=f"URL access denied: {str(e)}",
                error_code="INVALID_ARGS"
            )
        except Exception as e:
            logger.error(f"URL validation failed: {e}")
            return ToolResult(
                success=False,
                error="Invalid URL format.",
                error_code="INVALID_ARGS"
            )

        logger.info(f"Fetching URL: {url[:100]}...")

        try:
            # Fetch page content with timeout
            content = await asyncio.wait_for(
                self._fetch_page(url),
                timeout=BROWSER_TIMEOUT
            )

            if not content:
                return ToolResult(
                    success=True,
                    result="The page appears to be empty or could not be read.",
                    links=[]
                )

            # Truncate if too long
            if len(content) > MAX_CONTENT_LENGTH:
                content = content[:MAX_CONTENT_LENGTH] + "\n\n[Content truncated...]"

            logger.info(f"Page fetched: {len(content)} characters")

            return ToolResult(
                success=True,
                result=f"Content from {parsed.netloc}:\n\n{content}",
                links=[{
                    "title": f"Source: {parsed.netloc}",
                    "url": url,
                    "snippet": content[:200] if content else None
                }]
            )

        except asyncio.TimeoutError:
            logger.error(f"Page fetch timed out after {BROWSER_TIMEOUT}s")
            return ToolResult(
                success=False,
                error="Page fetch timed out. The server may be slow or unresponsive.",
                error_code="TIMEOUT"
            )
        except ImportError as e:
            logger.error(f"Browser dependency not installed: {e}")
            return ToolResult(
                success=False,
                error="Browser service is not available.",
                error_code="EXECUTION_ERROR"
            )
        except Exception as e:
            logger.error(f"Page fetch failed: {type(e).__name__}: {e}")

            # Check for network-related errors
            error_str = str(e).lower()
            if any(x in error_str for x in ["connection", "network", "refused", "reset"]):
                return ToolResult(
                    success=False,
                    error="Unable to connect to the website. The server may be down.",
                    error_code="CONNECTION_ERROR"
                )
            if "timeout" in error_str:
                return ToolResult(
                    success=False,
                    error="Connection timed out.",
                    error_code="TIMEOUT"
                )
            if any(x in error_str for x in ["404", "not found"]):
                return ToolResult(
                    success=False,
                    error="Page not found.",
                    error_code="EXECUTION_ERROR"
                )
            if any(x in error_str for x in ["403", "forbidden", "401", "unauthorized"]):
                return ToolResult(
                    success=False,
                    error="Access to this page is restricted.",
                    error_code="EXECUTION_ERROR"
                )

            return ToolResult(
                success=False,
                error=f"Failed to fetch page: {str(e)}",
                error_code="EXECUTION_ERROR"
            )

    async def _fetch_page(self, url: str) -> str:
        """
        Fetch and extract text content from a URL.

        Args:
            url: URL to fetch

        Returns:
            Extracted text content
        """
        import requests
        from bs4 import BeautifulSoup

        # Run sync operation in thread pool
        def _sync_fetch():
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; SpecBot/1.0; +http://example.com/bot)"
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text

        loop = asyncio.get_event_loop()
        html = await loop.run_in_executor(None, _sync_fetch)

        # Extract text content
        soup = BeautifulSoup(html, "lxml")

        # Remove script and style elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
            element.decompose()

        # Extract text from main content tags
        main_content = soup.find("main") or soup.find("article") or soup.body or soup

        if main_content:
            # Get text with reasonable spacing
            text = main_content.get_text(separator="\n", strip=True)

            # Clean up excessive whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = "\n".join(lines)

            return text

        return ""

    def to_langchain_tool(self):
        """
        Convert to LangChain tool format.
        """
        from langchain_core.tools import StructuredTool
        from pydantic import BaseModel, Field

        class BrowseInput(BaseModel):
            url: str = Field(description="The URL of the web page to read")

        async def _browse(url: str) -> str:
            result = await self.execute(url=url)
            if result.success:
                return result.result or "Page fetched successfully."
            else:
                return f"Error: {result.error}"

        return StructuredTool.from_function(
            coroutine=_browse,
            name="browse_url",
            description=self.description,
            args_schema=BrowseInput,
        )
