"""
Unit Tests for Tool Configuration Loading

Tests the tool configuration system including:
- Default-disabled behavior (no tools when TOOLS env var not set)
- Environment variable parsing
- Validation errors

Feature: 024-add-langchain-tools
Task: T041, T051
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
)


class TestLoadToolConfiguration:
    """Test suite for load_tool_configuration function."""

    def test_returns_default_tools_when_env_not_set(self):
        """T051: Tools should be DISABLED by default when TOOLS env var is not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove TOOLS if present
            os.environ.pop("TOOLS", None)

            configs = load_tool_configuration()

            # No tools should be loaded by default (disabled by default)
            assert len(configs) == 0, "Tools should be disabled by default when TOOLS env var is not set"

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

    def test_returns_empty_when_no_tools_configured(self):
        """T051: Should return empty list when TOOLS env var is not set."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("TOOLS", None)

            enabled = get_enabled_tool_configs()

            assert len(enabled) == 0, "No tools should be enabled by default"


class TestGetToolConfigById:
    """Test suite for get_tool_config_by_id function."""

    def test_returns_tool_by_id(self):
        """T041: Should return tool config when ID exists in TOOLS env var."""
        custom_tools = [
            {
                "id": "duckduckgo-search",
                "name": "Web Search",
                "description": "Search the web using DuckDuckGo",
                "enabled": True,
            }
        ]
        with patch.dict(os.environ, {"TOOLS": json.dumps(custom_tools)}):
            config = get_tool_config_by_id("duckduckgo-search")

            assert config is not None
            assert config.id == "duckduckgo-search"
            assert config.name == "Web Search"

    def test_returns_none_for_unknown_id(self):
        """T041: Should return None when tool ID doesn't exist."""
        custom_tools = [
            {
                "id": "some-other-tool",
                "name": "Other Tool",
                "description": "Some other tool",
                "enabled": True,
            }
        ]
        with patch.dict(os.environ, {"TOOLS": json.dumps(custom_tools)}):
            config = get_tool_config_by_id("nonexistent-tool")

            assert config is None

    def test_returns_none_when_no_tools_configured(self):
        """T051: Should return None when no tools are configured (default)."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("TOOLS", None)

            config = get_tool_config_by_id("duckduckgo-search")

            assert config is None, "No tools should exist when TOOLS env var is not set"
