"""
Base tool protocol and ToolResult dataclass.

Feature: 023-add-search-tools Tasks T006, T007
"""

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class ToolResult:
    """Result from tool execution.

    Attributes:
        success: Whether the tool executed successfully
        content: Result content or error message
        sources: List of source references (URLs, titles, etc.)
        error_code: Machine-readable error code if failed
    """

    success: bool
    content: str
    sources: list[dict[str, Any]] = field(default_factory=list)
    error_code: str | None = None


class BaseTool(Protocol):
    """Protocol for all tools.

    Tools must implement this protocol to be registered and used
    by the LLM service. The protocol follows the existing provider
    pattern in the codebase.
    """

    @property
    def id(self) -> str:
        """Unique tool identifier (e.g., 'web_search', 'bbc_news')."""
        ...

    @property
    def name(self) -> str:
        """Human-readable tool name (e.g., 'Web Search')."""
        ...

    @property
    def description(self) -> str:
        """Description for LLM to understand when to use tool."""
        ...

    def is_enabled(self) -> bool:
        """Check if tool is enabled and available for use."""
        ...

    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with given arguments.

        Args:
            **kwargs: Tool-specific arguments

        Returns:
            ToolResult with success status and content
        """
        ...
