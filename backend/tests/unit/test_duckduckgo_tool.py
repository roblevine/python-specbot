"""
Unit Tests for DuckDuckGo Search Tool

Tests the DuckDuckGo search tool including:
- Tool properties
- Input validation
- Error handling

Feature: 024-add-langchain-tools
Task: T042
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

from src.services.tools.duckduckgo import DuckDuckGoSearchTool
from src.services.tools.base import ToolResult


class TestDuckDuckGoToolProperties:
    """Test suite for tool properties."""

    def test_has_correct_id(self):
        """T042: Tool should have correct ID."""
        tool = DuckDuckGoSearchTool()
        assert tool.id == "duckduckgo-search"

    def test_has_correct_name(self):
        """T042: Tool should have human-readable name."""
        tool = DuckDuckGoSearchTool()
        assert tool.name == "Web Search"

    def test_has_description(self):
        """T042: Tool should have description for LLM context."""
        tool = DuckDuckGoSearchTool()
        assert "search" in tool.description.lower()
        assert len(tool.description) > 10


class TestDuckDuckGoToolExecution:
    """Test suite for tool execution."""

    @pytest.mark.asyncio
    async def test_returns_error_for_empty_query(self):
        """T042: Should return error for empty query."""
        tool = DuckDuckGoSearchTool()

        result = await tool.execute(query="")

        assert result.success is False
        assert result.error_code == "INVALID_ARGS"
        assert "empty" in result.error.lower()

    @pytest.mark.asyncio
    async def test_returns_error_for_whitespace_query(self):
        """T042: Should return error for whitespace-only query."""
        tool = DuckDuckGoSearchTool()

        result = await tool.execute(query="   ")

        assert result.success is False
        assert result.error_code == "INVALID_ARGS"

    @pytest.mark.asyncio
    async def test_returns_formatted_results_on_success(self):
        """T042: Should return formatted results with links on success."""
        tool = DuckDuckGoSearchTool()

        mock_results = [
            {
                "title": "Test Result 1",
                "href": "https://example.com/1",
                "body": "This is the first test result snippet.",
            },
            {
                "title": "Test Result 2",
                "href": "https://example.com/2",
                "body": "This is the second test result snippet.",
            },
        ]

        with patch.object(tool, "_search", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_results

            result = await tool.execute(query="test query")

            assert result.success is True
            assert "Test Result 1" in result.result
            assert result.links is not None
            assert len(result.links) == 2
            assert result.links[0]["url"] == "https://example.com/1"

    @pytest.mark.asyncio
    async def test_returns_no_results_message_when_empty(self):
        """T042: Should return appropriate message when no results found."""
        tool = DuckDuckGoSearchTool()

        with patch.object(tool, "_search", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = []

            result = await tool.execute(query="very obscure query")

            assert result.success is True
            assert "no results" in result.result.lower()
            assert result.links == []

    @pytest.mark.asyncio
    async def test_handles_timeout_error(self):
        """T042: Should handle timeout gracefully."""
        tool = DuckDuckGoSearchTool()

        with patch.object(tool, "_search", new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = asyncio.TimeoutError()

            result = await tool.execute(query="test query")

            assert result.success is False
            assert result.error_code == "TIMEOUT"
            assert "timed out" in result.error.lower()

    @pytest.mark.asyncio
    async def test_handles_import_error(self):
        """T042: Should handle missing dependency gracefully."""
        tool = DuckDuckGoSearchTool()

        with patch.object(tool, "_search", new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = ImportError("duckduckgo_search not found")

            result = await tool.execute(query="test query")

            assert result.success is False
            assert result.error_code == "EXECUTION_ERROR"

    @pytest.mark.asyncio
    async def test_handles_connection_error(self):
        """Should handle network/proxy connection errors gracefully."""
        tool = DuckDuckGoSearchTool()

        with patch.object(tool, "_search", new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = ConnectionError("Unable to connect to search service: tunnel error")

            result = await tool.execute(query="test query")

            assert result.success is False
            assert result.error_code == "CONNECTION_ERROR"
            assert "network restrictions" in result.error.lower() or "connect" in result.error.lower()

    @pytest.mark.asyncio
    async def test_handles_network_related_exception(self):
        """Should detect network errors from exception message."""
        tool = DuckDuckGoSearchTool()

        with patch.object(tool, "_search", new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = Exception("unsuccessful tunnel connection refused")

            result = await tool.execute(query="test query")

            assert result.success is False
            assert result.error_code == "CONNECTION_ERROR"


class TestDuckDuckGoToolLangChain:
    """Test suite for LangChain integration."""

    def test_to_langchain_tool_returns_structured_tool(self):
        """T042: Should convert to LangChain StructuredTool."""
        tool = DuckDuckGoSearchTool()

        lc_tool = tool.to_langchain_tool()

        assert lc_tool is not None
        assert lc_tool.name == "web_search"
        assert lc_tool.description == tool.description
