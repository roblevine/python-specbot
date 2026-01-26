"""
Unit Tests for Tool Configuration Loading

Tests the tool configuration system including:
- Default tool configuration
- Environment variable parsing
- Validation errors

Feature: 024-add-langchain-tools
Task: T041
"""

import json
import os
import pytest
from unittest.mock import patch

from src.config.tools import (
    load_tool_configuration,
    get_enabled_tool_configs,
    get_tool_config_by_id,
    ToolConfigurationError,
    DEFAULT_TOOLS,
)


class TestLoadToolConfiguration:
    """Test suite for load_tool_configuration function."""

    def test_returns_default_tools_when_env_not_set(self):
        """T041: Should return default tools when TOOLS env var is not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove TOOLS if present
            os.environ.pop("TOOLS", None)

            configs = load_tool_configuration()

            assert len(configs) == len(DEFAULT_TOOLS)
            assert configs[0].id == "duckduckgo-search"
            assert configs[1].id == "web-browser"
            assert all(c.enabled for c in configs)

    def test_parses_valid_json_config(self):
        """T041: Should parse valid JSON tool configuration."""
        custom_tools = [
            {
                "id": "custom-tool",
                "name": "Custom Tool",
                "description": "A custom tool",
                "enabled": True,
            }
        ]

        with patch.dict(os.environ, {"TOOLS": json.dumps(custom_tools)}):
            configs = load_tool_configuration()

            assert len(configs) == 1
            assert configs[0].id == "custom-tool"
            assert configs[0].name == "Custom Tool"
            assert configs[0].enabled is True

    def test_parses_disabled_tool(self):
        """T041: Should correctly parse disabled tools."""
        custom_tools = [
            {
                "id": "disabled-tool",
                "name": "Disabled Tool",
                "description": "This tool is disabled",
                "enabled": False,
            }
        ]

        with patch.dict(os.environ, {"TOOLS": json.dumps(custom_tools)}):
            configs = load_tool_configuration()

            assert len(configs) == 1
            assert configs[0].enabled is False

    def test_raises_error_for_invalid_json(self):
        """T041: Should raise ToolConfigurationError for invalid JSON."""
        with patch.dict(os.environ, {"TOOLS": "not valid json"}):
            with pytest.raises(ToolConfigurationError) as exc_info:
                load_tool_configuration()

            assert "Invalid JSON" in str(exc_info.value)

    def test_raises_error_for_non_array_json(self):
        """T041: Should raise error when TOOLS is not a JSON array."""
        with patch.dict(os.environ, {"TOOLS": '{"id": "tool"}'}):
            with pytest.raises(ToolConfigurationError) as exc_info:
                load_tool_configuration()

            assert "must be a JSON array" in str(exc_info.value)

    def test_raises_error_for_missing_required_fields(self):
        """T041: Should raise error when required fields are missing."""
        invalid_tools = [
            {
                "id": "incomplete-tool",
                # Missing name and description
            }
        ]

        with patch.dict(os.environ, {"TOOLS": json.dumps(invalid_tools)}):
            with pytest.raises(ToolConfigurationError) as exc_info:
                load_tool_configuration()

            assert "Invalid tool configuration" in str(exc_info.value)

    def test_raises_error_for_duplicate_ids(self):
        """T041: Should raise error for duplicate tool IDs."""
        duplicate_tools = [
            {
                "id": "same-id",
                "name": "Tool 1",
                "description": "First tool",
                "enabled": True,
            },
            {
                "id": "same-id",
                "name": "Tool 2",
                "description": "Second tool",
                "enabled": True,
            },
        ]

        with patch.dict(os.environ, {"TOOLS": json.dumps(duplicate_tools)}):
            with pytest.raises(ToolConfigurationError) as exc_info:
                load_tool_configuration()

            assert "Duplicate tool ID" in str(exc_info.value)


class TestGetEnabledToolConfigs:
    """Test suite for get_enabled_tool_configs function."""

    def test_returns_only_enabled_tools(self):
        """T041: Should return only tools with enabled=True."""
        mixed_tools = [
            {
                "id": "enabled-tool",
                "name": "Enabled",
                "description": "This is enabled",
                "enabled": True,
            },
            {
                "id": "disabled-tool",
                "name": "Disabled",
                "description": "This is disabled",
                "enabled": False,
            },
        ]

        with patch.dict(os.environ, {"TOOLS": json.dumps(mixed_tools)}):
            enabled = get_enabled_tool_configs()

            assert len(enabled) == 1
            assert enabled[0].id == "enabled-tool"


class TestGetToolConfigById:
    """Test suite for get_tool_config_by_id function."""

    def test_returns_tool_by_id(self):
        """T041: Should return tool config when ID exists."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("TOOLS", None)

            config = get_tool_config_by_id("duckduckgo-search")

            assert config is not None
            assert config.id == "duckduckgo-search"
            assert config.name == "Web Search"

    def test_returns_none_for_unknown_id(self):
        """T041: Should return None when tool ID doesn't exist."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("TOOLS", None)

            config = get_tool_config_by_id("nonexistent-tool")

            assert config is None
