"""
DuckDuckGo Search Tool

Web search tool using DuckDuckGo via langchain_community.
Returns structured results with links for display.

Feature: 024-add-langchain-tools
Task: T017
"""

import asyncio
from typing import Any, List, Optional

from src.services.tools.base import BaseTool, ToolResult
from src.services.tools import register_tool
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Timeout for search operations (seconds)
SEARCH_TIMEOUT = 30


@register_tool
class DuckDuckGoSearchTool(BaseTool):
    """
    Web search tool using DuckDuckGo.

    Uses langchain_community.tools.ddg_search.DuckDuckGoSearchResults
    for structured search results with links.
    """

    @property
    def id(self) -> str:
        return "duckduckgo-search"

    @property
    def name(self) -> str:
        return "Web Search"

    @property
    def description(self) -> str:
        return "Search the web using DuckDuckGo to find current information, news, and facts."

    async def execute(self, query: str = "", **kwargs: Any) -> ToolResult:
        """
        Execute a web search.

        Args:
            query: Search query string

        Returns:
            ToolResult with search results and links
        """
        if not query or not query.strip():
            return ToolResult(
                success=False,
                error="Search query cannot be empty",
                error_code="INVALID_ARGS"
            )

        query = query.strip()
        logger.info(f"Executing DuckDuckGo search: {query[:50]}...")

        try:
            # Import here to handle missing dependency gracefully
            from duckduckgo_search import DDGS

            # Run search with timeout
            results = await asyncio.wait_for(
                self._search(query),
                timeout=SEARCH_TIMEOUT
            )

            if not results:
                return ToolResult(
                    success=True,
                    result="No results found for your query.",
                    links=[]
                )

            # Format results for display
            formatted_results = []
            links = []

            for i, result in enumerate(results[:5], 1):  # Limit to 5 results
                title = result.get("title", "Untitled")
                url = result.get("href", result.get("link", ""))
                snippet = result.get("body", result.get("snippet", ""))

                formatted_results.append(f"{i}. {title}\n   {snippet[:200]}...")

                if url:
                    links.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet[:300] if snippet else None
                    })

            result_text = f"Found {len(results)} results for '{query}':\n\n" + "\n\n".join(formatted_results)

            logger.info(f"Search completed: {len(results)} results found")

            return ToolResult(
                success=True,
                result=result_text,
                links=links
            )

        except asyncio.TimeoutError:
            logger.error(f"Search timed out after {SEARCH_TIMEOUT}s")
            return ToolResult(
                success=False,
                error="Search timed out. Please try again.",
                error_code="TIMEOUT"
            )
        except ImportError as e:
            logger.error(f"DuckDuckGo search dependency not installed: {e}")
            return ToolResult(
                success=False,
                error="Search service is not available.",
                error_code="EXECUTION_ERROR"
            )
        except ConnectionError as e:
            logger.error(f"Connection error during search: {e}")
            return ToolResult(
                success=False,
                error="Unable to connect to search service. This may be due to network restrictions or firewall settings.",
                error_code="CONNECTION_ERROR"
            )
        except Exception as e:
            logger.error(f"Search failed: {type(e).__name__}: {e}")

            # Check for network-related errors
            error_str = str(e).lower()
            if any(x in error_str for x in ["connection", "network", "timeout", "refused", "tunnel", "unreachable"]):
                return ToolResult(
                    success=False,
                    error="Unable to connect to search service. This may be due to network restrictions or firewall settings.",
                    error_code="CONNECTION_ERROR"
                )

            return ToolResult(
                success=False,
                error=f"Search failed: {str(e)}",
                error_code="EXECUTION_ERROR"
            )

    async def _search(self, query: str, max_results: int = 5) -> List[dict]:
        """
        Perform the actual search using DuckDuckGo.

        Args:
            query: Search query
            max_results: Maximum number of results to return

        Returns:
            List of search result dictionaries

        Raises:
            ConnectionError: If unable to connect to DuckDuckGo
            Exception: For other search errors
        """
        from duckduckgo_search import DDGS
        from duckduckgo_search.exceptions import DuckDuckGoSearchException

        # Run sync operation in thread pool
        def _sync_search():
            try:
                with DDGS() as ddgs:
                    # Use region parameter for better results
                    # wt-wt = worldwide, us-en = US English, uk-en = UK English
                    results = list(ddgs.text(
                        query,
                        max_results=max_results,
                        region="wt-wt"  # Worldwide results
                    ))
                    logger.debug(f"DuckDuckGo raw results count: {len(results)}")
                    if results:
                        logger.debug(f"First result keys: {results[0].keys() if results else 'N/A'}")
                    return results
            except DuckDuckGoSearchException as e:
                error_str = str(e).lower()
                # Detect network/proxy/connection errors
                if any(x in error_str for x in ["connect", "tunnel", "network", "timeout", "refused", "unreachable"]):
                    logger.error(f"DuckDuckGo connection error: {e}")
                    raise ConnectionError(f"Unable to connect to search service: {e}")
                logger.error(f"DuckDuckGo search error: {type(e).__name__}: {e}")
                raise
            except Exception as e:
                logger.error(f"DuckDuckGo search error in sync: {type(e).__name__}: {e}")
                raise

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, _sync_search)
        return results

    def to_langchain_tool(self):
        """
        Convert to LangChain tool format.

        Uses a custom function wrapper for proper async handling.
        """
        from langchain_core.tools import StructuredTool
        from pydantic import BaseModel, Field

        class SearchInput(BaseModel):
            query: str = Field(description="The search query to find information on the web")

        async def _search(query: str) -> str:
            result = await self.execute(query=query)
            if result.success:
                return result.result or "Search completed."
            else:
                return f"Error: {result.error}"

        return StructuredTool.from_function(
            coroutine=_search,
            name="web_search",
            description=self.description,
            args_schema=SearchInput,
        )
