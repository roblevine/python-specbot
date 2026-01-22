"""
Web search tool using DuckDuckGo (free, no API key required).

Feature: 023-add-search-tools Task T014
"""

import logging
import os
from urllib.parse import quote_plus

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

from .base import ToolResult

logger = logging.getLogger(__name__)


class WebSearchTool:
    """Web search tool using DuckDuckGo (free, no API key).

    This tool provides web search capabilities using the DuckDuckGo
    search engine via LangChain's community tools.

    Configuration:
        TOOLS_WEB_SEARCH_ENABLED: Set to 'false' to disable (default: 'true')
    """

    def __init__(self) -> None:
        """Initialize the web search tool."""
        self._search = DuckDuckGoSearchRun()
        self._enabled = os.getenv("TOOLS_WEB_SEARCH_ENABLED", "true").lower() == "true"

    @property
    def id(self) -> str:
        """Unique tool identifier."""
        return "web_search"

    @property
    def name(self) -> str:
        """Human-readable tool name."""
        return "Web Search"

    @property
    def description(self) -> str:
        """Description for LLM to understand when to use tool."""
        return "Search the web for current information about any topic"

    def is_enabled(self) -> bool:
        """Check if tool is enabled via environment variable."""
        return self._enabled

    async def execute(self, query: str) -> ToolResult:
        """Execute web search.

        Args:
            query: Search query string

        Returns:
            ToolResult with search results or error
        """
        if not self.is_enabled():
            logger.warning("Web search tool invoked but is disabled")
            return ToolResult(
                success=False,
                content="Web search is not available",
                error_code="TOOL_DISABLED"
            )

        try:
            logger.info(f"Executing web search for: {query}")

            # DuckDuckGo search - no API key needed
            result = self._search.invoke(query)

            logger.info(f"Web search completed successfully for: {query}")

            return ToolResult(
                success=True,
                content=result,
                sources=[{
                    "title": "DuckDuckGo Search",
                    "url": f"https://duckduckgo.com/?q={quote_plus(query)}"
                }]
            )

        except Exception as e:
            logger.error(f"Web search failed for query '{query}': {e}")
            return ToolResult(
                success=False,
                content="Web search temporarily unavailable",
                error_code="SEARCH_ERROR"
            )

    def as_langchain_tool(self):
        """Convert to LangChain tool format for model binding.

        Returns:
            LangChain tool that can be bound to an LLM
        """
        # Capture self for the closure
        tool_instance = self

        @tool
        async def web_search(query: str) -> str:
            """Search the web for current information about any topic.

            Args:
                query: The search query

            Returns:
                Search results with relevant information
            """
            result = await tool_instance.execute(query=query)
            return result.content

        return web_search
