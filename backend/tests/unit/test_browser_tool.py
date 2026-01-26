"""
Unit Tests for Web Browser Tool

Tests the web browser tool including:
- Tool properties
- Input validation
- URL handling
- Error handling

Feature: 024-add-langchain-tools
Task: T043
"""

import pytest
from unittest.mock import patch, AsyncMock
import asyncio

from src.services.tools.browser import WebBrowserTool


class TestWebBrowserToolProperties:
    """Test suite for tool properties."""

    def test_has_correct_id(self):
        """T043: Tool should have correct ID."""
        tool = WebBrowserTool()
        assert tool.id == "web-browser"

    def test_has_correct_name(self):
        """T043: Tool should have human-readable name."""
        tool = WebBrowserTool()
        assert tool.name == "Browse URL"

    def test_has_description(self):
        """T043: Tool should have description for LLM context."""
        tool = WebBrowserTool()
        assert "web page" in tool.description.lower() or "url" in tool.description.lower()
        assert len(tool.description) > 10


class TestWebBrowserToolInputValidation:
    """Test suite for input validation."""

    @pytest.mark.asyncio
    async def test_returns_error_for_empty_url(self):
        """T043: Should return error for empty URL."""
        tool = WebBrowserTool()

        result = await tool.execute(url="")

        assert result.success is False
        assert result.error_code == "INVALID_ARGS"
        assert "empty" in result.error.lower()

    @pytest.mark.asyncio
    async def test_returns_error_for_whitespace_url(self):
        """T043: Should return error for whitespace-only URL."""
        tool = WebBrowserTool()

        result = await tool.execute(url="   ")

        assert result.success is False
        assert result.error_code == "INVALID_ARGS"

    @pytest.mark.asyncio
    async def test_returns_error_for_invalid_scheme(self):
        """T043: Should return error for non-http(s) URLs."""
        tool = WebBrowserTool()

        result = await tool.execute(url="ftp://example.com")

        assert result.success is False
        assert result.error_code == "INVALID_ARGS"
        assert "http" in result.error.lower()

    @pytest.mark.asyncio
    async def test_returns_error_for_invalid_url_format(self):
        """T043: Should return error for malformed URLs that can't be parsed."""
        tool = WebBrowserTool()

        # Use a URL with only scheme, no netloc - this can't be parsed
        result = await tool.execute(url="https://")

        assert result.success is False
        assert result.error_code == "INVALID_ARGS"

    @pytest.mark.asyncio
    async def test_adds_https_scheme_when_missing(self):
        """T043: Should add https:// scheme when missing."""
        tool = WebBrowserTool()

        # Mock the fetch to verify the URL was corrected
        with patch.object(tool, "_fetch_page", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = "Test content"

            result = await tool.execute(url="example.com")

            # Should have succeeded because the URL was corrected
            assert result.success is True


class TestWebBrowserToolExecution:
    """Test suite for tool execution."""

    @pytest.mark.asyncio
    async def test_returns_content_on_success(self):
        """T043: Should return page content on success."""
        tool = WebBrowserTool()

        with patch.object(tool, "_fetch_page", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = "This is the page content."

            result = await tool.execute(url="https://example.com")

            assert result.success is True
            assert "This is the page content." in result.result
            assert result.links is not None
            assert len(result.links) == 1
            assert result.links[0]["url"] == "https://example.com"

    @pytest.mark.asyncio
    async def test_truncates_long_content(self):
        """T043: Should truncate content that exceeds MAX_CONTENT_LENGTH."""
        tool = WebBrowserTool()

        long_content = "x" * 10000  # Much longer than MAX_CONTENT_LENGTH (4000)

        with patch.object(tool, "_fetch_page", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = long_content

            result = await tool.execute(url="https://example.com")

            assert result.success is True
            assert len(result.result) < len(long_content)
            assert "[Content truncated...]" in result.result

    @pytest.mark.asyncio
    async def test_handles_empty_page(self):
        """T043: Should handle empty page content gracefully."""
        tool = WebBrowserTool()

        with patch.object(tool, "_fetch_page", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = ""

            result = await tool.execute(url="https://example.com")

            assert result.success is True
            assert "empty" in result.result.lower()

    @pytest.mark.asyncio
    async def test_handles_timeout_error(self):
        """T043: Should handle timeout gracefully."""
        tool = WebBrowserTool()

        with patch.object(tool, "_fetch_page", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = asyncio.TimeoutError()

            result = await tool.execute(url="https://example.com")

            assert result.success is False
            assert result.error_code == "TIMEOUT"
            assert "timed out" in result.error.lower()

    @pytest.mark.asyncio
    async def test_handles_connection_error(self):
        """T043: Should handle connection errors gracefully."""
        tool = WebBrowserTool()

        with patch.object(tool, "_fetch_page", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = Exception("Connection refused")

            result = await tool.execute(url="https://example.com")

            assert result.success is False
            assert result.error_code == "CONNECTION_ERROR"


class TestWebBrowserToolLangChain:
    """Test suite for LangChain integration."""

    def test_to_langchain_tool_returns_structured_tool(self):
        """T043: Should convert to LangChain StructuredTool."""
        tool = WebBrowserTool()

        lc_tool = tool.to_langchain_tool()

        assert lc_tool is not None
        assert lc_tool.name == "browse_url"
        assert lc_tool.description == tool.description
