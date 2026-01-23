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

import logging

from .base import BaseTool, ToolResult
from .errors import ToolDisabledError, ToolError, ToolExecutionError
from .registry import ToolRegistry, registry

logger = logging.getLogger(__name__)

# Optional tool imports - handle missing dependencies gracefully
try:
    from .web_search import WebSearchTool
    _web_search_available = True
except ImportError as e:
    logger.warning(f"WebSearchTool unavailable: {e}")
    WebSearchTool = None  # type: ignore
    _web_search_available = False

try:
    from .bbc_news import BBCNewsTool
    _bbc_news_available = True
except ImportError as e:
    logger.warning(f"BBCNewsTool unavailable: {e}")
    BBCNewsTool = None  # type: ignore
    _bbc_news_available = False


def _register_tools() -> None:
    """Register all available tools (only those with satisfied dependencies)."""
    if _web_search_available and WebSearchTool is not None:
        registry.register(WebSearchTool())
    if _bbc_news_available and BBCNewsTool is not None:
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
]

# Only export tools if available
if _web_search_available:
    __all__.append("WebSearchTool")
if _bbc_news_available:
    __all__.append("BBCNewsTool")
