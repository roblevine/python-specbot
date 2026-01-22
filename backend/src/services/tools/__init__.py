"""
Tool subsystem for SpecBot chatbot.

Feature: 023-add-search-tools Task T010, T015

This module provides a modular tool architecture that enables
LLM-driven tool usage during conversations.

Usage:
    from src.services.tools import registry

    # Get all enabled tools
    enabled_tools = registry.get_enabled()

    # Get a specific tool
    web_search = registry.get("web_search")
"""

from .base import BaseTool, ToolResult
from .bbc_news import BBCNewsTool
from .errors import ToolDisabledError, ToolError, ToolExecutionError
from .registry import ToolRegistry, registry
from .web_search import WebSearchTool


def _register_tools() -> None:
    """Register all available tools."""
    registry.register(WebSearchTool())
    registry.register(BBCNewsTool())


_register_tools()

__all__ = [
    "BaseTool",
    "ToolResult",
    "ToolRegistry",
    "registry",
    "ToolError",
    "ToolDisabledError",
    "ToolExecutionError",
    "WebSearchTool",
    "BBCNewsTool",
]
