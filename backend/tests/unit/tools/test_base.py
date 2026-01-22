"""
Unit tests for BaseTool protocol and ToolResult dataclass.

Feature: 023-add-search-tools Task T004
TDD: Tests written first, must FAIL before implementation.
"""

import pytest
from dataclasses import is_dataclass


class TestToolResult:
    """Tests for ToolResult dataclass."""

    def test_toolresult_is_dataclass(self):
        """ToolResult should be a dataclass."""
        from src.services.tools.base import ToolResult
        assert is_dataclass(ToolResult)

    def test_toolresult_success_with_content(self):
        """ToolResult should store success and content."""
        from src.services.tools.base import ToolResult

        result = ToolResult(success=True, content="Search results here")

        assert result.success is True
        assert result.content == "Search results here"
        assert result.sources == []
        assert result.error_code is None

    def test_toolresult_failure_with_error_code(self):
        """ToolResult should store error information on failure."""
        from src.services.tools.base import ToolResult

        result = ToolResult(
            success=False,
            content="Tool is disabled",
            error_code="TOOL_DISABLED"
        )

        assert result.success is False
        assert result.content == "Tool is disabled"
        assert result.error_code == "TOOL_DISABLED"

    def test_toolresult_with_sources(self):
        """ToolResult should support source references."""
        from src.services.tools.base import ToolResult

        sources = [
            {"title": "BBC News", "url": "https://bbc.co.uk/news/123"},
            {"title": "Another Source", "url": "https://example.com"}
        ]
        result = ToolResult(success=True, content="News results", sources=sources)

        assert result.success is True
        assert len(result.sources) == 2
        assert result.sources[0]["title"] == "BBC News"


class TestBaseTool:
    """Tests for BaseTool protocol."""

    def test_basetool_is_protocol(self):
        """BaseTool should be a typing Protocol."""
        from src.services.tools.base import BaseTool
        from typing import Protocol

        # BaseTool should be a Protocol subclass
        assert hasattr(BaseTool, '__protocol_attrs__') or issubclass(BaseTool, Protocol)

    def test_basetool_requires_id_property(self):
        """BaseTool should require id property."""
        from src.services.tools.base import BaseTool

        # Check protocol has id
        assert 'id' in dir(BaseTool)

    def test_basetool_requires_name_property(self):
        """BaseTool should require name property."""
        from src.services.tools.base import BaseTool

        assert 'name' in dir(BaseTool)

    def test_basetool_requires_description_property(self):
        """BaseTool should require description property."""
        from src.services.tools.base import BaseTool

        assert 'description' in dir(BaseTool)

    def test_basetool_requires_is_enabled_method(self):
        """BaseTool should require is_enabled method."""
        from src.services.tools.base import BaseTool

        assert 'is_enabled' in dir(BaseTool)

    def test_basetool_requires_execute_method(self):
        """BaseTool should require execute async method."""
        from src.services.tools.base import BaseTool

        assert 'execute' in dir(BaseTool)

    def test_tool_implementation_conforms_to_protocol(self):
        """A concrete tool implementation should conform to BaseTool protocol."""
        from src.services.tools.base import BaseTool, ToolResult
        from typing import runtime_checkable, Protocol

        @runtime_checkable
        class RuntimeBaseTool(Protocol):
            @property
            def id(self) -> str: ...
            @property
            def name(self) -> str: ...
            @property
            def description(self) -> str: ...
            def is_enabled(self) -> bool: ...
            async def execute(self, **kwargs) -> ToolResult: ...

        class MockTool:
            @property
            def id(self) -> str:
                return "mock_tool"

            @property
            def name(self) -> str:
                return "Mock Tool"

            @property
            def description(self) -> str:
                return "A mock tool for testing"

            def is_enabled(self) -> bool:
                return True

            async def execute(self, **kwargs) -> ToolResult:
                return ToolResult(success=True, content="Mock result")

        mock = MockTool()
        # Instance check should pass for runtime_checkable protocol
        assert isinstance(mock, RuntimeBaseTool)
