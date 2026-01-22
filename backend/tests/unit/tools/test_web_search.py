"""
Unit tests for WebSearchTool.

Feature: 023-add-search-tools Task T012
TDD: Tests written first.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestWebSearchToolProperties:
    """Tests for WebSearchTool properties."""

    def test_web_search_tool_has_correct_id(self):
        """WebSearchTool should have id 'web_search'."""
        from src.services.tools.web_search import WebSearchTool

        tool = WebSearchTool()
        assert tool.id == "web_search"

    def test_web_search_tool_has_name(self):
        """WebSearchTool should have a human-readable name."""
        from src.services.tools.web_search import WebSearchTool

        tool = WebSearchTool()
        assert tool.name == "Web Search"

    def test_web_search_tool_has_description(self):
        """WebSearchTool should have a description for LLM."""
        from src.services.tools.web_search import WebSearchTool

        tool = WebSearchTool()
        assert "search" in tool.description.lower()
        assert len(tool.description) > 10


class TestWebSearchToolEnabled:
    """Tests for WebSearchTool enablement."""

    def test_enabled_by_default(self):
        """WebSearchTool should be enabled by default."""
        with patch.dict(os.environ, {}, clear=True):
            # Clear the env var if it exists
            os.environ.pop("TOOLS_WEB_SEARCH_ENABLED", None)

            from importlib import reload
            import src.services.tools.web_search as ws_module
            reload(ws_module)

            from src.services.tools.web_search import WebSearchTool
            tool = WebSearchTool()
            assert tool.is_enabled() is True

    def test_can_be_disabled_via_env(self):
        """WebSearchTool should respect TOOLS_WEB_SEARCH_ENABLED=false."""
        with patch.dict(os.environ, {"TOOLS_WEB_SEARCH_ENABLED": "false"}):
            from src.services.tools.web_search import WebSearchTool
            tool = WebSearchTool()
            assert tool.is_enabled() is False

    def test_enabled_when_env_true(self):
        """WebSearchTool should be enabled when TOOLS_WEB_SEARCH_ENABLED=true."""
        with patch.dict(os.environ, {"TOOLS_WEB_SEARCH_ENABLED": "true"}):
            from src.services.tools.web_search import WebSearchTool
            tool = WebSearchTool()
            assert tool.is_enabled() is True


class TestWebSearchToolExecution:
    """Tests for WebSearchTool execution."""

    @pytest.mark.asyncio
    async def test_execute_returns_tool_result(self):
        """execute() should return a ToolResult."""
        from src.services.tools.web_search import WebSearchTool
        from src.services.tools.base import ToolResult

        tool = WebSearchTool()

        # Mock the underlying search
        with patch.object(tool, '_search') as mock_search:
            mock_search.invoke.return_value = "Search results for weather"

            result = await tool.execute(query="weather in London")

            assert isinstance(result, ToolResult)
            assert result.success is True
            assert "Search results" in result.content

    @pytest.mark.asyncio
    async def test_execute_when_disabled_returns_error(self):
        """execute() should return error when tool is disabled."""
        with patch.dict(os.environ, {"TOOLS_WEB_SEARCH_ENABLED": "false"}):
            from src.services.tools.web_search import WebSearchTool

            tool = WebSearchTool()
            result = await tool.execute(query="test query")

            assert result.success is False
            assert result.error_code == "TOOL_DISABLED"

    @pytest.mark.asyncio
    async def test_execute_handles_search_errors(self):
        """execute() should handle search errors gracefully."""
        from src.services.tools.web_search import WebSearchTool

        tool = WebSearchTool()

        with patch.object(tool, '_search') as mock_search:
            mock_search.invoke.side_effect = Exception("Network error")

            result = await tool.execute(query="test query")

            assert result.success is False
            assert result.error_code == "SEARCH_ERROR"

    @pytest.mark.asyncio
    async def test_execute_includes_source_reference(self):
        """execute() should include DuckDuckGo as source."""
        from src.services.tools.web_search import WebSearchTool

        tool = WebSearchTool()

        with patch.object(tool, '_search') as mock_search:
            mock_search.invoke.return_value = "Some search results"

            result = await tool.execute(query="test")

            assert len(result.sources) >= 1
            assert "duckduckgo" in result.sources[0]["url"].lower()


class TestWebSearchToolLangChain:
    """Tests for LangChain integration."""

    def test_has_as_langchain_tool_method(self):
        """WebSearchTool should have as_langchain_tool method."""
        from src.services.tools.web_search import WebSearchTool

        tool = WebSearchTool()
        assert hasattr(tool, 'as_langchain_tool')
        assert callable(tool.as_langchain_tool)

    def test_as_langchain_tool_returns_structured_tool(self):
        """as_langchain_tool should return a LangChain StructuredTool."""
        from src.services.tools.web_search import WebSearchTool
        from langchain_core.tools import StructuredTool

        tool = WebSearchTool()
        lc_tool = tool.as_langchain_tool()

        # Should be a StructuredTool (which has name and description)
        assert isinstance(lc_tool, StructuredTool)
        assert lc_tool.name == "web_search"
