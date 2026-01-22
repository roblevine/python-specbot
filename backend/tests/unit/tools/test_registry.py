"""
Unit tests for ToolRegistry class.

Feature: 023-add-search-tools Task T005
TDD: Tests written first, must FAIL before implementation.
"""

import pytest
from src.services.tools.base import ToolResult


class MockTool:
    """Mock tool for testing registry."""

    def __init__(self, tool_id: str = "mock_tool", enabled: bool = True):
        self._id = tool_id
        self._enabled = enabled

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return "Mock Tool"

    @property
    def description(self) -> str:
        return "A mock tool for testing"

    def is_enabled(self) -> bool:
        return self._enabled

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(success=True, content="Mock result")


class TestToolRegistry:
    """Tests for ToolRegistry class."""

    def test_registry_can_be_instantiated(self):
        """ToolRegistry should be instantiable."""
        from src.services.tools.registry import ToolRegistry

        registry = ToolRegistry()
        assert registry is not None

    def test_registry_register_tool(self):
        """ToolRegistry should allow registering tools."""
        from src.services.tools.registry import ToolRegistry

        registry = ToolRegistry()
        tool = MockTool()

        registry.register(tool)

        # Should be able to get the tool back
        retrieved = registry.get("mock_tool")
        assert retrieved is tool

    def test_registry_get_returns_none_for_unknown(self):
        """ToolRegistry.get should return None for unknown tool IDs."""
        from src.services.tools.registry import ToolRegistry

        registry = ToolRegistry()

        result = registry.get("nonexistent_tool")
        assert result is None

    def test_registry_get_enabled_returns_only_enabled_tools(self):
        """ToolRegistry.get_enabled should only return enabled tools."""
        from src.services.tools.registry import ToolRegistry

        registry = ToolRegistry()
        enabled_tool = MockTool("enabled", enabled=True)
        disabled_tool = MockTool("disabled", enabled=False)

        registry.register(enabled_tool)
        registry.register(disabled_tool)

        enabled = registry.get_enabled()

        assert len(enabled) == 1
        assert enabled[0].id == "enabled"

    def test_registry_get_all_returns_all_tools(self):
        """ToolRegistry.get_all should return all registered tools."""
        from src.services.tools.registry import ToolRegistry

        registry = ToolRegistry()
        tool1 = MockTool("tool1")
        tool2 = MockTool("tool2")

        registry.register(tool1)
        registry.register(tool2)

        all_tools = registry.get_all()

        assert len(all_tools) == 2
        tool_ids = [t.id for t in all_tools]
        assert "tool1" in tool_ids
        assert "tool2" in tool_ids

    def test_registry_overwrite_existing_tool(self):
        """Registering a tool with same ID should overwrite."""
        from src.services.tools.registry import ToolRegistry

        registry = ToolRegistry()

        class Tool1(MockTool):
            @property
            def name(self) -> str:
                return "First Tool"

        class Tool2(MockTool):
            @property
            def name(self) -> str:
                return "Second Tool"

        tool1 = Tool1("same_id")
        tool2 = Tool2("same_id")

        registry.register(tool1)
        registry.register(tool2)

        retrieved = registry.get("same_id")
        assert retrieved.name == "Second Tool"

    def test_registry_empty_by_default(self):
        """New registry should have no tools."""
        from src.services.tools.registry import ToolRegistry

        registry = ToolRegistry()

        assert registry.get_all() == []
        assert registry.get_enabled() == []


class TestGlobalRegistry:
    """Tests for the global registry instance."""

    def test_global_registry_exists(self):
        """A global registry instance should be exported."""
        from src.services.tools.registry import registry

        assert registry is not None

    def test_global_registry_is_toolregistry(self):
        """Global registry should be a ToolRegistry instance."""
        from src.services.tools.registry import registry, ToolRegistry

        assert isinstance(registry, ToolRegistry)
