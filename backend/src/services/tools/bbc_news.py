"""
BBC News search tool using RSS feeds (free, no API key required).

Feature: 023-add-search-tools Task T023
"""

import logging
import os

import feedparser
from langchain_core.tools import tool

from .base import ToolResult

logger = logging.getLogger(__name__)

# BBC RSS feed URLs by category
BBC_FEEDS = {
    "top": "https://feeds.bbci.co.uk/news/rss.xml",
    "world": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "uk": "https://feeds.bbci.co.uk/news/uk/rss.xml",
    "business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "science": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    "health": "https://feeds.bbci.co.uk/news/health/rss.xml",
}


class BBCNewsTool:
    """BBC News search tool using RSS feeds (free, no API key).

    This tool provides BBC News search capabilities by parsing
    BBC's public RSS feeds.

    Configuration:
        TOOLS_BBC_NEWS_ENABLED: Set to 'false' to disable (default: 'true')
    """

    def __init__(self) -> None:
        """Initialize the BBC News tool."""
        self._enabled = os.getenv("TOOLS_BBC_NEWS_ENABLED", "true").lower() == "true"

    @property
    def id(self) -> str:
        """Unique tool identifier."""
        return "bbc_news"

    @property
    def name(self) -> str:
        """Human-readable tool name."""
        return "BBC News Search"

    @property
    def description(self) -> str:
        """Description for LLM to understand when to use tool."""
        return "Search BBC News for recent news articles on a topic"

    def is_enabled(self) -> bool:
        """Check if tool is enabled via environment variable."""
        return self._enabled

    async def execute(self, query: str = None, category: str = "top", **kwargs) -> ToolResult:
        """Search BBC News.

        Args:
            query: Search query string
            category: News category (top, world, uk, business, technology, science, health)
            **kwargs: Additional arguments (handles LLM variations like 'input', 'search_query')

        Returns:
            ToolResult with matching articles or error
        """
        # Handle different argument names that LLMs might use
        if query is None:
            query = kwargs.get('input') or kwargs.get('search_query') or kwargs.get('topic') or ''

        if not query:
            logger.warning(f"BBC News search called with empty query. kwargs={kwargs}")
            return ToolResult(
                success=False,
                content="No search query provided",
                error_code="EMPTY_QUERY"
            )

        if not self.is_enabled():
            logger.warning("BBC News tool invoked but is disabled")
            return ToolResult(
                success=False,
                content="BBC News search is not available",
                error_code="TOOL_DISABLED"
            )

        try:
            logger.info(f"Searching BBC News for: {query} (category: {category})")

            # Get the appropriate feed URL
            feed_url = BBC_FEEDS.get(category, BBC_FEEDS["top"])
            feed = feedparser.parse(feed_url)

            # Simple keyword matching against titles and summaries
            query_terms = query.lower().split()
            matches = []

            for entry in feed.entries[:20]:  # Check first 20 entries
                title = entry.get("title", "").lower()
                summary = entry.get("summary", "").lower()

                # Match if any query term appears in title or summary
                if any(term in title or term in summary for term in query_terms):
                    matches.append({
                        "title": entry.get("title"),
                        "url": entry.get("link"),
                        "snippet": entry.get("summary", "")[:200],
                        "published": entry.get("published"),
                    })

            if not matches:
                logger.info(f"No BBC News articles found for: {query}")
                return ToolResult(
                    success=True,
                    content="No BBC News articles found matching your query",
                    sources=[]
                )

            # Take top 5 matches
            sources = matches[:5]
            content = "\n".join(
                f"- {s['title']}: {s['snippet']}" for s in sources
            )

            logger.info(f"Found {len(sources)} BBC News articles for: {query}")

            return ToolResult(
                success=True,
                content=content,
                sources=sources
            )

        except Exception as e:
            logger.error(f"BBC News search failed for query '{query}': {e}")
            return ToolResult(
                success=False,
                content="BBC News search temporarily unavailable",
                error_code="TOOL_ERROR"
            )

    def as_langchain_tool(self):
        """Convert to LangChain tool format for model binding.

        Returns:
            LangChain tool that can be bound to an LLM
        """
        tool_instance = self

        @tool
        async def bbc_news_search(query: str) -> str:
            """Search BBC News for recent news articles on a topic.

            Args:
                query: The news topic to search for

            Returns:
                Recent BBC News articles matching the query
            """
            result = await tool_instance.execute(query=query)
            return result.content

        return bbc_news_search
