"""
Base Tool Interface

Defines the protocol for all tool implementations.
Tools must implement the execute method and provide metadata.

Feature: 024-add-langchain-tools
Task: T012
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ToolResult(BaseModel):
    """Result from a tool execution."""

    success: bool
    result: Optional[str] = None
    links: Optional[List[Dict[str, str]]] = None
    error: Optional[str] = None
    error_code: Optional[str] = None


class BaseTool(ABC):
    """
    Abstract base class for all tools.

    All tool implementations must inherit from this class and implement
    the required methods.
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """Unique tool identifier (e.g., 'duckduckgo-search')."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable display name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for LLM context."""
        pass

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """
        Execute the tool with the given arguments.

        Args:
            **kwargs: Tool-specific arguments

        Returns:
            ToolResult: Result of the tool execution
        """
        pass

    def to_langchain_tool(self):
        """
        Convert this tool to a LangChain tool format.

        Returns a callable that can be passed to LLM.bind_tools().
        """
        from langchain_core.tools import StructuredTool

        async def _run(**kwargs) -> str:
            result = await self.execute(**kwargs)
            if result.success:
                return result.result or "Tool completed successfully"
            else:
                return f"Error: {result.error}"

        return StructuredTool.from_function(
            coroutine=_run,
            name=self.id.replace("-", "_"),  # LangChain requires underscores
            description=self.description,
        )
