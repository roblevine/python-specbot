"""
Tool Configuration Module

Manages tool configuration from environment variables.
Follows the same pattern as models.py for consistency.

Feature: 024-add-langchain-tools
Task: T014
"""

import json
import os
from typing import List, Optional

from pydantic import ValidationError

from src.schemas import ToolConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ToolConfigurationError(Exception):
    """Custom exception for tool configuration errors."""

    def __init__(self, message: str, help_text: Optional[str] = None):
        self.message = message
        self.help_text = help_text
        full_message = message
        if help_text:
            full_message = f"{message}\n\nHow to fix:\n{help_text}"
        super().__init__(full_message)


# Example tool configurations (for documentation/reference only)
# Tools are DISABLED by default - must be explicitly enabled via TOOLS env var
EXAMPLE_TOOLS = [
    {
        "id": "duckduckgo-search",
        "name": "Web Search",
        "description": "Search the web using DuckDuckGo",
        "enabled": True,
    },
    {
        "id": "web-browser",
        "name": "Browse URL",
        "description": "Fetch and read content from a web page",
        "enabled": True,
    },
]


def load_tool_configuration() -> List[ToolConfig]:
    """
    Load tool configuration from TOOLS environment variable.

    IMPORTANT: Tools are DISABLED by default for security and predictability.
    Administrators must explicitly enable tools via the TOOLS environment variable.

    If TOOLS is not set, returns empty list (no tools enabled).

    Environment variable format:
        TOOLS='[{"id": "duckduckgo-search", "name": "Web Search", "description": "...", "enabled": true}]'

    Returns:
        List[ToolConfig]: List of validated tool configurations (empty if TOOLS not set)

    Raises:
        ToolConfigurationError: If configuration is invalid
    """
    tools_json = os.getenv("TOOLS")

    if not tools_json:
        logger.info("TOOLS env var not set - all tools DISABLED by default")
        logger.info("To enable tools, set TOOLS environment variable with JSON array:")
        logger.info('  Example: TOOLS=\'[{"id": "duckduckgo-search", "name": "Web Search", "description": "Search the web", "enabled": true}]\'')
        return []

    # Parse TOOLS JSON
    try:
        tools_data = json.loads(tools_json)
        if not isinstance(tools_data, list):
            raise ToolConfigurationError(
                "TOOLS must be a JSON array",
                'Set TOOLS to a JSON array: \'[{"id": "tool-id", "name": "...", "description": "...", "enabled": true}]\''
            )
    except json.JSONDecodeError as e:
        raise ToolConfigurationError(
            f"Invalid JSON in TOOLS: {str(e)}",
            "Ensure TOOLS contains valid JSON."
        ) from e

    # Validate each tool config
    configs: List[ToolConfig] = []
    seen_ids: set = set()

    for i, tool_data in enumerate(tools_data):
        try:
            config = ToolConfig(**tool_data)

            # Check for duplicate IDs
            if config.id in seen_ids:
                raise ToolConfigurationError(
                    f"Duplicate tool ID '{config.id}' at index {i}",
                    "Each tool must have a unique ID."
                )
            seen_ids.add(config.id)

            configs.append(config)
        except ValidationError as e:
            raise ToolConfigurationError(
                f"Invalid tool configuration at index {i}: {str(e)}",
                "Each tool must have: id, name, description, enabled."
            ) from e

    logger.info(f"Loaded {len(configs)} tool configuration(s)")

    # Log enabled/disabled status
    enabled = [c.id for c in configs if c.enabled]
    disabled = [c.id for c in configs if not c.enabled]

    if enabled:
        logger.info(f"Enabled tools: {', '.join(enabled)}")
    if disabled:
        logger.info(f"Disabled tools: {', '.join(disabled)}")

    return configs


def get_enabled_tool_configs() -> List[ToolConfig]:
    """
    Get only enabled tool configurations.

    Returns:
        List[ToolConfig]: List of enabled tool configurations
    """
    all_configs = load_tool_configuration()
    return [c for c in all_configs if c.enabled]


def get_tool_config_by_id(tool_id: str) -> Optional[ToolConfig]:
    """
    Get a specific tool configuration by ID.

    Args:
        tool_id: Tool identifier

    Returns:
        ToolConfig if found, None otherwise
    """
    configs = load_tool_configuration()
    for config in configs:
        if config.id == tool_id:
            return config
    return None
