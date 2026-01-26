"""
Tool Registry

Manages available tools and provides loading/retrieval functions.
Tools are registered here and loaded based on configuration.

Feature: 024-add-langchain-tools
Task: T013
"""

from typing import Dict, List, Optional, Type

from src.utils.logger import get_logger
from src.services.tools.base import BaseTool

logger = get_logger(__name__)

# Registry of available tool classes by ID
# Tools are added here when implemented
TOOL_REGISTRY: Dict[str, Type[BaseTool]] = {}


def register_tool(tool_class: Type[BaseTool]) -> Type[BaseTool]:
    """
    Decorator to register a tool class in the registry.

    Usage:
        @register_tool
        class MyTool(BaseTool):
            ...
    """
    # Instantiate temporarily to get the ID
    try:
        instance = tool_class()
        tool_id = instance.id
        TOOL_REGISTRY[tool_id] = tool_class
        logger.debug(f"Registered tool: {tool_id}")
    except Exception as e:
        logger.error(f"Failed to register tool {tool_class.__name__}: {e}")
    return tool_class


def get_tool_class(tool_id: str) -> Optional[Type[BaseTool]]:
    """
    Get a tool class by ID.

    Args:
        tool_id: Tool identifier

    Returns:
        Tool class if found, None otherwise
    """
    return TOOL_REGISTRY.get(tool_id)


def get_available_tool_ids() -> List[str]:
    """
    Get list of all registered tool IDs.

    Returns:
        List of tool IDs
    """
    return list(TOOL_REGISTRY.keys())


def load_enabled_tools(tool_configs: List[dict]) -> List[BaseTool]:
    """
    Load tool instances based on configuration.

    Args:
        tool_configs: List of tool configuration dicts with id and enabled fields

    Returns:
        List of instantiated tool objects for enabled tools

    Logs:
        - Successfully loaded tools
        - Disabled tools (skipped)
        - Unknown tool IDs (warning)
        - Failed tool instantiation (error)
    """
    loaded_tools: List[BaseTool] = []
    disabled_tools: List[str] = []
    unknown_tools: List[str] = []
    failed_tools: List[str] = []

    for config in tool_configs:
        tool_id = config.get("id", "")
        enabled = config.get("enabled", True)

        if not enabled:
            disabled_tools.append(tool_id)
            continue

        tool_class = TOOL_REGISTRY.get(tool_id)
        if not tool_class:
            unknown_tools.append(tool_id)
            continue

        try:
            tool_instance = tool_class()
            loaded_tools.append(tool_instance)
            logger.info(f"Loaded tool: {tool_id} ({tool_instance.name})")
        except Exception as e:
            failed_tools.append(tool_id)
            logger.error(f"Failed to instantiate tool {tool_id}: {e}")

    # Log summary
    if disabled_tools:
        logger.info(f"Disabled tools (skipped): {', '.join(disabled_tools)}")
    if unknown_tools:
        logger.warning(f"Unknown tool IDs in config: {', '.join(unknown_tools)}")
    if failed_tools:
        logger.error(f"Failed to load tools: {', '.join(failed_tools)}")

    logger.info(f"Tool loading complete: {len(loaded_tools)} loaded, "
                f"{len(disabled_tools)} disabled, "
                f"{len(unknown_tools)} unknown, "
                f"{len(failed_tools)} failed")

    return loaded_tools


def get_langchain_tools(tools: List[BaseTool]) -> List:
    """
    Convert a list of BaseTool instances to LangChain tools.

    Args:
        tools: List of BaseTool instances

    Returns:
        List of LangChain-compatible tool objects
    """
    langchain_tools = []
    for tool in tools:
        try:
            lc_tool = tool.to_langchain_tool()
            langchain_tools.append(lc_tool)
        except Exception as e:
            logger.error(f"Failed to convert tool {tool.id} to LangChain format: {e}")
    return langchain_tools


# Import tools to register them (must be after TOOL_REGISTRY is defined)
# These imports will trigger the @register_tool decorator
def _register_builtin_tools():
    """Import builtin tools to register them."""
    try:
        from src.services.tools import duckduckgo  # noqa: F401
        from src.services.tools import browser  # noqa: F401
    except ImportError as e:
        logger.warning(f"Some builtin tools could not be imported: {e}")


# Auto-register builtin tools when this module is imported
_register_builtin_tools()
