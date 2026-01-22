"""
Unit tests for BBCNewsTool.

Feature: 023-add-search-tools Task T022
TDD: Tests written first.
"""

import os
from unittest.mock import MagicMock, patch

import pytest


class TestBBCNewsToolProperties:
    """Tests for BBCNewsTool properties."""

    def test_bbc_news_tool_has_correct_id(self):
        """BBCNewsTool should have id 'bbc_news'."""
        from src.services.tools.bbc_news import BBCNewsTool

        tool = BBCNewsTool()
        assert tool.id == "bbc_news"

    def test_bbc_news_tool_has_name(self):
        """BBCNewsTool should have a human-readable name."""
        from src.services.tools.bbc_news import BBCNewsTool

        tool = BBCNewsTool()
        assert tool.name == "BBC News Search"

    def test_bbc_news_tool_has_description(self):
        """BBCNewsTool should have a description for LLM."""
        from src.services.tools.bbc_news import BBCNewsTool

        tool = BBCNewsTool()
        assert "bbc" in tool.description.lower() or "news" in tool.description.lower()
        assert len(tool.description) > 10


class TestBBCNewsToolEnabled:
    """Tests for BBCNewsTool enablement."""

    def test_enabled_by_default(self):
        """BBCNewsTool should be enabled by default."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("TOOLS_BBC_NEWS_ENABLED", None)

            from importlib import reload
            import src.services.tools.bbc_news as bbc_module
            reload(bbc_module)

            from src.services.tools.bbc_news import BBCNewsTool
            tool = BBCNewsTool()
            assert tool.is_enabled() is True

    def test_can_be_disabled_via_env(self):
        """BBCNewsTool should respect TOOLS_BBC_NEWS_ENABLED=false."""
        with patch.dict(os.environ, {"TOOLS_BBC_NEWS_ENABLED": "false"}):
            from src.services.tools.bbc_news import BBCNewsTool
            tool = BBCNewsTool()
            assert tool.is_enabled() is False


class TestBBCNewsToolExecution:
    """Tests for BBCNewsTool execution."""

    @pytest.mark.asyncio
    async def test_execute_returns_tool_result(self):
        """execute() should return a ToolResult."""
        from src.services.tools.bbc_news import BBCNewsTool
        from src.services.tools.base import ToolResult

        tool = BBCNewsTool()

        # Mock feedparser response
        mock_feed = MagicMock()
        mock_feed.entries = [
            {
                "title": "Climate Change Update",
                "link": "https://bbc.co.uk/news/123",
                "summary": "Latest news about climate change impacts",
                "published": "2026-01-22",
            },
            {
                "title": "Environmental Report",
                "link": "https://bbc.co.uk/news/456",
                "summary": "New environmental report released",
                "published": "2026-01-21",
            },
        ]

        with patch('feedparser.parse', return_value=mock_feed):
            result = await tool.execute(query="climate")

            assert isinstance(result, ToolResult)
            assert result.success is True
            assert len(result.sources) > 0

    @pytest.mark.asyncio
    async def test_execute_when_disabled_returns_error(self):
        """execute() should return error when tool is disabled."""
        with patch.dict(os.environ, {"TOOLS_BBC_NEWS_ENABLED": "false"}):
            from src.services.tools.bbc_news import BBCNewsTool

            tool = BBCNewsTool()
            result = await tool.execute(query="test")

            assert result.success is False
            assert result.error_code == "TOOL_DISABLED"

    @pytest.mark.asyncio
    async def test_execute_handles_no_matches(self):
        """execute() should handle case where no articles match query."""
        from src.services.tools.bbc_news import BBCNewsTool

        tool = BBCNewsTool()

        mock_feed = MagicMock()
        mock_feed.entries = [
            {
                "title": "Sports News",
                "link": "https://bbc.co.uk/news/789",
                "summary": "Football match results",
                "published": "2026-01-22",
            },
        ]

        with patch('feedparser.parse', return_value=mock_feed):
            result = await tool.execute(query="zyxwvutsrq")  # Unlikely to match

            assert result.success is True
            assert "no" in result.content.lower() or len(result.sources) == 0

    @pytest.mark.asyncio
    async def test_execute_handles_parse_errors(self):
        """execute() should handle feedparser errors gracefully."""
        from src.services.tools.bbc_news import BBCNewsTool

        tool = BBCNewsTool()

        with patch('feedparser.parse', side_effect=Exception("Network error")):
            result = await tool.execute(query="test")

            assert result.success is False
            assert result.error_code == "TOOL_ERROR"


class TestBBCNewsToolCategories:
    """Tests for BBC News feed categories."""

    @pytest.mark.asyncio
    async def test_supports_category_parameter(self):
        """execute() should support category parameter."""
        from src.services.tools.bbc_news import BBCNewsTool

        tool = BBCNewsTool()

        mock_feed = MagicMock()
        mock_feed.entries = []

        with patch('feedparser.parse', return_value=mock_feed) as mock_parse:
            await tool.execute(query="test", category="technology")

            # Verify it tried to fetch from technology feed
            call_url = mock_parse.call_args[0][0]
            assert "technology" in call_url


class TestBBCNewsToolLangChain:
    """Tests for LangChain integration."""

    def test_has_as_langchain_tool_method(self):
        """BBCNewsTool should have as_langchain_tool method."""
        from src.services.tools.bbc_news import BBCNewsTool

        tool = BBCNewsTool()
        assert hasattr(tool, 'as_langchain_tool')
        assert callable(tool.as_langchain_tool)

    def test_as_langchain_tool_returns_structured_tool(self):
        """as_langchain_tool should return a LangChain StructuredTool."""
        from src.services.tools.bbc_news import BBCNewsTool
        from langchain_core.tools import StructuredTool

        tool = BBCNewsTool()
        lc_tool = tool.as_langchain_tool()

        assert isinstance(lc_tool, StructuredTool)
        assert lc_tool.name == "bbc_news_search"
