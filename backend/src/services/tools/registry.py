"""
Tool registry for managing and discovering tools.

Feature: 023-add-search-tools Task T008
"""

from typing import Dict

from .base import BaseTool


class ToolRegistry:
    """Registry for managing tools.

    Follows the same pattern as the provider registry in
    the existing codebase.
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool.

        Args:
            tool: Tool instance conforming to BaseTool protocol

        Note:
            If a tool with the same ID is already registered,
            it will be overwritten.
        """
        self._tools[tool.id] = tool

    def get(self, tool_id: str) -> BaseTool | None:
        """Get tool by ID.

        Args:
            tool_id: Unique tool identifier

        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(tool_id)

    def get_enabled(self) -> list[BaseTool]:
        """Get all enabled tools.

        Returns:
            List of tools where is_enabled() returns True
        """
        return [t for t in self._tools.values() if t.is_enabled()]

    def get_all(self) -> list[BaseTool]:
        """Get all registered tools.

        Returns:
            List of all registered tools regardless of enabled status
        """
        return list(self._tools.values())


# Global registry instance
registry = ToolRegistry()
